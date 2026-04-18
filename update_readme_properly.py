import sys

def main():
    with open('README.md', 'r') as f:
        content = f.read()

    # Table replacement
    old_table_row = "| `GEMINI_API_KEY` | Google Gemini 的 API Key | 無 | `AIzaSy...` |"
    new_table_rows = """| `GEMINI_API_KEY` | Google Gemini 的 API Key | 無 | `AIzaSy...` |
| `LITELLM_API_KEY` | LiteLLM (OpenAI 相容) 的 API Key | 無 | `sk-...` |
| `LITELLM_MODEL` | 使用的 LiteLLM 模型 | `gpt-3.5-turbo` | `gpt-4o` |
| `LITELLM_BASE_URL`| LiteLLM API 基礎 URL | `https://litellm.lianghsun.dev` | `https://api.openai.com` |"""
    content = content.replace(old_table_row, new_table_rows)

    # Env block replacement
    old_env_block = """GEMINI_API_KEY=你的_Google_Gemini_API_Key

# AI 提供者設定
AI_PROVIDER=gemini-api  # 或 ollama

# Ollama API 設定 (如果使用 Ollama)"""
    new_env_block = """GEMINI_API_KEY=你的_Google_Gemini_API_Key

# LiteLLM 設定 (如果使用 LiteLLM)
LITELLM_API_KEY=your_litellm_key_here
LITELLM_MODEL=gpt-3.5-turbo
LITELLM_BASE_URL=https://litellm.lianghsun.dev

# AI 提供者設定
AI_PROVIDER=gemini-api  # 或 ollama, litellm

# Ollama API 設定 (如果使用 Ollama)"""
    content = content.replace(old_env_block, new_env_block)

    with open('README.md', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main()
