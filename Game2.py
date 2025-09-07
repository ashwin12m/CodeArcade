import pygame
import math
import random

pygame.init()

# Score and coin system
score = 0
coins = 0
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except:
    high_score = 0

# Screen setup
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trailing Ball Shooter")
clock = pygame.time.Clock()

# Fonts
FONT = pygame.font.SysFont("Comic Sans MS", 20)
BIG_FONT = pygame.font.SysFont("Comic Sans MS", 50)

# Load coin image
coin_img = pygame.image.load("coin.png")
coin_img = pygame.transform.scale(coin_img, (24, 24))

# Colors
WHITE = (255, 255, 255)
BACKGROUND_TOP = (20, 20, 30)
BACKGROUND_BOTTOM = (30, 30, 50)
COLOR_LIST = [(255, 100, 100), (100, 255, 100), (100, 100, 255),
              (255, 255, 100), (255, 100, 255), (100, 255, 255)]

# Constants
BRICK_WIDTH = 80
BRICK_HEIGHT = 45
BRICK_SPACING = 5
ROWS = 5
COLS = WIDTH // (BRICK_WIDTH + BRICK_SPACING)
SCOREBOARD_HEIGHT = 80

class Ball:
    def __init__(self, x, y, angle):
        speed = 8
        self.x = x
        self.y = y
        self.radius = 5
        self.dx = speed * math.cos(math.radians(angle))
        self.dy = -speed * math.sin(math.radians(angle))
        self.active = True

    def move(self):
        if not self.active:
            return
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= WIDTH:
            self.dx *= -1
        if self.y <= SCOREBOARD_HEIGHT:
            self.dy *= -1
        if self.y >= HEIGHT:
            self.active = False

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, (0, 200, 255), (int(self.x), int(self.y)), self.radius)

class Brick:
    def __init__(self, x, y, hits, color):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.hits = hits
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        text = FONT.render(str(self.hits), True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

class Paddle:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 30
        self.radius = 10

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (self.x, self.y), self.radius)

def draw_gradient_background():
    for y in range(HEIGHT):
        r = BACKGROUND_TOP[0] + (BACKGROUND_BOTTOM[0] - BACKGROUND_TOP[0]) * y // HEIGHT
        g = BACKGROUND_TOP[1] + (BACKGROUND_BOTTOM[1] - BACKGROUND_TOP[1]) * y // HEIGHT
        b = BACKGROUND_TOP[2] + (BACKGROUND_BOTTOM[2] - BACKGROUND_TOP[2]) * y // HEIGHT
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def create_brick_grid():
    bricks = []
    for row in range(ROWS):
        for col in range(COLS):
            x = col * (BRICK_WIDTH + BRICK_SPACING) + BRICK_SPACING
            y = row * (BRICK_HEIGHT + BRICK_SPACING) + SCOREBOARD_HEIGHT + 10
            hits = random.randint(1, 5)
            color = random.choice(COLOR_LIST)
            bricks.append(Brick(x, y, hits, color))
    return bricks

def add_new_brick_row(bricks):
    for brick in bricks:
        brick.rect.y += BRICK_HEIGHT + BRICK_SPACING
    for col in range(COLS):
        if random.random() < 0.8:
            x = col * (BRICK_WIDTH + BRICK_SPACING) + BRICK_SPACING
            y = SCOREBOARD_HEIGHT + 10
            hits = random.randint(1, 5)
            color = random.choice(COLOR_LIST)
            bricks.append(Brick(x, y, hits, color))

def main_menu():
    play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 80)
    while True:
        draw_gradient_background()
        title = BIG_FONT.render("Trailing Ball Shooter", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        # Animated play button
        pulse = 10 * math.sin(pygame.time.get_ticks() / 300)
        pygame.draw.rect(screen, (50, 200, 100), play_button.inflate(pulse, pulse), border_radius=12)
        play_text = FONT.render("PLAY", True, WHITE)
        screen.blit(play_text, (play_button.centerx - play_text.get_width() // 2,
                                play_button.centery - play_text.get_height() // 2))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    main()
                    return

def main():
    global score, high_score, coins
    score = 0
    coins = 0
    run = True
    angle = 60
    balls = []
    paddle = Paddle()
    shoot_ready = True
    bricks = create_brick_grid()
    total_balls_to_launch = 10
    launch_delay = 10
    ball_launch_timer = 0
    balls_launched = 0
    shooting = False

    while run:
        draw_gradient_background()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            angle = max(10, angle - 1)
        if keys[pygame.K_RIGHT]:
            angle = min(170, angle + 1)

        if keys[pygame.K_SPACE] and shoot_ready and not shooting:
            shooting = True
            balls_launched = 0
            ball_launch_timer = 0
            balls = []

        if shooting:
            ball_launch_timer += 1
            if ball_launch_timer >= launch_delay and balls_launched < total_balls_to_launch:
                balls.append(Ball(paddle.x, paddle.y, angle))
                balls_launched += 1
                ball_launch_timer = 0
            if balls_launched == total_balls_to_launch:
                shooting = False
                shoot_ready = False

        all_inactive = True
        for ball in balls:
            if ball.active:
                all_inactive = False
            ball.move()
            ball.draw(screen)

            for brick in bricks:
                if brick.rect.colliderect(pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2)):
                    brick.hits -= 1
                    score += 10
                    coins += random.randint(1, 3)
                    ball.dy *= -1
                    break

        bricks = [b for b in bricks if b.hits > 0]

        if all_inactive and not shooting and not shoot_ready:
            add_new_brick_row(bricks)
            shoot_ready = True

        for brick in bricks:
            brick.draw(screen)
            if brick.rect.bottom >= paddle.y:
                game_over_text = FONT.render("Game Over!", True, (255, 0, 0))
                screen.blit(game_over_text, (WIDTH // 2 - 60, HEIGHT // 2))
                pygame.display.flip()
                pygame.time.delay(2000)
                run = False
                break

        paddle.draw(screen)

        # Scoreboard background
        pygame.draw.rect(screen, (10, 10, 20), (0, 0, WIDTH, SCOREBOARD_HEIGHT))

        # Score display
        score_text = FONT.render(f"Score: {score}", True, WHITE)
        highscore_text = FONT.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 150, 10))
        screen.blit(highscore_text, (WIDTH - 150, 40))

        # Coin display
        screen.blit(coin_img, (10, 40))
        coin_text = FONT.render(f"{coins}", True, WHITE)
        screen.blit(coin_text, (40, 40))

        pygame.display.flip()
        clock.tick(60)

    if score > high_score:
        high_score = score
        with open("highscore.txt", "w") as f:
            f.write(str(high_score))
    pygame.quit()

# Start game
if __name__ == "__main__":
    main_menu()
