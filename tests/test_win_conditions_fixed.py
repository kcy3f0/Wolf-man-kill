import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Mock dependencies
mock_discord = MagicMock()
sys.modules['discord'] = mock_discord
sys.modules['discord.ext'] = MagicMock()
sys.modules['discord.ext.commands'] = MagicMock()
sys.modules['discord.app_commands'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()

import bot

class TestWinConditions(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_ctx = MagicMock()
        self.mock_ctx.guild.id = 999
        self.mock_ctx.send = AsyncMock()
        self.mock_ctx.channel.set_permissions = AsyncMock()
        self.mock_ctx.set_permissions = AsyncMock()
        self.mock_ctx.guild.default_role = MagicMock()
        bot.games = {}

    async def test_win_condition_wolves_win_slaughter_villagers(self):
        """
        Test scenario: Wolves kill all Villagers (Side Kill).
        Expectation: Game should end (game_active = False).
        """
        game = bot.get_game(self.mock_ctx.guild.id)

        # Setup players
        p1 = MagicMock(name="Wolf1")
        p1.name = "Wolf1"
        p2 = MagicMock(name="Villager1")
        p2.name = "Villager1"
        p3 = MagicMock(name="Seer1") # God
        p3.name = "Seer1"

        game.players = [p1, p2, p3]
        game.roles = {
            p1: "狼人",
            p2: "平民",
            p3: "預言家"
        }
        game.role_to_players = {
            "狼人": [p1],
            "平民": [p2],
            "預言家": [p3]
        }
        game.game_active = True

        # Simulate Night: Wolf kills Villager (p2)
        dead_players = [p2]

        # Call perform_day with GAME object
        # We need to mock announce_event because it calls ai_manager
        with patch('bot.announce_event', new_callable=AsyncMock):
            await bot.perform_day(self.mock_ctx, game, dead_players)

        self.assertFalse(game.game_active, "Game should end when all Villagers are dead")

    async def test_win_condition_wolves_win_slaughter_gods(self):
        """
        Test scenario: Wolves kill all Gods (Side Kill).
        Expectation: Game should end.
        """
        game = bot.get_game(self.mock_ctx.guild.id)

        p1 = MagicMock(name="Wolf1")
        p1.name = "Wolf1"
        p2 = MagicMock(name="Villager1")
        p2.name = "Villager1"
        p3 = MagicMock(name="Seer1")
        p3.name = "Seer1"

        game.players = [p1, p2, p3]
        game.roles = {
            p1: "狼人",
            p2: "平民",
            p3: "預言家"
        }
        game.role_to_players = {
            "狼人": [p1],
            "平民": [p2],
            "預言家": [p3]
        }
        game.game_active = True

        # Simulate Night: Wolf kills Seer (p3)
        dead_players = [p3]

        with patch('bot.announce_event', new_callable=AsyncMock):
            await bot.perform_day(self.mock_ctx, game, dead_players)

        self.assertFalse(game.game_active, "Game should end when all Gods are dead")

    async def test_win_condition_good_wins(self):
        """
        Test scenario: Good team votes out the last Wolf.
        Expectation: Game should end.
        """
        game = bot.get_game(self.mock_ctx.guild.id)

        p1 = MagicMock(name="Wolf1")
        p1.name = "Wolf1"
        p2 = MagicMock(name="Villager1")
        p2.name = "Villager1"

        game.players = [p1, p2]
        game.roles = {
            p1: "狼人",
            p2: "平民"
        }
        game.role_to_players = {
            "狼人": [p1],
            "平民": [p2]
        }
        game.game_active = True
        game.votes = {p1: 2} # Both vote for wolf
        game.voted_players = {p1, p2}

        # Call resolve_votes with GAME object
        with patch('bot.announce_event', new_callable=AsyncMock):
            with patch('bot.request_last_words', new_callable=AsyncMock):
                await bot.resolve_votes(self.mock_ctx, game)

        self.assertFalse(game.game_active, "Game should end when all Wolves are dead")

if __name__ == '__main__':
    unittest.main()
