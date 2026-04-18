import sys

def main():
    with open('tests/test_ai_providers.py', 'r') as f:
        content = f.read()

    new_test = """
    async def test_litellm_provider(self):
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_API_KEY': 'test-litellm-key',
            'LITELLM_MODEL': 'test-litellm-model',
            'LITELLM_BASE_URL': 'https://test-litellm.com'
        }):
            manager = AIManager()
            self.managers_to_close.append(manager)
            self.assertEqual(manager.provider, 'litellm')

            # Mock session
            mock_session = AsyncMock()
            mock_session.closed = False
            manager.session = mock_session

            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "LiteLLM response"
                    }
                }]
            }

            # Mock context manager
            mock_post_ctx = MagicMock()
            mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post_ctx.__aexit__ = AsyncMock(return_value=None)

            # session.post must be MagicMock
            mock_session.post = MagicMock(return_value=mock_post_ctx)

            response = await manager.generate_response("test prompt")
            self.assertEqual(response, "LiteLLM response")

            # Verify URL and Headers
            args, kwargs = mock_session.post.call_args
            self.assertEqual(args[0], "https://test-litellm.com/v1/chat/completions")
            self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test-litellm-key')
            self.assertEqual(kwargs['json']['model'], 'test-litellm-model')
"""
    search_str = "    async def test_default_fallback(self):"

    content = content.replace(search_str, new_test + "\n" + search_str)

    with open('tests/test_ai_providers.py', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main()
