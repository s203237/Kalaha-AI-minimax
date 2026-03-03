"""CLI entry point: play Kalah against an AI opponent."""

from __future__ import annotations

import argparse
import sys

from game.board import Board, PLAYER0_PITS, PLAYER0_STORE, PLAYER1_PITS, PLAYER1_STORE
from game.engine import apply_move, get_legal_moves
from game.move import Move
from ai.alphabeta import get_best_move

# ──────────────────────────────────────────────────────────────────────────────
# Board display
# ──────────────────────────────────────────────────────────────────────────────

_DIVIDER = "+" + "-" * 52 + "+"


def _fmt(n: int) -> str:
    return f"{n:2d}"


def print_board(board: Board) -> None:
    """Pretty-print the current board state.

    Layout (pit labels shown above / below the seed counts):

        Player 1 (AI)
            [6]  [5]  [4]  [3]  [2]  [1]
    [13]     v    v    v    v    v    v      [ 6]
            [1]  [2]  [3]  [4]  [5]  [6]
        Player 0 (You)
    """
    p1_seeds = [board.pits[i] for i in range(12, 6, -1)]   # pits 12..7 (display L→R)
    p0_seeds = [board.pits[i] for i in range(0, 6)]         # pits  0..5 (display L→R)

    p1_labels = [str(i) for i in range(6, 0, -1)]           # 6 5 4 3 2 1
    p0_labels = [str(i) for i in range(1, 7)]               # 1 2 3 4 5 6

    col_w = 5  # fixed column width

    def row(values: list, width: int = col_w) -> str:
        return "  ".join(f"{v:^{width}}" for v in values)

    print()
    print(_DIVIDER)
    print(f"|  {'Player 1 (AI)':^48}  |")
    print(f"|  {row(p1_labels):^48}  |")
    print(f"|  {row([_fmt(v) for v in p1_seeds]):^48}  |")
    print(
        f"| [{_fmt(board.pits[PLAYER1_STORE])}]{' ' * 42}[{_fmt(board.pits[PLAYER0_STORE])}] |"
    )
    print(f"|  {row([_fmt(v) for v in p0_seeds]):^48}  |")
    print(f"|  {row(p0_labels):^48}  |")
    print(f"|  {'Player 0 (You)':^48}  |")
    print(_DIVIDER)
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Human input
# ──────────────────────────────────────────────────────────────────────────────

def _pit_label_to_index(label: int, player: int) -> int:
    """Convert a 1-based pit label (1-6) to its board index."""
    if player == 0:
        return label - 1          # labels 1-6  →  indices 0-5
    return label + 6              # labels 1-6  →  indices 7-12


def _pit_index_to_label(pit_index: int, player: int) -> int:
    """Convert a board index back to a 1-based pit label."""
    if player == 0:
        return pit_index + 1
    return pit_index - 6


def get_human_move(board: Board) -> Move:
    """Prompt the human player for a move, validating input."""
    legal = get_legal_moves(board)
    legal_labels = sorted(_pit_index_to_label(m.pit_index, 0) for m in legal)
    while True:
        try:
            raw = input(f"  Your move (pits {legal_labels}): ").strip()
            label = int(raw)
            if label < 1 or label > 6:
                raise ValueError
            pit_index = _pit_label_to_index(label, 0)
            move = Move(pit_index)
            if move in legal:
                return move
            print(f"  Pit {label} is empty or invalid. Choose from {legal_labels}.")
        except (ValueError, EOFError):
            print(f"  Invalid input. Enter a number from {legal_labels}.")


# ──────────────────────────────────────────────────────────────────────────────
# Game loop
# ──────────────────────────────────────────────────────────────────────────────

def play(depth: int) -> None:
    board = Board.new_game()
    print("\n=== Kalah ===")
    print(f"AI search depth: {depth}")
    print("You are Player 0 (pits 1-6 along the bottom).")
    print("The AI is Player 1 (pits 1-6 along the top).\n")

    while not board.is_game_over():
        print_board(board)

        if board.current_player == 0:
            # Human turn
            print("Your turn.")
            move = get_human_move(board)
        else:
            # AI turn
            print("AI is thinking…")
            move = get_best_move(board, depth)
            if move is None:
                print("AI has no legal moves — passing.")
                break
            ai_label = _pit_index_to_label(move.pit_index, 1)
            print(f"  AI plays pit {ai_label}.")

        board = apply_move(board, move)

        # Announce extra turn
        # (current_player unchanged means extra turn was granted)
        prev_player = 0 if board.current_player == 1 else 1
        # We can't know from the new board alone without checking the move result,
        # so we just let the loop iterate naturally.

    # Final board
    print_board(board)
    result = board.winner()
    s0 = board.pits[PLAYER0_STORE]
    s1 = board.pits[PLAYER1_STORE]
    print(f"Game over!  You: {s0}  |  AI: {s1}")
    if result == 0:
        print("You win! 🎉")
    elif result == 1:
        print("AI wins.")
    else:
        print("It's a draw.")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Play Kalah (Mancala) against a Minimax/Alpha-Beta AI."
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=6,
        help="AI search depth (default: 6).  Higher = stronger but slower.",
    )
    args = parser.parse_args()

    if args.depth < 1:
        print("Depth must be at least 1.", file=sys.stderr)
        sys.exit(1)

    play(args.depth)


if __name__ == "__main__":
    main()
