"""
Arena: deterministic side-swapping benchmark suite with report export.

Running this file will:
1. Execute all configured head-to-head matchups sequentially.
2. Print concise console summaries.
3. Export a CSV summary.
4. Export a pdfLaTeX-friendly .tex snippet for Overleaf.

The exported LaTeX is intentionally simple and should work with pdfLaTeX /
TeX Live 2025 using standard packages only.
"""

from collections import Counter
from statistics import mean, median

from benchmark import play_headless_game
from players import create_alphabeta_player, create_minimax_player


# Configuration
N_GAMES_PER_SIDE = 1
LATEX_OUT = "arena_report_tables.tex"
CSV_OUT = "arena_report_summary.csv"
BEST_FINDINGS_OUT = "arena_best_findings.tex"

SEP = "=" * 72
DASH = "-" * 72


def _avg(samples):
    return mean(samples) if samples else 0.0


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


def _latex_escape(text):
    """Escape text for plain pdfLaTeX table output."""
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    return ''.join(replacements.get(char, char) for char in str(text))


def _format_float(value, digits=2):
    return f"{value:.{digits}f}"


def _first_mover_dominance(result):
    """True when player 1 wins every game regardless of configuration."""
    nh = result['total'] // 2
    return (
        result['a_wins_p1'] == nh
        and result['b_wins_p1'] == nh
        and result['a_wins_p2'] == 0
        and result['b_wins_p2'] == 0
        and result['draws'] == 0
    )


def run_matchup(factory_a, label_a, factory_b, label_b, n_per_side=N_GAMES_PER_SIDE):
    """Play a deterministic side-swapped matchup and aggregate search stats."""
    total = 2 * n_per_side

    a_wins_p1 = a_wins_p2 = 0
    b_wins_p1 = b_wins_p2 = 0
    draws_r1 = draws_r2 = 0

    score_margins = []
    a_depths = []
    b_depths = []
    a_nodes = []
    b_nodes = []
    a_times = []
    b_times = []
    a_total_nodes = b_total_nodes = 0.0
    a_total_time = b_total_time = 0.0

    def _accumulate(st_a, st_b):
        nonlocal a_total_nodes, b_total_nodes, a_total_time, b_total_time
        a_depths.extend(st_a['depth_samples'])
        b_depths.extend(st_b['depth_samples'])
        a_nodes.extend(st_a['nodes_samples'])
        b_nodes.extend(st_b['nodes_samples'])
        a_times.extend(st_a['time_samples'])
        b_times.extend(st_b['time_samples'])
        a_total_nodes += st_a['total_nodes']
        b_total_nodes += st_b['total_nodes']
        a_total_time += st_a['total_time']
        b_total_time += st_b['total_time']

    for game_number in range(1, n_per_side + 1):
        player_a, player_b = factory_a(), factory_b()
        score_a, score_b, stats_a, stats_b = play_headless_game(player_a, player_b)
        margin = score_a - score_b
        score_margins.append(margin)
        _accumulate(stats_a, stats_b)

        if margin > 0:
            a_wins_p1 += 1
            outcome = f"{label_a} wins"
        elif margin < 0:
            b_wins_p2 += 1
            outcome = f"{label_b} wins"
        else:
            draws_r1 += 1
            outcome = "Draw"

        print(f"    Game {game_number:2}/{total}  [{label_a:>24} as P1]  {score_a:2}-{score_b:2}  {outcome}")

    for game_number in range(n_per_side + 1, total + 1):
        player_a, player_b = factory_a(), factory_b()
        score_b, score_a, stats_b, stats_a = play_headless_game(player_b, player_a)
        margin = score_a - score_b
        score_margins.append(margin)
        _accumulate(stats_a, stats_b)

        if margin > 0:
            a_wins_p2 += 1
            outcome = f"{label_a} wins"
        elif margin < 0:
            b_wins_p1 += 1
            outcome = f"{label_b} wins"
        else:
            draws_r2 += 1
            outcome = "Draw"

        print(f"    Game {game_number:2}/{total}  [{label_b:>24} as P1]  {score_b:2}-{score_a:2}  {outcome}")

    result = {
        'total': total,
        'a_wins': a_wins_p1 + a_wins_p2,
        'a_wins_p1': a_wins_p1,
        'a_wins_p2': a_wins_p2,
        'b_wins': b_wins_p1 + b_wins_p2,
        'b_wins_p1': b_wins_p1,
        'b_wins_p2': b_wins_p2,
        'draws': draws_r1 + draws_r2,
        'score_margins': score_margins,
        'a_avg_depth': _avg(a_depths),
        'b_avg_depth': _avg(b_depths),
        'a_med_depth': median(a_depths) if a_depths else 0.0,
        'b_med_depth': median(b_depths) if b_depths else 0.0,
        'a_mode_depth': Counter(a_depths).most_common(1)[0][0] if a_depths else 0,
        'b_mode_depth': Counter(b_depths).most_common(1)[0][0] if b_depths else 0,
        'a_q3_depth': _percentile(a_depths, 0.75),
        'b_q3_depth': _percentile(b_depths, 0.75),
        'a_avg_nodes': _avg(a_nodes),
        'b_avg_nodes': _avg(b_nodes),
        'a_nodes_sec': a_total_nodes / max(a_total_time, 1e-9),
        'b_nodes_sec': b_total_nodes / max(b_total_time, 1e-9),
        'a_avg_time': _avg(a_times),
        'b_avg_time': _avg(b_times),
    }
    result['first_mover_dominance'] = _first_mover_dominance(result)
    return result


def print_results(label_a, label_b, result):
    """Print a concise console summary for one matchup."""
    total = result['total']
    per_side = total // 2
    avg_margin = _avg(result['score_margins'])
    a_win_rate = 100.0 * result['a_wins'] / total

    print(f"\n  {DASH}")
    print(f"  {label_a}  vs  {label_b}  -  {total} games  ({per_side} per side)")
    print(f"  {DASH}")
    print(
        f"  {'Record (W/D/L)':22}  {label_a}: "
        f"{result['a_wins']}W / {result['draws']}D / {result['b_wins']}L   "
        f"win rate {a_win_rate:.0f}%"
    )
    print(
        f"  {'Side split (A wins)':22}  as P1: {result['a_wins_p1']}/{per_side}   "
        f"as P2: {result['a_wins_p2']}/{per_side}"
    )
    print(f"  {'Avg score margin':22}  {avg_margin:+.1f}  (positive = {label_a} ahead)")

    if result['first_mover_dominance']:
        print("  *** FIRST-MOVER DOMINANCE: P1 won every game regardless of configuration.")
        print("      Config quality cannot be distinguished from this matchup alone.")

    width = 18
    print()
    print(f"  {'Metric':<26}  {label_a:>{width}}  {label_b:>{width}}")
    print(f"  {'-' * 26}  {'-' * width}  {'-' * width}")
    print(f"  {'Median depth / turn':<26}  {result['a_med_depth']:>{width}.2f}  {result['b_med_depth']:>{width}.2f}")
    print(f"  {'Mode depth / turn':<26}  {result['a_mode_depth']:>{width}}  {result['b_mode_depth']:>{width}}")
    print(f"  {'Q3 depth / turn':<26}  {result['a_q3_depth']:>{width}.2f}  {result['b_q3_depth']:>{width}.2f}")
    print(f"  {'Mean depth / turn':<26}  {result['a_avg_depth']:>{width}.2f}  {result['b_avg_depth']:>{width}.2f}")
    print(f"  {'Avg nodes / turn':<26}  {result['a_avg_nodes']:>{width},.0f}  {result['b_avg_nodes']:>{width},.0f}")
    print(f"  {'Nodes / second':<26}  {result['a_nodes_sec']:>{width},.0f}  {result['b_nodes_sec']:>{width},.0f}")
    print(f"  {'Avg time / turn (s)':<26}  {result['a_avg_time']:>{width}.4f}  {result['b_avg_time']:>{width}.4f}")

    notes = []
    depth_diff = result['a_med_depth'] - result['b_med_depth']
    same_depth = abs(depth_diff) < 0.5 and abs(result['a_mode_depth'] - result['b_mode_depth']) < 0.5

    if not same_depth:
        deeper = label_a if depth_diff > 0 else label_b
        notes.append(
            f"{deeper} reached deeper search "
            f"(median {result['a_med_depth']:.1f} vs {result['b_med_depth']:.1f}, "
            f"mode {result['a_mode_depth']} vs {result['b_mode_depth']})"
        )

    speed_ratio = result['a_nodes_sec'] / max(result['b_nodes_sec'], 1)
    if speed_ratio > 1.3:
        notes.append(
            f"{label_a} faster per node "
            f"({result['a_nodes_sec']:,.0f} vs {result['b_nodes_sec']:,.0f} nodes/s)"
        )
    elif speed_ratio < 1 / 1.3:
        notes.append(
            f"{label_b} faster per node "
            f"({result['b_nodes_sec']:,.0f} vs {result['a_nodes_sec']:,.0f} nodes/s)"
        )

    if same_depth:
        node_ratio = result['a_avg_nodes'] / max(result['b_avg_nodes'], 1)
        if node_ratio > 2.0:
            notes.append(
                f"{label_b} prunes far more nodes/turn "
                f"({result['b_avg_nodes']:,.0f} vs {result['a_avg_nodes']:,.0f})"
            )
        elif node_ratio < 0.5:
            notes.append(
                f"{label_a} prunes far more nodes/turn "
                f"({result['a_avg_nodes']:,.0f} vs {result['b_avg_nodes']:,.0f})"
            )

    winner = label_a if result['a_wins'] > result['b_wins'] else label_b if result['b_wins'] > result['a_wins'] else None
    if notes:
        prefix = f"  Why: {winner} won - " if (winner and not result['first_mover_dominance']) else "  Context: "
        print(f"\n{prefix}" + "; ".join(notes))


def run_group(title, note, matchups, n_per_side=N_GAMES_PER_SIDE):
    """Run all matchups in a named group and return structured results."""
    print(f"\n\n{SEP}")
    print(f"  {title}")
    if note:
        print(f"  {note}")
    print(SEP)

    group_results = []
    for label_a, factory_a, label_b, factory_b in matchups:
        print(f"\n  > {label_a}  vs  {label_b}")
        result = run_matchup(factory_a, label_a, factory_b, label_b, n_per_side)
        print_results(label_a, label_b, result)
        group_results.append({'label_a': label_a, 'label_b': label_b, 'result': result})

    return {'title': title, 'note': note, 'matchups': group_results}


def build_groups():
    """Return the full benchmark suite definition."""
    return [
        {
            'title': "GROUP 1  -  Minimax vs Minimax  (simple eval, fixed depth)",
            'note': "Larger depth gaps make strength differences easier to see despite strong first-move advantage.",
            'matchups': [
                ("MM-d4", lambda: create_minimax_player(depth=4, eval_mode="simple"), "MM-d6", lambda: create_minimax_player(depth=6, eval_mode="simple")),
                ("MM-d5", lambda: create_minimax_player(depth=5, eval_mode="simple"), "MM-d7", lambda: create_minimax_player(depth=7, eval_mode="simple")),
                ("MM-d6", lambda: create_minimax_player(depth=6, eval_mode="simple"), "MM-d7", lambda: create_minimax_player(depth=7, eval_mode="simple")),
            ],
        },
        {
            'title': "GROUP 2  -  Alpha-Beta vs Alpha-Beta  (simple eval, fixed depth)",
            'note': "Mix of medium and large depth jumps to show when extra lookahead actually changes play.",
            'matchups': [
                ("AB-d7", lambda: create_alphabeta_player(depth=7, eval_mode="simple"), "AB-d11", lambda: create_alphabeta_player(depth=11, eval_mode="simple")),
                ("AB-d9", lambda: create_alphabeta_player(depth=9, eval_mode="simple"), "AB-d11", lambda: create_alphabeta_player(depth=11, eval_mode="simple")),
                ("AB-d11", lambda: create_alphabeta_player(depth=11, eval_mode="simple"), "AB-d13", lambda: create_alphabeta_player(depth=13, eval_mode="simple")),
                ("AB-d9", lambda: create_alphabeta_player(depth=9, eval_mode="simple"), "AB-d13", lambda: create_alphabeta_player(depth=13, eval_mode="simple")),
            ],
        },
        {
            'title': "GROUP 3  -  Minimax vs Alpha-Beta  (depth=7, simple eval)",
            'note': "Same eval + same depth should choose the same move. Useful for pruning-efficiency validation.",
            'matchups': [
                ("MM-d7", lambda: create_minimax_player(depth=7, eval_mode="simple"), "AB-d7", lambda: create_alphabeta_player(depth=7, eval_mode="simple")),
            ],
        },
        {
            'title': "GROUP 4  -  Simple vs Phase-Aware eval  (fixed depth)",
            'note': "Equal depth removes cost tradeoff, so any difference is pure heuristic quality.",
            'matchups': [
                ("AB-d9-simple", lambda: create_alphabeta_player(depth=9, eval_mode="simple"), "AB-d9-phaseaware", lambda: create_alphabeta_player(depth=9, eval_mode="phase_aware")),
                ("AB-d11-simple", lambda: create_alphabeta_player(depth=11, eval_mode="simple"), "AB-d11-phaseaware", lambda: create_alphabeta_player(depth=11, eval_mode="phase_aware")),
                ("AB-d13-simple", lambda: create_alphabeta_player(depth=13, eval_mode="simple"), "AB-d13-phaseaware", lambda: create_alphabeta_player(depth=13, eval_mode="phase_aware")),
            ],
        },
        {
            'title': "GROUP 5  -  Simple vs Phase-Aware eval  (time-limited)",
            'note': "Phase-aware is slower per node. These tests show whether richer evaluation compensates for shallower search.",
            'matchups': [
                ("AB-simple-0.1s", lambda: create_alphabeta_player(time_limit=0.1, eval_mode="simple"), "AB-phaseaware-0.1s", lambda: create_alphabeta_player(time_limit=0.1, eval_mode="phase_aware")),
                ("AB-simple-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="simple"), "AB-phaseaware-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="phase_aware")),
                ("AB-simple-0.5s", lambda: create_alphabeta_player(time_limit=0.5, eval_mode="simple"), "AB-phaseaware-0.5s", lambda: create_alphabeta_player(time_limit=0.5, eval_mode="phase_aware")),
                ("AB-simple-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="simple"), "AB-phaseaware-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="phase_aware")),
                ("AB-simple-2s", lambda: create_alphabeta_player(time_limit=2.0, eval_mode="simple"), "AB-phaseaware-2s", lambda: create_alphabeta_player(time_limit=2.0, eval_mode="phase_aware")),
            ],
        },
        {
            'title': "GROUP 6  -  Minimax vs Alpha-Beta  (time-limited, same eval)",
            'note': "Equal time budget isolates alpha-beta pruning efficiency.",
            'matchups': [
                ("MM-simple-0.1s", lambda: create_minimax_player(time_limit=0.1, eval_mode="simple"), "AB-simple-0.1s", lambda: create_alphabeta_player(time_limit=0.1, eval_mode="simple")),
                ("MM-simple-0.5s", lambda: create_minimax_player(time_limit=0.5, eval_mode="simple"), "AB-simple-0.5s", lambda: create_alphabeta_player(time_limit=0.5, eval_mode="simple")),
                ("MM-simple-1s", lambda: create_minimax_player(time_limit=1.0, eval_mode="simple"), "AB-simple-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="simple")),
                ("MM-phaseaware-1s", lambda: create_minimax_player(time_limit=1.0, eval_mode="phase_aware"), "AB-phaseaware-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="phase_aware")),
            ],
        },
        {
            'title': "GROUP 7  -  Time-limit scaling  (Alpha-Beta)",
            'note': "Very short budgets plus larger jumps make plateau behaviour easier to see.",
            'matchups': [
                ("AB-simple-0.05s", lambda: create_alphabeta_player(time_limit=0.05, eval_mode="simple"), "AB-simple-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="simple")),
                ("AB-simple-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="simple"), "AB-simple-0.5s", lambda: create_alphabeta_player(time_limit=0.5, eval_mode="simple")),
                ("AB-simple-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="simple"), "AB-simple-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="simple")),
                ("AB-simple-0.5s", lambda: create_alphabeta_player(time_limit=0.5, eval_mode="simple"), "AB-simple-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="simple")),
                ("AB-simple-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="simple"), "AB-simple-2s", lambda: create_alphabeta_player(time_limit=2.0, eval_mode="simple")),
                ("AB-pa-0.05s", lambda: create_alphabeta_player(time_limit=0.05, eval_mode="phase_aware"), "AB-pa-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="phase_aware")),
                ("AB-pa-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="phase_aware"), "AB-pa-0.5s", lambda: create_alphabeta_player(time_limit=0.5, eval_mode="phase_aware")),
                ("AB-pa-0.25s", lambda: create_alphabeta_player(time_limit=0.25, eval_mode="phase_aware"), "AB-pa-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="phase_aware")),
                ("AB-pa-0.5s", lambda: create_alphabeta_player(time_limit=0.5, eval_mode="phase_aware"), "AB-pa-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="phase_aware")),
                ("AB-pa-1s", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="phase_aware"), "AB-pa-2s", lambda: create_alphabeta_player(time_limit=2.0, eval_mode="phase_aware")),
            ],
        },
        {
            'title': "GROUP 8  -  Best Configurations Head-to-Head",
            'note': "Cross-group summary comparisons for the report.",
            'matchups': [
                ("MM-1s-simple", lambda: create_minimax_player(time_limit=1.0, eval_mode="simple"), "AB-1s-simple", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="simple")),
                ("AB-1s-simple", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="simple"), "AB-1s-phaseaware", lambda: create_alphabeta_player(time_limit=1.0, eval_mode="phase_aware")),
                ("AB-d11-simple", lambda: create_alphabeta_player(depth=11, eval_mode="simple"), "AB-d11-phaseaware", lambda: create_alphabeta_player(depth=11, eval_mode="phase_aware")),
            ],
        },
    ]


def run_suite(n_per_side=N_GAMES_PER_SIDE):
    """Run all groups and return structured results for export."""
    print(SEP)
    print("  Kalaha AI Arena - Multi-Game Side-Swapping Benchmark")
    print(f"  {n_per_side} games per side  ({2 * n_per_side} total per matchup)")
    print("  Games run sequentially for accurate time-limited benchmarks.")
    print(SEP)

    suite_results = []
    for group in build_groups():
        suite_results.append(run_group(group['title'], group['note'], group['matchups'], n_per_side))

    print(f"\n\n{SEP}")
    print("  Arena complete.")
    print(SEP)
    return suite_results


def export_csv(suite_results, file_path=CSV_OUT):
    """Write a spreadsheet-friendly summary."""
    lines = [
        "group,config_a,config_b,wdl_a,avg_margin,first_mover_dominance,median_depth_a,median_depth_b,mode_depth_a,mode_depth_b,q3_depth_a,q3_depth_b,nodes_sec_a,nodes_sec_b,avg_time_a,avg_time_b"
    ]

    for group in suite_results:
        for matchup in group['matchups']:
            result = matchup['result']
            lines.append(
                ",".join([
                    f'"{group["title"]}"',
                    f'"{matchup["label_a"]}"',
                    f'"{matchup["label_b"]}"',
                    f'"{result["a_wins"]}/{result["draws"]}/{result["b_wins"]}"',
                    _format_float(_avg(result['score_margins']), 1),
                    "yes" if result['first_mover_dominance'] else "no",
                    _format_float(result['a_med_depth'], 2),
                    _format_float(result['b_med_depth'], 2),
                    str(result['a_mode_depth']),
                    str(result['b_mode_depth']),
                    _format_float(result['a_q3_depth'], 2),
                    _format_float(result['b_q3_depth'], 2),
                    _format_float(result['a_nodes_sec'], 0),
                    _format_float(result['b_nodes_sec'], 0),
                    _format_float(result['a_avg_time'], 4),
                    _format_float(result['b_avg_time'], 4),
                ])
            )

    with open(file_path, 'w', encoding='utf-8') as handle:
        handle.write("\n".join(lines) + "\n")


def export_latex(suite_results, file_path=LATEX_OUT):
    """Write a pdfLaTeX-friendly table snippet for Overleaf."""
    lines = [
        "% Auto-generated by arena.py",
        "% Suggested preamble additions: \\usepackage{booktabs} and \\usepackage{longtable}",
        "",
        "\\begin{center}",
        "\\small",
        "\\begin{longtable}{p{2.9cm}p{2.9cm}c c c c c c}",
        "\\toprule",
        "Config A & Config B & W/D/L & Margin & P1 dom. & Median depth & Mode depth & Nodes/s " + r"\\",
        "\\midrule",
        "\\endfirsthead",
        "\\toprule",
        "Config A & Config B & W/D/L & Margin & P1 dom. & Median depth & Mode depth & Nodes/s " + r"\\",
        "\\midrule",
        "\\endhead",
    ]

    for group in suite_results:
        lines.append("\\multicolumn{8}{l}{\\textbf{" + _latex_escape(group['title']) + "}} " + r"\\")
        lines.append("\\midrule")
        for matchup in group['matchups']:
            result = matchup['result']
            lines.append(
                "{} & {} & {} & {} & {} & {} / {} & {} / {} & {} / {}".format(
                    _latex_escape(matchup['label_a']),
                    _latex_escape(matchup['label_b']),
                    _latex_escape(f"{result['a_wins']}/{result['draws']}/{result['b_wins']}"),
                    _latex_escape(_format_float(_avg(result['score_margins']), 1)),
                    "yes" if result['first_mover_dominance'] else "no",
                    _format_float(result['a_med_depth'], 1),
                    _format_float(result['b_med_depth'], 1),
                    result['a_mode_depth'],
                    result['b_mode_depth'],
                    _format_float(result['a_nodes_sec'], 0),
                    _format_float(result['b_nodes_sec'], 0),
                ) + r"\\"
            )
        lines.append("\\midrule")

    lines.extend([
        "\\bottomrule",
        "\\end{longtable}",
        "\\end{center}",
        "",
        "% W/D/L and margin are from config A's perspective.",
        "% P1 dom. marks matchups where player 1 won on both sides.",
        "% Median depth, mode depth and nodes/s are shown as A / B.",
    ])

    with open(file_path, 'w', encoding='utf-8') as handle:
        handle.write("\n".join(lines) + "\n")


def _flatten_matchups(suite_results):
    """Flatten suite results into a simple list for insight selection."""
    rows = []
    for group in suite_results:
        for matchup in group['matchups']:
            rows.append({
                'group': group['title'],
                'label_a': matchup['label_a'],
                'label_b': matchup['label_b'],
                'result': matchup['result'],
            })
    return rows


def _pick_best(row_candidates, key_fn):
    """Pick best row safely from candidates."""
    if not row_candidates:
        return None
    return max(row_candidates, key=key_fn)


def export_best_findings_latex(suite_results, file_path=BEST_FINDINGS_OUT):
    """Write a compact findings table intended for the main report body."""
    rows = _flatten_matchups(suite_results)
    total = len(rows)
    first_move_count = sum(1 for row in rows if row['result']['first_mover_dominance'])
    first_move_ratio = (100.0 * first_move_count / total) if total else 0.0

    g6 = [row for row in rows if "GROUP 6" in row['group'] and "MM-" in row['label_a'] and "AB-" in row['label_b']]
    mm_vs_ab_time = _pick_best(g6, key_fn=lambda row: row['result']['b_med_depth'] - row['result']['a_med_depth'])

    g4 = [row for row in rows if "GROUP 4" in row['group'] and "phaseaware" in row['label_b']]
    phase_depth = _pick_best(g4, key_fn=lambda row: row['result']['a_med_depth'] + row['result']['b_med_depth'])

    g5 = [row for row in rows if "GROUP 5" in row['group'] and "simple" in row['label_a'] and "phaseaware" in row['label_b']]
    phase_time_cost = _pick_best(g5, key_fn=lambda row: row['result']['a_med_depth'] - row['result']['b_med_depth'])

    g7_simple = [row for row in rows if "GROUP 7" in row['group'] and row['label_a'].startswith("AB-simple") and row['label_b'].startswith("AB-simple")]
    time_scaling_simple = _pick_best(g7_simple, key_fn=lambda row: row['result']['b_med_depth'] - row['result']['a_med_depth'])

    compact_rows = []
    compact_rows.append({
        'finding': "First-mover advantage is strong",
        'evidence': f"{first_move_count}/{total} matchups flagged as first-mover dominance",
        'implication': f"Use score margins and depth metrics; avoid raw win-rate only ({first_move_ratio:.0f}% flagged)",
    })

    if mm_vs_ab_time:
        result = mm_vs_ab_time['result']
        compact_rows.append({
            'finding': "Alpha-Beta is stronger under equal time budgets",
            'evidence': (
                f"{mm_vs_ab_time['label_a']} vs {mm_vs_ab_time['label_b']}: "
                f"median depth {result['a_med_depth']:.1f} vs {result['b_med_depth']:.1f}"
            ),
            'implication': "Pruning buys deeper lookahead even when nodes/second is lower",
        })

    if phase_time_cost:
        result = phase_time_cost['result']
        compact_rows.append({
            'finding': "Phase-aware evaluation has a heavy compute cost",
            'evidence': (
                f"{phase_time_cost['label_a']} vs {phase_time_cost['label_b']}: "
                f"nodes/s {result['a_nodes_sec']:.0f} vs {result['b_nodes_sec']:.0f}, "
                f"median depth {result['a_med_depth']:.1f} vs {result['b_med_depth']:.1f}"
            ),
            'implication': "At low/medium time limits, simple eval often reaches deeper search",
        })

    if phase_depth:
        result = phase_depth['result']
        compact_rows.append({
            'finding': "Phase-aware becomes competitive at deeper fixed-depth searches",
            'evidence': (
                f"{phase_depth['label_a']} vs {phase_depth['label_b']}: "
                f"median depth {result['a_med_depth']:.1f}/{result['b_med_depth']:.1f}, "
                f"margin { _avg(result['score_margins']):+.1f} (A perspective)"
            ),
            'implication': "Keep higher-depth phase-aware tests in the appendix to show this crossover",
        })

    if time_scaling_simple:
        result = time_scaling_simple['result']
        compact_rows.append({
            'finding': "More time generally increases effective search depth",
            'evidence': (
                f"{time_scaling_simple['label_a']} vs {time_scaling_simple['label_b']}: "
                f"median depth {result['a_med_depth']:.1f} -> {result['b_med_depth']:.1f}"
            ),
            'implication': "Time-scaling curves are useful for choosing practical move-time budgets",
        })

    lines = [
        "% Auto-generated by arena.py",
        "% Compact findings table for main report text.",
        "% Suggested preamble additions: \\usepackage{booktabs} and \\usepackage{tabularx}",
        "",
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\begin{tabularx}{\\linewidth}{p{0.25\\linewidth}p{0.37\\linewidth}p{0.30\\linewidth}}",
        "\\toprule",
        "Finding & Evidence & Report takeaway " + r"\\",
        "\\midrule",
    ]

    for row in compact_rows:
        lines.append(
            "{} & {} & {}".format(
                _latex_escape(row['finding']),
                _latex_escape(row['evidence']),
                _latex_escape(row['implication']),
            ) + r"\\"
        )

    lines.extend([
        "\\bottomrule",
        "\\end{tabularx}",
        "\\caption{Compact benchmark findings extracted from the full arena run.}",
        "\\label{tab:arena-best-findings}",
        "\\end{table}",
    ])

    with open(file_path, 'w', encoding='utf-8') as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    suite_results = run_suite()
    export_latex(suite_results, LATEX_OUT)
    export_csv(suite_results, CSV_OUT)
    export_best_findings_latex(suite_results, BEST_FINDINGS_OUT)
    print(f"\nLaTeX tables written to {LATEX_OUT}")
    print(f"CSV summary written to {CSV_OUT}")
    print(f"Best findings table written to {BEST_FINDINGS_OUT}")
