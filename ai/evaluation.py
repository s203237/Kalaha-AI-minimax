"""Heuristic evaluation function for Kalah board states."""

from __future__ import annotations

from game.board import Board, PLAYER0_PITS, PLAYER0_STORE, PLAYER1_PITS, PLAYER1_STORE

_WIN_SCORE = 1000.0


def evaluate(board: Board, player: int) -> float:
    """
    Return a heuristic score for *board* from the perspective of *player*.

    Positive values favour *player*; negative values favour the opponent.

    Components (in order of importance):
    1. Terminal detection — returns ±WIN_SCORE or 0 for draws.
    2. Store difference — number of seeds already secured.
    3. Pit-seed difference — seeds still in play on each side (weighted lower).
    """
    if board.is_game_over():
        s0 = board.pits[PLAYER0_STORE]
        s1 = board.pits[PLAYER1_STORE]
        player_score = s0 if player == 0 else s1
        opponent_score = s1 if player == 0 else s0
        if player_score > opponent_score:
            return _WIN_SCORE
        if player_score < opponent_score:
            return -_WIN_SCORE
        return 0.0

    player_store = PLAYER0_STORE if player == 0 else PLAYER1_STORE
    opponent_store = PLAYER1_STORE if player == 0 else PLAYER0_STORE
    player_pits = PLAYER0_PITS if player == 0 else PLAYER1_PITS
    opponent_pits = PLAYER1_PITS if player == 0 else PLAYER0_PITS

    store_diff = board.pits[player_store] - board.pits[opponent_store]
    pit_diff = (
        sum(board.pits[i] for i in player_pits)
        - sum(board.pits[i] for i in opponent_pits)
    )

    return store_diff + 0.1 * pit_diff
