# Kalah Game Implementation

# Created by an LLM


from AI import get_ai_move

def display_board(board):
    print("\n" + "="*40)
    print("               AI (Player 2)")
    print(f"       [{board[12]:2}][{board[11]:2}][{board[10]:2}][{board[9]:2}][{board[8]:2}][{board[7]:2}]")
    print(f"  [{board[13]:2}]                                [{board[6]:2}]")
    print(f"       [{board[0]:2}][{board[1]:2}][{board[2]:2}][{board[3]:2}][{board[4]:2}][{board[5]:2}]")
    print("             Human (Player 1)")
    print("        (1) (2) (3) (4) (5) (6)")
    print("="*40 + "\n")

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

def play_game():
    # Standard Kalah setup: 4 seeds per pit, 0 in stores
    board = [4] * 6 + [0] + [4] * 6 + [0]
    current_player = 1 # 1 for Human, 2 for AI

    print("Welcome to Kalah!")
    
    while not check_endgame(board):
        display_board(board)
        
        if current_player == 1:
            try:
                user_input = int(input("Choose a pit (1-6): "))
                pit = user_input - 1
                
                if not (0 <= pit <= 5):
                    print("Invalid move: Out of range. Try again.")
                    continue
                if board[pit] == 0:
                    print("Invalid move: Pit is empty. Try again.")
                    continue
            except ValueError:
                print("Please enter a valid number.")
                continue
        else:
            print("AI is thinking...")
            pit = get_ai_move(board)
            
            # Since the AI isn't built yet, let's catch None values to prevent crashing instantly
            if pit is None:
                print("Error: AI function returned None. Did you implement get_ai_move?")
                return
                
            if not (7 <= pit <= 12) or board[pit] == 0:
                print(f"Error: AI attempted an invalid move (Pit {pit}). Game terminating.")
                return
            
            print(f"AI plays pit at index {pit}")

        board, extra_turn = make_move(board, current_player, pit)

        if extra_turn:
            print(f"{'Human' if current_player == 1 else 'AI'} gets an extra turn!")
        else:
            # Switch player
            current_player = 2 if current_player == 1 else 1

    display_board(board)
    print("Game Over!")
    
    print(f"Human Score: {board[6]}")
    print(f"AI Score: {board[13]}")
    
    if board[6] > board[13]:
        print("🎉 Human wins!")
    elif board[13] > board[6]:
        print("🤖 AI wins!")
    else:
        print("It's a tie!")

if __name__ == "__main__":
    play_game()