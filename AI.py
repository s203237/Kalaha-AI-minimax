import random
import copy
import math
from Kalah import make_move

def get_ai_move(board):
    """
    Determine the AI's next move.
    
    The board is a 14-element list:
    - Indices 0-5: Human player's pits (left to right)
    - Index 6: Human player's store (Mancala)
    - Indices 7-12: AI's pits (right to left from the AI's perspective)
    - Index 13: AI's store (Mancala)
    
    Returns:
        int: The index of the pit the AI chooses to play (must be between 7 and 12).
    """
    # TODO: Implement your AI logic here
    return random.randint(7, 12)
    depth = 5
    pass

def score(board):
    # Calculate the score difference (AI's score - Player's score)
    return board[13] - board[6]

def valid_moves(board):
    # Return a list of non-empty pits to help the AI choose a valid move
    return [i for i in range(7, 13) if board[i] > 0]

def minimax(board, depth, is_maximizing):
    """
    The recursive Minimax algorithm with Alpha-Beta Pruning.
    """
    # 1. Base case: If depth is 0 or the game is over, return the board evaluation and no move.
    
    if is_maximizing: # AI's turn
        # 2. Setup max_eval to -infinity
        # 3. Loop through all valid AI moves:
            # a. Create a deepcopy of the board.
            # b. Simulate the move on the copied board.
            # c. Determine if the AI gets an extra turn.
            # d. Recursively call minimax() with the new board.
                # * If extra turn: is_maximizing remains True.
                # * If normal turn: is_maximizing becomes False.
            # e. Update max_eval and alpha.
            # f. If beta <= alpha, break (Prune).
        # 4. Return the best evaluation and the best move.
        pass
        
    else: # Human's turn (Minimizing)
        # 5. Setup min_eval to +infinity
        # 6. Loop through all valid Human moves:
            # a. Create a deepcopy of the board.
            # b. Simulate the move.
            # c. Determine if Human gets an extra turn.
            # d. Recursively call minimax().
                # * If extra turn: is_maximizing remains False.
                # * If normal turn: is_maximizing becomes True.
            # e. Update min_eval and beta.
            # f. If beta <= alpha, break (Prune).
        # 7. Return the best evaluation and the best move.
        pass
