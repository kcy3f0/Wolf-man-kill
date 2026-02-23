import sys
import os
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock, patch
from collections import deque

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock environment variables BEFORE import
os.environ['DISCORD_TOKEN'] = 'fake_token'
os.environ['GEMINI_API_KEY'] = 'fake_key'

# MOCK MODULES
mock_discord = MagicMock()
mock_discord.Intents.default.return_value = MagicMock()
mock_discord.app_commands = MagicMock()
mock_discord.ext = MagicMock()
mock_discord.ext.commands = MagicMock()

# Custom MockBot to avoid MagicMock init issues
class MockBot:
    def __init__(self, *args, **kwargs):
        self.tree = MagicMock()
        self.tree.command = lambda *args, **kwargs: lambda func: func
        self.user = "MockBot"

    async def setup_hook(self):
        pass

    async def close(self):
        pass

    def event(self, func):
        return func

    def process_commands(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        pass

    async def wait_for(self, *args, **kwargs):
        return MagicMock(content="no")

mock_discord.ext.commands.Bot = MockBot

sys.modules['discord'] = mock_discord
sys.modules['discord.app_commands'] = mock_discord.app_commands
sys.modules['discord.ext'] = mock_discord.ext
sys.modules['discord.ext.commands'] = mock_discord.ext.commands

sys.modules['dotenv'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()

# Now import bot
import bot
from game_objects import GameState, AIPlayer

async def benchmark():
    print("Setting up benchmark...")

    # bot.bot is already instantiated as WerewolfBot (which inherits MockBot)
    # We can use it.

    channel = AsyncMock()
    channel.send = AsyncMock()
    # Need to handle channel.permissions_for(role).send_messages access
    perms = MagicMock()
    perms.send_messages = True
    channel.permissions_for.return_value = perms

    # Mock ai_manager.get_ai_speech to return instantly
    bot.ai_manager.get_ai_speech = AsyncMock(return_value="Mocked Speech Content")

    # Mock set_player_mute
    bot.set_player_mute = AsyncMock()

    # Mock perform_ai_voting to avoid background tasks
    bot.perform_ai_voting = AsyncMock()

    # Mock unmute_all_players
    bot.unmute_all_players = AsyncMock()

    iterations = 5
    print(f"Running {iterations} iterations of AI turn processing...")

    total_time = 0

    for i in range(iterations):
        game = GameState()
        ai_player = AIPlayer("AI-1")

        game.players = [ai_player]
        game.player_id_map = {ai_player: 1}
        game.roles = {ai_player: "Villager"}
        game.ai_players = [ai_player]

        # Setup queue with 1 AI player
        game.speaking_queue = deque([ai_player])
        game.speaking_active = True

        start = time.time()
        await bot.start_next_turn(channel, game)
        end = time.time()

        duration = end - start
        total_time += duration
        print(f"Iteration {i+1}: {duration:.4f}s")

    avg_time = total_time / iterations
    print(f"Average time per turn: {avg_time:.4f}s")

if __name__ == "__main__":
    asyncio.run(benchmark())
