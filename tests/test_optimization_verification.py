import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Mock dependencies before importing bot
mock_discord = MagicMock()
sys.modules['discord'] = mock_discord
sys.modules['discord.ext'] = MagicMock()
sys.modules['discord.app_commands'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()

# We need a custom mock for the decorator to preserve the function
class MockTree:
    def command(self, *args, **kwargs):
        def decorator(func):
            func.callback = func # Mocking the .callback attribute
            return func
        return decorator

# Create a mock bot class
class MockBot:
    def __init__(self):
        self.tree = MockTree()
    def event(self, func):
        return func

# Replace the WerewolfBot class before import
with patch('bot.WerewolfBot', return_value=MockBot()):
    import bot

import asyncio
import unittest

class TestOptimizationVerification(unittest.IsolatedAsyncioTestCase):
    @patch('bot.perform_night', new_callable=AsyncMock)
    @patch('bot.announce_event', new_callable=AsyncMock)
    async def test_god_send_concurrent(self, mock_announce_event, mock_perform_night):
        # Setup
        interaction = MagicMock()
        interaction.guild_id = 12345
        interaction.channel.send = AsyncMock()
        interaction.followup.send = AsyncMock()
        interaction.response.send_message = AsyncMock()

        game = bot.get_game(interaction.guild_id)
        game.reset()

        # Add 3 players
        p1 = MagicMock()
        p1.name = "P1"
        p1.send = AsyncMock()
        p1.mention = "P1_mention"
        p1.bot = False
        p2 = MagicMock()
        p2.name = "P2"
        p2.send = AsyncMock()
        p2.mention = "P2_mention"
        p2.bot = False
        p3 = MagicMock()
        p3.name = "P3"
        p3.send = AsyncMock()
        p3.mention = "P3_mention"
        p3.bot = False
        game.players = [p1, p2, p3]

        # Add 2 gods
        g1 = MagicMock()
        g1.name = "G1"
        g1.send = AsyncMock()
        g1.mention = "G1_mention"
        g1.bot = False
        g2 = MagicMock()
        g2.name = "G2"
        g2.send = AsyncMock()
        g2.mention = "G2_mention"
        g2.bot = False
        game.gods = [g1, g2]

        # The 'start' command in bot.py should have a .callback attribute now
        await bot.start.callback(interaction)

        # Verify gods received the summary
        g1.send.assert_called_once()
        g2.send.assert_called_once()

        # Verify they received the same summary message
        msg1 = g1.send.call_args[0][0]
        msg2 = g2.send.call_args[0][0]
        self.assertEqual(msg1, msg2)
        self.assertIn("本局板子：", msg1)
        self.assertIn("本局身分列表：", msg1)

if __name__ == "__main__":
    unittest.main()
