import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import asyncio
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestGeminiOptimization(unittest.TestCase):
    def setUp(self):
        # We need to mock dependencies that might be missing in some environments
        # We use patch.dict to safely patch sys.modules without permanent side effects
        self.modules_patcher = patch.dict(sys.modules, {
            'dotenv': MagicMock(),
            'aiohttp': MagicMock()
        })
        self.modules_patcher.start()

        # Now we can import safely.
        # Note: In a real environment with deps installed, this import would work without mocks.
        # But we patch to ensure it works here.
        # However, to be clean, we should only patch if import fails?
        # No, for consistency in this test file, let's just patch.
        # The reviewer wanted to avoid *global* pollution. setup/teardown is scoped.

        # We must clear AIManager from sys.modules if it was already imported to ensure clean import
        if 'ai_manager' in sys.modules:
            del sys.modules['ai_manager']

        from ai_manager import AIManager
        self.AIManager = AIManager

    def tearDown(self):
        self.modules_patcher.stop()
        # Clean up ai_manager from sys.modules to avoid polluting other tests
        if 'ai_manager' in sys.modules:
            del sys.modules['ai_manager']

    @patch('ai_manager.AIManager._generate_with_gemini_api', new_callable=AsyncMock)
    @patch('asyncio.create_subprocess_exec')
    def test_gemini_cli_optimization(self, mock_subprocess, mock_api_method):
        """
        Verify that _generate_with_gemini_cli delegates to _generate_with_gemini_api
        when GEMINI_API_KEY is present.
        """
        AIManager = self.AIManager

        # Scenario 1: API Key Present -> Use API
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key', 'AI_PROVIDER': 'gemini-cli'}):
            ai_manager = AIManager()
            # Ensure key is picked up
            self.assertEqual(ai_manager.gemini_api_key, 'fake_key')

            # Reset mocks
            mock_subprocess.reset_mock()
            mock_api_method.reset_mock()
            mock_api_method.return_value = "API_RESPONSE"

            # Call method
            result = asyncio.run(ai_manager._generate_with_gemini_cli("test prompt"))

            # Expectation: API method called, Subprocess NOT called
            mock_api_method.assert_called_once_with("test prompt")
            mock_subprocess.assert_not_called()
            self.assertEqual(result, "API_RESPONSE")

        # Scenario 2: API Key Missing -> Use Subprocess
        with patch.dict(os.environ, {'AI_PROVIDER': 'gemini-cli'}):
             if 'GEMINI_API_KEY' in os.environ:
                 del os.environ['GEMINI_API_KEY']

             ai_manager = AIManager()
             # Ensure key is None
             self.assertIsNone(ai_manager.gemini_api_key)

             # Mock subprocess to return success
             process_mock = MagicMock()
             process_mock.communicate = AsyncMock(return_value=(b"CLI_RESPONSE", b""))
             process_mock.returncode = 0
             mock_subprocess.return_value = process_mock

             mock_subprocess.reset_mock()
             mock_api_method.reset_mock()

             # Call method
             result = asyncio.run(ai_manager._generate_with_gemini_cli("test prompt"))

             # Expectation: Subprocess called, API NOT called
             mock_subprocess.assert_called_once()
             mock_api_method.assert_not_called()
             self.assertEqual(result, "CLI_RESPONSE")

if __name__ == '__main__':
    unittest.main()
