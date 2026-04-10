import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add the parent directory to sys.path to import bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bot

class TestCodeHealth(unittest.IsolatedAsyncioTestCase):
    @patch('bot.logger')
    async def test_set_player_mute_logs_warning_on_exception(self, mock_logger):
        # Mock member
        member = MagicMock()
        member.name = "TestPlayer"
        member.voice = MagicMock()
        member.voice.mute = False

        # Mock edit to raise an exception
        member.edit = AsyncMock(side_effect=Exception("Discord API Error"))

        # Call the function
        await bot.set_player_mute(member, True)

        # Verify logger.warning was called
        mock_logger.warning.assert_called()
        args, _ = mock_logger.warning.call_args
        self.assertIn("Failed to edit member TestPlayer", args[0])

if __name__ == "__main__":
    unittest.main()
