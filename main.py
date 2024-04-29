import sys

from src.globals import TRAINING_PARAMETERS, Player
from run import main

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SOFT_BLUE = (173, 216, 230)  # Soft blue color for buttons


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
    """Main menu loop to select the players and start the game."""
    button_width = 300
    button_height = 50
    button_margin = 20
    row_height = button_height + button_margin
    top_margin = 180  # Adjust this value to lower the buttons
    difficulty = TRAINING_PARAMETERS["DIFFICULTY"][Player.orange]  # type: ignore
    while True:
        window_surface.blit(background_image, (0, 0))

        # Player Selection Buttons
        interactables_orange_button_rect = pygame.Rect(
            50, top_margin, button_width, button_height
        )
        draw_rounded_button(
            interactables_orange_button_rect,
            SOFT_BLUE,
            "Player Orange: "
            + (
                TRAINING_PARAMETERS["INTERACTABLES"][0]  # type: ignore
                if TRAINING_PARAMETERS["INTERACTABLES"]
                else "Bot"
            ),  # type: ignore
            WHITE,
        )

        interactables_white_button_rect = pygame.Rect(
            50 + button_width + button_margin, top_margin, button_width, button_height
        )
        draw_rounded_button(
            interactables_white_button_rect,
            SOFT_BLUE,
            "Player White: "
            + (
                TRAINING_PARAMETERS["INTERACTABLES"][1]  # type: ignore
                if len(TRAINING_PARAMETERS["INTERACTABLES"]) > 1  # type: ignore
                else "Bot"
            ),  # type: ignore
            WHITE,
        )

        difficulty_button_rect = pygame.Rect(
            50, top_margin + button_height * 2, button_width, button_height
        )
        draw_rounded_button(
            difficulty_button_rect,
            SOFT_BLUE,
            "Difficulty: " + str(difficulty),
            WHITE,
        )

        stupidity_button_rect = pygame.Rect(
            50 + button_width + button_margin,
            top_margin + button_height * 2,
            button_width,
            button_height,
        )
        draw_rounded_button(
            stupidity_button_rect,
            SOFT_BLUE,
            "Stupidity: " + str(TRAINING_PARAMETERS["STUPIDITY"]),
            WHITE,
        )

        sparsity_button_rect = pygame.Rect(
            50, top_margin + 3 * row_height, button_width, button_height
        )
        draw_rounded_button(
            sparsity_button_rect,
            SOFT_BLUE,
            "Sparsity(DEV): " + str(TRAINING_PARAMETERS["USE_SPARSITY"]),
            WHITE,
        )

        max_operations_button_rect = pygame.Rect(
            50 + button_width + button_margin,
            top_margin + 3 * row_height,
            button_width,
            button_height,
        )
        draw_rounded_button(
            max_operations_button_rect,
            SOFT_BLUE,
            "Max Ops(DEV): " + str(TRAINING_PARAMETERS["MAX_N_OPERATIONS"]),
            WHITE,
        )

        start_button_rect = pygame.Rect(
            250, top_margin + 4 * row_height, button_width, button_height
        )
        draw_rounded_button(start_button_rect, SOFT_BLUE, "Start Game", WHITE)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in [MOUSEMOTION, MOUSEBUTTONDOWN]:
                x, y = pygame.mouse.get_pos()
                if interactables_orange_button_rect.collidepoint(x, y):
                    if event.type == MOUSEBUTTONDOWN:
                        click_sound.play()
                        if TRAINING_PARAMETERS["INTERACTABLES"]:
                            TRAINING_PARAMETERS["INTERACTABLES"][0] = (  # type: ignore
                                "Human"
                                if TRAINING_PARAMETERS["INTERACTABLES"][0] == "Bot"  # type: ignore
                                else "Bot"
                            )  # type: ignore
                        else:
                            TRAINING_PARAMETERS["INTERACTABLES"].append("Bot")  # type: ignore
                elif interactables_white_button_rect.collidepoint(x, y):
                    if event.type == MOUSEBUTTONDOWN:
                        click_sound.play()
                        if len(TRAINING_PARAMETERS["INTERACTABLES"]) > 1:  # type: ignore
                            TRAINING_PARAMETERS["INTERACTABLES"][1] = (  # type: ignore
                                "Human"
                                if TRAINING_PARAMETERS["INTERACTABLES"][1] == "Bot"  # type: ignore
                                else "Bot"
                            )  # type: ignore
                        else:
                            TRAINING_PARAMETERS["INTERACTABLES"].append("Bot")  # type: ignore

                elif difficulty_button_rect.collidepoint(x, y):
                    if event.type == MOUSEBUTTONDOWN:
                        click_sound.play()
                        difficulty = (difficulty % 10) + 1  # type: ignore

                elif stupidity_button_rect.collidepoint(x, y):
                    if event.type == MOUSEBUTTONDOWN:
                        click_sound.play()
                        TRAINING_PARAMETERS["STUPIDITY"] = round(
                            min(TRAINING_PARAMETERS["STUPIDITY"] + 0.1, 2.0),
                            2,  # type: ignore
                        )  # type: ignore

                elif sparsity_button_rect.collidepoint(x, y):
                    if event.type == MOUSEBUTTONDOWN:
                        click_sound.play()
                        TRAINING_PARAMETERS["USE_SPARSITY"] = not TRAINING_PARAMETERS[
                            "USE_SPARSITY"
                        ]

                elif max_operations_button_rect.collidepoint(x, y):
                    if event.type == MOUSEBUTTONDOWN:
                        click_sound.play()
                        if not TRAINING_PARAMETERS["MAX_N_OPERATIONS"]:
                            TRAINING_PARAMETERS["MAX_N_OPERATIONS"] = 10000
                        elif TRAINING_PARAMETERS["MAX_N_OPERATIONS"] < 1000000:  # type: ignore
                            TRAINING_PARAMETERS["MAX_N_OPERATIONS"] += (
                                int(TRAINING_PARAMETERS["MAX_N_OPERATIONS"] / 2.0)  # type: ignore
                                if TRAINING_PARAMETERS["MAX_N_OPERATIONS"] is not None
                                else None
                            )  # type: ignore
                        else:
                            TRAINING_PARAMETERS["MAX_N_OPERATIONS"] = None

                elif start_button_rect.collidepoint(x, y):
                    if event.type == MOUSEBUTTONDOWN:
                        click_sound.play()

                        if len(TRAINING_PARAMETERS["INTERACTABLES"]) > 0:  # type: ignore
                            TRAINING_PARAMETERS["INTERACTABLES"][0] = (  # type: ignore
                                Player.orange
                                if TRAINING_PARAMETERS["INTERACTABLES"][0] == "Human"  # type: ignore
                                else "Bot"
                            )  # type: ignore
                        if len(TRAINING_PARAMETERS["INTERACTABLES"]) > 1:  # type: ignore
                            TRAINING_PARAMETERS["INTERACTABLES"][1] = (  # type: ignore
                                Player.white
                                if TRAINING_PARAMETERS["INTERACTABLES"][1] == "Human"  # type: ignore
                                else "Bot"
                            )  # type: ignore
                        TRAINING_PARAMETERS["INTERACTABLES"] = [
                            x
                            for x in TRAINING_PARAMETERS["INTERACTABLES"]  # type: ignore
                            if x != "Bot"
                        ]  # type: ignore

                        TRAINING_PARAMETERS["DIFFICULTY"][Player.orange] = difficulty  # type: ignore
                        TRAINING_PARAMETERS["DIFFICULTY"][Player.white] = difficulty  # type: ignore
                        main_menu_soundtrack.stop()
                        main()
                        return

        pygame.display.update()


if __name__ == "__main__":
    import pygame
    from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION

    # Initialize Pygame
    pygame.init()

    # Load sounds
    main_menu_soundtrack = pygame.mixer.Sound("assets/main_menu_soundtrack.mp3")
    main_menu_soundtrack.set_volume(0.6)
    click_sound = pygame.mixer.Sound("assets/GUI_click.mp3")
    hover_sound = pygame.mixer.Sound("assets/GUI_hover.mp3")

    # Set up the window
    window_width = 800
    window_height = 800
    window_surface = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Jeu Du Moulin")

    # Load background image
    background_image = pygame.image.load("assets/menubackground.jpg")
    background_image = pygame.transform.scale(
        background_image, (window_width, window_height)
    )

    # Fonts
    font = pygame.font.SysFont(None, 36)  # type: ignore

    # Play main menu soundtrack
    main_menu_soundtrack.play(-1)

    # Start main menu
    main_menu()
