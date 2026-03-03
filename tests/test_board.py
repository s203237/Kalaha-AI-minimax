"""Tests for game.board."""

import pytest
from game.board import (
    Board,
    INITIAL_SEEDS,
    BOARD_SIZE,
    PLAYER0_PITS,
    PLAYER0_STORE,
    PLAYER1_PITS,
    PLAYER1_STORE,
)


class TestBoardNewGame:
    def test_board_size(self):
        board = Board.new_game()
        assert len(board.pits) == BOARD_SIZE

    def test_initial_seeds(self):
        board = Board.new_game()
        for i in PLAYER0_PITS + PLAYER1_PITS:
            assert board.pits[i] == INITIAL_SEEDS

    def test_stores_empty(self):
        board = Board.new_game()
        assert board.pits[PLAYER0_STORE] == 0
        assert board.pits[PLAYER1_STORE] == 0

    def test_player0_starts(self):
        board = Board.new_game()
        assert board.current_player == 0

    def test_custom_seeds(self):
        board = Board.new_game(seeds_per_pit=3)
        for i in PLAYER0_PITS + PLAYER1_PITS:
            assert board.pits[i] == 3


class TestBoardCopy:
    def test_copy_is_independent(self):
        board = Board.new_game()
        copy = board.copy()
        copy.pits[0] = 99
        assert board.pits[0] != 99

    def test_copy_player_independent(self):
        board = Board.new_game()
        copy = board.copy()
        copy.current_player = 1
        assert board.current_player == 0


class TestBoardQueries:
    def test_get_pits_player0(self):
        board = Board.new_game()
        assert board.get_pits(0) == PLAYER0_PITS

    def test_get_pits_player1(self):
        board = Board.new_game()
        assert board.get_pits(1) == PLAYER1_PITS

    def test_get_store(self):
        board = Board.new_game()
        assert board.get_store(0) == PLAYER0_STORE
        assert board.get_store(1) == PLAYER1_STORE

    def test_seeds_in_pits(self):
        board = Board.new_game()
        assert board.seeds_in_pits(0) == INITIAL_SEEDS * 6
        assert board.seeds_in_pits(1) == INITIAL_SEEDS * 6

    def test_score_initial(self):
        board = Board.new_game()
        assert board.score(0) == 0
        assert board.score(1) == 0


class TestBoardGameOver:
    def test_not_over_at_start(self):
        board = Board.new_game()
        assert not board.is_game_over()

    def test_over_when_player0_empty(self):
        board = Board.new_game()
        for i in PLAYER0_PITS:
            board.pits[i] = 0
        assert board.is_game_over()

    def test_over_when_player1_empty(self):
        board = Board.new_game()
        for i in PLAYER1_PITS:
            board.pits[i] = 0
        assert board.is_game_over()

    def test_winner_none_when_in_progress(self):
        assert Board.new_game().winner() is None

    def test_winner_player0(self):
        board = Board.new_game()
        for i in PLAYER0_PITS + PLAYER1_PITS:
            board.pits[i] = 0
        board.pits[PLAYER0_STORE] = 30
        board.pits[PLAYER1_STORE] = 18
        assert board.winner() == 0

    def test_winner_player1(self):
        board = Board.new_game()
        for i in PLAYER0_PITS + PLAYER1_PITS:
            board.pits[i] = 0
        board.pits[PLAYER0_STORE] = 10
        board.pits[PLAYER1_STORE] = 38
        assert board.winner() == 1

    def test_draw(self):
        board = Board.new_game()
        for i in PLAYER0_PITS + PLAYER1_PITS:
            board.pits[i] = 0
        board.pits[PLAYER0_STORE] = 24
        board.pits[PLAYER1_STORE] = 24
        assert board.winner() == -1
