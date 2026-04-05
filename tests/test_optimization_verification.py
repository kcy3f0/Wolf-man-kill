import sys
import os
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

# Mock dependencies before importing anything
mock_discord = MagicMock()
sys.modules['discord'] = mock_discord
sys.modules['discord.ext'] = MagicMock()
sys.modules['discord.app_commands'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()

import bot
from game_data import GAME_TEMPLATES, SUPPORTED_COUNTS

class TestTargetCountLogic(unittest.TestCase):
    def test_supported_counts_sorted(self):
        # Verify the constant is sorted correctly
        expected = sorted(GAME_TEMPLATES.keys(), reverse=True)
        self.assertEqual(SUPPORTED_COUNTS, expected)

    def get_target_count(self, current_player_count):
        # Mirroring the logic in bot.py
        return next((count for count in SUPPORTED_COUNTS if current_player_count >= count), 6)

    def test_logic_exact_match(self):
        self.assertEqual(self.get_target_count(6), 6)
        self.assertEqual(self.get_target_count(12), 12)
        self.assertEqual(self.get_target_count(8), 8)
        self.assertEqual(self.get_target_count(7), 7)

    def test_logic_overflow(self):
        self.assertEqual(self.get_target_count(11), 10)
        self.assertEqual(self.get_target_count(15), 12)

    def test_logic_underflow(self):
        self.assertEqual(self.get_target_count(5), 6)
        self.assertEqual(self.get_target_count(3), 6)

if __name__ == "__main__":
    unittest.main()
