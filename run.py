from src.game_env.board import Board
from src.globals import CELL_SIZE, MARGIN, MIN_DRAW_MOVES, Player, Phase

from src.globals import TRAINING_PARAMETERS
from src.agents.autonomous_agents import MinMaxAgent
from src.agents.human_agent import HumanAgent
import numpy as np
from threading import Thread

# Control variables to manage AI thinking state and sound playback.
ai_thinking = False
play_sound = False


def main():
    """ Main function to execute the game setup and loop. """

    global ai_thinking, play_sound

    # Set up the display if rendering is enabled in training parameters.
    if TRAINING_PARAMETERS["RENDER"]:
        import pygame

        screen = pygame.display.set_mode(
            (7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN)
        )
        move_sound = pygame.mixer.Sound("assets/move_sound.mp3")
        background_music = pygame.mixer.Sound("assets/background_music.mp3")
        background_music.set_volume(0.6)
        background_music.play(-1)
    else:
        screen = None

    # Initialize the game board with specific settings such as interactables and display properties.
    board = Board(
        interactables=TRAINING_PARAMETERS["INTERACTABLES"], # type: ignore
        screen=screen,
        margin=MARGIN,
        cell_size=CELL_SIZE,
    )  # type: ignore

    # Calculate the maximum number of operations allowed for each player based on difficulty settings.
    max_n_samples = {Player.orange: None, Player.white: None}
    if TRAINING_PARAMETERS["MAX_N_OPERATIONS"]:
        max_n_samples = {
            turn: int(
                np.exp(
                    np.log(TRAINING_PARAMETERS["MAX_N_OPERATIONS"]) # type: ignore
                    / TRAINING_PARAMETERS["DIFFICULTY"][turn] # type: ignore
                )  # type: ignore
                # type: ignore
            )
            for turn in [Player.orange, Player.white]
        }
    # Assign agents to each player based on their interactability, with MinMaxAgents for non-interactables.
    agents = {
        color: (
            MinMaxAgent(max_n_samples=TRAINING_PARAMETERS["MAX_N_OPERATIONS"]) # type: ignore
            if color not in board.interactables # type: ignore
            else HumanAgent()
        )
        for color in board.available_pieces.keys()
    }  # type: ignore

    board.latest_phase = board.phase

    print("Starting game : ")
    print("Difficulty : ", TRAINING_PARAMETERS["DIFFICULTY"])
    print("Interactables : ", TRAINING_PARAMETERS["INTERACTABLES"])
    print("Use sparsity : ", TRAINING_PARAMETERS["USE_SPARSITY"])
    print("Stupidity : ", TRAINING_PARAMETERS["STUPIDITY"])
    print("Max number of operations : ", TRAINING_PARAMETERS["MAX_N_OPERATIONS"])
    print("Max number of samples : ", max_n_samples)
    latest_moves = []
    can_add = False

    # Main game loop to handle game logic and rendering.
    while True:  
        board.update_draggable_pieces()
        if TRAINING_PARAMETERS["RENDER"]:
            board.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif not board.game_over:
                    if board.turn in board.interactables:  # type: ignore
                        if isinstance(agents[board.turn], HumanAgent):
                            move = agents[board.turn].move(event, board)  # type: ignore
                            if move is not None:
                                play_sound = True
                            if can_add:
                                if move is not None:
                                    latest_moves.append(move)

        board.update_draggable_pieces()
        if TRAINING_PARAMETERS["RENDER"]:
            board.draw()

        # Handle AI turn without letting the player interact while the AI is thinking.
        if board.turn not in board.interactables:  # type: ignore
            if not board.game_over:
                if isinstance(agents[board.turn], MinMaxAgent):
                    if not ai_thinking:
                        ai_thinking = True
                        Thread(
                            target=process_bot,
                            args=(board, agents, max_n_samples, latest_moves, can_add),
                        ).start()

        # Play movement sound if set to play.
        if TRAINING_PARAMETERS["RENDER"] and play_sound:
            move_sound.play()
            play_sound = False

        # Update game state rules and progress.
        if not can_add and board.phase == Phase.moving:
            can_add = True

        if (
            len(latest_moves) > MIN_DRAW_MOVES
            and not any(latest_moves[-MIN_DRAW_MOVES:])
            and board.phase == Phase.moving
        ):
            board.is_draw = True


def process_bot(
    board: Board,
    agents: dict[Player, MinMaxAgent],
    max_n_samples: dict,
    latest_moves: list,
    can_add: bool,
):
    """ Function to process AI moves using MinMax strategy in a separate process. and update the game state according."""
    global ai_thinking, play_sound
    
    # Calculate the best move for the current player using the MinMax algorithm with the given parameters.
    best_move, _ = agents[board.turn].minimax(  # type: ignore
        board,
        depth=TRAINING_PARAMETERS["DIFFICULTY"][board.turn],  # type: ignore
        alpha=float("-inf"),
        beta=float("inf"),
        fanning=max_n_samples[board.turn],
        multicore=TRAINING_PARAMETERS["N_PROCESS"], # type: ignore
    )

    # Make the best move on the board and render the move when rendering is enabled.
    move = agents[board.turn].make_move(
        board, best_move, render=TRAINING_PARAMETERS["RENDER"] # type: ignore
    )  # type: ignore

    if can_add:
        if move is not None:
            latest_moves.append(move)

    
    ai_thinking = False
    play_sound = True


if __name__ == "__main__":
    main()
