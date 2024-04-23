from src.env.board import Board
from src.globals import NODE_LOOKUP
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from src.env.node import Node

from src.globals import TRAINING_PARAMETERS


def generate_possible_moves(board: Board) -> list[tuple[int | None, "Node", int]]:
    generated_moves = []

    if board.phase == "placing":
        piece_to_place = [piece for piece in board.pieces[board.turn] if piece.first_move][0]
        for node in board.available_nodes:
            legality = piece_to_place.check_legal_move(board=board, new_node=node, just_check=True)
            if legality in ["move", "remove"]:
                generated_moves.append((piece_to_place.id, node, legality))

    elif board.phase == "moving":
        for piece in board.pieces[board.turn]:
            for node in NODE_LOOKUP[piece.piece.node] if len(board.pieces[board.turn]) > 3 else board.available_nodes:
                legality = piece.check_legal_move(board=board, new_node=node, just_check=True)
                if legality in ["move", "remove"]:
                    generated_moves.append((piece.id, node, legality))

    elif board.phase == "capturing":
        other_turn = "orange" if board.turn == "white" else "white"
        for piece in board.pieces[other_turn]:
            if not piece.first_move:
                generated_moves.append((None, piece.piece.node, "remove"))

    return generated_moves


def minimax(board: Board, depth, alpha, beta):
    board.update_draggable_pieces()
    if depth == 0 or board.game_over:
        return None, evaluate(board)

    maximizing_player = board.turn == "orange"

    possible_moves = generate_possible_moves(board)
    if TRAINING_PARAMETERS["MAX_N_OPERATIONS"]:
        n_samples = min(
            len(possible_moves),
            int(np.exp(np.log(TRAINING_PARAMETERS["MAX_N_OPERATIONS"]) / TRAINING_PARAMETERS["DIFFICULTY"])),
        )
        samples_idx = np.random.choice(len(possible_moves), n_samples, replace=False)
    possible_moves = [possible_moves[i] for i in samples_idx]
    if len(possible_moves) == 0:
        return None, float("-inf") if maximizing_player else float("inf")

    if maximizing_player:
        max_value = float("-inf")
        best_move = None
        for move in possible_moves:
            board_copy = board.ai_copy()
            make_move(board_copy, move)
            _, value = minimax(board_copy, depth - 1, alpha, beta)
            if value > max_value or best_move is None:
                max_value = value
                best_move = move
            alpha = max(alpha, max_value)
            if beta <= alpha:
                break
        return best_move, max_value
    else:
        min_value = float("inf")
        best_move = None

        for move in possible_moves:
            board_copy = board.ai_copy()
            make_move(board_copy, move)
            _, value = minimax(board_copy, depth - 1, alpha, beta)
            if value < min_value or best_move is None:
                min_value = value
                best_move = move
            beta = min(beta, min_value)
            if beta <= alpha:
                break
        return best_move, min_value


def evaluate(board: Board):  # Reward function
    sparsity_eval = 0
    if TRAINING_PARAMETERS["USE_SPARSITY"]:
        for player in ["orange", "white"]:
            for piece in board.pieces[player]:
                if len(board.pieces[player]) > 3:
                    availables = [node for node in NODE_LOOKUP[piece.piece.node] if node in board.available_nodes]
                    sparsity_eval += len(availables) if player == "orange" else -len(availables)

    sparsity_eval = sparsity_eval / 3
    n_pieces_eval = len(board.pieces["orange"]) - len(board.pieces["white"])

    entropy = np.random.normal(0, TRAINING_PARAMETERS["STUPIDITY"])  # type: ignore

    return sparsity_eval + n_pieces_eval + entropy


def make_move(board: Board, move: tuple[int | None, "Node", int]):
    if not move:
        board.winner = "orange" if board.turn == "white" else "white"
        return

    moved_piece_id, move_node, _ = move
    moved_piece = [piece for piece in board.pieces[board.turn] if piece.id == moved_piece_id][0] if moved_piece_id is not None else None
    other_turn = "orange" if board.turn == "white" else "white"
    if moved_piece is not None:
        move_result = moved_piece.move(move_node, board)
        if move_result == "remove":
            board.phase = "capturing"
        else:
            board.turn = other_turn
    else:
        captured_piece = [piece for piece in board.pieces[other_turn] if piece.piece.node == move_node][0]

        board.pieces[other_turn].remove(captured_piece)
        board.available_nodes.append(move_node)
        board.phase = board.latest_phase
        board.turn = other_turn
