"""Minimax algorithm (without pruning) for Kalah."""

from __future__ import annotations

from typing import Optional, Tuple

from game.board import Board
from game.engine import apply_move, get_legal_moves
from game.move import Move
from ai.evaluation import evaluate


def minimax(
    board: Board,
    depth: int,
    maximizing_player: int,
) -> Tuple[float, Optional[Move]]:
    """
    Minimax search without alpha-beta pruning.

    Parameters
    ----------
    board:
        Current board state.
    depth:
        Remaining search depth (0 triggers leaf evaluation).
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
            score, _ = minimax(apply_move(board, move), depth - 1, maximizing_player)
            if score > best_score:
                best_score = score
                best_move = move
    else:
        best_score = float("inf")
        for move in legal_moves:
            score, _ = minimax(apply_move(board, move), depth - 1, maximizing_player)
            if score < best_score:
                best_score = score
                best_move = move

    return best_score, best_move
