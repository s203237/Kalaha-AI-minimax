"""
Benchmarking Arena.

Runs headless (no UI) matches between configurations of AI agents to 
gather performance metrics (nodes expanded, execution time, win rates).
"""

from kalah_engine import make_move, check_endgame
from players import create_minimax_player

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
    
    p1 = create_minimax_player(depth=8)
    
    p2 = create_minimax_player(time_limit=0.3)
    
    score1, score2, p1_stats, p2_stats = play_headless_game(p1, p2)
    
    print("\n--- Match Results ---")
    print(f"Player 1 (Depth 8) Score: {score1}")
    print(f"Player 2 (Time 0.3s) Score: {score2}")
    
    if score1 > score2:
        print("Player 1 Wins!")
    elif score2 > score1:
        print("Player 2 Wins!")
    else:
        print("Draw!")
        
    print("\n--- Player 1 (Depth-based) Statistics ---")
    print(f"Total Nodes Expanded: {p1_stats['total_nodes']}")
    print(f"Average Time per Turn: {p1_stats['total_time'] / max(1, p1_stats['turns']):.4f} seconds")
    print(f"Max Depth Reached: {p1_stats['max_depth']}")

    print("\n--- Player 2 (Time-based) Statistics ---")
    print(f"Total Nodes Expanded: {p2_stats['total_nodes']}")
    print(f"Average Time per Turn: {p2_stats['total_time'] / max(1, p2_stats['turns']):.4f} seconds")
    print(f"Max Depth Reached: {p2_stats['max_depth']} (Iterative Deepening)")