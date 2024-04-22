import pygame
from board import Board
from globals import CELL_SIZE, MARGIN, NODES
import numpy as np

RENDER = True

def generate_possible_moves(board: Board) -> list:
    generated_moves = []
    if board.phase == "placing":
        piece_to_place = [piece for piece in board.pieces[board.turn] if piece.first_move][0]
        for node in NODES:
            legality = piece_to_place.check_legal_move(board=board, new_node=node, just_check=True)
            if legality in ["move", "remove"]:
                generated_moves.append((piece_to_place, node, int(legality == "remove")))
    elif board.phase == "moving":
        for piece in board.pieces[board.turn]:
            for node in NODES:
                legality = piece.check_legal_move(board=board, new_node=node, just_check=True)
                if legality in ["move", "remove"]:
                    generated_moves.append((piece, node, int(legality == "remove")))
    elif board.phase == "capturing":
        other_turn = "orange" if board.turn == "white" else "white"
        for piece in board.pieces[other_turn]:
            if not piece.first_move:
                generated_moves.append((None, piece, 0))
    return generated_moves

def minimax(board, depth, maximizing_player, alpha, beta):
    if depth == 0 or board.game_over():
        return None, None, evaluate(board)

    if maximizing_player:
        max_eval = float("-inf")
        best_move = None
    
        for move in generate_possible_moves(board):
            board_copy = board.copy()
            make_move(board_copy, move)
            _, _, eval = minimax(board_copy, depth - 1, False, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        if best_move:
            return best_move[0], best_move[1], max_eval
        else: 
            return None, None, max_eval
    else:
        min_eval = float("inf")
        best_move = None
        for move in generate_possible_moves(board):
            board_copy = board.copy()
            make_move(board_copy, move)
            _, _, eval = minimax(board_copy, depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break

        if best_move:
            return best_move[0], best_move[1], min_eval
        else:
            return None, None, min_eval

def evaluate(board):
    # Your evaluation function goes here
    return 0

def make_move(board, move):
    moved_piece, move_node, move_value = move
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
        screen = pygame.display.set_mode((7 * CELL_SIZE + MARGIN * 5, 7 * CELL_SIZE + MARGIN))
    board = Board()
    board.latest_phase = board.phase

    while True:
        board.update_draggable_pieces()
        if RENDER:
            board.draw(screen, CELL_SIZE, MARGIN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

        if not board.game_over():
            possible_moves = generate_possible_moves(board)
            moved_piece, move_node, score = possible_moves[np.random.randint(len(possible_moves))]
            # moved_piece, move_node, _ = minimax(board, depth=3, maximizing_player=True, alpha=float("-inf"), beta=float("inf"))
            make_move(board, (moved_piece, move_node, 0))
        else:
            board = Board()
            board.latest_phase = board.phase
