import pygame
from AI import get_ai_move
from kalah_engine import make_move, check_endgame

pygame.init()

WIDTH = 900
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kalah Game")
font = pygame.font.SysFont(None, 30)


board = [4] * 6 + [0] + [4] * 6 + [0]
current_player =1
PIT_RADIUS = 35
PIT_SPACING = 100
STORE_WIDTH = 80
STORE_HEIGHT = 200
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

def draw_board(board):
    screen.fill((200, 180, 140))
    pits=[]
    ai_text = font.render("AI Player", True, (0,0,0))
    screen.blit(ai_text, (CENTER_X-40, CENTER_Y-230))

    human_text = font.render("Human Player", True, (0,0,0))
    screen.blit(human_text, (CENTER_X-50, CENTER_Y+220))
    
    text = font.render("Game Over", True, (0,0,0))
    screen.blit(text, (CENTER_X-120, CENTER_Y))
    
     #player pits
    for i in range(6):
        x = CENTER_X - 255+ i*PIT_SPACING
        y = CENTER_Y +150
        pygame.draw.circle(screen, (120,180,120), (x, y), PIT_RADIUS)
        text = font.render(str(board[i]), True, (0, 0, 0))
        screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))
        pits.append((x, y))
    # AI pits
    for i in range(6):
        x = CENTER_X + 255- i*PIT_SPACING
        y = CENTER_Y - 150
        pygame.draw.circle(screen, (200, 200, 200), (x, y), PIT_RADIUS)
        text = font.render(str(board[12 - i]), True, (0, 0, 0))
        screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))
    # Stores
    pygame.draw.rect(screen,(220,220,220),(CENTER_X-350, CENTER_Y-80,70,160))
    text = font.render(str(board[13]),True,(0,0,0))
    screen.blit(text,(CENTER_X-330,CENTER_Y-10))
    
    pygame.draw.rect(screen,(120,180,120),(CENTER_X+280, CENTER_Y-80,70,160))
    text = font.render(str(board[6]),True,(0,0,0))
    screen.blit(text,(CENTER_X+300,CENTER_Y-10))
    return pits
    
def run_game():
    board = [4] * 6 + [0] + [4] * 6 + [0]
    current_player = 1
    running=True
    while running:
        pits = draw_board(board)
        pygame.display.flip()
        
        if check_endgame(board):
            human_score = board[6]
            ai_score = board[13]
            if human_score > ai_score:
                message = "Congratulations! You win!"
            elif ai_score > human_score:
                message = "AI wins! Better luck next time."
            else:
                message = "It's a tie!"
            screen.fill((200, 180, 140))
            game_over = font.render("Game Over!", True, (0, 0, 0))
            winner = font.render(message, True, (0, 0, 0))
            screen.blit(game_over, (CENTER_X-120, CENTER_Y-40))
            screen.blit(winner, (CENTER_X-120, CENTER_Y+20))

            pygame.display.flip()

            pygame.time.wait(4000)

            running = False
            continue
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #Player clicks
            elif event.type == pygame.MOUSEBUTTONDOWN and current_player == 1:
                mx, my = event.pos
                for i,(x,y) in enumerate(pits[:6]):
                    dist =((mx - x) ** 2 + (my - y) ** 2) ** 0.5
                    if dist <= PIT_RADIUS and board[i] > 0:
                        board, extra_turn = make_move(board, current_player,i)
                        if not extra_turn:
                            current_player = 2
            
            # AI move
        if current_player == 2 and not check_endgame(board):
            pygame.time.wait(500)
            pit = get_ai_move(board)
            board, extra_turn = make_move(board, current_player, pit)
            if not extra_turn:
                current_player = 1
                
    pygame.quit()
                
        