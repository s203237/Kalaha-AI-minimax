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


def _player_view(board, player_id):
    """Returns player-specific board slices to simplify evaluation logic."""
    if player_id == 1:
        return board[0:6], board[7:13], 6, 13
    return board[7:13], board[0:6], 13, 6


def _landing_index(board, player_id, pit):
    """Computes where the last seed lands for a candidate move."""
    seeds = board[pit]
    current = pit

    while seeds > 0:
        current = (current + 1) % 14
        if player_id == 1 and current == 13:
            continue
        if player_id == 2 and current == 6:
            continue
        seeds -= 1

    return current


def evaluate_board_simple(board, ai_player_id):
    """
    Baseline heuristic: score difference only.

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


def evaluate_board_phase_aware(board, ai_player_id):
    """
    Phase-aware heuristic with tactical and strategic features.
    """
    my_pits, opp_pits, my_store_idx, opp_store_idx = _player_view(board, ai_player_id)
    opp_player_id = 2 if ai_player_id == 1 else 1

    my_store = board[my_store_idx]
    opp_store = board[opp_store_idx]
    my_side_sum = sum(my_pits)
    opp_side_sum = sum(opp_pits)

    # Core strategic signals
    store_diff = my_store - opp_store
    side_seed_diff = my_side_sum - opp_side_sum
    mobility_diff = sum(1 for s in my_pits if s > 0) - sum(1 for s in opp_pits if s > 0)

    # Tactical opportunities next turn
    extra_turn_potential = 0
    capture_potential = 0

    my_start, my_end = (0, 6) if ai_player_id == 1 else (7, 13)
    for pit in range(my_start, my_end):
        if board[pit] == 0:
            continue

        landing = _landing_index(board, ai_player_id, pit)

        if landing == my_store_idx:
            extra_turn_potential += 1

        if ai_player_id == 1 and 0 <= landing <= 5 and board[landing] == 0:
            opposite = 12 - landing
            if board[opposite] > 0:
                capture_potential += board[opposite] + 1
        elif ai_player_id == 2 and 7 <= landing <= 12 and board[landing] == 0:
            opposite = 12 - landing
            if board[opposite] > 0:
                capture_potential += board[opposite] + 1

    # Opponent tactical threats (capture risk)
    capture_risk = 0
    opp_start, opp_end = (0, 6) if opp_player_id == 1 else (7, 13)
    for pit in range(opp_start, opp_end):
        if board[pit] == 0:
            continue

        landing = _landing_index(board, opp_player_id, pit)
        if opp_player_id == 1 and 0 <= landing <= 5 and board[landing] == 0:
            opposite = 12 - landing
            if board[opposite] > 0:
                capture_risk += board[opposite] + 1
        elif opp_player_id == 2 and 7 <= landing <= 12 and board[landing] == 0:
            opposite = 12 - landing
            if board[opposite] > 0:
                capture_risk += board[opposite] + 1

    # Endgame pressure: valuable when one side is close to empty
    endgame_pressure = 0
    if my_side_sum == 0:
        endgame_pressure -= opp_side_sum
    elif opp_side_sum == 0:
        endgame_pressure += my_side_sum
    else:
        endgame_pressure += (opp_side_sum - my_side_sum) * 0.25

    remaining = my_side_sum + opp_side_sum
    if remaining > 30:
        weights = (8, 2, 2, 4, 3, 3, 1)
    elif remaining >= 14:
        weights = (10, 1, 1, 5, 5, 4, 2)
    else:
        weights = (16, 1, 1, 3, 2, 2, 6)

    w_store, w_side, w_mob, w_extra, w_cap, w_risk, w_end = weights
    score = (
        w_store * store_diff
        + w_side * side_seed_diff
        + w_mob * mobility_diff
        + w_extra * extra_turn_potential
        + w_cap * capture_potential
        - w_risk * capture_risk
        + w_end * endgame_pressure
    )

    return score


def evaluate_board(board, ai_player_id, eval_mode="simple"):
    """Evaluation dispatcher supporting multiple heuristic modes."""
    if eval_mode == "phase_aware":
        return evaluate_board_phase_aware(board, ai_player_id)
    return evaluate_board_simple(board, ai_player_id)


def get_ai_move_minimax(board, ai_player_id, depth=None, time_limit=None, eval_mode="simple"):
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
                    stats, start_time, time_limit, eval_mode
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
            stats, start_time, None, eval_mode
        )
        if move is not None:
            best_move = move
        stats['depth_reached'] = search_depth

    stats['time_taken'] = time.time() - start_time
    return best_move, stats


def get_ai_move_alphabeta(board, ai_player_id, depth=None, time_limit=None, eval_mode="simple"):
    """
    Wrapper function to initiate Minimax with Alpha-Beta pruning.
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

                score, move = alphabeta(
                    board, current_depth, True, ai_player_id,
                    -math.inf, math.inf, stats, start_time, time_limit, eval_mode
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
            # Time limit exceeded. Return the best move found from the last
            # fully completed depth.
            pass

    else:
        # --- Fixed Depth Search ---
        # If no depth is provided and no time limit, default to a safe depth of 4
        search_depth = depth if depth is not None else 4
        score, move = alphabeta(
            board, search_depth, True, ai_player_id,
            -math.inf, math.inf, stats, start_time, None, eval_mode
        )
        if move is not None:
            best_move = move
        stats['depth_reached'] = search_depth

    stats['time_taken'] = time.time() - start_time
    return best_move, stats


def minimax(board, depth, is_maximizing, ai_player_id, stats, start_time, time_limit, eval_mode="simple"):
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
        return evaluate_board(board_for_check, ai_player_id, eval_mode=eval_mode), None

    # Determine whose turn it is currently
    current_player = ai_player_id if is_maximizing else (1 if ai_player_id == 2 else 2)
        
    if is_maximizing:
        # --- Maximizing Player (AI) ---
        max_eval = -math.inf
        best_move = None
        
        possible_moves = get_valid_moves(board, player=current_player)
        
        if not possible_moves:
            return evaluate_board(board_for_check, ai_player_id, eval_mode=eval_mode), None
            
        for move in possible_moves:
            board_copy = board.copy()
            new_board, extra_turn = make_move(board_copy, player=current_player, pit=move, verbose=False)
            
            # Kalah rule: If an extra turn is granted, the turn does NOT switch
            next_is_maximizing = True if extra_turn else False
            
            eval_score, _ = minimax(new_board, depth - 1, next_is_maximizing, ai_player_id, stats, start_time, time_limit, eval_mode)
            
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
            return evaluate_board(board_for_check, ai_player_id, eval_mode=eval_mode), None
            
        for move in possible_moves:
            board_copy = board.copy()
            new_board, extra_turn = make_move(board_copy, player=current_player, pit=move, verbose=False)
            
            # Kalah rule: If an extra turn is granted, the turn does NOT switch
            next_is_maximizing = False if extra_turn else True
            
            eval_score, _ = minimax(new_board, depth - 1, next_is_maximizing, ai_player_id, stats, start_time, time_limit, eval_mode)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
                
        return min_eval, best_move


def alphabeta(board, depth, is_maximizing, ai_player_id, alpha, beta, stats, start_time, time_limit, eval_mode="simple"):
    """
    Recursive Minimax algorithm with Alpha-Beta pruning.

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
        return evaluate_board(board_for_check, ai_player_id, eval_mode=eval_mode), None

    # Determine whose turn it is currently
    current_player = ai_player_id if is_maximizing else (1 if ai_player_id == 2 else 2)

    if is_maximizing:
        max_eval = -math.inf
        best_move = None

        possible_moves = get_valid_moves(board, player=current_player)
        if not possible_moves:
            return evaluate_board(board_for_check, ai_player_id, eval_mode=eval_mode), None

        for move in possible_moves:
            board_copy = board.copy()
            new_board, extra_turn = make_move(board_copy, player=current_player, pit=move, verbose=False)

            # Kalah rule: If an extra turn is granted, the turn does NOT switch
            next_is_maximizing = True if extra_turn else False

            eval_score, _ = alphabeta(
                new_board, depth - 1, next_is_maximizing, ai_player_id,
                alpha, beta, stats, start_time, time_limit, eval_mode
            )

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, max_eval)
            if beta <= alpha:
                break

        return max_eval, best_move

    else:
        min_eval = math.inf
        best_move = None

        possible_moves = get_valid_moves(board, player=current_player)
        if not possible_moves:
            return evaluate_board(board_for_check, ai_player_id, eval_mode=eval_mode), None

        for move in possible_moves:
            board_copy = board.copy()
            new_board, extra_turn = make_move(board_copy, player=current_player, pit=move, verbose=False)

            # Kalah rule: If an extra turn is granted, the turn does NOT switch
            next_is_maximizing = False if extra_turn else True

            eval_score, _ = alphabeta(
                new_board, depth - 1, next_is_maximizing, ai_player_id,
                alpha, beta, stats, start_time, time_limit, eval_mode
            )

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, min_eval)
            if beta <= alpha:
                break

        return min_eval, best_move