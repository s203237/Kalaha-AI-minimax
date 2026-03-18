
import pygame
from kalah_engine import make_move, check_endgame
from config import *

WIDTH = 900
HEIGHT = 700
screen = None
font = None

board = [4] * 6 + [0] + [4] * 6 + [0]
current_player =1
PIT_RADIUS = 35
PIT_SPACING = 100
STORE_WIDTH = 80
STORE_HEIGHT = 200
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

PLAYER_OPTIONS = [
    "Human",
    "Random AI",
    "Minimax AI",
    "Alpha-Beta AI"
]

def menu_screen():
    _ensure_visual_context()

    p1_config = PlayerConfig()
    p2_config = PlayerConfig()
    
    p1_dropdown_open = False
    p2_dropdown_open = False
    
    p1_config_dropdown = False
    p2_config_dropdown = False
    
    p1_eval_dropdown = False
    p2_eval_dropdown = False
    
    p1_ai_controls = None
    p2_ai_controls = None
    running = True

    while running:
        screen.fill((180, 160, 120))

        title = font.render("KALAH GAME MENU", True, (0, 0, 0))
        screen.blit(title, (CENTER_X - 120, 80))
        
        # Labels
        p1_label = font.render("Player 1:", True, (0, 0, 0))
        screen.blit(p1_label, (CENTER_X - 250, 150))

        p2_label = font.render("Player 2:", True, (0, 0, 0))
        screen.blit(p2_label, (CENTER_X - 250, 300))

        #  Main dropdown boxes
        p1_main_rect = pygame.Rect(CENTER_X - 100, 145, 220, 40)
        p2_main_rect = pygame.Rect(CENTER_X - 100, 295, 220, 40)

        pygame.draw.rect(screen, (220, 220, 220), p1_main_rect)
        pygame.draw.rect(screen, (220, 220, 220), p2_main_rect)

        p1_text = font.render(PLAYER_OPTIONS[p1_config.type], True, (0, 0, 0))
        p2_text = font.render(PLAYER_OPTIONS[p2_config.type], True, (0, 0, 0))

        screen.blit(p1_text, (p1_main_rect.x + 10, p1_main_rect.y + 8))
        screen.blit(p2_text, (p2_main_rect.x + 10, p2_main_rect.y + 8))

        arrow1 = font.render(" ▼ ", True, (0, 0, 0))
        arrow2 = font.render(" ▼ ", True, (0, 0, 0))
        screen.blit(arrow1, (p1_main_rect.right - 25, p1_main_rect.y + 8))
        screen.blit(arrow2, (p2_main_rect.right - 25, p2_main_rect.y + 8))

        p1_option_rects = []
        p2_option_rects = []

        #  Dropdown options 
        if p1_dropdown_open:
            for i, option in enumerate(PLAYER_OPTIONS):
                rect = pygame.Rect(p1_main_rect.x, p1_main_rect.bottom + i * 40, 220, 40)
                color = (120, 200, 120) if i == p1_config.type else (240, 240, 240)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

                text = font.render(option, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.y + 8))

                p1_option_rects.append((rect, i))

        if p2_dropdown_open:
            for i, option in enumerate(PLAYER_OPTIONS):
                rect = pygame.Rect(p2_main_rect.x, p2_main_rect.bottom + i * 40, 220, 40)
                color = (120, 200, 120) if i == p2_config.type else (240, 240, 240)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

                text = font.render(option, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.y + 8))

                p2_option_rects.append((rect, i))
                
        # Always define rects, even if not used
        p1_config_rect = None
        p1_eval_rect = None
        p1_minus_rect = None
        p1_plus_rect = None
        p2_config_rect = None
        p2_eval_rect = None
        p2_minus_rect = None
        p2_plus_rect = None
        p1_config_options = []
        p2_config_options = []
        p1_eval_options = []
        p2_eval_options = []

        if p1_config.type in [MINIMAX, ALPHABETA]:
            p1_config_rect = pygame.Rect(p1_main_rect.x, p1_main_rect.bottom + 10, p1_main_rect.width, 40)
            value_x = p1_config_rect.right + 20
            value_y = p1_config_rect.y
            if p1_config.constraint == DEPTH:
                label = f"Depth: {p1_config.depth}"
            else:
                label = f"Time: {p1_config.time:.1f}s"
            value_text = font.render(label, True, (0, 0, 0))
            screen.blit(value_text, (value_x, value_y))
            pygame.draw.rect(screen, (220, 220, 220), p1_config_rect)
            text = font.render(
                "Fixed Depth" if p1_config.constraint == DEPTH else "Time Limit",
                True, (0, 0, 0)
            )
            screen.blit(text, (p1_config_rect.x + 10, p1_config_rect.y + 8))
            arrow = font.render("▼", True, (0, 0, 0))
            screen.blit(arrow, (p1_config_rect.right - 20, p1_config_rect.y + 8))
            p1_eval_rect = pygame.Rect(p1_main_rect.right + 20, p1_main_rect.y, 180, 40)
            pygame.draw.rect(screen, (220, 220, 220), p1_eval_rect)
            eval_text = font.render(
                "Simple Eval" if p1_config.eval == SIMPLE else "Phase-aware Eval",
                True, (0, 0, 0)
            )
            screen.blit(eval_text, (p1_eval_rect.x + 10, p1_eval_rect.y + 8))
            arrow = font.render("▼", True, (0, 0, 0))
            screen.blit(arrow, (p1_eval_rect.right - 20, p1_eval_rect.y + 8))
            p1_minus_rect = pygame.Rect(value_x + 120, value_y, 30, 30)
            p1_plus_rect = pygame.Rect(value_x + 160, value_y, 30, 30)
            pygame.draw.rect(screen, (200, 100, 100), p1_minus_rect)
            pygame.draw.rect(screen, (100, 200, 100), p1_plus_rect)
            minus_text = font.render("-", True, (0, 0, 0))
            plus_text = font.render("+", True, (0, 0, 0))
            screen.blit(minus_text, (p1_minus_rect.x + 8, p1_minus_rect.y + 5))
            screen.blit(plus_text, (p1_plus_rect.x + 8, p1_plus_rect.y + 5))

        if p2_config.type in [MINIMAX, ALPHABETA]:
            p2_config_rect = pygame.Rect(p2_main_rect.x, p2_main_rect.bottom + 10, p2_main_rect.width, 40)
            value_x = p2_config_rect.right + 20
            value_y = p2_config_rect.y
            if p2_config.constraint == DEPTH:
                label = f"Depth: {p2_config.depth}"
            else:
                label = f"Time: {p2_config.time:.1f}s"
            value_text = font.render(label, True, (0, 0, 0))
            screen.blit(value_text, (value_x, value_y))
            pygame.draw.rect(screen, (220, 220, 220), p2_config_rect)
            text = font.render(
                "Fixed Depth" if p2_config.constraint == DEPTH else "Time Limit",
                True, (0, 0, 0)
            )
            screen.blit(text, (p2_config_rect.x + 10, p2_config_rect.y + 8))
            arrow = font.render("▼", True, (0, 0, 0))
            screen.blit(arrow, (p2_config_rect.right - 20, p2_config_rect.y + 8))
            p2_eval_rect = pygame.Rect(p2_main_rect.right + 20, p2_main_rect.y, 180, 40)
            pygame.draw.rect(screen, (220, 220, 220), p2_eval_rect)
            eval_text = font.render(
                "Simple Eval" if p2_config.eval == SIMPLE else "Phase-aware Eval",
                True, (0, 0, 0)
            )
            screen.blit(eval_text, (p2_eval_rect.x + 10, p2_eval_rect.y + 8))
            arrow = font.render("▼", True, (0, 0, 0))
            screen.blit(arrow, (p2_eval_rect.right - 20, p2_eval_rect.y + 8))
            p2_minus_rect = pygame.Rect(value_x + 120, value_y, 30, 30)
            p2_plus_rect = pygame.Rect(value_x + 160, value_y, 30, 30)
            pygame.draw.rect(screen, (200, 100, 100), p2_minus_rect)
            pygame.draw.rect(screen, (100, 200, 100), p2_plus_rect)
            screen.blit(font.render("-", True, (0,0,0)), (p2_minus_rect.x + 8, value_y + 5))
            screen.blit(font.render("+", True, (0,0,0)), (p2_plus_rect.x + 8, value_y + 5))
            
        # Dropdown options for AI config
        if p1_config_dropdown:
            options = ["Fixed Depth", "Time Limit"]

            for i, opt in enumerate(options):
                rect = pygame.Rect(p1_config_rect.x, p1_config_rect.bottom + i * 40, p1_config_rect.width, 40)
                pygame.draw.rect(screen, (240, 240, 240), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

                text = font.render(opt, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.y + 8))

                p1_config_options.append((rect, i))
        
        if p2_config_dropdown:
            options = ["Fixed Depth", "Time Limit"]

            for i, opt in enumerate(options):
                rect = pygame.Rect(p2_config_rect.x, p2_config_rect.bottom + i * 40, p2_config_rect.width, 40)
                pygame.draw.rect(screen, (240, 240, 240), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

                text = font.render(opt, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.y + 8))

                p2_config_options.append((rect, i))
                
        #Dropdown options for eval mode (if AI selected)
        if p1_config.type in [MINIMAX, ALPHABETA] and p1_eval_dropdown:
            options = ["Simple Eval", "Phase-aware Eval"]
            for i, opt in enumerate(options):
                rect = pygame.Rect(
                    p1_eval_rect.x,
                    p1_eval_rect.bottom + i * 40,
                    p1_eval_rect.width,
                    40
                )
                pygame.draw.rect(screen, (240, 240, 240), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
                text = font.render(opt, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.y + 8))
                p1_eval_options.append((rect, i))
    
        if p2_config.type in [MINIMAX, ALPHABETA] and p2_eval_dropdown:
            options = ["Simple Eval", "Phase-aware Eval"]
            for i, opt in enumerate(options):
                rect = pygame.Rect(
                    p2_eval_rect.x,
                    p2_eval_rect.bottom + i * 40,
                    p2_eval_rect.width,
                    40
                )
                pygame.draw.rect(screen, (240, 240, 240), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
                text = font.render(opt, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.y + 8))
                p2_eval_options.append((rect, i))
                
        
        # ---------- Buttons ----------
        start_btn = pygame.Rect(WIDTH -200, HEIGHT -100 , 160, 40)
        quit_btn = pygame.Rect(WIDTH -200, HEIGHT -50, 160, 40)

        pygame.draw.rect(screen, (70, 130, 180), start_btn)
        pygame.draw.rect(screen, (200, 100, 100), quit_btn)

        start_text = font.render("START GAME", True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=start_btn.center)
        screen.blit(start_text, start_text_rect)
        
        quit_text = font.render("QUIT", True, (0, 0, 0))
        quit_text_rect = quit_text.get_rect(center=quit_btn.center)
        screen.blit(quit_text, quit_text_rect)
    

        pygame.display.flip()

        # ---------- Events ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Toggle dropdowns
                if p1_main_rect.collidepoint(mx, my):
                    p1_dropdown_open = not p1_dropdown_open
                    p2_dropdown_open = False
                    continue

                if p2_main_rect.collidepoint(mx, my):
                    p2_dropdown_open = not p2_dropdown_open
                    p1_dropdown_open = False
                    continue

                # Select Player 1 option
                clicked_option = False
                if p1_dropdown_open:
                    for rect, i in p1_option_rects:
                        if rect.collidepoint(mx, my):
                            p1_config.type = i
                            p1_dropdown_open = False
                            clicked_option = True
                            break
                    if clicked_option:
                        continue

                # Select Player 2 option
                if p2_dropdown_open:
                    for rect, i in p2_option_rects:
                        if rect.collidepoint(mx, my):
                            p2_config.type = i
                            p2_dropdown_open = False
                            clicked_option = True
                            break
                    if clicked_option:
                        continue
                    
                # Toggle AI config dropdowns
                if p1_config.type in [MINIMAX, ALPHABETA]:
                    # toggle config dropdown
                        if 'p1_config_rect' in locals() and p1_config_rect is not None and p1_config_rect.collidepoint(mx, my):
                            p1_config_dropdown = not p1_config_dropdown
                            p1_eval_dropdown = False
                            p2_config_dropdown = False
                            p2_eval_dropdown = False
                            continue

                    # toggle eval dropdown
                        elif 'p1_eval_rect' in locals() and p1_eval_rect is not None and p1_eval_rect.collidepoint(mx, my):
                            p1_eval_dropdown = not p1_eval_dropdown
                            p1_config_dropdown = False
                            p2_config_dropdown = False
                            p2_eval_dropdown = False
                            continue

                    # choose config option
                        elif p1_config_dropdown:
                            for rect, i in p1_config_options:
                                if rect.collidepoint(mx, my):
                                    p1_config.constraint = DEPTH if i == 0 else TIME
                                    p1_config_dropdown = False
                                    break

                        # choose eval option
                        elif p1_eval_dropdown:
                            for rect, i in p1_eval_options:
                                if rect.collidepoint(mx, my):
                                    p1_config.eval = SIMPLE if i == 0 else PHASE
                                    p1_eval_dropdown = False
                                    break
                    # Adjust AI parameters with +/- buttons
                        if 'p1_minus_rect' in locals() and p1_minus_rect is not None and p1_minus_rect.collidepoint(mx, my):
                            if p1_config.constraint == DEPTH:
                                if p1_config.depth > 1:
                                    p1_config.depth -= 1
                            else:
                                if p1_config.time > 0.5:
                                    p1_config.time -= 0.5
                            continue

                        if 'p1_plus_rect' in locals() and p1_plus_rect is not None and p1_plus_rect.collidepoint(mx, my):
                            if p1_config.constraint == DEPTH:
                                p1_config.depth += 1
                            else:
                                p1_config.time += 0.5
                            continue       
                                    
                if p2_config.type in [MINIMAX, ALPHABETA]:
                    
                        if 'p2_config_rect' in locals() and p2_config_rect is not None and p2_config_rect.collidepoint(mx, my):
                            p2_config_dropdown = not p2_config_dropdown
                            p2_eval_dropdown = False
                            p1_config_dropdown = False
                            p1_eval_dropdown = False
                            continue

                        elif 'p2_eval_rect' in locals() and p2_eval_rect is not None and p2_eval_rect.collidepoint(mx, my):
                            p2_eval_dropdown = not p2_eval_dropdown
                            p2_config_dropdown = False
                            p1_config_dropdown = False
                            p1_eval_dropdown = False
                            continue

                        elif p2_config_dropdown:
                            for rect, i in p2_config_options:
                                if rect.collidepoint(mx, my):
                                    p2_config.constraint = DEPTH if i == 0 else TIME
                                    p2_config_dropdown = False
                                    break

                        elif p2_eval_dropdown:
                            for rect, i in p2_eval_options:
                                if rect.collidepoint(mx, my):
                                    p2_config.eval = SIMPLE if i == 0 else PHASE
                                    p2_eval_dropdown = False
                                    break
                            
                    # Adjust AI parameters with +/- buttons
                        if 'p2_minus_rect' in locals() and p2_minus_rect is not None and p2_minus_rect.collidepoint(mx, my):
                            if p2_config.constraint == DEPTH:
                                if p2_config.depth > 1:
                                    p2_config.depth -= 1
                            else:
                                if p2_config.time > 0.5:
                                    p2_config.time -= 0.5
                            continue    
                    
                    # Click outside closes dropdown
                        p1_dropdown_open = False
                        p2_dropdown_open = False

                # Start / Quit
                if start_btn.collidepoint(mx, my):
                    return p1_config, p2_config

                if quit_btn.collidepoint(mx, my):
                    pygame.quit()
                    return None, None

from players import (
    create_human_player,
    create_random_ai_player,
    create_minimax_player,
    create_alphabeta_player,
)
def create_player_from_config(config):

    if config.type == HUMAN:
        return create_human_player()

    elif config.type == RANDOM:
        return create_random_ai_player()

    elif config.type == MINIMAX:
        if config.constraint == DEPTH:
            return create_minimax_player(
                depth=config.depth,
                eval_mode="phase_aware" if config.eval == PHASE else "simple"
            )
        else:
            return create_minimax_player(
                time_limit=config.time,
                eval_mode="phase_aware" if config.eval == PHASE else "simple"
            )

    elif config.type == ALPHABETA:
        if config.constraint == DEPTH:
            return create_alphabeta_player(
                depth=config.depth,
                eval_mode="phase_aware" if config.eval == PHASE else "simple"
            )
        else:
            return create_alphabeta_player(
                time_limit=config.time,
                eval_mode="phase_aware" if config.eval == PHASE else "simple"
            )
            
    
def _ensure_visual_context():
    """Initializes pygame and rendering objects only when visual mode is used."""
    global screen, font
    if screen is not None and font is not None:
        return

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kalah Game")
    font = pygame.font.SysFont(None, 30)

def draw_board(board,p1_config, p2_config):
    screen.fill((200, 180, 140))
    pits=[]
    p1_name = PLAYER_OPTIONS[p1_config.type]
    p2_name = PLAYER_OPTIONS[p2_config.type]
    p1_text = font.render(p1_name, True, (0,0,0))
    p2_text = font.render(p2_name, True, (0,0,0))
    screen.blit(p1_text, (CENTER_X-40, CENTER_Y-230))
    screen.blit(p2_text, (CENTER_X-50, CENTER_Y+220))
    
    
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

def draw_ai_config(config, x, y):

    # Constraint
    text = font.render(
        f"Constraint: {'Depth' if config.constraint == DEPTH else 'Time'}",
        True, (0,0,0)
    )
    screen.blit(text, (x, y))

    # Eval
    text = font.render(
        f"Eval: {'Simple' if config.eval == SIMPLE else 'Phase'}",
        True, (0,0,0)
    )
    screen.blit(text, (x, y + 40))

    # Value
    if config.constraint == DEPTH:
        text = font.render(f"Depth: {config.depth}", True, (0,0,0))
    else:
        text = font.render(f"Time: {config.time}", True, (0,0,0))

    screen.blit(text, (x, y + 80))
    
def _draw_endgame_screen(board, p1_config, p2_config):
    """Renders the game-over screen and final winner message."""
    p1_score = board[6]
    p2_score = board[13]

    if p1_score > p2_score:
        message = f"{PLAYER_OPTIONS[p1_config.type]} wins!"
    elif p2_score > p1_score:
        message = f"{PLAYER_OPTIONS[p2_config.type]} wins!"
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

def run_game(player1, player2, p1_config, p2_config, show_console=False):
    """
    Runs the main visual game loop using injected player callables.

    Args:
        player1 (callable): Function(board, player_id) -> (pit, stats)
        player2 (callable): Function(board, player_id) -> (pit, stats)
        p1_config (object): Configuration object for player 1.
        p2_config (object): Configuration object for player 2.
        show_console (bool): Print turn and stats to terminal when True.
    """
    _ensure_visual_context()

    board = [4] * 6 + [0] + [4] * 6 + [0]
    current_player = 1
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        pits = draw_board(board, p1_config, p2_config)
        pygame.display.flip()

        if check_endgame(board):
            _draw_endgame_screen(board, p1_config, p2_config)
            pygame.time.wait(5000)
            running = False
            break

        current_config = p1_config if current_player == 1 else p2_config
        current_actor = player1 if current_player == 1 else player2

        move_to_play = None
        stats = {}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and current_config.type == HUMAN
            ):
                mx, my = event.pos

                if current_player == 1:
                    for i, (x, y) in enumerate(pits[:6]):
                        dist = ((mx - x) ** 2 + (my - y) ** 2) ** 0.5
                        if dist <= PIT_RADIUS and board[i] > 0:
                            move_to_play = i
                            break

                elif current_player == 2:
                    ai_pit_positions = []
                    for i in range(6):
                        x = CENTER_X + 255 - i * PIT_SPACING
                        y = CENTER_Y - 150
                        ai_pit_positions.append((x, y))

                    for i, (x, y) in enumerate(ai_pit_positions):
                        dist = ((mx - x) ** 2 + (my - y) ** 2) ** 0.5
                        board_index = 12 - i
                        if dist <= PIT_RADIUS and board[board_index] > 0:
                            move_to_play = board_index
                            break

        if not running:
            break

        if current_config.type != HUMAN:
            pygame.time.wait(300)
            move_to_play, stats = current_actor(board, current_player)

        if move_to_play is None:
            continue

        board, extra_turn = make_move(board, current_player, move_to_play, verbose=show_console)

        if show_console and stats and "time_taken" in stats:
            print(
                f"Player {current_player} evaluated {stats.get('nodes', 0)} nodes "
                f"to depth {stats.get('depth_reached', 0)} in "
                f"{stats.get('time_taken', 0):.3f} seconds."
            )

        if not extra_turn:
            current_player = 2 if current_player == 1 else 1

    pygame.quit()



