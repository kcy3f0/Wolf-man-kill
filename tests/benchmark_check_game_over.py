import sys
import os
import timeit
from unittest.mock import MagicMock

# Mock discord before importing anything that needs it
sys.modules['discord'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from game_objects import GameState, AIPlayer
from game_data import WOLF_FACTION, GOD_FACTION, VILLAGER_FACTION

def setup_game():
    game = GameState()
    for i in range(12):
        p = AIPlayer(f"Player{i}")
        game.players.append(p)
        role = '狼人' if i < 4 else '預言家' if i == 4 else '女巫' if i == 5 else '獵人' if i == 6 else '守衛' if i == 7 else '平民'
        game.roles[p] = role
        if role not in game.role_to_players:
            game.role_to_players[role] = []
        game.role_to_players[role].append(p)
    return game

def orig(game):
    wolf_count = 0
    god_count = 0
    villager_count = 0
    for p in game.players:
        role = game.roles.get(p)
        if role in WOLF_FACTION:
            wolf_count += 1
        elif role in GOD_FACTION:
            god_count += 1
        elif role in VILLAGER_FACTION:
            villager_count += 1
    return wolf_count, god_count, villager_count

def opt1(game):
    players_set = game.players._set
    wolf_count = sum(1 for role in WOLF_FACTION for p in game.role_to_players.get(role, []) if p in players_set)
    god_count = sum(1 for role in GOD_FACTION for p in game.role_to_players.get(role, []) if p in players_set)
    villager_count = sum(1 for role in VILLAGER_FACTION for p in game.role_to_players.get(role, []) if p in players_set)
    return wolf_count, god_count, villager_count

def opt3(game):
    # This assumes role_to_players only has ALIVE players!
    # Let's mock a game where we manually maintain role_to_players
    wolf_count = sum(len(game.role_to_players.get(r, [])) for r in WOLF_FACTION)
    god_count = sum(len(game.role_to_players.get(r, [])) for r in GOD_FACTION)
    villager_count = sum(len(game.role_to_players.get(r, [])) for r in VILLAGER_FACTION)
    return wolf_count, god_count, villager_count

def run_opt3():
    game = setup_game()
    n = 100000
    orig_time = timeit.timeit(lambda: orig(game), number=n)
    opt1_time = timeit.timeit(lambda: opt1(game), number=n)
    opt3_time = timeit.timeit(lambda: opt3(game), number=n)
    print(f"Orig: {orig_time:.5f}s")
    print(f"Opt1 (Generator):  {opt1_time:.5f}s")
    print(f"Opt3 (Assume Managed list): {opt3_time:.5f}s")

if __name__ == '__main__':
    run_opt3()
