import random
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
    pass