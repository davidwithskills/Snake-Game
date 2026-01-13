import pygame
import random

pygame.init()
pygame.mixer.init()
eat_sound = pygame.mixer.Sound("eat.wav")
gameover_sound = pygame.mixer.Sound("gameover.wav")

# Optional: volume control (0.0 to 1.0)
eat_sound.set_volume(0.6)
gameover_sound.set_volume(0.8)



# Colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (30, 120, 60)
grid_color = (40, 130, 180)

# Layout
TOP_BAR_HEIGHT = 60
UI_MARGIN = 10
UI_BG = (34, 139, 34)  # top bar background
PLAY_BG = (187, 240, 148)  # play area background
PLAY_BORDER_COLOR = (34, 139, 34)
GRID_SHADE_A = (180, 230, 140)
GRID_SHADE_B = (165, 215, 120)
BORDER_THICKNESS = 5

# Screen size
width = 600
height = 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game')

clock = pygame.time.Clock()
snake_block = 10
base_speed = 15

font = pygame.font.SysFont("bahnschrift", 25)

# Gradient settings
SNAKE_GRADIENT_START = (0, 100, 0)
SNAKE_GRADIENT_END = (0, 255, 0)
HEAD_BORDER_RADIUS_FACTOR = 3

# Highscore storage
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(int(score)))
    except Exception:
        pass


def gradient_color(index, total):
    if total <= 1:
        return SNAKE_GRADIENT_END
    t = index / (total - 1)
    r = int(SNAKE_GRADIENT_START[0] + (SNAKE_GRADIENT_END[0] - SNAKE_GRADIENT_START[0]) * t)
    g = int(SNAKE_GRADIENT_START[1] + (SNAKE_GRADIENT_END[1] - SNAKE_GRADIENT_START[1]) * t)
    b = int(SNAKE_GRADIENT_START[2] + (SNAKE_GRADIENT_END[2] - SNAKE_GRADIENT_START[2]) * t)
    return (r, g, b)


def draw_grid(play_x, play_y, play_w, play_h):
    # draw a checkerboard of two green shades
    cols = play_w // snake_block
    rows = play_h // snake_block
    for row in range(rows):
        for col in range(cols):
            x = play_x + col * snake_block
            y = play_y + row * snake_block
            color = GRID_SHADE_A if (row + col) % 2 == 0 else GRID_SHADE_B
            pygame.draw.rect(screen, color, (x, y, snake_block, snake_block))


def our_snake(snake_list, direction):
    total = len(snake_list)

    # Body (gradient)
    for i, block in enumerate(snake_list[:-1]):
        color = gradient_color(i, total)
        pygame.draw.rect(screen, color, (*block, snake_block, snake_block), border_radius=4)

    # Head
    head = snake_list[-1]
    hx, hy = head
    radius = max(1, snake_block // HEAD_BORDER_RADIUS_FACTOR)
    pygame.draw.rect(screen, green, (hx, hy, snake_block, snake_block), border_radius=radius)

    # Eyes
    eye_r = max(1, snake_block // 4)
    s = snake_block // 4
    l = (3 * snake_block) // 4

    if direction == "UP":
        eyes = [(hx + s, hy + s), (hx + l, hy + s)]
    elif direction == "DOWN":
        eyes = [(hx + s, hy + l), (hx + l, hy + l)]
    elif direction == "LEFT":
        eyes = [(hx + s, hy + s), (hx + s, hy + l)]
    else:  # RIGHT
        eyes = [(hx + l, hy + s), (hx + l, hy + l)]

    for e in eyes:
        pygame.draw.circle(screen, black, e, eye_r)


def show_score(score, highscore):
    # draw inside top UI bar, left-aligned
    top_y = (TOP_BAR_HEIGHT - font.get_height()) // 2
    hs = font.render(f"Highscore: {highscore}", True, yellow)
    value = font.render(f"Score: {score}", True, yellow)
    screen.blit(hs, (UI_MARGIN, top_y))
    screen.blit(value, (UI_MARGIN + 160, top_y))


def gameLoop():
    game_over = False
    game_close = False

    # Play area coordinates and size
    play_x = UI_MARGIN
    play_y = TOP_BAR_HEIGHT + UI_MARGIN
    play_w = width - 2 * UI_MARGIN
    play_h = height - TOP_BAR_HEIGHT - 2 * UI_MARGIN

    # compute inner playable area (inside the drawn border)
    available_w = play_w - 2 * BORDER_THICKNESS
    available_h = play_h - 2 * BORDER_THICKNESS

    # make inner play size a multiple of snake_block so positions align to grid
    cols = available_w // snake_block
    rows = available_h // snake_block
    play_inner_w = cols * snake_block
    play_inner_h = rows * snake_block

    # center the inner play area within the border thickness
    play_inner_x = play_x + BORDER_THICKNESS + (available_w - play_inner_w) // 2
    play_inner_y = play_y + BORDER_THICKNESS + (available_h - play_inner_h) // 2

    # start centered in inner play area and aligned to grid
    center_x = play_inner_x + play_inner_w // 2
    center_y = play_inner_y + play_inner_h // 2
    x = center_x - ((center_x - play_inner_x) % snake_block)
    y = center_y - ((center_y - play_inner_y) % snake_block)
    dx = dy = 0
    direction = "RIGHT"

    snake = []
    length = 1
    highscore = load_highscore()

    # initial food spawn inside inner playable area (aligned to grid)
    foodx = random.randrange(play_inner_x, play_inner_x + play_inner_w - snake_block, snake_block)
    foody = random.randrange(play_inner_y, play_inner_y + play_inner_h - snake_block, snake_block)

    while not game_over:

        while game_close:
            screen.fill(blue)
            msg = font.render("Game Over! Press C-Play Again or Q-Quit", True, red)
            screen.blit(msg, (width // 9, height // 3))
            show_score(length - 1, highscore)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        # save highscore if beaten
                        current_score = length - 1
                        if current_score > highscore:
                            save_highscore(current_score)
                            highscore = current_score
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        # save highscore if beaten then restart
                        current_score = length - 1
                        if current_score > highscore:
                            save_highscore(current_score)
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    dx, dy = -snake_block, 0
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    dx, dy = snake_block, 0
                    direction = "RIGHT"
                elif event.key == pygame.K_UP:
                    dx, dy = 0, -snake_block
                    direction = "UP"
                elif event.key == pygame.K_DOWN:
                    dx, dy = 0, snake_block
                    direction = "DOWN"

        # collision when the snake's block would go outside the inner play area
        min_x = play_inner_x
        min_y = play_inner_y
        max_x = play_inner_x + play_inner_w - snake_block
        max_y = play_inner_y + play_inner_h - snake_block
        if x < min_x or x > max_x or y < min_y or y > max_y:
            gameover_sound.play()
            game_close = True

        x += dx
        y += dy

        # Background: top bar + play area
        screen.fill(blue)
        # top UI bar
        pygame.draw.rect(screen, UI_BG, (0, 0, width, TOP_BAR_HEIGHT))
        # play area background (full area behind the border)
        pygame.draw.rect(screen, PLAY_BG, (play_x, play_y, play_w, play_h))
        # draw checkerboard grid inside inner playable area
        draw_grid(play_inner_x, play_inner_y, play_inner_w, play_inner_h)
        # play area border on top of grid
        pygame.draw.rect(screen, PLAY_BORDER_COLOR, (play_x, play_y, play_w, play_h), BORDER_THICKNESS)

        # Food (circle + outline) - coordinates are top-left of block
        pygame.draw.circle(screen, red, (foodx + snake_block // 2, foody + snake_block // 2), snake_block // 2)
        pygame.draw.circle(screen, white, (foodx + snake_block // 2, foody + snake_block // 2), snake_block // 2, 1)

        snake.append([x, y])
        if len(snake) > length:
            del snake[0]

        for block in snake[:-1]:
            if block == [x, y]:
                gameover_sound.play()
                game_close = True

        our_snake(snake, direction)
        show_score(length - 1, highscore)

        pygame.display.update()

        if x == foodx and y == foody:
            eat_sound.play()
            foodx, foody = generate_food(snake, play_inner_x, play_inner_y, play_inner_w, play_inner_h)
            length += 1

        # Speed increases with score
        speed = base_speed + (length // 1)
        clock.tick(speed)

    pygame.quit()
    quit()

def generate_food(snake, play_inner_x, play_inner_y, play_inner_w, play_inner_h):
    free_cells = []

    for x in range(play_inner_x,
                   play_inner_x + play_inner_w - snake_block,
                   snake_block):
        for y in range(play_inner_y,
                       play_inner_y + play_inner_h - snake_block,
                       snake_block):
            if [x, y] not in snake:
                free_cells.append((x, y))

    return random.choice(free_cells)

gameLoop()
