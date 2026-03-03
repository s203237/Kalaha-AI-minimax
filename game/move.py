"""Move representation for the Kalah game."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Move:
    """A move is identified solely by the pit index chosen by the current player."""

    pit_index: int  # board index (0-5 for player 0, 7-12 for player 1)

    def __repr__(self) -> str:
        return f"Move(pit={self.pit_index})"
