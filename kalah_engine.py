"""
Kalah Game Engine.

This module contains the core game logic, state representation, and transition 
rules for the Kalah (Mancala) board game. It acts as a strict API that other 
modules (like the AI or the game loop) can interact with, ensuring a complete 
separation of concerns.
"""

def display_board(board):
    """
    Prints the current state of the board to the console in a human-readable format.
    
    Args:
        board (list of int): A 14-element list representing the current board state.
    """
    print("\n" + "="*40)
    print("               Player 2")
    print(f"       [{board[12]:2}][{board[11]:2}][{board[10]:2}][{board[9]:2}][{board[8]:2}][{board[7]:2}]")
    print(f"  [{board[13]:2}]                                [{board[6]:2}]")
    print(f"       [{board[0]:2}][{board[1]:2}][{board[2]:2}][{board[3]:2}][{board[4]:2}][{board[5]:2}]")
    print("               Player 1")
    print("        (1) (2) (3) (4) (5) (6)")
    print("="*40 + "\n")


def get_valid_moves(board, player):
    """
    Determines all legal moves for a given player in the current state.
    
    Args:
        board (list of int): The current board state.
        player (int): The ID of the player (1 or 2).
        
    Returns:
        list of int: A list of indices corresponding to non-empty pits 
                     that the player is allowed to choose.
    """
    if player == 1:
        # Player 1 controls pits 0 through 5
        return [i for i in range(0, 6) if board[i] > 0]
    else:
        # Player 2 controls pits 7 through 12
        return [i for i in range(7, 13) if board[i] > 0]


def make_move(board, player, pit, verbose=False):
    """
    Executes a chosen move on the board, updating the state in place.
    Handles the distribution of seeds, extra turns, and captures.
    
    Args:
        board (list of int): The current board state (mutated by this function).
        player (int): The ID of the player making the move (1 or 2).
        pit (int): The index of the pit selected by the player.
        verbose (bool): If True, prints capture events to standard output. 
                        Should be False during AI simulations to avoid I/O bottlenecks.
                        
    Returns:
        tuple: (board, extra_turn)
            - board (list of int): The updated board.
            - extra_turn (bool): True if the player's last seed landed in their own store.
    """
    seeds = board[pit]
    board[pit] = 0
    current_pit = pit

    # Sowing phase: Distribute the picked up seeds counter-clockwise
    while seeds > 0:
        current_pit = (current_pit + 1) % 14
        
        # Skip the opponent's store (Mancala)
        if player == 1 and current_pit == 13:
            continue
        if player == 2 and current_pit == 6:
            continue

        board[current_pit] += 1
        seeds -= 1

    extra_turn = False
    
    # Check if the last seed landed in the player's own store, granting an extra turn
    if player == 1 and current_pit == 6:
        extra_turn = True
    elif player == 2 and current_pit == 13:
        extra_turn = True

    # Capture phase: Check if the last seed landed in an empty pit on the player's own side
    if board[current_pit] == 1:
        # Calculate the index of the opponent's opposite pit
        opposite_pit = 12 - current_pit 
        
        # Player 1 capture logic
        if player == 1 and 0 <= current_pit <= 5:
            if board[opposite_pit] > 0:
                # Move both the capturing seed and the captured seeds to Player 1's store
                board[6] += board[current_pit] + board[opposite_pit]
                board[current_pit] = 0
                board[opposite_pit] = 0
                if verbose:
                    print("\n*** Player 1 captures seeds! ***")
                
        # Player 2 capture logic
        elif player == 2 and 7 <= current_pit <= 12:
            if board[opposite_pit] > 0:
                # Move both the capturing seed and the captured seeds to Player 2's store
                board[13] += board[current_pit] + board[opposite_pit]
                board[current_pit] = 0
                board[opposite_pit] = 0
                if verbose:
                    print("\n*** Player 2 captures seeds! ***")

    return board, extra_turn


def check_endgame(board):
    """
    Evaluates whether the terminal condition of the game has been met.
    The game ends when all pits on one side of the board are completely empty.
    If the game ends, all remaining seeds are moved to their respective stores.
    
    Args:
        board (list of int): The current board state (mutated if the game ends).
        
    Returns:
        bool: True if the game has ended, False otherwise.
    """
    p1_empty = all(s == 0 for s in board[0:6])
    p2_empty = all(s == 0 for s in board[7:13])

    if p1_empty or p2_empty:
        # Sweep remaining seeds to the respective stores
        board[6] += sum(board[0:6])
        board[13] += sum(board[7:13])
        
        # Clear all pits to reflect the final board state
        for i in range(6): 
            board[i] = 0
        for i in range(7, 13): 
            board[i] = 0
            
        return True
        
    return False