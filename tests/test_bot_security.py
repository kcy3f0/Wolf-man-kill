import sys
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

# --- Setup Global Mocks for Missing Dependencies ---
discord = MagicMock()
discord.Intents = MagicMock()
discord.ext = MagicMock()
discord.ext.commands = MagicMock()
discord.app_commands = MagicMock()
discord.Interaction = MagicMock()

# Mock the Bot class NOT as a MagicMock subclass to avoid initialization issues
class MockBot:
    def __init__(self, *args, **kwargs):
        self.tree = MagicMock()

        # Decorator that returns a Mock object with .callback pointing to the original function
        def command_decorator(*d_args, **d_kwargs):
            def wrapper(func):
                # We return a mock that acts like the Command object
                # and has the .callback attribute
                cmd_mock = MagicMock()
                cmd_mock.callback = func
                return cmd_mock
            return wrapper

        self.tree.command = MagicMock(side_effect=command_decorator)
        self.tree.sync = AsyncMock()

        self.user = MagicMock()
        self.user.__str__ = lambda x: "MockBot"

        # .event decorator
        self.event = MagicMock(side_effect=lambda func: func)

    async def setup_hook(self):
        pass

    async def close(self):
        pass

    def run(self, *args, **kwargs):
        pass

    async def process_commands(self, *args, **kwargs):
        pass

    async def wait_for(self, *args, **kwargs):
        return MagicMock()

discord.ext.commands.Bot = MockBot

sys.modules["discord"] = discord
sys.modules["discord.ext"] = discord.ext
sys.modules["discord.ext.commands"] = discord.ext.commands
sys.modules["discord.app_commands"] = discord.app_commands
sys.modules["dotenv"] = MagicMock()
sys.modules["aiohttp"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

# Now import bot
import bot

# Mock Discord Context
class MockContext:
    def __init__(self, author_id, guild_id):
        self.user = MagicMock()
        self.user.id = author_id
        self.user.name = f"User{author_id}"
        self.user.mention = f"<@{author_id}>"
        self.author = self.user # Backwards compatibility if needed
        self.guild = MagicMock()
        self.guild.id = guild_id
        self.guild_id = guild_id
        self.send = AsyncMock() # Legacy
        self.response = MagicMock()
        self.response.send_message = AsyncMock()
        self.channel = MagicMock()
        self.channel.send = AsyncMock()
        self.channel.set_permissions = AsyncMock()
        self.channel.guild = MagicMock()
        # Mock followup for slash commands sometimes used
        self.followup = MagicMock()
        self.followup.send = AsyncMock()

class TestBotSecurity(unittest.IsolatedAsyncioTestCase):
    async def test_join_concurrency(self):
        # Reset game
        guild_id = 123
        game = bot.get_game(guild_id)
        game.reset()

        # Simulate 30 users joining concurrently
        users = [MockContext(i, guild_id) for i in range(30)]

        # Directly calling the callback function of the command
        tasks = [bot.join.callback(ctx) for ctx in users]
        await asyncio.gather(*tasks)

        print(f"Players joined: {len(game.players)}")
        self.assertLessEqual(len(game.players), 20)
        self.assertEqual(len(game.players), 20) # Should fill up to 20

    async def test_vote_input_validation(self):
        guild_id = 456
        game = bot.get_game(guild_id)
        game.reset()
        game.game_active = True
        # Ensure vote can proceed (not speaking active)
        game.speaking_active = False

        p1 = MagicMock()
        p1.id = 1
        p1.name = "P1"
        game.players = [p1]
        game.player_ids = {1: p1}
        # Ensure user hasn't voted yet
        game.voted_players = set()
        game.votes = {}

        ctx = MockContext(1, guild_id)
        ctx.user = p1
        ctx.author = p1

        # Test long input
        long_str = "a" * 200

        # Run the callback
        await bot.vote.callback(ctx, target_id=long_str)

        # Check response
        # Verify that send_message was called with the error message
        ctx.response.send_message.assert_called_once()
        args, _ = ctx.response.send_message.call_args
        self.assertIn("輸入過長", args[0])

    async def test_die_permission_bypass(self):
        guild_id = 789
        game = bot.get_game(guild_id)
        game.reset()

        # Creator
        creator = MagicMock()
        creator.id = 1
        creator.guild_permissions.administrator = False
        creator.mention = "<@1>"

        # Random User
        user = MagicMock()
        user.id = 2
        user.guild_permissions.administrator = False
        user.mention = "<@2>"

        # Admin
        admin = MagicMock()
        admin.id = 3
        admin.guild_permissions.administrator = True
        admin.mention = "<@3>"

        game.creator = creator
        game.game_active = True

        # Case 1: Random user tries to use !die
        ctx = MockContext(2, guild_id)
        ctx.user = user
        ctx.author = user

        await bot.die.callback(ctx, target="1")

        args, _ = ctx.response.send_message.call_args
        self.assertIn("權限不足", args[0])

        # Case 2: Creator uses !die
        # Setup players for this case
        game.players = [user]
        game.player_ids = {2: user}

        ctx = MockContext(1, guild_id)
        ctx.user = creator
        ctx.author = creator

        # Call die on target "2"
        await bot.die.callback(ctx, target="2")

        # Should succeed (game.players empty after die?)
        self.assertNotIn(user, game.players)

        # Check success message
        args, _ = ctx.response.send_message.call_args
        self.assertIn("已死亡", args[0])

if __name__ == "__main__":
    unittest.main()
