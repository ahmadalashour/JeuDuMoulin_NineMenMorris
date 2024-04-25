import pygame
from src.game_env.board import Board
from src.globals import CELL_SIZE, MARGIN

from src.globals import TRAINING_PARAMETERS
from src.agents.autonomous_agents import MinMaxAgent
from src.agents.human_agent import HumanAgent
import numpy as np


def main():
    """Main function to run the game."""
    if TRAINING_PARAMETERS["RENDER"]:
        screen = pygame.display.set_mode((7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN))
    board = Board(interactables=TRAINING_PARAMETERS["INTERACTABLES"])  # type: ignore
    max_n_samples = None
    if TRAINING_PARAMETERS["MAX_N_OPERATIONS"]:
        max_n_samples = int(np.exp(np.log(TRAINING_PARAMETERS["MAX_N_OPERATIONS"]) / TRAINING_PARAMETERS["DIFFICULTY"]))

    agents = {color: (MinMaxAgent(max_n_samples) if color not in board.interactables else HumanAgent()) for color in board.available_pieces.keys()}  # type: ignore

    board.latest_phase = board.phase

    print("Starting game : ")
    print("Difficulty : ", TRAINING_PARAMETERS["DIFFICULTY"])
    print("Interactables : ", TRAINING_PARAMETERS["INTERACTABLES"])
    print("Use sparsity : ", TRAINING_PARAMETERS["USE_SPARSITY"])
    print("Stupidity : ", TRAINING_PARAMETERS["STUPIDITY"])
    print("Max number of operations : ", TRAINING_PARAMETERS["MAX_N_OPERATIONS"])
    print("Max number of samples : ", max_n_samples)

    while True:
        board.update_draggable_pieces()
        if TRAINING_PARAMETERS["RENDER"]:
            board.draw(screen, CELL_SIZE, MARGIN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif not board.game_over:
                    if board.turn in board.interactables:  # type: ignore
                        if isinstance(agents[board.turn], HumanAgent):
                            agents[board.turn].move(event, board)  # type: ignore

        board.update_draggable_pieces()
        if TRAINING_PARAMETERS["RENDER"]:
            board.draw(screen, CELL_SIZE, MARGIN)

        if board.turn not in board.interactables:  # type: ignore
            if not board.game_over:
                if isinstance(agents[board.turn], MinMaxAgent):
                    best_move, _ = agents[board.turn].minimax(  # type: ignore
                        board,
                        depth=TRAINING_PARAMETERS["DIFFICULTY"],  # type: ignore
                        alpha=float("-inf"),
                        beta=float("inf"),
                    )

                    agents[board.turn].make_move(board, best_move)  # type: ignore


if __name__ == "__main__":
    main()
