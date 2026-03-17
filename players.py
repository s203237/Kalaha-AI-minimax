"""
Player Agents.

Provides factory functions to instantiate different types of players.
Each player function takes the board and player_id, and returns a tuple:
(chosen_pit, statistics_dictionary).
"""

import random
from kalah_engine import get_valid_moves
from AI import get_ai_move_minimax, get_ai_move_alphabeta

def create_human_player():
    """Factory for a human CLI player."""
    def player(board, player_id):
        valid_moves = get_valid_moves(board, player=player_id)
        while True:
            try:
                user_input = int(input(f"Player {player_id}, choose a pit (1-6): "))
                pit = (user_input - 1) if player_id == 1 else (user_input + 6)
                
                if pit in valid_moves:
                    return pit, {} # Return empty stats for humans
                else:
                    print("Invalid move: Pit is empty or out of range. Try again.")
            except ValueError:
                print("Please enter a valid numeric value.")
    return player

def create_random_ai_player():
    """Factory for a random AI player."""
    def player(board, player_id):
        valid_moves = get_valid_moves(board, player=player_id)
        if valid_moves:
            move = random.choice(valid_moves)
            return move, {}
        return None, {}
    player.player_type = "Random"
    player.constraint_type = "none"
    player.constraint_value = None
    return player

def create_minimax_player(depth=None, time_limit=None, eval_mode="simple"):
    """
    Factory for a Minimax AI player.
    Can be configured to run up to a fixed depth OR for a fixed amount of time.
    
    Args:
        depth (int): The search depth.
        time_limit (float): Max time in seconds per turn.
        eval_mode (str): Heuristic mode used by evaluation function.
    """
    def player(board, player_id):
        move, stats = get_ai_move_minimax(board, player_id, depth=depth, time_limit=time_limit, eval_mode=eval_mode)
        return move, stats
    player.player_type = "Minimax"
    if time_limit is not None:
        player.constraint_type = "time"
        player.constraint_value = time_limit
    else:
        player.constraint_type = "depth"
        player.constraint_value = depth if depth is not None else 4
    player.eval_mode = eval_mode
    return player


def create_alphabeta_player(depth=None, time_limit=None, eval_mode="simple"):
    """
    Factory for a Minimax + Alpha-Beta pruning AI player.
    Can be configured to run up to a fixed depth OR for a fixed amount of time.

    Args:
        depth (int): The search depth.
        time_limit (float): Max time in seconds per turn.
        eval_mode (str): Heuristic mode used by evaluation function.
    """
    def player(board, player_id):
        move, stats = get_ai_move_alphabeta(board, player_id, depth=depth, time_limit=time_limit, eval_mode=eval_mode)
        return move, stats
    player.player_type = "Alpha-Beta"
    if time_limit is not None:
        player.constraint_type = "time"
        player.constraint_value = time_limit
    else:
        player.constraint_type = "depth"
        player.constraint_value = depth if depth is not None else 4
    player.eval_mode = eval_mode
    return player