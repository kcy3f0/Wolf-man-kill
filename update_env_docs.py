import sys

def main():
    # Update .env.example
    with open('.env.example', 'r') as f:
        env_content = f.read()

    env_search = "AI_PROVIDER=gemini-api # Options: ollama, gemini-api"
    env_replace = """AI_PROVIDER=gemini-api # Options: ollama, gemini-api, litellm
LITELLM_API_KEY=your_litellm_key_here
LITELLM_MODEL=gpt-3.5-turbo
LITELLM_BASE_URL=https://litellm.lianghsun.dev"""

    env_content = env_content.replace(env_search, env_replace)
    with open('.env.example', 'w') as f:
        f.write(env_content)

    # Update README.md
    with open('README.md', 'r') as f:
        readme_content = f.read()

    readme_search1 = "| `AI_PROVIDER` | 選擇 AI 提供者 (`gemini-api` 或 `ollama`) | `gemini-api` | `ollama` |"
    readme_replace1 = "| `AI_PROVIDER` | 選擇 AI 提供者 (`gemini-api`, `ollama` 或 `litellm`) | `gemini-api` | `ollama`, `litellm` |"

    readme_search2 = "### 3. 設定環境變數"
    readme_replace2 = "### 3. 設定環境變數"

    # Check if we have litellm section in readme already
    if "LITELLM_API_KEY" not in readme_content:
        # insert after Gemini section
        gemini_section = "| `GEMINI_MODEL` | 使用的 Gemini 模型 | `gemini-2.5-flash-lite` | `gemini-pro` |"
        litellm_section = """
| `LITELLM_API_KEY` | LiteLLM (OpenAI API 相容) 金鑰 | 無 (必填，若使用 litellm) | `sk-...` |
| `LITELLM_MODEL` | 使用的 LiteLLM 模型 | `gpt-3.5-turbo` | `gpt-4o`, `claude-3-opus` |
| `LITELLM_BASE_URL`| LiteLLM API 基礎 URL | `https://litellm.lianghsun.dev` | `https://api.openai.com` |"""
        readme_content = readme_content.replace(gemini_section, gemini_section + litellm_section)

        # Update .env example block in README
        env_block_search = """GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# AI 提供者設定
AI_PROVIDER=gemini-api  # 或 ollama

# Ollama API 設定 (如果使用 Ollama)"""

        env_block_replace = """GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# LiteLLM 設定 (如果使用 LiteLLM)
LITELLM_API_KEY=your_litellm_key_here
LITELLM_MODEL=gpt-3.5-turbo
LITELLM_BASE_URL=https://litellm.lianghsun.dev

# AI 提供者設定
AI_PROVIDER=gemini-api  # 或 ollama, litellm

# Ollama API 設定 (如果使用 Ollama)"""
        readme_content = readme_content.replace(env_block_search, env_block_replace)

    with open('README.md', 'w') as f:
        f.write(readme_content)

if __name__ == '__main__':
    main()
