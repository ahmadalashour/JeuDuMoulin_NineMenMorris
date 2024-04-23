import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from globals import TRAINING_PARAMETERS
from main import main

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SOFT_BLUE = (173, 216, 230)  # Soft blue color for buttons

# Initialize Pygame
pygame.init()

# Set up the window
window_width = 800
window_height = 600
window_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Game Menu")

# Load background image
background_image = pygame.image.load("assets/menubackground.jpg")
background_image = pygame.transform.scale(background_image, (window_width, window_height))

# Fonts
font = pygame.font.SysFont(None, 36) # type: ignore


# Function to display text on the screen
def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    window_surface.blit(text_surface, text_rect)


# Function to draw buttons with rounded edges
def draw_rounded_button(rect, color, text, text_color, radius=10):
    pygame.draw.rect(window_surface, color, rect, border_radius=radius)
    draw_text(text, text_color, rect.centerx, rect.centery)


# Main menu loop
def main_menu():
    button_width = 300
    button_height = 50
    button_margin = 20
    row_height = button_height + button_margin
    top_margin = 100  # Adjust this value to lower the buttons

    while True:
        window_surface.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if render_button_rect.collidepoint(x, y):
                    TRAINING_PARAMETERS["RENDER"] = not TRAINING_PARAMETERS["RENDER"]
                elif interactables_button_rect.collidepoint(x, y):
                    TRAINING_PARAMETERS["INTERACTABLES"] = ["white"] if TRAINING_PARAMETERS["INTERACTABLES"] == ["orange"] else ["orange"]
                elif difficulty_button_rect.collidepoint(x, y):
                    TRAINING_PARAMETERS["DIFFICULTY"] = (TRAINING_PARAMETERS["DIFFICULTY"] % 10) + 1 # type: ignore
                elif stupidity_button_rect.collidepoint(x, y):
                    TRAINING_PARAMETERS["STUPIDITY"] = round(min(TRAINING_PARAMETERS["STUPIDITY"] + 0.1, 2.0), 2) # type: ignore
                elif sparsity_button_rect.collidepoint(x, y):
                    TRAINING_PARAMETERS["USE_SPARSITY"] = not TRAINING_PARAMETERS["USE_SPARSITY"]
                elif max_operations_button_rect.collidepoint(x, y):
                    TRAINING_PARAMETERS["MAX_N_OPERATIONS"] += 8196 if TRAINING_PARAMETERS["MAX_N_OPERATIONS"] is not None else None # type: ignore
                    TRAINING_PARAMETERS["MAX_N_OPERATIONS"] = TRAINING_PARAMETERS["MAX_N_OPERATIONS"] % 256000 if TRAINING_PARAMETERS["MAX_N_OPERATIONS"] is not None else None # type: ignore
                elif start_button_rect.collidepoint(x, y):
                    main()
                    return

        # Draw buttons
        render_button_rect = pygame.Rect(50, top_margin, button_width, button_height)
        draw_rounded_button(
            render_button_rect,
            SOFT_BLUE,
            "Render(DEV): " + str(TRAINING_PARAMETERS["RENDER"]),
            WHITE,
        )

        interactables_button_rect = pygame.Rect(50, top_margin + row_height, button_width, button_height)
        draw_rounded_button(
            interactables_button_rect,
            SOFT_BLUE,
            "Color : " + TRAINING_PARAMETERS["INTERACTABLES"][0], # type: ignore
            WHITE,
        )

        difficulty_button_rect = pygame.Rect(50 + button_width + button_margin, top_margin, button_width, button_height)
        draw_rounded_button(
            difficulty_button_rect,
            SOFT_BLUE,
            "Difficulty: " + str(TRAINING_PARAMETERS["DIFFICULTY"]),
            WHITE,
        )

        stupidity_button_rect = pygame.Rect(
            50 + button_width + button_margin,
            top_margin + row_height,
            button_width,
            button_height,
        )
        draw_rounded_button(
            stupidity_button_rect,
            SOFT_BLUE,
            "Stupidity: " + str(TRAINING_PARAMETERS["STUPIDITY"]),
            WHITE,
        )

        sparsity_button_rect = pygame.Rect(50, top_margin + 2 * row_height, button_width, button_height)
        draw_rounded_button(
            sparsity_button_rect,
            SOFT_BLUE,
            "Sparsity(DEV): " + str(TRAINING_PARAMETERS["USE_SPARSITY"]),
            WHITE,
        )

        max_operations_button_rect = pygame.Rect(
            50 + button_width + button_margin,
            top_margin + 2 * row_height,
            button_width,
            button_height,
        )
        draw_rounded_button(
            max_operations_button_rect,
            SOFT_BLUE,
            "Max Ops(DEV): " + str(TRAINING_PARAMETERS["MAX_N_OPERATIONS"]),
            WHITE,
        )

        start_button_rect = pygame.Rect(250, top_margin + 3 * row_height, button_width, button_height)
        draw_rounded_button(start_button_rect, SOFT_BLUE, "Start Game", WHITE)

        pygame.display.update()


# Start main menu
main_menu()
