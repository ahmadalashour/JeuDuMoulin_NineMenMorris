import pygame
from board import Board
from globals import CELL_SIZE, MARGIN, NODES
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION


def generate_possible_moves(board: Board) -> list:
    generated_moves = []
    if board.phase == "placing":
        piece_to_place = [
            piece for piece in board.pieces[board.turn] if piece.first_move
        ][0]
        for node in NODES:
            piece_to_place.starting_node = piece_to_place.piece.node
            if piece_to_place.check_legal_move(board=board, new_node=node) in [
                "move",
                "remove",
            ]:
                generated_moves.append((piece_to_place, node))
    elif board.phase == "moving":
        for piece in board.pieces[board.turn]:
            for node in NODES:
                if piece.check_legal_move(board=board, new_node=node) in [
                    "move",
                    "remove",
                ]:
                    generated_moves.append((piece, node))
    elif board.phase == "capturing":
        other_turn = "orange" if board.turn == "white" else "white"
        for piece in board.pieces[other_turn]:
            generated_moves.append((None, piece))
    return generated_moves
