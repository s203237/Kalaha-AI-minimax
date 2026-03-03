"""Alpha-beta pruning optimisation of Minimax for Kalah."""

from __future__ import annotations

from typing import Optional, Tuple

from game.board import Board
from game.engine import apply_move, get_legal_moves
from game.move import Move
from ai.evaluation import evaluate


def alphabeta(
    board: Board,
    depth: int,
    alpha: float,
    beta: float,
    maximizing_player: int,
) -> Tuple[float, Optional[Move]]:
    """
    Minimax with alpha-beta pruning.

    Parameters
    ----------
    board:
        Current board state.
    depth:
        Remaining search depth (0 triggers leaf evaluation).
    alpha:
        Best score the maximising player is guaranteed so far (lower bound).
    beta:
        Best score the minimising player is guaranteed so far (upper bound).
    maximizing_player:
        The player index (0 or 1) we are maximising for throughout the tree.

    Returns
    -------
    (score, best_move)
        *best_move* is None at leaf nodes.
    """
    if depth == 0 or board.is_game_over():
        return evaluate(board, maximizing_player), None

    legal_moves = get_legal_moves(board)
    if not legal_moves:
        return evaluate(board, maximizing_player), None

    is_maximizing = board.current_player == maximizing_player
    best_move: Optional[Move] = None

    if is_maximizing:
        best_score = float("-inf")
        for move in legal_moves:
            score, _ = alphabeta(
                apply_move(board, move), depth - 1, alpha, beta, maximizing_player
            )
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # β-cutoff
    else:
        best_score = float("inf")
        for move in legal_moves:
            score, _ = alphabeta(
                apply_move(board, move), depth - 1, alpha, beta, maximizing_player
            )
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # α-cutoff

    return best_score, best_move


def get_best_move(board: Board, depth: int) -> Optional[Move]:
    """Convenience wrapper: return the best move for the current player."""
    player = board.current_player
    _, move = alphabeta(board, depth, float("-inf"), float("inf"), player)
    return move
