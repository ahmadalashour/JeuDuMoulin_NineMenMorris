from src.game_env.board import Board
from src.globals import (
    NODE_LOOKUP,
    TRAINING_PARAMETERS,
    EVALUATION_COEFFICIENTS,
    Player,
    Phase,
    Action,
)
from typing import Optional, Any
import numpy as np
import dataclasses as dc
from copy import deepcopy
from src.game_env.node import Node
from multiprocessing import Pool, cpu_count

import signal
import time


@dc.dataclass
class MinMaxAgent:
    """Class to represent a MinMax agent.

    Args:
        max_n_samples (int): The maximum number of samples to consider.
    """

    max_n_samples: int = 10000
    render_steps: int = 30

    @staticmethod
    def init_worker():
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    @staticmethod
    def generate_possible_moves(board: Board) -> list[tuple[int | None, "Node", int]]:
        """Method to generate all possible moves for the agent.

        Args:
            board (Board): The board to generate moves for.

        Returns:
            list[tuple[int | None, Node, int]]: The list of possible moves.
        """
        generated_moves = []

        if board.phase == Phase.placing:
            piece_to_place = [
                piece for piece in board.pieces[board.turn] if piece.first_move
            ][0]

            if board.available_nodes is not None:
                for node in board.available_nodes:
                    legality = piece_to_place.check_legal_move(
                        board=board, new_node=node, just_check=True
                    )
                    if legality in [Action.move, Action.remove]:
                        generated_moves.append((piece_to_place.id, node, legality))

        elif board.phase == Phase.moving:
            for piece in board.pieces[board.turn]:
                for node in (
                    NODE_LOOKUP[piece.piece.node]
                    if len(board.pieces[board.turn]) > 3
                    else board.available_nodes
                ):  # type: ignore
                    legality = piece.check_legal_move(
                        board=board, new_node=node, just_check=True
                    )
                    if legality in [Action.move, Action.remove]:
                        generated_moves.append((piece.id, node, legality))

        elif board.phase == Phase.capturing:
            other_turn = Player.orange if board.turn == Player.white else Player.white
            for piece in board.pieces[other_turn]:
                if not piece.first_move:
                    if piece.removable(board):
                        generated_moves.append((None, piece.piece.node, Action.remove))

        return generated_moves

    @staticmethod
    def evaluate(
        board: Board,
        evaluation_coefficients: dict[str, dict[str, float]] = EVALUATION_COEFFICIENTS,
        training_parameters: dict[str, Any] = TRAINING_PARAMETERS,
        node_lookup: dict["Node", list["Node"]] = NODE_LOOKUP,
    ) -> float:
        """Method to evaluate the board state.

        Args:
            board (Board): The board to evaluate
            evaluation_coefficients (dict[str, dict[str, float]], optional): The evaluation coefficients. Defaults to EVALUATION_COEFFICIENTS.
            training_parameters (dict[str, Any], optional): The training parameters. Defaults to TRAINING_PARAMETERS.
            node_lookup (dict[Node, list[Node]], optional): The node lookup. Defaults to NODE_LOOKUP.

        Returns:
            float: The evaluation of the board state.
        """

        game_phase = "placing"
        if board.started_moving:
            game_phase = "moving"
            if len(board.pieces[board.turn]) <= 3:
                game_phase = "flying"

        coefs = evaluation_coefficients[game_phase]

        sparsity_eval = 0
        if training_parameters["USE_SPARSITY"]:
            for player in [Player.orange, Player.white]:
                for piece in board.pieces[player]:
                    if len(board.pieces[player]) > 3:
                        if board.available_nodes is None:
                            continue
                        availables = [
                            node
                            for node in node_lookup[piece.piece.node]
                            if node in board.available_nodes
                        ]
                        sparsity_eval += (
                            len(availables)
                            if player == Player.orange
                            else -len(availables)
                        )

        sparsity_eval = sparsity_eval / 24.0  # in the range [-1, 1]
        n_pieces_eval = (
            len(board.pieces[Player.orange]) - len(board.pieces[Player.white])
        ) / 9.0  # in the range [-1, 1]

        if board.started_moving:
            if len(board.pieces[Player.orange]) <= 2:
                return -np.inf
            if len(board.pieces[Player.white]) <= 2:
                return np.inf

        if board.current_mills is None or board.piece_mapping is None:
            return 0
        white_mills = [
            mill
            for mill in board.current_mills
            if board.piece_mapping[mill[0][0]].piece.player == player.white  # type: ignore
        ]
        orange_mills = [
            mill
            for mill in board.current_mills
            if board.piece_mapping[mill[0][0]].piece.player == player.orange  # type: ignore
        ]
        n_mills_eval = (
            len(orange_mills) - len(white_mills)
        ) / 4.0  # in the range [-1, 1]

        entropy = 0
        if training_parameters["STUPIDITY"] > 0:
            entropy = (
                np.random.normal(0, training_parameters["STUPIDITY"])
                / training_parameters["STUPIDITY"]
            )  # in the range [-1, 1]

        return (
            coefs["sparsity"] * sparsity_eval
            + coefs["n_pieces"] * n_pieces_eval
            + coefs["n_mills"] * n_mills_eval
            + coefs["entropy"] * entropy
        )

    def make_move(
        self, board: Board, move: tuple[int | None, "Node", int], render: bool = True
    ) -> Optional[bool]:
        """Method to make a move on the board.

        Args:
            board (Board): The board to make the move on.
            move (tuple[int | None, Node, int]): The move to make.
            render (bool, optional): Whether to render the move. Defaults to True.

        Returns:
            Optional[bool]: Whether a piece was removed.
        """

        if not move:
            board.winner = Player.orange if board.turn == Player.white else Player.white
            return

        moved_piece_id, move_node, _ = move
        moved_piece = (
            [piece for piece in board.pieces[board.turn] if piece.id == moved_piece_id][
                0
            ]
            if moved_piece_id is not None
            else None
        )
        other_turn = Player.orange if board.turn == Player.white else Player.white
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
                    time.sleep(0.02)
            moved_piece.piece.node = backup_start_node
            move_result = moved_piece.move(move_node, board)

            if move_result == Action.remove:
                board.phase = Phase.capturing
            else:
                board.turn = other_turn
        else:
            captured_piece = [
                piece
                for piece in board.pieces[other_turn]
                if piece.piece.node == move_node
            ][0]

            if board.available_nodes is None:
                return False
            captured_piece.remove_mill_containing_piece(board)
            board.pieces[other_turn].remove(captured_piece)
            board.available_nodes.append(move_node)
            board.phase = board.latest_phase
            board.turn = other_turn
            return True

        return False

    def minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        fanning: Optional[int] = None,
        cumulative_n_samples: int = 1,
        multicore: int = 1,
        first_call: bool = True,
        evaluation_coefficients: dict[str, dict[str, float]] = EVALUATION_COEFFICIENTS,
        training_parameters: dict[str, Any] = TRAINING_PARAMETERS,
        node_lookup: dict["Node", list["Node"]] = NODE_LOOKUP,
    ) -> tuple[Any, float]:
        """Method to perform the minimax algorithm.

        Args:
            board (Board): The board to perform the minimax on.
            depth (int): The depth to perform the minimax to.
            alpha (float): The alpha value.
            beta (float): The beta value.
            fanning (Optional[int], optional): The number of samples to consider. Defaults to None.
            cumulative_n_samples (int, optional): The cumulative number of samples. Defaults to 1.
            multicore (int, optional): The number of cores to use. Defaults to 1.
            first_call (bool, optional): Whether it is the first call. Defaults to True.
            evaluation_coefficients (dict[str, dict[str, float]], optional): The evaluation coefficients. Defaults to EVALUATION_COEFFICIENTS.
            training_parameters (dict[str, Any], optional): The training parameters. Defaults to TRAINING_PARAMETERS.
            node_lookup (dict[Node, list[Node]], optional): The node lookup. Defaults to NODE_LOOKUP.

        Returns:
            tuple[int | None, float]: The best move and its value.
        """

        board.update_draggable_pieces()
        if depth == 0 or board.game_over:
            return None, self.evaluate(
                board, evaluation_coefficients, training_parameters, node_lookup
            )

        maximizing_player = board.turn == Player.orange

        possible_moves = self.generate_possible_moves(board)
        next_n_fanning = None
        if (
            fanning
            and fanning > 0
            and (
                len(board.pieces[Player.orange]) <= 3
                or len(board.pieces[Player.white]) <= 3
            )
        ):
            fanning = int(depth * fanning)

            if first_call:
                fanning = len(possible_moves)

            n_samples = min(
                len(possible_moves),
                fanning,
            )

            cumulative_n_samples *= n_samples

            if depth > 1 and n_samples > 0:
                next_n_fanning = int(
                    np.exp(
                        np.log(self.max_n_samples / cumulative_n_samples) / (depth - 1)
                    )
                )

            samples_idx = np.random.choice(
                len(possible_moves), n_samples, replace=False
            )
            possible_moves = [possible_moves[i] for i in samples_idx]

        if len(possible_moves) == 0:
            return None, float("-inf") if maximizing_player else float("inf")

        extreme_value = float("-inf") if maximizing_player else float("inf")
        best_move = None
        if multicore == 1 or depth < 4 or len(possible_moves) / cpu_count() < 0.5:
            for move in possible_moves:
                best_move, extreme_value, alpha, beta = self._check_single_move(
                    board=board,
                    move=move,
                    depth=depth,
                    extreme_value=extreme_value,
                    alpha=alpha,
                    beta=beta,
                    maximizing_player=maximizing_player,
                    next_n_fanning=next_n_fanning,
                    cumulative_n_samples=cumulative_n_samples,
                    best_move=best_move,
                    evaluation_coefficients=evaluation_coefficients,
                    training_parameters=training_parameters,
                    node_lookup=node_lookup,
                )
                if beta <= alpha:
                    break
        else:
            with Pool(
                cpu_count() if multicore == -1 else multicore,
                initializer=self.init_worker,
            ) as pool:
                processes = [
                    pool.apply_async(
                        self._check_single_move,
                        (
                            board.ai_copy(),
                            move,
                            depth,
                            extreme_value,
                            alpha,
                            beta,
                            maximizing_player,
                            next_n_fanning,
                            cumulative_n_samples,
                            best_move,
                            evaluation_coefficients,
                            training_parameters,
                            node_lookup,
                        ),
                    )
                    for move in possible_moves
                ]
                try:
                    for process in processes:
                        result = process.get()
                        move, value, alpha, beta = result
                        if (
                            (maximizing_player and value > extreme_value)
                            or (not maximizing_player and value < extreme_value)
                            or best_move is None
                        ):
                            extreme_value = value
                            best_move = move
                        if maximizing_player:
                            alpha = max(alpha, extreme_value)
                        else:
                            beta = min(beta, extreme_value)
                        if beta <= alpha:
                            break
                except KeyboardInterrupt:
                    print("Keyboard interrupt received. Stopping processes...")
                    pool.terminate()
                    pool.join()
                    raise KeyboardInterrupt
        return best_move, extreme_value

    def _check_single_move(
        self,
        board: Board,
        move: tuple[int | None, "Node", int],
        depth: int,
        extreme_value: float,
        alpha: float,
        beta: float,
        maximizing_player: bool,
        next_n_fanning: Optional[int],
        cumulative_n_samples: int,
        best_move: Any,
        evaluation_coefficients: dict[str, dict[str, float]],
        training_parameters: dict[str, Any],
        node_lookup: dict["Node", list["Node"]],
    ) -> tuple[Any, float, float, float]:
        board_copy = board.ai_copy()
        try:
            self.make_move(board_copy, move, render=False)
            _, value = self.minimax(
                board_copy,
                depth - 1,
                alpha,
                beta,
                next_n_fanning,
                cumulative_n_samples,
                multicore=1,
                first_call=False,
                evaluation_coefficients=evaluation_coefficients,
                training_parameters=training_parameters,
                node_lookup=node_lookup,
            )
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Stopping processes...")
            return best_move, extreme_value, alpha, beta

        if (
            (maximizing_player and value > extreme_value)
            or (not maximizing_player and value < extreme_value)
            or best_move is None
        ):
            extreme_value = value
            best_move = move

        if maximizing_player:
            alpha = max(alpha, extreme_value)
        else:
            beta = min(beta, extreme_value)

        return best_move, extreme_value, alpha, beta
