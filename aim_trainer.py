import math
import random
import time
import pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Initialize the game window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

# Constants for target spawning and events
TARGET_INCREMENT = 400  # Time interval (ms) or spawning targets
TARGET_EVENT = pygame.USEREVENT  # Custom event for spawning targets

# Padding for target placement
TARGET_PADDING = 30

# Background color and game settings
BG_COLOR = (0, 25, 40)
LIVES = 3  # Number of lives before game over
TOP_BAR_HEIGHT = 50  # Height of the top bar

# Font for displaying text
LABEL_FONT = pygame.font.SysFont("comicsans", 24)


class Target:
    # Constants for target properties
    MAX_SIZE = 30  # Maximum size of the target
    GROWTH_RATE = 0.2  # Rate at which the target grows
    COLOR = "red"  # Primary color of the target
    SECOND_COLOR = "white"  # Secondary color for concentric circles

    def __init__(self, x, y):
        # Initialize target position and size
        self.x = x
        self.y = y
        self.size = 0  # Initial size of the target
        self.grow = True  # Whether the target is growing

    def update(self):
        # Update the size of the target
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False  # Stop growing when max size is reached

        if self.grow:
            self.size += self.GROWTH_RATE  # Increase size
        else:
            self.size -= self.GROWTH_RATE  # Decrease size

    def draw(self, win):
        # Draw concentric circles to represent the target
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR,
                           (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR,
                           (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        # Check if a point (x, y) collides with the target
        dis = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return dis <= self.size


def draw(win, targets):
    # Draw the background and all targets
    win.fill(BG_COLOR)

    for target in targets:
        target.draw(win)


def format_time(secs):
    # Format elapsed time as MM:SS.m
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)

    return f"{minutes:02d}:{seconds:02d}.{milli}"


def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    # Draw the top bar with game stats
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "black")

    # Calculate and display speed (targets per second)
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")

    # Display hits and remaining lives
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")

    # Position the labels on the top bar
    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))


def end_screen(win, elapsed_time, targets_pressed, clicks):
    # Display the end screen with final stats
    win.fill(BG_COLOR)
    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", 1, "white")

    # Calculate and display speed and accuracy
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "white")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "white")
    accuracy = round(targets_pressed / clicks * 100, 1)
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "white")

    # Center the labels on the screen
    win.blit(time_label, (get_middle(time_label), 100))
    win.blit(speed_label, (get_middle(speed_label), 200))
    win.blit(hits_label, (get_middle(hits_label), 300))
    win.blit(accuracy_label, (get_middle(accuracy_label), 400))

    pygame.display.update()

    # Wait for user input to quit
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                quit()


def get_middle(surface):
    # Calculate the x-coordinate to center a surface
    return WIDTH / 2 - surface.get_width() / 2


def main():
    # Main game loop
    run = True
    targets = []  # List of active targets
    clock = pygame.time.Clock()

    # Initialize game stats
    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()

    # Set a timer for spawning targets
    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)  # Limit the frame rate to 60 FPS
        click = False
        mouse_pos = pygame.mouse.get_pos()  # Get mouse position
        elapsed_time = time.time() - start_time  # Calculate elapsed time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # Exit the game loop
                break

            if event.type == TARGET_EVENT:
                # Spawn a new target at a random position
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(
                    TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                target = Target(x, y)
                targets.append(target)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True  # Register a mouse click
                clicks += 1

        for target in targets:
            target.update()  # Update target size

            if target.size <= 0:
                # Remove target if it shrinks to zero
                targets.remove(target)
                misses += 1

            if click and target.collide(*mouse_pos):
                # Remove target if clicked
                targets.remove(target)
                targets_pressed += 1

        if misses >= LIVES:
            # End the game if the player runs out of lives
            end_screen(WIN, elapsed_time, targets_pressed, clicks)

        # Draw the game elements
        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()

    pygame.quit()  # Quit the game


if __name__ == "__main__":
    main()  # Run the game