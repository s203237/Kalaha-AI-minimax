"""
Main Application Entry Point.

Interactive script to configure and run a visual Kalah game.
Allows the user to dynamically select player types (Human, Random, Minimax) 
and configure AI parameters (depth vs. time limits) via a CLI menu before 
launching the game loop.
"""

from kalah_engine import display_board, make_move, check_endgame
from players import (
    create_human_player,
    create_random_ai_player,
    create_minimax_player,
    create_alphabeta_player,
)

# Single-line toggle: set to False to run without the visual window.
VISUAL_MODE = True


def choose_eval_mode():
    """Prompts the user to choose which heuristic evaluator an AI should use."""
    print("\nSelect evaluation function:")
    print("1. Simple (store difference only)")
    print("2. Phase-aware (store + mobility + tactical features)")
    eval_choice = input("Select evaluation function (1-2): ").strip()

    if eval_choice == '2':
        return "phase_aware"
    if eval_choice != '1':
        print("Invalid choice. Defaulting to Simple evaluation.")
    return "simple"


def setup_player(player_id):
    """
    Provides an interactive CLI menu to configure a player agent.
    
    Args:
        player_id (int): The ID of the player being configured (1 or 2).
        
    Returns:
        callable: A player function that takes (board, player_id) and returns (move, stats).
    """
    print(f"\n--- Configuring Player {player_id} ---")
    print("1. Human")
    print("2. Random AI (Baseline)")
    print("3. Minimax AI")
    print("4. Alpha-Beta AI")
    
    while True:
        choice = input("Select player type (1-4): ").strip()
        
        if choice == '1':
            return create_human_player()
            
        elif choice == '2':
            return create_random_ai_player()
            
        elif choice == '3':
            print("\nConfigure Minimax AI:")
            print("1. Fixed Depth (e.g., consistently look X moves ahead)")
            print("2. Time Limit (Iterative Deepening for X seconds)")
            limit_choice = input("Select constraint type (1-2): ").strip()
            eval_mode = choose_eval_mode()
            
            if limit_choice == '1':
                try:
                    depth = int(input("Enter search depth (e.g., 6): ").strip())
                    return create_minimax_player(depth=depth, eval_mode=eval_mode)
                except ValueError:
                    print("Invalid input. Defaulting to depth 6.")
                    return create_minimax_player(depth=6, eval_mode=eval_mode)
                    
            elif limit_choice == '2':
                try:
                    time_limit = float(input("Enter time limit in seconds (e.g., 1.5): ").strip())
                    return create_minimax_player(time_limit=time_limit, eval_mode=eval_mode)
                except ValueError:
                    print("Invalid input. Defaulting to 1.0 seconds.")
                    return create_minimax_player(time_limit=1.0, eval_mode=eval_mode)
            else:
                print("Invalid constraint type. Try again.")

        elif choice == '4':
            print("\nConfigure Alpha-Beta AI:")
            print("1. Fixed Depth (e.g., consistently look X moves ahead)")
            print("2. Time Limit (Iterative Deepening for X seconds)")
            limit_choice = input("Select constraint type (1-2): ").strip()
            eval_mode = choose_eval_mode()

            if limit_choice == '1':
                try:
                    depth = int(input("Enter search depth (e.g., 6): ").strip())
                    return create_alphabeta_player(depth=depth, eval_mode=eval_mode)
                except ValueError:
                    print("Invalid input. Defaulting to depth 6.")
                    return create_alphabeta_player(depth=6, eval_mode=eval_mode)

            elif limit_choice == '2':
                try:
                    time_limit = float(input("Enter time limit in seconds (e.g., 1.5): ").strip())
                    return create_alphabeta_player(time_limit=time_limit, eval_mode=eval_mode)
                except ValueError:
                    print("Invalid input. Defaulting to 1.0 seconds.")
                    return create_alphabeta_player(time_limit=1.0, eval_mode=eval_mode)
            else:
                print("Invalid constraint type. Try again.")
                
        else:
            print("Invalid player choice. Try again.")


def play_interactive_game():
    """
    Main game loop orchestrator with visual terminal output.
    Hooks up the configured players to the game engine and manages turn state.
    """
    print("========================================")
    print("          WELCOME TO KALAH AI           ")
    print("========================================")
    
    # 1. Setup Phase: Interactively construct both players
    p1 = setup_player(1)
    p2 = setup_player(2)

    # 2. Launch selected loop (visual or terminal)
    print("\nStarting the match...\n")
    if VISUAL_MODE:
        from visual import run_game

        run_game(p1, p2, show_console=True)
        return

    board = [4] * 6 + [0] + [4] * 6 + [0]
    current_player = 1

    while not check_endgame(board):
        display_board(board)
        print(f"--- Player {current_player}'s Turn ---")

        active_player = p1 if current_player == 1 else p2
        pit, stats = active_player(board, current_player)

        if stats and 'time_taken' in stats:
            print(
                f"> AI evaluated {stats.get('nodes', 0)} nodes to depth "
                f"{stats.get('depth_reached', 0)} in {stats.get('time_taken', 0):.3f} seconds."
            )

        board, extra_turn = make_move(board, current_player, pit, verbose=True)

        if extra_turn:
            print(f"\n*** Player {current_player} gets an extra turn! ***")
        else:
            current_player = 2 if current_player == 1 else 1

    display_board(board)
    print("========================================")
    print("               GAME OVER                ")
    print("========================================")
    print(f"Player 1 Final Score: {board[6]}")
    print(f"Player 2 Final Score: {board[13]}")
    print("----------------------------------------")

    if board[6] > board[13]:
        print("Result: Player 1 wins!")
    elif board[13] > board[6]:
        print("Result: Player 2 wins!")
    else:
        print("Result: It's a draw!")


if __name__ == "__main__":
    # Launch the interactive game setup
    try:
        play_interactive_game()
    except KeyboardInterrupt:
        # Graceful exit if the user presses Ctrl+C
        print("\n\nGame terminated by user. Goodbye!")
