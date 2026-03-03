"""Tests for ai modules: evaluation, minimax, alphabeta."""

import pytest
from game.board import Board, PLAYER0_STORE, PLAYER1_STORE
from game.engine import apply_move, get_legal_moves
from game.move import Move
from ai.evaluation import evaluate
from ai.minimax import minimax
from ai.alphabeta import alphabeta, get_best_move


# ──────────────────────────────────────────────────────────────────────────────
# Evaluation
# ──────────────────────────────────────────────────────────────────────────────

class TestEvaluate:
    def test_symmetric_initial_board(self):
        board = Board.new_game()
        assert evaluate(board, 0) == 0.0
        assert evaluate(board, 1) == 0.0

    def test_positive_when_player_leads_in_store(self):
        board = Board.new_game()
        board.pits[PLAYER0_STORE] = 10
        board.pits[PLAYER1_STORE] = 4
        assert evaluate(board, 0) > 0
        assert evaluate(board, 1) < 0

    def test_terminal_win(self):
        board = Board.new_game()
        for i in list(range(0, 6)) + list(range(7, 13)):
            board.pits[i] = 0
        board.pits[PLAYER0_STORE] = 30
        board.pits[PLAYER1_STORE] = 18
        assert evaluate(board, 0) == 1000.0
        assert evaluate(board, 1) == -1000.0

    def test_terminal_draw(self):
        board = Board.new_game()
        for i in list(range(0, 6)) + list(range(7, 13)):
            board.pits[i] = 0
        board.pits[PLAYER0_STORE] = 24
        board.pits[PLAYER1_STORE] = 24
        assert evaluate(board, 0) == 0.0
        assert evaluate(board, 1) == 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Minimax
# ──────────────────────────────────────────────────────────────────────────────

class TestMinimax:
    def test_returns_a_move_from_start(self):
        board = Board.new_game()
        _, move = minimax(board, depth=2, maximizing_player=0)
        assert move is not None
        assert move in get_legal_moves(board)

    def test_depth_zero_returns_no_move(self):
        board = Board.new_game()
        _, move = minimax(board, depth=0, maximizing_player=0)
        assert move is None

    def test_terminal_returns_no_move(self):
        board = Board.new_game()
        for i in range(0, 6):
            board.pits[i] = 0
        _, move = minimax(board, depth=3, maximizing_player=0)
        assert move is None

    def test_picks_extra_turn_move(self):
        # Pit 5 has exactly 1 seed → last seed lands in store → extra turn.
        # Minimax should strongly prefer this move.
        board = Board.new_game()
        for i in range(6):
            board.pits[i] = 0
        board.pits[5] = 1  # only legal move, leads to extra turn
        _, move = minimax(board, depth=2, maximizing_player=0)
        assert move == Move(5)


# ──────────────────────────────────────────────────────────────────────────────
# Alpha-Beta
# ──────────────────────────────────────────────────────────────────────────────

class TestAlphaBeta:
    def test_returns_a_move_from_start(self):
        board = Board.new_game()
        _, move = alphabeta(board, depth=2, alpha=float("-inf"), beta=float("inf"),
                            maximizing_player=0)
        assert move is not None
        assert move in get_legal_moves(board)

    def test_same_score_as_minimax(self):
        """Alpha-beta must return the same score as plain minimax."""
        board = Board.new_game()
        depth = 3
        mm_score, _ = minimax(board, depth, maximizing_player=0)
        ab_score, _ = alphabeta(board, depth, float("-inf"), float("inf"),
                                maximizing_player=0)
        assert mm_score == pytest.approx(ab_score)

    def test_get_best_move_returns_legal_move(self):
        board = Board.new_game()
        move = get_best_move(board, depth=3)
        assert move is not None
        assert move in get_legal_moves(board)

    def test_terminal_returns_no_move(self):
        board = Board.new_game()
        for i in range(0, 6):
            board.pits[i] = 0
        _, move = alphabeta(board, depth=3, alpha=float("-inf"), beta=float("inf"),
                            maximizing_player=0)
        assert move is None

    def test_picks_extra_turn_move(self):
        board = Board.new_game()
        for i in range(6):
            board.pits[i] = 0
        board.pits[5] = 1
        _, move = alphabeta(board, depth=2, alpha=float("-inf"), beta=float("inf"),
                            maximizing_player=0)
        assert move == Move(5)

    def test_player1_ai_move(self):
        board = Board.new_game()
        board.current_player = 1
        move = get_best_move(board, depth=3)
        assert move is not None
        assert move in get_legal_moves(board)
