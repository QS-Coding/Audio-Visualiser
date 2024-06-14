import pygame
import random
import os
from voronoi import *

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Color settings for Voronoi diagrams
COLOR_PALETTE = [(0, 0, 0), (15, 15, 15), (23, 23, 23), (30, 30, 30)]

# Generate Voronoi Diagrams
def generate_voronoi_image(filename):
    generate(
        path=filename,
        width=SCREEN_WIDTH,
        height=SCREEN_HEIGHT,
        regions=70,
        colors=COLOR_PALETTE,
        color_algorithm=ColorAlgorithm.no_adjacent_same,
    )

# Generate initial Voronoi diagrams
generate_voronoi_image("voronoi_1.png")
generate_voronoi_image("voronoi_2.png")

# Load Voronoi images
def load_voronoi_image(filename):
    return pygame.image.load(filename)

voronoi_1 = load_voronoi_image("voronoi_1.png")
voronoi_2 = load_voronoi_image("voronoi_2.png")

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Window with Animated Voronoi Background")

# Blending function for crossfade effect
def blend_images(img1, img2, alpha):
    blended_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
    img1.set_alpha(255 * (1 - alpha))
    img2.set_alpha(255 * alpha)
    blended_img.blit(img1, (0, 0))
    blended_img.blit(img2, (0, 0))
    return blended_img

# Main loop
running = True
clock = pygame.time.Clock()
time_since_last_gen = 0
transition_time = 2  # Time in seconds for each transition
alpha = 0.0  # Alpha value for blending
fade_in = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Time-based transition logic
    dt = clock.get_time() / 1000
    time_since_last_gen += dt
    if time_since_last_gen >= transition_time:
        time_since_last_gen = 0
        alpha = 0.0
        fade_in = not fade_in

        # Generate new Voronoi image for the next transition
        new_voronoi_filename = "voronoi_2.png" if fade_in else "voronoi_1.png"
        generate_voronoi_image(new_voronoi_filename)
        if fade_in:
            voronoi_2 = load_voronoi_image(new_voronoi_filename)
        else:
            voronoi_1 = load_voronoi_image(new_voronoi_filename)

    # Update alpha for blending
    alpha = min(alpha + (dt / transition_time), 1.0)
    if fade_in:
        blended_image = blend_images(voronoi_1, voronoi_2, alpha)
    else:
        blended_image = blend_images(voronoi_2, voronoi_1, alpha)

    # Draw the blended image as the background
    screen.blit(blended_image, (0, 0))

    # Update display
    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

pygame.quit()

# Cleanup generated images
os.remove("voronoi_1.png")
os.remove("voronoi_2.png")