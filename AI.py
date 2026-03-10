"""
Adversarial Search Algorithms.

Contains the AI logic for the Kalah game. Includes the Minimax algorithm 
with Iterative Deepening to support time-limited queries, alongside 
comprehensive performance tracking (nodes expanded, time taken).
"""

import math
import time
from kalah_engine import make_move, get_valid_moves, check_endgame

class SearchTimeout(Exception):
    """Custom exception raised when the AI search exceeds the allotted time."""
    pass


def evaluate_board(board, ai_player_id):
    """
    Heuristic evaluation function (EVAL).
    
    Calculates the relative advantage of the AI player over its opponent.
    This simple heuristic looks purely at the material advantage (score difference).
    
    Args:
        board (list of int): The current board state.
        ai_player_id (int): The ID of the AI player (1 or 2).
        
    Returns:
        int: The heuristic value of the board. Positive implies an AI advantage.
    """
    if ai_player_id == 1:
        return board[6] - board[13]
    else:
        return board[13] - board[6]


def get_ai_move_minimax(board, ai_player_id, depth=None, time_limit=None):
    """
    Wrapper function to initiate the Minimax search.
    Supports either fixed-depth search or time-limited search using Iterative Deepening.
    
    Args:
        board (list of int): The current board state.
        ai_player_id (int): The ID of the AI player.
        depth (int, optional): The fixed depth to search.
        time_limit (float, optional): The maximum time in seconds allowed for the search.
        
    Returns:
        tuple: (best_move, stats_dictionary)
    """
    stats = {'nodes': 0, 'depth_reached': 0, 'time_taken': 0.0}
    start_time = time.time()
    best_move = None
    
    # Fallback move in case time expires before even depth 1 finishes
    valid_moves = get_valid_moves(board, ai_player_id)
    if not valid_moves:
        return None, stats
    best_move = valid_moves[0] 

    if time_limit is not None:
        # --- Iterative Deepening Search (Time-based) ---
        current_depth = 1
        previous_iteration_nodes = 0
        
        try:
            while True:
                # Keep track of nodes expanded before this depth iteration begins
                nodes_before = stats['nodes']
                
                score, move = minimax(
                    board, current_depth, True, ai_player_id, 
                    stats, start_time, time_limit
                )
                
                if move is not None:
                    best_move = move
                stats['depth_reached'] = current_depth
                
                # Calculate how many nodes were expanded during this specific depth level
                nodes_this_iteration = stats['nodes'] - nodes_before
                
                # SMART BREAK: Prevent the "End-Game Spin"
                # If the tree didn't grow compared to the last depth iteration, it means 
                # all branches hit a terminal state (Game Over) naturally. 
                # Further deepening is useless.
                if nodes_this_iteration == previous_iteration_nodes:
                    break
                    
                previous_iteration_nodes = nodes_this_iteration
                current_depth += 1
                
        except SearchTimeout:
            # Time limit exceeded. We safely catch the exception and return the 
            # best_move found from the last fully completed depth.
            pass
            
    else:
        # --- Fixed Depth Search ---
        # If no depth is provided and no time limit, default to a safe depth of 4
        search_depth = depth if depth is not None else 4
        score, move = minimax(
            board, search_depth, True, ai_player_id, 
            stats, start_time, None
        )
        if move is not None:
            best_move = move
        stats['depth_reached'] = search_depth

    stats['time_taken'] = time.time() - start_time
    return best_move, stats


def minimax(board, depth, is_maximizing, ai_player_id, stats, start_time, time_limit):
    """
    Recursive Minimax algorithm.
    
    Includes node counting for benchmarking and time-checking. If the time limit 
    is reached during traversal, it raises a SearchTimeout to instantly collapse 
    the search tree and halt execution.
    """
    # Increment node counter for performance metrics
    stats['nodes'] += 1
    
    # Check for timeout and abort if necessary
    if time_limit is not None and (time.time() - start_time) >= time_limit:
        raise SearchTimeout()

    # Create an independent copy of the board to prevent mutation during endgame checks
    board_for_check = board.copy()
    
    # Base case: Cutoff depth reached or terminal state encountered
    if depth == 0 or check_endgame(board_for_check):
        return evaluate_board(board_for_check, ai_player_id), None

    # Determine whose turn it is currently
    current_player = ai_player_id if is_maximizing else (1 if ai_player_id == 2 else 2)
        
    if is_maximizing:
        # --- Maximizing Player (AI) ---
        max_eval = -math.inf
        best_move = None
        
        possible_moves = get_valid_moves(board, player=current_player)
        
        if not possible_moves:
            return evaluate_board(board_for_check, ai_player_id), None
            
        for move in possible_moves:
            board_copy = board.copy()
            new_board, extra_turn = make_move(board_copy, player=current_player, pit=move, verbose=False)
            
            # Kalah rule: If an extra turn is granted, the turn does NOT switch
            next_is_maximizing = True if extra_turn else False
            
            eval_score, _ = minimax(new_board, depth - 1, next_is_maximizing, ai_player_id, stats, start_time, time_limit)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
                
        return max_eval, best_move
        
    else:
        # --- Minimizing Player (Opponent) ---
        min_eval = math.inf
        best_move = None
        
        possible_moves = get_valid_moves(board, player=current_player)
        
        if not possible_moves:
            return evaluate_board(board_for_check, ai_player_id), None
            
        for move in possible_moves:
            board_copy = board.copy()
            new_board, extra_turn = make_move(board_copy, player=current_player, pit=move, verbose=False)
            
            # Kalah rule: If an extra turn is granted, the turn does NOT switch
            next_is_maximizing = False if extra_turn else True
            
            eval_score, _ = minimax(new_board, depth - 1, next_is_maximizing, ai_player_id, stats, start_time, time_limit)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
                
        return min_eval, best_move