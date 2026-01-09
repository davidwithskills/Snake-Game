import pygame
import time
import random

# Initialize pygame
pygame.init()

# Colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Screen size
width = 600
height = 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game')

clock = pygame.time.Clock()
snake_block = 10
snake_speed = 15

font = pygame.font.SysFont("bahnschrift", 25)

def gradient_color(index, total, start=None, end=None):
    # use configured defaults if not provided
    if start is None:
        start = SNAKE_GRADIENT_START
    if end is None:
        end = SNAKE_GRADIENT_END
    if total <= 1:
        return end
    t = index / float(total - 1)
    r = int(start[0] + (end[0] - start[0]) * t)
    g = int(start[1] + (end[1] - start[1]) * t)
    b = int(start[2] + (end[2] - start[2]) * t)
    return (r, g, b)

# Configurable appearance
SNAKE_GRADIENT_START = (0, 100, 0)
SNAKE_GRADIENT_END = (0, 255, 0)
# head border radius is snake_block // HEAD_BORDER_RADIUS_FACTOR
HEAD_BORDER_RADIUS_FACTOR = 3

def our_snake(snake_block, snake_list, direction):
    if not snake_list:
        return
    # draw body with gradient
    total = len(snake_list)
    for i, x in enumerate(snake_list[:-1]):
        color = gradient_color(i, total)
        pygame.draw.rect(screen, color, [int(x[0]), int(x[1]), snake_block, snake_block])
    # draw head (brighter)
    head = snake_list[-1]
    hx = int(head[0])
    hy = int(head[1])
    border_radius = max(1, snake_block // HEAD_BORDER_RADIUS_FACTOR)
    pygame.draw.rect(screen, (0,255,0), [hx, hy, snake_block, snake_block], border_radius=border_radius)

    # draw eyes based on direction (centered proportions)
    eye_radius = max(1, snake_block // 4)
    offset_small = snake_block // 4
    offset_large = (3 * snake_block) // 4
    eyes = []
    if direction == "UP":
        eyes = [(hx + offset_small, hy + offset_small), (hx + offset_large, hy + offset_small)]
    elif direction == "DOWN":
        eyes = [(hx + offset_small, hy + offset_large), (hx + offset_large, hy + offset_large)]
    elif direction == "LEFT":
        eyes = [(hx + offset_small, hy + offset_small), (hx + offset_small, hy + offset_large)]
    elif direction == "RIGHT":
        eyes = [(hx + offset_large, hy + offset_small), (hx + offset_large, hy + offset_large)]

    for eye in eyes:
        pygame.draw.circle(screen, (0,0,0), eye, eye_radius)

def Your_score(score):
    value = font.render(f"Score: {score}", True, yellow)
    screen.blit(value, [0, 0])

def gameLoop():
    game_over = False
    game_close = False

    x1 = width // 2
    y1 = height // 2

    x1_change = 0
    y1_change = 0
    direction = "RIGHT"

    snake_List = []
    Length_of_snake = 1

    foodx = random.randrange(0, width - snake_block, snake_block)
    foody = random.randrange(0, height - snake_block, snake_block)

    while not game_over:

        while game_close:
            screen.fill(blue)
            message = font.render("Game Over! Press C-Play Again or Q-Quit", True, red)
            screen.blit(message, [width / 9, height / 3])
            Your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                    direction = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                    direction = "RIGHT"
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                    direction = "UP"
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0
                    direction = "DOWN"

        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        screen.fill(blue)
        pygame.draw.rect(screen, red, [foodx, foody, snake_block, snake_block])
        snake_Head = []
        snake_Head.append(int(x1))
        snake_Head.append(int(y1))
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List, direction)
        Your_score(Length_of_snake - 1)

        pygame.display.update()

        if int(x1) == foodx and int(y1) == foody:
            foodx = random.randrange(0, width - snake_block, snake_block)
            foody = random.randrange(0, height - snake_block, snake_block)
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

gameLoop()
