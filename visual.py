import pygame
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


def _draw_endgame_screen(board):
    """Renders the game-over screen and final winner message."""
    p1_score = board[6]
    p2_score = board[13]

    if p1_score > p2_score:
        message = "Player 1 wins!"
    elif p2_score > p1_score:
        message = "Player 2 wins!"
    else:
        message = "It's a tie!"

    screen.fill((200, 180, 140))
    game_over = font.render("Game Over!", True, (0, 0, 0))
    winner = font.render(message, True, (0, 0, 0))
    score_line = font.render(f"P1: {p1_score}   P2: {p2_score}", True, (0, 0, 0))

    screen.blit(game_over, (CENTER_X - 80, CENTER_Y - 50))
    screen.blit(winner, (CENTER_X - 110, CENTER_Y))
    screen.blit(score_line, (CENTER_X - 100, CENTER_Y + 40))

    pygame.display.flip()


def run_game(player1, player2, show_console=True):
    """
    Runs the main visual game loop using injected player callables.

    Args:
        player1 (callable): Function(board, player_id) -> (pit, stats)
        player2 (callable): Function(board, player_id) -> (pit, stats)
        show_console (bool): Print turn and stats to terminal when True.
    """
    board = [4] * 6 + [0] + [4] * 6 + [0]
    current_player = 1
    running = True

    while running:
        pits = draw_board(board)
        pygame.display.flip()

        if check_endgame(board):
            _draw_endgame_screen(board)
            pygame.time.wait(4000)
            running = False
            continue

        human_move = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and current_player == 1:
                mx, my = event.pos
                for i, (x, y) in enumerate(pits[:6]):
                    dist = ((mx - x) ** 2 + (my - y) ** 2) ** 0.5
                    if dist <= PIT_RADIUS and board[i] > 0:
                        human_move = i
                        break

        if not running:
            break

        # Player 1 is human-click driven only when a human player was configured.
        if current_player == 1 and getattr(player1, "player_type", None) is None:
            if human_move is None:
                continue
            pit, stats = human_move, {}
        else:
            if current_player == 2:
                pygame.time.wait(300)
            active_player = player1 if current_player == 1 else player2
            pit, stats = active_player(board, current_player)

        if pit is None:
            running = False
            continue

        board, extra_turn = make_move(board, current_player, pit, verbose=show_console)

        if show_console and stats and "time_taken" in stats:
            print(
                f"Player {current_player} evaluated {stats.get('nodes', 0)} nodes to depth "
                f"{stats.get('depth_reached', 0)} in {stats.get('time_taken', 0):.3f} seconds."
            )

        if not extra_turn:
            current_player = 2 if current_player == 1 else 1

    pygame.quit()

