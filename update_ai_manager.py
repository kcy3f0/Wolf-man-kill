import sys

def main():
    with open('ai_manager.py', 'r') as f:
        content = f.read()

    # 1. Update init variables
    init_search = "        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite')\n        self.session: Optional[aiohttp.ClientSession] = None"
    init_replace = """        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite')
        self.litellm_api_key = os.getenv('LITELLM_API_KEY')
        self.litellm_model = os.getenv('LITELLM_MODEL', 'gpt-3.5-turbo')
        self.litellm_base_url = os.getenv('LITELLM_BASE_URL', 'https://litellm.lianghsun.dev')
        self.session: Optional[aiohttp.ClientSession] = None"""
    content = content.replace(init_search, init_replace)

    # 2. Update logging in init
    log_search = "        elif self.provider == 'gemini-api':\n            logger.info(f\"Gemini API Model: {self.gemini_model}\")"
    log_replace = """        elif self.provider == 'gemini-api':
            logger.info(f"Gemini API Model: {self.gemini_model}")
        elif self.provider == 'litellm':
            logger.info(f"LiteLLM Model: {self.litellm_model}, Base URL: {self.litellm_base_url}")"""
    content = content.replace(log_search, log_replace)

    # 3. Add litellm generation method
    method_search = "    async def _generate_with_gemini_api(self, prompt: str) -> str:"
    method_replace = """    async def _generate_with_litellm(self, prompt: str) -> str:
        \"\"\"透過 LiteLLM (OpenAI compatible) API 生成回應。\"\"\"
        if not self.litellm_api_key:
            logger.error("LiteLLM API Key is missing.")
            return ""

        url = f"{self.litellm_base_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.litellm_api_key}"
        }
        payload = {
            "model": self.litellm_model,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            session = await self.get_session()
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    choices = data.get("choices", [])
                    if choices:
                        message = choices[0].get("message", {})
                        return message.get("content", "").strip()
                    return ""
                elif response.status == 429:
                    error_text = await response.text()
                    raise RateLimitError(f"LiteLLM 429: {error_text}")
                else:
                    error_text = await response.text()
                    logger.error(f"LiteLLM Error: {response.status} - {error_text}")
                    return ""
        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"LiteLLM Connection Error: {e}")
            return ""

    async def _generate_with_gemini_api(self, prompt: str) -> str:"""
    content = content.replace(method_search, method_replace)

    # 4. Update generate_response routing
    route_search = "            elif self.provider == 'gemini-api' or self.provider == 'gemini':\n                return await self._generate_with_gemini_api(prompt)"
    route_replace = """            elif self.provider == 'gemini-api' or self.provider == 'gemini':
                return await self._generate_with_gemini_api(prompt)
            elif self.provider == 'litellm':
                return await self._generate_with_litellm(prompt)"""
    content = content.replace(route_search, route_replace)

    rate_limit_search = "                # 主動速率限制 (僅針對 Gemini，因為其有嚴格配額)\n                if 'gemini' in self.provider:\n                    await self.rate_limiter.acquire()"
    rate_limit_replace = """                # 主動速率限制 (針對 Gemini 和 LiteLLM)\n                if 'gemini' in self.provider or self.provider == 'litellm':\n                    await self.rate_limiter.acquire()"""
    content = content.replace(rate_limit_search, rate_limit_replace)

    with open('ai_manager.py', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main()
