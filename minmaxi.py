import pygame
from board import Board
from globals import CELL_SIZE, MARGIN, NODES
import numpy as np


def generate_possible_moves(board: Board) -> list:
    generated_moves = []
    if board.phase == "placing":
        piece_to_place = [piece for piece in board.pieces[board.turn] if piece.first_move][0]
        for node in NODES:
            if piece_to_place.check_legal_move(board=board, new_node=node, just_check=True) in [
                "move",
                "remove",
            ]:
                generated_moves.append((piece_to_place, node))
    elif board.phase == "moving":
        for piece in board.pieces[board.turn]:
            for node in NODES:
                if piece.check_legal_move(board=board, new_node=node, just_check=True) in [
                    "move",
                    "remove",
                ]:
                    generated_moves.append((piece, node))
    elif board.phase == "capturing":
        other_turn = "orange" if board.turn == "white" else "white"
        for piece in board.pieces[other_turn]:
            if not piece.first_move:
                generated_moves.append((None, piece))
    return generated_moves


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN))
    board = Board()
    latest_phase = board.phase

    while True:

        board.update_draggable_pieces()
        board.draw(screen, CELL_SIZE, MARGIN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if not board.game_over():
            generated_moves = generate_possible_moves(board)
            choosen_move = generated_moves[np.random.randint(0, len(generated_moves))]
            other_turn = "orange" if board.turn == "white" else "white"
            if choosen_move[0] is not None:
                move = choosen_move[0].move(choosen_move[1], board)
                if move == "remove":
                    latest_phase = board.phase
                    board.phase = "capturing"
                else:
                    board.turn = other_turn
            else:
                board.pieces[other_turn].remove(choosen_move[1])
                board.phase = latest_phase
                board.turn = other_turn
        else:
            board = Board()
            latest_phase = board.phase
