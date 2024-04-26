import pygame
from src.game_env.board import Board
from src.globals import CELL_SIZE, MARGIN, MIN_DRAW_MOVES

from src.globals import TRAINING_PARAMETERS, EVALUATION_COEFFICIENTS, N_REPITITIONS
from src.agents.autonomous_agents import MinMaxAgent
from src.agents.human_agent import HumanAgent
import numpy as np
import json
from pathlib import Path
import datetime


def main():
    """Main function to run the game."""
    pygame.init()
    screen = None

    if TRAINING_PARAMETERS["RENDER"]:
        screen = pygame.display.set_mode((7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN))
        move_sound = pygame.mixer.Sound("assets/move_sound.mp3")
        background_music = pygame.mixer.Sound("assets/background_music.mp3")
        background_music.set_volume(0.6)
        background_music.play(-1)

    # Evaluation Results
    evaluation_folder = Path(
        "./evaluation_results/{}".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    )
    evaluation_folder.mkdir(exist_ok=True, parents=True)

    # Loop over all possible combinations of difficulties
    for difficulty_1 in range(1, 6):
        for difficulty_2 in range(1, 6):
            for i in range(N_REPITITIONS):
                start_time = datetime.datetime.now()
                TRAINING_PARAMETERS["DIFFICULTY"] = {"orange": difficulty_1, "white": difficulty_2}
                board = Board(interactables=TRAINING_PARAMETERS["INTERACTABLES"], screen=screen, margin=MARGIN, cell_size=CELL_SIZE)  # type: ignore
                board.latest_phase = board.phase
                print(board.winner)
                dummy_agent = MinMaxAgent()

                evaluations = {"orange": [], "white": []}
                max_n_samples = {"orange": None, "white": None}
                if TRAINING_PARAMETERS["MAX_N_OPERATIONS"]:
                    max_n_samples = {
                        turn: int(
                            np.exp(np.log(TRAINING_PARAMETERS["MAX_N_OPERATIONS"]) / TRAINING_PARAMETERS["DIFFICULTY"][turn])  # type: ignore
                            # type: ignore
                        )
                        for turn in ["orange", "white"]
                    }

                agents = {color: (MinMaxAgent(max_n_samples[color]) if color not in board.interactables else HumanAgent()) for color in board.available_pieces.keys()}  # type: ignore

                print("Starting game : ")
                print("Difficulty : ", TRAINING_PARAMETERS["DIFFICULTY"])
                print("Interactables : ", TRAINING_PARAMETERS["INTERACTABLES"])
                print("Use sparsity : ", TRAINING_PARAMETERS["USE_SPARSITY"])
                print("Stupidity : ", TRAINING_PARAMETERS["STUPIDITY"])
                print("Max number of operations : ", TRAINING_PARAMETERS["MAX_N_OPERATIONS"])
                print("Max number of samples : ", max_n_samples)
                latest_moves = []
                can_add = False

                while True:  # Main game loop
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
                                            evaluations[board.turn].append(dummy_agent.evaluate(board))
                                            print(
                                                "Turn : ",
                                                board.turn,
                                                "Evaluation : ",
                                                evaluations[board.turn][-1],
                                            )

                                            if TRAINING_PARAMETERS["RENDER"]:
                                                move_sound.play()
                                        if can_add:

                                            if move is not None:
                                                latest_moves.append(move)

                    board.update_draggable_pieces()
                    if TRAINING_PARAMETERS["RENDER"]:
                        board.draw()

                    if board.turn not in board.interactables:  # type: ignore
                        if not board.game_over:
                            if isinstance(agents[board.turn], MinMaxAgent):
                                best_move, _ = agents[board.turn].minimax(  # type: ignore
                                    board,
                                    depth=TRAINING_PARAMETERS["DIFFICULTY"][board.turn],  # type: ignore
                                    alpha=float("-inf"),
                                    beta=float("inf"),
                                )
                                move = agents[board.turn].make_move(board, best_move, render=TRAINING_PARAMETERS["RENDER"])  # type: ignore
                                if TRAINING_PARAMETERS["RENDER"]:
                                    move_sound.play()
                                evaluations[board.turn].append(dummy_agent.evaluate(board))
                                print("Turn : ", board.turn, "Evaluation : ", evaluations[board.turn][-1])
                                if can_add:
                                    if move is not None:
                                        latest_moves.append(move)

                    if not can_add and board.phase == "moving":
                        can_add = True

                    if (
                        len(latest_moves) > MIN_DRAW_MOVES
                        and not any(latest_moves[-MIN_DRAW_MOVES:])
                        and board.phase == "moving"
                    ):
                        board.is_draw = True

                    if board.game_over:
                        print("Game over")
                        print("N Pieces ", board.pieces)
                        end_time = datetime.datetime.now()
                        with open(evaluation_folder / "evaluation_results.txt", "a") as f:
                            f.write("Game : {}\n".format(i))
                            f.write("Start Time : {} , End Time : {}\n".format(start_time, end_time))
                            f.write(
                                "Difficulties : Orange : {} White : {}\n".format(difficulty_1, difficulty_2)
                            )
                            f.write("Training Parameters : \n")
                            f.write("Use Sparsity : {}\n".format(TRAINING_PARAMETERS["USE_SPARSITY"]))
                            f.write("Stupidity : {}\n".format(TRAINING_PARAMETERS["STUPIDITY"]))
                            f.write(
                                "Max Number of Operations : {}\n".format(
                                    TRAINING_PARAMETERS["MAX_N_OPERATIONS"]
                                )
                            )
                            f.write("Max Number of Samples : {}\n".format(max_n_samples))
                            f.write("Evaluation Coefficients : \n")
                            f.write(json.dumps(EVALUATION_COEFFICIENTS))
                            f.write("\n")
                            f.write("Winner : {}\n".format(board.winner))
                            f.write(str(evaluations))
                            f.write("\n\n\n")
                        del board
                        break


if __name__ == "__main__":
    main()