import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Dot settings
NUM_DOTS = 5000
DOT_RADIUS = 1
ATTRACTION_FORCE = 0.05
MAX_VELOCITY = 3
MIN_ALPHA = 50  # Minimum alpha value for the most distant dots
MAX_ALPHA = 255  # Maximum alpha value for the closest dots
IMPULSE_FORCE = 1  # Force of the outward impulse

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Floating Dots")

# Dot class
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = random.uniform(-1, 1)  # Z value for depth
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)

    def update(self, target_pos, random_movement=False):
        if random_movement:
            # Move randomly
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.5, 0.5)
        else:
            # Calculate distance to target
            dx = target_pos[0] - self.x
            dy = target_pos[1] - self.y
            dist = math.sqrt(dx**2 + dy**2)

            # Apply attraction force
            if dist != 0:
                self.vx += (dx / dist) * ATTRACTION_FORCE
                self.vy += (dy / dist) * ATTRACTION_FORCE

        # Limit velocity
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > MAX_VELOCITY:
            self.vx = (self.vx / speed) * MAX_VELOCITY
            self.vy = (self.vy / speed) * MAX_VELOCITY

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Keep dots within screen bounds
        if self.x < 0 or self.x > SCREEN_WIDTH:
            self.vx *= -1
        if self.y < 0 or self.y > SCREEN_HEIGHT:
            self.vy *= -1

    def draw(self, screen):
        # Calculate alpha based on Z value
        alpha = int((self.z + 1) / 2 * (MAX_ALPHA - MIN_ALPHA) + MIN_ALPHA)
        color = (WHITE[0], WHITE[1], WHITE[2], alpha)

        # Create temporary surface for drawing the circle
        temp_surface = pygame.Surface((DOT_RADIUS * 2, DOT_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, color, (DOT_RADIUS, DOT_RADIUS), DOT_RADIUS)
        screen.blit(temp_surface, (int(self.x - DOT_RADIUS), int(self.y - DOT_RADIUS)))

    def apply_impulse(self, target_pos):
        # Calculate distance to target
        dx = self.x - target_pos[0]
        dy = self.y - target_pos[1]
        dist = math.sqrt(dx**2 + dy**2)

        # Apply impulse force
        if dist != 0:
            self.vx += (dx / dist) * IMPULSE_FORCE
            self.vy += (dy / dist) * IMPULSE_FORCE

# Create dots
dots = [Dot(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(NUM_DOTS)]

# Main loop
running = True
clock = pygame.time.Clock()
last_click_time = 0
target_pos = pygame.mouse.get_pos()
follow_cursor = True
random_movement = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            current_click_time = time.time()
            if event.button == 1:  # Left click
                if current_click_time - last_click_time < 0.3:
                    follow_cursor = not follow_cursor
                else:
                    target_pos = pygame.mouse.get_pos()
                last_click_time = current_click_time
            elif event.button == 3:  # Right click
                random_movement = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right click release
                random_movement = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                for dot in dots:
                    dot.apply_impulse(target_pos)

    # Clear screen
    screen.fill(BLACK)

    # Get cursor position
    cursor_pos = pygame.mouse.get_pos()
    if follow_cursor:
        target_pos = cursor_pos

    # Update and draw dots
    for dot in dots:
        dot.update(target_pos, random_movement)
        dot.draw(screen)

    # Update display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

pygame.quit()