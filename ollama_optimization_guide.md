# Ollama 效能優化指南 (針對 RTX 5060 Ti 16GB VRAM)

本指南彙整了網路上的最佳實踐，旨在幫助擁有 16GB VRAM 顯示卡 (如 NVIDIA RTX 5060 Ti / RTX 4060 Ti 16G / RTX 4080 16G) 的使用者，最大化 Ollama 在本地端的推論效能。

## 1. 硬體資源與模型選擇 (16GB VRAM 的極限與甜區)

對於本地大型語言模型 (LLM) 推論，**VRAM 大小是最關鍵的瓶頸**。模型如果能完全載入 VRAM (GPU)，速度將是載入到系統記憶體 (CPU) 的 10 倍以上。

根據 16GB VRAM 的容量，以下是不同參數量級模型的建議配置：

*   **7B - 8B 模型 (如 Llama 3 8B, Qwen 2.5 7B, Mistral 7B)**
    *   **狀態**：非常輕鬆。
    *   **量化等級**：可以無壓力使用無量化 (FP16) 或高精度的 `Q8_0` 量化模型。
    *   **效能**：極高，通常能達到 80~100+ tokens/sec。支援超長上下文 (Context Window)。
*   **13B - 14B 模型 (如 Qwen 2.5 14B)**
    *   **狀態**：甜區 (Sweet Spot)，兼具高品質與高效能。
    *   **量化等級**：建議使用 `Q6_K` 或 `Q8_0`。
    *   **效能**：依然能完全塞進 VRAM，保有極快的推論速度。
*   **20B - 24B 模型 (如 Mistral Small 24B, Command R)**
    *   **狀態**：適合。
    *   **量化等級**：強烈建議使用 `Q4_K_M` 或 `Q5_K_M` 量化。
    *   **效能**：在 16GB VRAM 中剛好能完全載入，生成速度依然非常流暢。
*   **32B - 35B 模型 (如 Qwen 2.5 32B, Llama 3 70B 的極度量化版)**
    *   **狀態**：吃力/緊繃。
    *   **量化等級**：必須使用 `Q4_K_M` 或更低 (如 `Q3_K_M`)。
    *   **效能**：大約佔用 18-22 GB，這意味著 16GB VRAM 無法完全容納。模型會被分割 (GPU + CPU Hybrid)，部分層數會卸載到系統 RAM 中。推論速度會顯著下降 (可能降至 10-20 tokens/sec 或更低)。

**總結建議：** 為了獲得最佳的互動體驗，建議優先選擇 **14B 到 24B 的模型**，並搭配 **`Q4_K_M` 到 `Q6_K` 的 GGUF 量化格式**，以確保模型能 100% 在 GPU 內執行。

---

## 2. Ollama 核心參數優化 (Runtime Parameters)

您可以透過 API 請求、命令列參數或撰寫自訂的 `Modelfile` 來調整以下參數，以提升效能與資源利用率。

### 2.1 記憶體常駐設定 (`OLLAMA_KEEP_ALIVE`)

**問題**：Ollama 預設在閒置 5 分鐘後會將模型從 VRAM 中卸載。下次呼叫時需要重新載入模型，導致第一次請求的延遲極高 (可能長達 5~10 秒)。
**解決方案**：延長或永久保持模型在 VRAM 中的常駐時間。
*   **設定方式 (環境變數)**：
    *   Windows (PowerShell): `[Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "-1", "User")`
    *   Linux / macOS (Terminal): `export OLLAMA_KEEP_ALIVE="-1"` (或設定為 `24h`)
    *   Docker: `docker run -e OLLAMA_KEEP_ALIVE=-1 ...`
*   **效果**：將值設為 `-1` 代表永久保留在記憶體中。這對頻繁進行對話或短時間內多次 API 呼叫的應用程式 (如 AI 狼人殺的連續發言) 來說，能大幅降低回應延遲。

### 2.2 上下文長度 (`num_ctx`)

**問題**：預設的上下文長度可能太短 (如 2048) 或不必要地太長 (佔用大量 VRAM)。
**解決方案**：根據您的實際需求設定適當的上下文長度。上下文越長，佔用的 VRAM 就越大。
*   **設定方式** (Modelfile / API):
    ```json
    // API 呼叫範例
    {
      "model": "llama3",
      "prompt": "Hello",
      "options": {
        "num_ctx": 4096  // 或 8192, 視對話歷史長度而定
      }
    }
    ```
*   **注意**：如果您發現載入 32B 模型時 OOM (Out of Memory)，可以嘗試調低 `num_ctx` 來騰出 VRAM 空間。

### 2.3 GPU 層數卸載 (`num_gpu`)

**問題**：當模型大於 16GB VRAM 時，Ollama 會自動嘗試將部分層數卸載到系統記憶體 (CPU)。
**解決方案**：通常 Ollama 會自動抓取最佳值，但在某些極端情況或多顯卡環境下，您可以手動干預。
*   **設定方式** (API Options):
    ```json
    "options": {
      "num_gpu": 99  // 設為極大值強制盡可能將所有層放入 GPU
    }
    ```
    *若設定為 0，則完全使用 CPU 推論。*

### 2.4 CPU 執行緒數 (`num_thread`)

**問題**：當模型無法完全塞進 VRAM，導致部分層數在 CPU 上運算時，預設的執行緒分配可能不是最佳的。
**解決方案**：調整 CPU 運算執行緒。
*   **建議**：通常將 `num_thread` 設定為與實體 CPU 核心數 (Physical Cores) 相同時，效能最佳。超過實體核心數 (使用到虛擬核心/Hyper-threading) 反而可能因為上下文切換 (Context Switching) 導致效能下降。

---

## 3. 進階與系統層級優化

1.  **確保最新的 NVIDIA 驅動程式與 CUDA Toolkit**：Ollama 底層依賴 `llama.cpp` 和 CUDA 加速。保持驅動程式更新能確保享有最新的效能優化與 Bug 修復。
2.  **Modelfile 的運用**：如果您有固定的系統提示詞 (System Prompt) 或參數需求，建議直接建立自訂的 `Modelfile`。
    ```dockerfile
    FROM qwen2.5:14b-instruct-q4_K_M
    PARAMETER num_ctx 8192
    PARAMETER temperature 0.7
    SYSTEM "你是一個專業的 AI 助手，請用繁體中文回答。"
    ```
    使用 `ollama create my-qwen-model -f ./Modelfile` 建立模型後，呼叫時就不需要每次都在 API 中夾帶這些參數，提升些微效率並簡化程式碼。
3.  **關閉背景大型應用程式**：在執行極限邊緣的模型 (如剛好 15GB 佔用的模型) 時，瀏覽器 (Chrome) 或其他硬體加速的應用程式也會佔用 1-2GB 的 VRAM。關閉它們可以釋出寶貴的空間，避免模型被迫卸載到 CPU。

## 4. 總結配置建議 (針對您的 AI 專案)

如果您打算在您的專案中使用此 RTX 5060 Ti 16GB，建議如下：

1.  **模型選擇**：下載 `qwen2.5:14b` 或 `mistral-nemo:12b` 的 `Q4_K_M` 或 `Q5_K_M` 版本。
2.  **環境變數設定**：啟動 Ollama 服務前，務必設定 `OLLAMA_KEEP_ALIVE="24h"`，避免遊戲中途模型被卸載。
3.  **API 參數**：在 `ai_manager.py` 發送 Ollama API 請求時，明確設定 `num_ctx: 4096` (或 8192，取決於遊戲歷史記錄長度)，確保記憶體使用可控。