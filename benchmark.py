"""
Benchmarking Arena.

Runs headless (no UI) matches between configurations of AI agents to 
gather performance metrics (nodes expanded, execution time, win rates).
"""

from collections import Counter
from statistics import mean, median

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


def _init_player_stats():
    """Create benchmark accumulator for one player."""
    return {
        'total_nodes': 0,
        'total_time': 0.0,
        'turns': 0,
        'max_depth': 0,
        'depth_samples': [],
        'time_samples': [],
        'nodes_samples': [],
    }


def _record_turn_stats(player_stats, stats):
    """Append per-turn stats so we can analyze full distributions later."""
    if not stats:
        return

    nodes = stats.get('nodes', 0)
    time_taken = stats.get('time_taken', 0.0)
    depth = stats.get('depth_reached', 0)

    player_stats['total_nodes'] += nodes
    player_stats['total_time'] += time_taken
    player_stats['max_depth'] = max(player_stats['max_depth'], depth)
    player_stats['turns'] += 1

    player_stats['depth_samples'].append(depth)
    player_stats['time_samples'].append(time_taken)
    player_stats['nodes_samples'].append(nodes)


def _percentile(values, p):
    """Return percentile using linear interpolation between nearest ranks."""
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])

    sorted_vals = sorted(values)
    rank = (len(sorted_vals) - 1) * p
    low = int(rank)
    high = min(low + 1, len(sorted_vals) - 1)
    weight = rank - low
    return sorted_vals[low] * (1 - weight) + sorted_vals[high] * weight


def _quartile_depth_averages(depth_samples):
    """Average depth in each chronological quartile (early -> late game)."""
    n = len(depth_samples)
    if n == 0:
        return []

    buckets = []
    for i in range(4):
        start = int(i * n / 4)
        end = int((i + 1) * n / 4)
        if end > start:
            segment = depth_samples[start:end]
            buckets.append(mean(segment))
        else:
            buckets.append(0.0)
    return buckets


def print_player_stats(label, player_func, stats):
    """Print richer benchmark metrics for one player."""
    print(f"\n--- {label} ({describe_player(player_func)}) Statistics ---")

    turns = stats['turns']
    if turns == 0:
        print("No turn data available.")
        return

    depth_samples = stats['depth_samples']
    time_samples = stats['time_samples']
    nodes_samples = stats['nodes_samples']

    depth_counter = Counter(depth_samples)
    mode_depth, mode_freq = depth_counter.most_common(1)[0]

    q1_depth, q2_depth, q3_depth = (
        _percentile(depth_samples, 0.25),
        _percentile(depth_samples, 0.50),
        _percentile(depth_samples, 0.75),
    )
    q1_time, q2_time, q3_time, p90_time = (
        _percentile(time_samples, 0.25),
        _percentile(time_samples, 0.50),
        _percentile(time_samples, 0.75),
        _percentile(time_samples, 0.90),
    )

    quartile_depths = _quartile_depth_averages(depth_samples)
    nodes_per_second = stats['total_nodes'] / max(stats['total_time'], 1e-9)

    print(f"Turns Played: {turns}")
    print(f"Total Nodes Expanded: {stats['total_nodes']}")
    print(f"Nodes / Second (aggregate): {nodes_per_second:.2f}")

    print("\nDepth Metrics:")
    print(f"  Max Depth: {stats['max_depth']}")
    print(f"  Mean Depth: {mean(depth_samples):.2f}")
    print(f"  Median Depth: {median(depth_samples):.2f}")
    print(f"  Mode Depth: {mode_depth} ({mode_freq}/{turns} turns)")
    print(f"  Depth Quartiles (Q1 / Q2 / Q3): {q1_depth:.2f} / {q2_depth:.2f} / {q3_depth:.2f}")
    print(
        "  Avg Depth by Game Quartile (Early->Late): "
        + " / ".join(f"{value:.2f}" for value in quartile_depths)
    )

    print("\nTime Metrics (seconds per turn):")
    print(f"  Total Time: {stats['total_time']:.4f}")
    print(f"  Mean: {mean(time_samples):.4f}")
    print(f"  Median: {median(time_samples):.4f}")
    print(f"  Min / Max: {min(time_samples):.4f} / {max(time_samples):.4f}")
    print(f"  Time Quartiles (Q1 / Q2 / Q3): {q1_time:.4f} / {q2_time:.4f} / {q3_time:.4f}")
    print(f"  P90 Time: {p90_time:.4f}")

    if getattr(player_func, 'constraint_type', None) == 'time':
        budget = float(getattr(player_func, 'constraint_value', 0.0) or 0.0)
        if budget > 0:
            mean_util = 100.0 * mean(time_samples) / budget
            p90_util = 100.0 * p90_time / budget
            print(f"  Budget Utilization (mean / p90): {mean_util:.1f}% / {p90_util:.1f}% of {budget:.2f}s")

    # Small extra signal that captures node growth volatility by turn.
    print(f"  Nodes per Turn (mean / median): {mean(nodes_samples):.1f} / {median(nodes_samples):.1f}")

def play_headless_game(player1_func, player2_func):
    """
    Runs a single game without printing the board, aggregating statistics.
    """
    board = [4] * 6 + [0] + [4] * 6 + [0]
    current_player = 1 
    
    # Stats aggregation
    p1_stats = _init_player_stats()
    p2_stats = _init_player_stats()

    while not check_endgame(board):
        if current_player == 1:
            pit, stats = player1_func(board, current_player)
            _record_turn_stats(p1_stats, stats)
        else:
            pit, stats = player2_func(board, current_player)
            _record_turn_stats(p2_stats, stats)
            
        board, extra_turn = make_move(board, current_player, pit, verbose=False)
        if not extra_turn:
            current_player = 2 if current_player == 1 else 1

    return board[6], board[13], p1_stats, p2_stats

if __name__ == "__main__":
    print("Starting AI vs AI Benchmark...")

    # Configure each side here.
    p1_depth = 9
    p2_depth = 12
    p1_eval_mode = "phase_aware"
    p2_eval_mode = "simple"

    p1 = create_minimax_player(time_limit=0.5, eval_mode=p1_eval_mode)

    p2 = create_alphabeta_player(time_limit=0.5, eval_mode=p2_eval_mode)

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
        
    print_player_stats("Player 1", p1, p1_stats)
    print_player_stats("Player 2", p2, p2_stats)

    if p1_stats['total_nodes'] > 0:
        node_reduction = 100.0 * (1 - (p2_stats['total_nodes'] / p1_stats['total_nodes']))
        print(f"\nAlpha-Beta node reduction vs Minimax: {node_reduction:.2f}%")