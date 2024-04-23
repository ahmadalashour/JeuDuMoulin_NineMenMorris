import pygame
from src.env.board import Board
from src.globals import CELL_SIZE, MARGIN

from src.globals import TRAINING_PARAMETERS
from src.autonomous_agent.agent import minimax, make_move


def main():
    if TRAINING_PARAMETERS["RENDER"]:
        screen = pygame.display.set_mode((7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN))
    board = Board(interactables=TRAINING_PARAMETERS["INTERACTABLES"])  # type: ignore
    board.latest_phase = board.phase
    remove_piece = False

    print("Starting game : ")
    print("Difficulty : ", TRAINING_PARAMETERS["DIFFICULTY"])
    print("Interactables : ", TRAINING_PARAMETERS["INTERACTABLES"])
    print("Use sparsity : ", TRAINING_PARAMETERS["USE_SPARSITY"])
    print("Stupidity : ", TRAINING_PARAMETERS["STUPIDITY"])
    print("Max number of operations : ", TRAINING_PARAMETERS["MAX_N_OPERATIONS"])

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
                        if not remove_piece:
                            # Handle events for draggable pieces
                            for piece in board.pieces[board.turn]:
                                legality = piece.handle_event(event, board)
                                if legality == "remove":
                                    remove_piece = True
                                    board.latest_phase = board.phase
                                    board.phase = "capturing"
                                    break
                                if legality == "move":
                                    board.turn = "orange" if board.turn == "white" else "white"
                                    break
                        else:
                            other_turn = "orange" if board.turn == "white" else "white"
                            removed = False
                            for piece in board.pieces[other_turn]:
                                if piece.handle_remove_event(event, board):
                                    removed = True
                                    board.pieces[other_turn].remove(piece)
                                    board.available_nodes.append(piece.piece.node)
                                    break
                            if removed:
                                remove_piece = False
                                board.turn = "orange" if board.turn == "white" else "white"
                                board.phase = board.latest_phase

        board.update_draggable_pieces()
        if TRAINING_PARAMETERS["RENDER"]:
            board.draw(screen, CELL_SIZE, MARGIN)

        if board.turn not in board.interactables:  # type: ignore
            if not board.game_over:
                best_move, _ = minimax(
                    board,
                    depth=TRAINING_PARAMETERS["DIFFICULTY"],
                    alpha=float("-inf"),
                    beta=float("inf"),
                )

                make_move(board, best_move)  # type: ignore


if __name__ == "__main__":
    main()
