import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 800
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick By Brick")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRICK_COLORS = [(255, 100, 100), (255, 165, 0), (255, 255, 0), (0, 255, 127), (135, 206, 250)]
BALL_SKINS = [(255, 255, 0), (255, 0, 255), (0, 255, 255)]
PADDLE_SKINS = [(100, 200, 255), (200, 100, 255), (255, 150, 50)]
BALL_COLOR = BALL_SKINS[0]
PADDLE_COLOR = PADDLE_SKINS[0]
FRAME_BG = (40, 40, 40)
TITLE_COLOR = (255, 215, 0)
BUTTON_COLOR = (0, 200, 100)
BUTTON_HOVER = (0, 255, 150)

# Fonts
font = pygame.font.SysFont("arial", 24)
title_font = pygame.font.SysFont("comicsansms", 48, bold=True)
button_font = pygame.font.SysFont("arial", 36)

# Load sounds
hit_sound = pygame.mixer.Sound("320282__vihaleipa__wine-bottle-hit_03.wav")
win_sound = pygame.mixer.Sound("341984__unadamlar__winning.wav")

# Score & Level
score = 0
level = 1
MAX_LEVELS = 50
high_score_file = "highscore.txt"
if os.path.exists(high_score_file):
    with open(high_score_file, "r") as f:
        high_score = int(f.read())
else:
    high_score = 0

# Game state: 'main_menu', 'start', 'select_level', 'select_skin', 'play', 'game_over', 'win'
game_state = "main_menu"
paused = False

# Paddle
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 40, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_speed = 7

# Ball
BALL_RADIUS = 10
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_dx = 4
ball_dy = -4

# Bricks
def create_bricks(level=1):
    bricks = []
    brick_rows = min(5 + level // 5, 10)
    brick_cols = 10
    brick_width = WIDTH // brick_cols
    brick_height = 30
    for row in range(brick_rows):
        for col in range(brick_cols):
            brick_color = random.choice(BRICK_COLORS)
            brick = pygame.Rect(col * brick_width, row * brick_height + 80, brick_width - 5, brick_height - 5)
            bricks.append((brick, brick_color))
    return bricks

bricks = create_bricks(level)

# Buttons
button_width, button_height = 300, 60
play_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 - 50, button_width, button_height)
level_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 30, button_width, button_height)
skin_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 110, button_width, button_height)

# Logo
logo_image = pygame.image.load("brick-breaker.png")
logo_image = pygame.transform.scale(logo_image, (100, 100))

selected_ball_index = 0
selected_paddle_index = 0

def draw_main_menu():
    screen.fill(BLACK)
    screen.blit(logo_image, logo_image.get_rect(center=(WIDTH//2, HEIGHT//2 - 180)))
    title_text = title_font.render("Brick By Brick", True, TITLE_COLOR)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    for button, text, state in [
        (play_button, "Play Game", "play"),
        (level_button, "Select Level", "select_level"),
        (skin_button, "Select Skins", "select_skin")
    ]:
        if button.collidepoint(mouse):
            pygame.draw.rect(screen, BUTTON_HOVER, button)
            if click[0]:
                pygame.time.wait(200)
                return state
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button)
        btn_text = button_font.render(text, True, BLACK)
        screen.blit(btn_text, btn_text.get_rect(center=button.center))
    pygame.display.flip()
    return "main_menu"

def draw_level_selector():
    screen.fill(BLACK)
    title = title_font.render("Select Level", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    selected = None
    for i in range(1, MAX_LEVELS+1):
        x = 60 + ((i-1) % 10) * 70
        y = 150 + ((i-1) // 10) * 70
        rect = pygame.Rect(x, y, 50, 50)
        pygame.draw.rect(screen, BUTTON_HOVER if rect.collidepoint(mouse) else BUTTON_COLOR, rect)
        text = font.render(str(i), True, BLACK)
        screen.blit(text, text.get_rect(center=rect.center))
        if rect.collidepoint(mouse) and click[0]:
            pygame.time.wait(200)
            return i
    pygame.display.flip()
    return None

def draw_skin_selector():
    global selected_ball_index, selected_paddle_index, BALL_COLOR, PADDLE_COLOR
    screen.fill(BLACK)
    title = title_font.render("Select Skins", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    for i, color in enumerate(BALL_SKINS):
        rect = pygame.Rect(100 + i * 150, 150, 100, 100)
        pygame.draw.circle(screen, color, rect.center, 40)
        if rect.collidepoint(mouse) and click[0]:
            selected_ball_index = i
            BALL_COLOR = BALL_SKINS[i]
    for i, color in enumerate(PADDLE_SKINS):
        rect = pygame.Rect(100 + i * 150, 300, 100, 30)
        pygame.draw.rect(screen, color, rect)
        if rect.collidepoint(mouse) and click[0]:
            selected_paddle_index = i
            PADDLE_COLOR = PADDLE_SKINS[i]
    pygame.display.flip()
    return None

# Game loop
running = True
while running:
    clock.tick(FPS)

    if game_state == "main_menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        game_state = draw_main_menu()
        continue

    if game_state == "select_level":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        selected = draw_level_selector()
        if selected:
            level = selected
            bricks = create_bricks(level)
            score = 0
            paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
            ball.x = WIDTH // 2
            ball.y = HEIGHT // 2
            ball_dx = 4
            ball_dy = -4
            game_state = "main_menu"
        continue

    if game_state == "select_skin":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state = "main_menu"
        draw_skin_selector()
        continue

    if game_state == "game_over":
        draw_game_over_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                score = 0
                level = 1
                paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
                ball.x = WIDTH // 2
                ball.y = HEIGHT // 2
                ball_dx = 4
                ball_dy = -4
                bricks = create_bricks(level)
                game_state = "play"
        continue

    if game_state == "win":
        draw_win_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                score = 0
                level = 1
                paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
                ball.x = WIDTH // 2
                ball.y = HEIGHT // 2
                ball_dx = 4
                ball_dy = -4
                bricks = create_bricks(level)
                game_state = "play"
        continue

    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            paused = not paused

    if paused:
        pause_text = font.render("Paused", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - 40, HEIGHT // 2))
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.x += paddle_speed

    ball.x += ball_dx
    ball.y += ball_dy

    if ball.left <= 0 or ball.right >= WIDTH:
        ball_dx *= -1
    if ball.top <= 0:
        ball_dy *= -1
    if ball.bottom >= HEIGHT:
        if score > high_score:
            with open(high_score_file, "w") as f:
                f.write(str(score))
        game_state = "game_over"
        continue

    if ball.colliderect(paddle):
        ball_dy *= -1
        offset = (ball.centerx - paddle.centerx) / (PADDLE_WIDTH / 2)
        ball_dx = offset * 5
        ball.y = paddle.top - BALL_RADIUS * 2

    for brick, color in bricks[:]:
        if ball.colliderect(brick):
            bricks.remove((brick, color))
            ball_dy *= -1
            hit_sound.play()
            score += 1
            break

    pygame.draw.rect(screen, PADDLE_COLOR, paddle)
    pygame.draw.circle(screen, BALL_COLOR, (ball.centerx, ball.centery), BALL_RADIUS)

    for brick, color in bricks:
        pygame.draw.rect(screen, color, brick)

    frame_height = 50
    pygame.draw.rect(screen, FRAME_BG, (0, 0, WIDTH, frame_height))
    frame_title = title_font.render("\U0001F525 Brick By Brick \U0001F525", True, TITLE_COLOR)
    screen.blit(frame_title, frame_title.get_rect(center=(WIDTH // 2, frame_height // 2)))

    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, frame_height + 10))
    screen.blit(high_score_text, (WIDTH - 200, frame_height + 10))
    screen.blit(level_text, (WIDTH // 2 - 40, frame_height + 10))

    if not bricks:
        if level < MAX_LEVELS:
            level += 1
            paddle.x = WIDTH // 2 - PADDLE_WIDTH // 2
            ball.x = WIDTH // 2
            ball.y = HEIGHT // 2
            ball_dx = 4 + level * 0.1
            ball_dy = -4 - level * 0.1
            bricks = create_bricks(level)
            pygame.time.delay(1000)
            continue
        else:
            if game_state != "win":
                win_sound.play()
                if score > high_score:
                    with open(high_score_file, "w") as f:
                        f.write(str(score))
                game_state = "win"
            continue

    pygame.display.flip()

pygame.quit()