"""
Benchmarking Arena.

Runs headless (no UI) matches between configurations of AI agents to 
gather performance metrics (nodes expanded, execution time, win rates).
"""

from kalah_engine import make_move, check_endgame
from players import create_minimax_player, create_alphabeta_player


def describe_player(player_func):
    """Build a human-readable label from metadata attached to player factories."""
    player_type = getattr(player_func, 'player_type', 'Unknown')
    constraint_type = getattr(player_func, 'constraint_type', 'none')
    constraint_value = getattr(player_func, 'constraint_value', None)
    eval_mode = getattr(player_func, 'eval_mode', None)

    if constraint_type == 'depth':
        constraint_label = f"Depth {constraint_value}"
    elif constraint_type == 'time':
        constraint_label = f"Time {constraint_value}s"
    else:
        constraint_label = None

    parts = [player_type]
    if constraint_label:
        parts.append(constraint_label)
    if eval_mode:
        parts.append(f"Eval {eval_mode}")
    return ", ".join(parts)

def play_headless_game(player1_func, player2_func):
    """
    Runs a single game without printing the board, aggregating statistics.
    """
    board = [4] * 6 + [0] + [4] * 6 + [0]
    current_player = 1 
    
    # Stats aggregation
    p1_stats = {'total_nodes': 0, 'total_time': 0.0, 'turns': 0, 'max_depth': 0}
    p2_stats = {'total_nodes': 0, 'total_time': 0.0, 'turns': 0, 'max_depth': 0}

    while not check_endgame(board):
        if current_player == 1:
            pit, stats = player1_func(board, current_player)
            if stats:
                p1_stats['total_nodes'] += stats.get('nodes', 0)
                p1_stats['total_time'] += stats.get('time_taken', 0.0)
                p1_stats['max_depth'] = max(p1_stats['max_depth'], stats.get('depth_reached', 0))
                p1_stats['turns'] += 1
        else:
            pit, stats = player2_func(board, current_player)
            if stats:
                p2_stats['total_nodes'] += stats.get('nodes', 0)
                p2_stats['total_time'] += stats.get('time_taken', 0.0)
                p2_stats['max_depth'] = max(p2_stats['max_depth'], stats.get('depth_reached', 0))
                p2_stats['turns'] += 1
            
        board, extra_turn = make_move(board, current_player, pit, verbose=False)
        if not extra_turn:
            current_player = 2 if current_player == 1 else 1

    return board[6], board[13], p1_stats, p2_stats

if __name__ == "__main__":
    print("Starting AI vs AI Benchmark...")

    # Configure each side here.
    p1_depth = 9
    p2_depth = 12
    p1_eval_mode = "simple"
    p2_eval_mode = "phase_aware"

    p1 = create_minimax_player(depth=p1_depth, eval_mode=p1_eval_mode)

    p2 = create_alphabeta_player(depth=p2_depth, eval_mode=p2_eval_mode)

    p1_label = describe_player(p1)
    p2_label = describe_player(p2)
    
    score1, score2, p1_stats, p2_stats = play_headless_game(p1, p2)
    
    print("\n--- Match Results ---")
    print(f"Player 1 ({p1_label}) Score: {score1}")
    print(f"Player 2 ({p2_label}) Score: {score2}")
    
    if score1 > score2:
        print("Player 1 Wins!")
    elif score2 > score1:
        print("Player 2 Wins!")
    else:
        print("Draw!")
        
    print(f"\n--- Player 1 ({p1_label}) Statistics ---")
    print(f"Total Nodes Expanded: {p1_stats['total_nodes']}")
    print(f"Average Time per Turn: {p1_stats['total_time'] / max(1, p1_stats['turns']):.4f} seconds")
    print(f"Max Depth Reached: {p1_stats['max_depth']}")

    print(f"\n--- Player 2 ({p2_label}) Statistics ---")
    print(f"Total Nodes Expanded: {p2_stats['total_nodes']}")
    print(f"Average Time per Turn: {p2_stats['total_time'] / max(1, p2_stats['turns']):.4f} seconds")
    print(f"Max Depth Reached: {p2_stats['max_depth']}")

    if p1_stats['total_nodes'] > 0:
        node_reduction = 100.0 * (1 - (p2_stats['total_nodes'] / p1_stats['total_nodes']))
        print(f"\nAlpha-Beta node reduction vs Minimax: {node_reduction:.2f}%")