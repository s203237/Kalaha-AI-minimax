"""
Main Application Entry Point.

Interactive script to configure and run a visual Kalah game.
Allows the user to dynamically select player types (Human, Random, Minimax) 
and configure AI parameters (depth vs. time limits) via a CLI menu before 
launching the game loop.
"""

from visual import menu_screen, create_player_from_config, run_game

if __name__ == "__main__":
    p1_config, p2_config = menu_screen()

    if p1_config is None or p2_config is None:
        raise SystemExit

    player1 = create_player_from_config(p1_config)
    player2 = create_player_from_config(p2_config)

    run_game(player1, player2, p1_config, p2_config)

