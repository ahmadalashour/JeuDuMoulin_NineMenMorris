from src.game_env.board import Board
from src.globals import CELL_SIZE, MARGIN, MIN_DRAW_MOVES, N_REPITITIONS, EVALUATION_COEFFICIENTS

from src.globals import TRAINING_PARAMETERS
from src.agents.autonomous_agents import MinMaxAgent
from src.agents.human_agent import HumanAgent
import numpy as np
from threading import Thread
from pathlib import Path
import datetime
import json 

ai_thinking = False
play_sound = False
evaluations = {"orange": [], "white": []}


def main():
    """Main function to run the game."""

    global ai_thinking, play_sound, evaluations

    if TRAINING_PARAMETERS["RENDER"]:
        import pygame
        pygame.init()

        screen = pygame.display.set_mode((7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN))
        move_sound = pygame.mixer.Sound("assets/move_sound.mp3")
        background_music = pygame.mixer.Sound("assets/background_music.mp3")
        background_music.set_volume(0.6)
        background_music.play(-1)
    else:
        screen = None

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

                board = Board(interactables=TRAINING_PARAMETERS["INTERACTABLES"], screen=screen, margin=MARGIN, cell_size=CELL_SIZE)  # type: ignore
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

                agents = {color: (MinMaxAgent(max_n_samples=TRAINING_PARAMETERS["MAX_N_OPERATIONS"]) if color not in board.interactables else HumanAgent()) for color in board.available_pieces.keys()}  # type: ignore

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
                                            play_sound = True
                                            evaluations[board.turn].append(dummy_agent.evaluate(board))
                                            print(
                                                "Turn : ",
                                                board.turn,
                                                "Evaluation : ",
                                                evaluations[board.turn][-1],
                                            )

                                        if can_add:

                                            if move is not None:
                                                latest_moves.append(move)

                    board.update_draggable_pieces()
                    if TRAINING_PARAMETERS["RENDER"]:
                        board.draw()

                    if board.turn not in board.interactables:  # type: ignore
                        if not board.game_over:
                            if isinstance(agents[board.turn], MinMaxAgent):
                                if not ai_thinking:
                                    ai_thinking = True
                                    Thread(
                                        target=process_bot, args=(board, agents, max_n_samples, latest_moves, can_add, dummy_agent, difficulty_1 if board.turn == "orange" else difficulty_2)
                                    ).start()

                    if TRAINING_PARAMETERS["RENDER"] and play_sound:
                        move_sound.play()
                        play_sound = False

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

def process_bot(board: Board, agents: dict["str", MinMaxAgent | HumanAgent], max_n_samples: dict, latest_moves: list, can_add: bool, dummy_agent: MinMaxAgent, difficulty: int):
    global ai_thinking, play_sound, evaluations
    best_move, _ = agents[board.turn].minimax(  # type: ignore
        board,
        depth=difficulty,  # type: ignore
        alpha=float("-inf"),
        beta=float("inf"),
        fanning=max_n_samples[board.turn],
        multicore=TRAINING_PARAMETERS["N_PROCESS"],
    )
    move = agents[board.turn].make_move(board, best_move, render=TRAINING_PARAMETERS["RENDER"])  # type: ignore
    evaluations[board.turn].append(dummy_agent.evaluate(board))
    print("Turn : ", board.turn, "Evaluation : ", evaluations[board.turn][-1])

    if can_add:
        if move is not None:
            latest_moves.append(move)

    ai_thinking = False
    play_sound = True


if __name__ == "__main__":
    main()
