import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

# Dot settings
NUM_DOTS = 10000
DOT_RADIUS = 1
ATTRACTION_FORCE = 0.03
MAX_VELOCITY = 3
MIN_ALPHA = 50  # Minimum alpha value for the most distant dots
MAX_ALPHA = 255  # Maximum alpha value for the closest dots
NEW_DOTS_VELOCITY = MAX_VELOCITY  # Maximum velocity for new dots
POUR_RATE = 250  # Number of new dots to pour per frame

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Floating Dots")

# Dot class
class Dot:
    def __init__(self, x, y, target_pos):
        self.x = x
        self.y = y
        self.z = random.uniform(-1, 1)  # Z value for depth
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.color = WHITE
        self.target_pos = target_pos

    def update(self, random_movement=False, moving_down=False):
        if moving_down:
            # Move downwards
            self.vy = MAX_VELOCITY
        elif random_movement:
            # Move randomly
            self.vx += random.uniform(-0.5, 0.5)
            self.vy += random.uniform(-0.5, 0.5)
        else:
            # Calculate distance to target
            dx = self.target_pos[0] - self.x
            dy = self.target_pos[1] - self.y
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
        color = (*self.color[:3], alpha)

        # Directly draw on the main screen surface
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), DOT_RADIUS)

    def change_color(self, new_color):
        self.color = new_color

# Create dots
dots = [Dot(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)) for _ in range(NUM_DOTS)]

# Main loop
running = True
clock = pygame.time.Clock()
target_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Center attractor
random_movement = False
shift_active = False
shift_start_time = 0
shift_duration = 2  # Shift effect lasts 2 seconds
shift_origin = None
shift_color = random.choice(COLORS)
pour_new_dots = False
old_dots_moving_down = False
pour_timer = 0
total_dots_poured = 0

def generate_new_dots(num_new_dots, target_pos):
    new_dots = []
    corners = [(0, 0), (SCREEN_WIDTH, 0)]  # Only top corners
    for corner in corners:
        for _ in range(num_new_dots // 2):  # Spread new dots across the top corners
            new_dot = Dot(corner[0], corner[1], target_pos)
            angle = math.atan2(target_pos[1] - corner[1], target_pos[0] - corner[0])
            new_dot.vx = math.cos(angle) * random.uniform(0, NEW_DOTS_VELOCITY)
            new_dot.vy = math.sin(angle) * random.uniform(0, NEW_DOTS_VELOCITY)
            new_dots.append(new_dot)
    return new_dots

def apply_color_spike(dots, origin, center, color, width):
    for dot in dots:
        dx = center[0] - origin[0]
        dy = center[1] - origin[1]
        line_angle = math.atan2(dy, dx)
        
        dot_dx = dot.x - origin[0]
        dot_dy = dot.y - origin[1]
        dot_angle = math.atan2(dot_dy, dot_dx)
        
        distance_to_line = abs(dot_dy - math.tan(line_angle) * dot_dx) / math.sqrt(1 + math.tan(line_angle) ** 2)
        
        if distance_to_line < width and min(dot_angle, line_angle) <= max(dot_angle, line_angle) <= max(dot_angle, line_angle) + math.pi:
            dot.change_color(color)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                target_pos = pygame.mouse.get_pos()
                for dot in dots:
                    dot.target_pos = target_pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                old_dots_moving_down = True
                pour_new_dots = False
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                shift_active = True
                shift_start_time = time.time()
                shift_origin = random.choice([(0, random.randint(0, SCREEN_HEIGHT)),
                                              (SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)),
                                              (random.randint(0, SCREEN_WIDTH), 0),
                                              (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT)])
                shift_color = random.choice(COLORS)
                shift_width = random.randint(5, 20)

    # Clear screen
    screen.fill(BLACK)

    # Color spike effect
    if shift_active:
        apply_color_spike(dots, shift_origin, target_pos, shift_color, shift_width)
        shift_active = False

    # Pour new dots effect
    if pour_new_dots:
        if pour_timer == 0:
            pour_timer = time.time()
        elapsed_time = time.time() - pour_timer
        num_new_dots = int(POUR_RATE * elapsed_time)
        if num_new_dots > 0:
            new_dots = generate_new_dots(num_new_dots, target_pos)
            dots.extend(new_dots)
            total_dots_poured += len(new_dots)
            if total_dots_poured >= NUM_DOTS:
                pour_new_dots = False
                total_dots_poured = 0
                old_dots_moving_down = False

    # Update and draw dots
    for dot in dots[:]:
        if old_dots_moving_down:
            dot.update(moving_down=True)
            if dot.y >= SCREEN_HEIGHT:
                dots.remove(dot)
                if len(dots) == 0:  # If all old dots are removed, start pouring new dots
                    pour_new_dots = True
                    pour_timer = 0
        else:
            dot.update(random_movement)
        dot.draw(screen)

    # Update display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

pygame.quit()
