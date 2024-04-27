from src.game_env.board import Board
from src.globals import NODE_LOOKUP, TRAINING_PARAMETERS, EVALUATION_COEFFICIENTS
from typing import Optional, Any
import numpy as np
import dataclasses as dc
from copy import deepcopy
from src.game_env.node import Node


@dc.dataclass
class MinMaxAgent:
    """Class to represent a MinMax agent.

    Args:
        max_n_samples (int): The maximum number of samples to consider.
    """

    render_steps: int = 10

    @staticmethod
    def generate_possible_moves(board: Board) -> list[tuple[int | None, "Node", int]]:
        """Method to generate all possible moves for the agent.

        Args:
            board (Board): The board to generate moves for.

        Returns:
            list[tuple[int | None, Node, int]]: The list of possible moves.
        """
        generated_moves = []

        if board.phase == "placing":
            piece_to_place = [piece for piece in board.pieces[board.turn] if piece.first_move][0]
            for node in board.available_nodes:
                legality = piece_to_place.check_legal_move(board=board, new_node=node, just_check=True)
                if legality in ["move", "remove"]:
                    generated_moves.append((piece_to_place.id, node, legality))

        elif board.phase == "moving":
            for piece in board.pieces[board.turn]:
                for node in (
                    NODE_LOOKUP[piece.piece.node]
                    if len(board.pieces[board.turn]) > 3
                    else board.available_nodes
                ):
                    legality = piece.check_legal_move(board=board, new_node=node, just_check=True)
                    if legality in ["move", "remove"]:
                        generated_moves.append((piece.id, node, legality))

        elif board.phase == "capturing":
            other_turn = "orange" if board.turn == "white" else "white"
            for piece in board.pieces[other_turn]:
                if not piece.first_move:
                    if piece.removable(board):
                        generated_moves.append((None, piece.piece.node, "remove"))

        return generated_moves

    @staticmethod
    def evaluate(board: Board) -> float: # Reward function
        """Method to evaluate the board state.

        Args:
            board (Board): The board to evaluate.

        Returns:
            float: The evaluation of the board state.
        """
        sparsity_eval = 0
        if TRAINING_PARAMETERS["USE_SPARSITY"]:
            for player in ["orange", "white"]:
                for piece in board.pieces[player]:
                    if len(board.pieces[player]) > 3:
                        availables = [
                            node for node in NODE_LOOKUP[piece.piece.node] if node in board.available_nodes
                        ]
                        sparsity_eval += len(availables) if player == "orange" else -len(availables)

        sparsity_eval = sparsity_eval
        n_pieces_eval = len(board.pieces["orange"]) - len(board.pieces["white"])
        white_mills = [mill for mill in board.current_mills if mill[0][0] in board.piece_mapping.keys() and board.piece_mapping[mill[0][0]].piece.player == "white"]
        orange_mills = [mill for mill in board.current_mills if mill[0][0] in board.piece_mapping.keys() and board.piece_mapping[mill[0][0]].piece.player == "orange"]
        n_mills_eval = len(orange_mills) - len(white_mills)
        entropy = np.random.normal(0, TRAINING_PARAMETERS["STUPIDITY"])  # type: ignore

        return (
            EVALUATION_COEFFICIENTS["sparsity"] * sparsity_eval
            + EVALUATION_COEFFICIENTS["n_pieces"] * n_pieces_eval
            + EVALUATION_COEFFICIENTS["n_mills"] * n_mills_eval
            + EVALUATION_COEFFICIENTS["entropy"] * entropy
        )

    def make_move(
        self, board: Board, move: tuple[int | None, "Node", int], render: bool = True
    ) -> Optional[bool]:
        """Method to make a move on the board.

        Args:
            board (Board): The board to make the move on.
            move (tuple[int | None, Node, int]): The move to make.
        """

        if not move:
            board.winner = "orange" if board.turn == "white" else "white"
            return

        moved_piece_id, move_node, _ = move
        moved_piece = (
            [piece for piece in board.pieces[board.turn] if piece.id == moved_piece_id][0]
            if moved_piece_id is not None
            else None
        )
        other_turn = "orange" if board.turn == "white" else "white"
        if moved_piece is not None:
            backup_start_node = deepcopy(moved_piece.piece.node)
            if render:
                start_node = deepcopy(moved_piece.piece.node)
                end_node = deepcopy(move_node)
                vector = end_node - start_node
                current_node = deepcopy(start_node)

                # Simulate move
                for i in range(self.render_steps):
                    current_node = Node.from_coords(
                        start_node.x + vector[0] / self.render_steps * (i + 1),
                        start_node.y + vector[1] / self.render_steps * (i + 1),
                    )
                    moved_piece.piece.node = current_node
                    board.draw()

            moved_piece.piece.node = backup_start_node
            move_result = moved_piece.move(move_node, board)
            if move_result == "remove":
                board.phase = "capturing"
            else:
                board.turn = other_turn
        else:
            captured_piece = [piece for piece in board.pieces[other_turn] if piece.piece.node == move_node][0]
            captured_piece.update_mills(board)
            board.pieces[other_turn].remove(captured_piece)
            board.available_nodes.append(move_node)
            board.phase = board.latest_phase
            board.turn = other_turn
            return True

        return False

    def minimax(self, board: Board, depth: int, alpha: float, beta: float, fanning: Optional[int] = None) -> tuple[Any, float]:
        """Method to perform the minimax algorithm.

        Args:
            board (Board): The board to perform the minimax on.
            depth (int): The depth to perform the minimax to.
            alpha (float): The alpha value.
            beta (float): The beta value.
            fanning (Optional[int], optional): The number of samples to consider. Defaults to None.

        Returns:
            tuple[int | None, float]: The best move and its value.
        """

        board.update_draggable_pieces()
        if depth == 0 or board.game_over:
            return None, self.evaluate(board)

        maximizing_player = board.turn == "orange"

        possible_moves = self.generate_possible_moves(board)
        next_n_fanning = None
        if fanning and fanning > 0:
            n_samples = min(
                len(possible_moves),
                fanning,
            )
            
            if depth > 1:
                next_n_fanning =  int(np.exp(np.log(TRAINING_PARAMETERS["MAX_N_OPERATIONS"] / n_samples) / (depth - 1)))

            samples_idx = np.random.choice(len(possible_moves), n_samples, replace=False)
            possible_moves = [possible_moves[i] for i in samples_idx]

        if len(possible_moves) == 0:
            return None, float("-inf") if maximizing_player else float("inf")

        if maximizing_player:
            max_value = float("-inf")
            best_move = None
            for move in possible_moves:
                board_copy = board.ai_copy()
                self.make_move(board_copy, move, render=False)
                _, value = self.minimax(board_copy, depth - 1, alpha, beta, next_n_fanning)
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
                self.make_move(board_copy, move, render=False)
                _, value = self.minimax(board_copy, depth - 1, alpha, beta, next_n_fanning)
                if value < min_value or best_move is None:
                    min_value = value
                    best_move = move
                beta = min(beta, min_value)
                if beta <= alpha:
                    break
            return best_move, min_value
