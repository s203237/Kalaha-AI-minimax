import random
import copy
import math


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

def check_endgame(board):
    p1_empty = all(s == 0 for s in board[0:6])
    p2_empty = all(s == 0 for s in board[7:13])

    if p1_empty or p2_empty:
        # Sweep remaining seeds to the respective stores
        board[6] += sum(board[0:6])
        board[13] += sum(board[7:13])
        
        # Empty the pits
        for i in range(6): 
            board[i] = 0
        for i in range(7, 13): 
            board[i] = 0
            
        return True
    return False


def make_move(board, player, pit):
    seeds = board[pit]
    board[pit] = 0
    current_pit = pit

    # Distribute the seeds
    while seeds > 0:
        current_pit = (current_pit + 1) % 14
        
        # Skip the opponent's store
        if player == 1 and current_pit == 13:
            continue
        if player == 2 and current_pit == 6:
            continue

        board[current_pit] += 1
        seeds -= 1

    extra_turn = False
    
    # Check for an extra turn
    if player == 1 and current_pit == 6:
        extra_turn = True
    elif player == 2 and current_pit == 13:
        extra_turn = True

    # Check for capture
    if board[current_pit] == 1:
        # Opposite pit math: opposite of i is 12 - i
        opposite_pit = 12 - current_pit 
        
        # Human capture
        if player == 1 and 0 <= current_pit <= 5:
            if board[opposite_pit] > 0:
                board[6] += board[current_pit] + board[opposite_pit]
                board[current_pit] = 0
                board[opposite_pit] = 0
                print("\n*** Human captures seeds! ***")
                
        # AI capture
        elif player == 2 and 7 <= current_pit <= 12:
            if board[opposite_pit] > 0:
                board[13] += board[current_pit] + board[opposite_pit]
                board[current_pit] = 0
                board[opposite_pit] = 0
                print("\n*** AI captures seeds! ***")

    return board, extra_turn

def check_endgame(board):
    p1_empty = all(s == 0 for s in board[0:6])
    p2_empty = all(s == 0 for s in board[7:13])

    if p1_empty or p2_empty:
        # Sweep remaining seeds to the respective stores
        board[6] += sum(board[0:6])
        board[13] += sum(board[7:13])
        
        # Empty the pits
        for i in range(6): 
            board[i] = 0
        for i in range(7, 13): 
            board[i] = 0
            
        return True
    return False

def minimax(board, depth, is_maximizing):
    """
    The recursive Minimax algorithm with Alpha-Beta Pruning.
    """
    # 1. Base case: If depth is 0 or the game is over, return the board evaluation and no move.
    if depth == 0 or check_endgame(board):
        return score(board), None
    
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
