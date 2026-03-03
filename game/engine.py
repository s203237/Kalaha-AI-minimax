"""Game engine: legal move generation and state transitions for Kalah."""

from __future__ import annotations

from typing import List

from game.board import (
    Board,
    BOARD_SIZE,
    PLAYER0_PITS,
    PLAYER0_STORE,
    PLAYER1_PITS,
    PLAYER1_STORE,
)
from game.move import Move


def get_legal_moves(board: Board) -> List[Move]:
    """Return all legal moves for the current player (non-empty pits only)."""
    return [Move(i) for i in board.get_pits(board.current_player) if board.pits[i] > 0]


def apply_move(board: Board, move: Move) -> Board:
    """
    Apply *move* to *board* and return the resulting board state.

    Rules applied:
    - Seeds are sown counter-clockwise, skipping the opponent's store.
    - If the last seed lands in the current player's store, they take another turn.
    - If the last seed lands in an empty pit on the current player's side and the
      opposite pit is non-empty, both pits are captured into the current player's store.
    - After any move, if one side's pits are completely empty, the remaining seeds on
      the other side are collected into the corresponding store (game-over collection).
    """
    new_board = board.copy()
    player = new_board.current_player
    player_store = PLAYER0_STORE if player == 0 else PLAYER1_STORE
    player_pits = PLAYER0_PITS if player == 0 else PLAYER1_PITS
    opponent_store = PLAYER1_STORE if player == 0 else PLAYER0_STORE

    # Pick up all seeds from the chosen pit.
    pit = move.pit_index
    seeds = new_board.pits[pit]
    new_board.pits[pit] = 0

    # Sow seeds counter-clockwise, skipping the opponent's store.
    pos = pit
    while seeds > 0:
        pos = (pos + 1) % BOARD_SIZE
        if pos == opponent_store:
            continue
        new_board.pits[pos] += 1
        seeds -= 1

    last_pos = pos

    # Capture rule: last seed lands in an empty pit on the player's own side,
    # and the directly opposite pit is non-empty.
    if (
        last_pos in player_pits
        and new_board.pits[last_pos] == 1  # was empty before this seed arrived
        and new_board.pits[_opposite(last_pos)] > 0
    ):
        opposite = _opposite(last_pos)
        new_board.pits[player_store] += new_board.pits[last_pos] + new_board.pits[opposite]
        new_board.pits[last_pos] = 0
        new_board.pits[opposite] = 0

    # Extra-turn rule: last seed lands in the player's own store.
    if last_pos == player_store:
        next_player = player  # same player moves again
    else:
        next_player = 1 - player

    new_board.current_player = next_player

    # Game-over collection: if either side is now empty, sweep remaining seeds.
    if new_board.is_game_over():
        for i in PLAYER0_PITS:
            new_board.pits[PLAYER0_STORE] += new_board.pits[i]
            new_board.pits[i] = 0
        for i in PLAYER1_PITS:
            new_board.pits[PLAYER1_STORE] += new_board.pits[i]
            new_board.pits[i] = 0

    return new_board


def _opposite(pit_index: int) -> int:
    """Return the board index of the pit directly opposite *pit_index*.

    Mapping (both directions):
        0 <-> 12,  1 <-> 11,  2 <-> 10,  3 <-> 9,  4 <-> 8,  5 <-> 7
    """
    return 12 - pit_index
