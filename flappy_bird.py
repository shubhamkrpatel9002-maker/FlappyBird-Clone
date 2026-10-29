import random
import sys
import pygame

# ---------- Settings ----------
WIDTH, HEIGHT = 400, 600
GROUND_HEIGHT = 60
FPS = 60

GRAVITY = 0.5
FLAP_VELOCITY = -9
PIPE_SPEED = 3
PIPE_WIDTH = 60
PIPE_GAP = 160
PIPE_SPAWN_MS = 1400

# ---------- Colors ----------
SKY = (105, 190, 235)
GREEN = (50, 180, 70)
DARK_GREEN = (30, 130, 50)
YELLOW = (255, 220, 40)
ORANGE = (240, 140, 20)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GROUND = (210, 180, 120)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 26)

# Custom event to create pipes
SPAWN_PIPE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_PIPE, PIPE_SPAWN_MS)


def make_pipe():
    """Create a pipe pair with a random opening."""
    margin = 90
    gap_y = random.randint(margin, HEIGHT - GROUND_HEIGHT - margin)

    return {
        "x": WIDTH,
        "gap_y": gap_y,
        "scored": False,
    }


def draw_bird(surface, rect):
    """Draw a simple bird using shapes."""
    pygame.draw.ellipse(surface, YELLOW, rect)
    pygame.draw.ellipse(
        surface,
        ORANGE,
        (rect.x + 5, rect.y + rect.height // 2, 20, 12),
    )
    pygame.draw.circle(surface, WHITE, (rect.right - 9, rect.y + 10), 6)
    pygame.draw.circle(surface, BLACK, (rect.right - 7, rect.y + 10), 3)
    pygame.draw.polygon(
        surface,
        ORANGE,
        [
            (rect.right - 2, rect.y + 20),
            (rect.right + 10, rect.y + 24),
            (rect.right - 2, rect.y + 28),
        ],
    )


def draw_pipe(surface, x, gap_y):
    """Draw the upper and lower pipes."""
    top_height = gap_y - PIPE_GAP // 2
    bottom_y = gap_y + PIPE_GAP // 2
    bottom_height = HEIGHT - GROUND_HEIGHT - bottom_y

    top_rect = pygame.Rect(x, 0, PIPE_WIDTH, top_height)
    bottom_rect = pygame.Rect(x, bottom_y, PIPE_WIDTH, bottom_height)

    pygame.draw.rect(surface, GREEN, top_rect)
    pygame.draw.rect(surface, GREEN, bottom_rect)

    # Pipe rims
    rim_height = 18
    pygame.draw.rect(
        surface,
        DARK_GREEN,
        (x - 5, top_height - rim_height, PIPE_WIDTH + 10, rim_height),
    )
    pygame.draw.rect(
        surface,
        DARK_GREEN,
        (x - 5, bottom_y, PIPE_WIDTH + 10, rim_height),
    )


def draw_ground(surface):
    ground_y = HEIGHT - GROUND_HEIGHT
    pygame.draw.rect(surface, GROUND, (0, ground_y, WIDTH, GROUND_HEIGHT))
    pygame.draw.line(surface, DARK_GREEN, (0, ground_y), (WIDTH, ground_y), 5)


def reset_game():
    bird = pygame.Rect(80, HEIGHT // 2, 34, 26)
    return bird, 0.0, [], 0, False


bird, bird_velocity, pipes, score, game_over = reset_game()
running = True

while running:
    clock.tick(FPS)

    # ---------- Events ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == SPAWN_PIPE and not game_over:
            pipes.append(make_pipe())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_SPACE:
                if game_over:
                    bird, bird_velocity, pipes, score, game_over = reset_game()
                bird_velocity = FLAP_VELOCITY

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                bird, bird_velocity, pipes, score, game_over = reset_game()
            bird_velocity = FLAP_VELOCITY

    # ---------- Update game ----------
    if not game_over:
        # Gravity and bird movement
        bird_velocity += GRAVITY
        bird.y += int(bird_velocity)

        # Move pipes
        for pipe in pipes:
            pipe["x"] -= PIPE_SPEED

        # Remove pipes that have left the screen
        pipes = [pipe for pipe in pipes if pipe["x"] + PIPE_WIDTH > 0]

        # Score when the bird passes a pipe
        for pipe in pipes:
            if not pipe["scored"] and pipe["x"] + PIPE_WIDTH < bird.left:
                score += 1
                pipe["scored"] = True

        # Check ground and ceiling collisions
        if bird.top <= 0 or bird.bottom >= HEIGHT - GROUND_HEIGHT:
            game_over = True

        # Check pipe collisions
        for pipe in pipes:
            x = pipe["x"]
            gap_y = pipe["gap_y"]

            top_height = gap_y - PIPE_GAP // 2
            bottom_y = gap_y + PIPE_GAP // 2

            top_rect = pygame.Rect(x, 0, PIPE_WIDTH, top_height)
            bottom_rect = pygame.Rect(
                x,
                bottom_y,
                PIPE_WIDTH,
                HEIGHT - GROUND_HEIGHT - bottom_y,
            )

            if bird.colliderect(top_rect) or bird.colliderect(bottom_rect):
                game_over = True

    # ---------- Draw ----------
    screen.fill(SKY)

    for pipe in pipes:
        draw_pipe(screen, pipe["x"], pipe["gap_y"])

    draw_ground(screen)
    draw_bird(screen, bird)

    score_text = font.render(str(score), True, WHITE)
    screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 45)))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        title = font.render("Game Over", True, WHITE)
        final_score = small_font.render(f"Score: {score}", True, WHITE)
        restart = small_font.render(
            "Press SPACE or click to restart",
            True,
            WHITE,
        )

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 45)))
        screen.blit(
            final_score,
            final_score.get_rect(center=(WIDTH // 2, HEIGHT // 2)),
        )
        screen.blit(
            restart,
            restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)),
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
