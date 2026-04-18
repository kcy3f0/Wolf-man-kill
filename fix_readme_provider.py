import sys

def main():
    with open('README.md', 'r') as f:
        content = f.read()

    # Update provider in table
    old_row = "| `AI_PROVIDER` | 選擇 AI 提供者 (`gemini-api` 或 `ollama`) | `gemini-api` | `ollama` |"
    new_row = "| `AI_PROVIDER` | 選擇 AI 提供者 (`gemini-api`, `ollama` 或 `litellm`) | `gemini-api` | `ollama`, `litellm` |"
    content = content.replace(old_row, new_row)

    with open('README.md', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main()
