"""Tests for game.engine."""

import pytest
from game.board import Board, PLAYER0_STORE, PLAYER1_STORE
from game.engine import apply_move, get_legal_moves, _opposite
from game.move import Move


class TestOpposite:
    def test_pit0_opposite_pit12(self):
        assert _opposite(0) == 12

    def test_pit5_opposite_pit7(self):
        assert _opposite(5) == 7

    def test_pit7_opposite_pit5(self):
        assert _opposite(7) == 5

    def test_pit12_opposite_pit0(self):
        assert _opposite(12) == 0

    def test_symmetry(self):
        for i in list(range(0, 6)) + list(range(7, 13)):
            assert _opposite(_opposite(i)) == i


class TestGetLegalMoves:
    def test_all_pits_legal_at_start(self):
        board = Board.new_game()
        moves = get_legal_moves(board)
        assert len(moves) == 6
        assert all(m.pit_index in range(0, 6) for m in moves)

    def test_empty_pit_not_legal(self):
        board = Board.new_game()
        board.pits[0] = 0
        moves = get_legal_moves(board)
        pit_indices = [m.pit_index for m in moves]
        assert 0 not in pit_indices
        assert len(moves) == 5

    def test_player1_legal_moves(self):
        board = Board.new_game()
        board.current_player = 1
        moves = get_legal_moves(board)
        assert all(m.pit_index in range(7, 13) for m in moves)

    def test_no_moves_when_all_empty(self):
        board = Board.new_game()
        for i in range(0, 6):
            board.pits[i] = 0
        moves = get_legal_moves(board)
        assert moves == []


class TestApplyMoveBasic:
    def test_seeds_picked_up(self):
        board = Board.new_game()
        new_board = apply_move(board, Move(0))
        assert new_board.pits[0] == 0

    def test_total_seeds_conserved(self):
        board = Board.new_game()
        total_before = sum(board.pits)
        new_board = apply_move(board, Move(0))
        assert sum(new_board.pits) == total_before

    def test_player_switches_after_normal_move(self):
        board = Board.new_game()
        new_board = apply_move(board, Move(0))
        assert new_board.current_player == 1

    def test_seeds_distributed(self):
        board = Board.new_game()
        # Pit 0 has 4 seeds → should land in pits 1, 2, 3, 4
        new_board = apply_move(board, Move(0))
        for i in range(1, 5):
            assert new_board.pits[i] == 5  # 4 original + 1 sown


class TestApplyMoveExtraTurn:
    def test_extra_turn_when_last_seed_in_store(self):
        # Give pit 5 exactly 1 seed so last drop falls in store (index 6).
        board = Board.new_game()
        for i in range(6):
            board.pits[i] = 0
        board.pits[5] = 1  # one seed in pit 5 → lands in store 6
        new_board = apply_move(board, Move(5))
        assert new_board.current_player == 0  # same player again

    def test_store_incremented_with_extra_turn(self):
        board = Board.new_game()
        for i in range(6):
            board.pits[i] = 0
        board.pits[5] = 1
        new_board = apply_move(board, Move(5))
        assert new_board.pits[PLAYER0_STORE] == 1


class TestApplyMoveCapture:
    def test_capture_moves_seeds_to_store(self):
        # Pit 4 (player 0) is empty; pit 8 (opposite, player 1) has seeds.
        # Sow one seed into pit 4 to trigger a capture.
        board = Board.new_game()
        # Set up: player 0's pit 3 has 1 seed, pit 4 is empty, opposite pit 8 has 4.
        for i in range(6):
            board.pits[i] = 0
        board.pits[3] = 1   # one seed: will land on pit 4 (the capture target)
        board.pits[4] = 0   # destination is empty
        board.pits[8] = 4   # opposite pit is non-empty

        new_board = apply_move(board, Move(3))
        # Pit 4 and pit 8 should both be emptied; seeds go to player 0's store.
        assert new_board.pits[4] == 0
        assert new_board.pits[8] == 0
        assert new_board.pits[PLAYER0_STORE] == 5  # 1 (own) + 4 (captured)

    def test_no_capture_when_opposite_empty(self):
        board = Board.new_game()
        for i in range(6):
            board.pits[i] = 0
        board.pits[3] = 1
        board.pits[4] = 0
        board.pits[8] = 0   # opposite is empty → no capture

        new_board = apply_move(board, Move(3))
        assert new_board.pits[4] == 1   # seed stays
        assert new_board.pits[PLAYER0_STORE] == 0


class TestApplyMoveGameOver:
    def test_remaining_seeds_collected_on_game_over(self):
        # Player 0 has 1 seed in pit 5; all other pits empty.
        # The seed lands in player 0's store (index 6), emptying player 0's side.
        # Player 1 still has seeds → game-over collection should sweep them.
        board = Board.new_game()
        for i in range(0, 6):
            board.pits[i] = 0
        for i in range(7, 13):
            board.pits[i] = 0
        board.pits[5] = 1   # one seed in pit 5 → lands in store
        board.pits[7] = 3   # player 1 still has seeds

        new_board = apply_move(board, Move(5))
        # All pits should be empty after collection.
        for i in list(range(0, 6)) + list(range(7, 13)):
            assert new_board.pits[i] == 0
        assert new_board.pits[PLAYER1_STORE] == 3

    def test_is_game_over_after_collection(self):
        board = Board.new_game()
        for i in range(0, 6):
            board.pits[i] = 0
        board.pits[0] = 1
        new_board = apply_move(board, Move(0))
        assert new_board.is_game_over()
