"""Board state representation for the Kalah game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# Board layout (14 positions total):
#   Indices 0-5  : Player 0's pits
#   Index   6    : Player 0's store (Kalah)
#   Indices 7-12 : Player 1's pits
#   Index   13   : Player 1's store (Kalah)

PITS_PER_PLAYER: int = 6
INITIAL_SEEDS: int = 4
BOARD_SIZE: int = 14

PLAYER0_PITS: List[int] = list(range(0, 6))
PLAYER0_STORE: int = 6
PLAYER1_PITS: List[int] = list(range(7, 13))
PLAYER1_STORE: int = 13


@dataclass
class Board:
    """Immutable-style board state for a Kalah game."""

    pits: List[int]
    current_player: int  # 0 or 1

    @classmethod
    def new_game(cls, seeds_per_pit: int = INITIAL_SEEDS) -> Board:
        """Create a fresh board with the standard starting position."""
        pits = [seeds_per_pit] * BOARD_SIZE
        pits[PLAYER0_STORE] = 0
        pits[PLAYER1_STORE] = 0
        return cls(pits=pits, current_player=0)

    def copy(self) -> Board:
        """Return a deep copy of this board."""
        return Board(pits=self.pits[:], current_player=self.current_player)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_pits(self, player: int) -> List[int]:
        """Return the pit indices for *player* (0 or 1)."""
        return PLAYER0_PITS if player == 0 else PLAYER1_PITS

    def get_store(self, player: int) -> int:
        """Return the store index for *player* (0 or 1)."""
        return PLAYER0_STORE if player == 0 else PLAYER1_STORE

    def seeds_in_pits(self, player: int) -> int:
        """Return the total number of seeds currently in *player*'s pits."""
        return sum(self.pits[i] for i in self.get_pits(player))

    def score(self, player: int) -> int:
        """Return the number of seeds in *player*'s store."""
        return self.pits[self.get_store(player)]

    def is_game_over(self) -> bool:
        """Return True when at least one side has no seeds left in its pits."""
        return self.seeds_in_pits(0) == 0 or self.seeds_in_pits(1) == 0

    def winner(self) -> Optional[int]:
        """
        Return the winning player (0 or 1), or -1 for a draw.
        Returns None if the game is still in progress.
        """
        if not self.is_game_over():
            return None
        s0 = self.pits[PLAYER0_STORE]
        s1 = self.pits[PLAYER1_STORE]
        if s0 > s1:
            return 0
        if s1 > s0:
            return 1
        return -1  # draw
