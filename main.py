import pygame
from board import Board
from globals import CELL_SIZE, MARGIN, NODES
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from node import Node

RENDER = True # Choose to view the gameplay
INTERACTABLES : list[Literal["orange", "white"]] = ["orange"]
DIFFICULTY = 3


def generate_possible_moves(board: Board) -> list[tuple[int | None, "Node", int]]:
    generated_moves = []

    if board.phase == "placing":
        piece_to_place = [
            piece for piece in board.pieces[board.turn] if piece.first_move
        ][0]
        for node in NODES:
            legality = piece_to_place.check_legal_move(
                board=board, new_node=node, just_check=True
            )
            if legality in ["move", "remove"]:
                generated_moves.append((piece_to_place.id, node, legality))

    elif board.phase == "moving":
        for piece in board.pieces[board.turn]:
            for node in NODES:
                legality = piece.check_legal_move(
                    board=board, new_node=node, just_check=True
                )
                if legality in ["move", "remove"]:
                    generated_moves.append((piece.id, node, legality))

    elif board.phase == "capturing":
        other_turn = "orange" if board.turn == "white" else "white"
        for piece in board.pieces[other_turn]:
            if not piece.first_move:
                generated_moves.append((None, piece, "capturing"))

    return generated_moves


def minimax(board: Board, depth, maximizing_player, alpha, beta):
    board.update_draggable_pieces()
    if depth == 0 or board.game_over():
        return None, evaluate(board)

    if maximizing_player:
        max_value = float("-inf")
        best_move = None
        for move in generate_possible_moves(board):
            board_copy = board.ai_copy()
            make_move(board_copy, move)
            _, value = minimax(board_copy, depth - 1, False, alpha, beta)
            if value > max_value:
                max_value = value
                best_move = move
            alpha = max(alpha, max_value)
            if beta <= alpha:
                break
        return best_move, max_value
    else:
        min_value = float("inf")
        best_move = None
        for move in generate_possible_moves(board):
            board_copy = board.ai_copy()
            make_move(board_copy, move)
            _, value = minimax(board_copy, depth - 1, True, alpha, beta)
            if value < min_value:
                min_value = value
                best_move = move
            beta = min(beta, min_value)
            if beta <= alpha:
                break
        return best_move, min_value


def evaluate(board):
    return len(board.pieces[board.turn]) - len(
        board.pieces["orange" if board.turn == "white" else "white"]
    )


def make_move(board, move):
    moved_piece_id, move_node, _ = move
    moved_piece = (
        [piece for piece in board.pieces[board.turn] if piece.id == moved_piece_id][0]
        if moved_piece_id is not None
        else None
    )
    other_turn = "orange" if board.turn == "white" else "white"
    if moved_piece is not None:
        move_result = moved_piece.move(move_node, board)
        if move_result == "remove":
            board.phase = "capturing"
        else:
            board.turn = other_turn
    else:
        board.pieces[other_turn].remove(move_node)
        board.phase = board.latest_phase
        board.turn = other_turn


if __name__ == "__main__":
    if RENDER:
        pygame.init()
        screen = pygame.display.set_mode(
            (7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN)
        )
    board = Board(interactables=INTERACTABLES)
    board.latest_phase = board.phase
    i = 0
    remove_piece = False
    played = False
    while True:
        board.update_draggable_pieces()
        if RENDER:
            board.draw(screen, CELL_SIZE, MARGIN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif not board.game_over():
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
                                    board.turn = (
                                        "orange" if board.turn == "white" else "white"
                                    )
                                    break
                        else:
                            other_turn = "orange" if board.turn == "white" else "white"
                            removed = False
                            for piece in board.pieces[other_turn]:
                                if piece.handle_remove_event(event, board):
                                    removed = True
                                    board.pieces[other_turn].remove(piece)
                                    break
                            if removed:
                                remove_piece = False
                                board.turn = (
                                    "orange" if board.turn == "white" else "white"
                                )
                                board.phase = board.latest_phase

                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        board = Board(interactables=INTERACTABLES)
                        board.latest_phase = board.phase
        board.update_draggable_pieces()
        if RENDER:
            board.draw(screen, CELL_SIZE, MARGIN)

        if board.turn not in board.interactables:  # type: ignore
            if not board.game_over():
                print("Thinking ...")
                best_move, value = minimax(
                    board,
                    depth=DIFFICULTY,
                    maximizing_player=True,
                    alpha=float("-inf"),
                    beta=float("inf"),
                )

                make_move(board, best_move)
