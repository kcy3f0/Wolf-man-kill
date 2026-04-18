import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import os
import sys
import asyncio

# Ensure ai_manager can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_manager import AIManager

class TestAIProviders(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.managers_to_close = []

    async def asyncTearDown(self):
        for manager in self.managers_to_close:
            await manager.close()

    async def test_ollama_provider(self):
        with patch.dict(os.environ, {'AI_PROVIDER': 'ollama', 'OLLAMA_HOST': 'http://test', 'OLLAMA_MODEL': 'test-model'}):
            manager = AIManager()
            self.managers_to_close.append(manager)
            self.assertEqual(manager.provider, 'ollama')

            # Mock session
            mock_session = AsyncMock()
            mock_session.closed = False
            manager.session = mock_session

            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"response": "Ollama response"}

            # Mock context manager
            mock_post_ctx = MagicMock()
            mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_post_ctx.__aexit__ = AsyncMock(return_value=None)

            # session.post must be MagicMock, not AsyncMock
            mock_session.post = MagicMock(return_value=mock_post_ctx)

            response = await manager.generate_response("test prompt")
            self.assertEqual(response, "Ollama response")

            # Verify URL and payload
            args, kwargs = mock_session.post.call_args
            self.assertEqual(args[0], "http://test/api/generate")
            self.assertEqual(kwargs['json']['model'], 'test-model')

    async def test_gemini_api_provider(self):
        with patch.dict(os.environ, {'AI_PROVIDER': 'gemini-api', 'GEMINI_API_KEY': 'test-key', 'GEMINI_MODEL': 'test-gemini'}):
            manager = AIManager()
            self.managers_to_close.append(manager)
            self.assertEqual(manager.provider, 'gemini-api')

            # Mock session
            mock_session = AsyncMock()
            mock_session.closed = False
            manager.session = mock_session

            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "candidates": [{
                    "content": {
                        "parts": [{"text": "Gemini API response"}]
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
            self.assertEqual(response, "Gemini API response")

            # Verify URL and Headers
            args, kwargs = mock_session.post.call_args
            self.assertIn("test-gemini", args[0])
            self.assertEqual(kwargs['headers']['x-goog-api-key'], 'test-key')


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

    async def test_default_fallback(self):
        with patch.dict(os.environ, {'AI_PROVIDER': 'unknown'}):
            manager = AIManager()
            self.managers_to_close.append(manager)

            # It should fallback to gemini-api and try to call it
            # Mock _generate_with_gemini_api directly
            manager._generate_with_gemini_api = AsyncMock(return_value="API Fallback response")

            response = await manager.generate_response("test prompt")
            self.assertEqual(response, "API Fallback response")
            manager._generate_with_gemini_api.assert_called_once_with("test prompt")

if __name__ == '__main__':
    unittest.main()
