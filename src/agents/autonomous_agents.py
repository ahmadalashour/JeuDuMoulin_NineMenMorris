"""
This module defines the MinMaxAgent class which implements the Minimax algorithm to
play a board game intelligently. It includes methods for move generation, game state evaluation, and
optimizing decision-making through recursive depth-first search with alpha-beta pruning. The agent is capable
of simulating moves, evaluating board states, and executing moves based on strategic calculations.
"""

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
    """Class to represent a MinMax agent using the Minimax algorithm for game strategy.

    This agent evaluates and decides on moves based on the game's current state. It uses a data class
    structure for better organization of the data attributes and methods.

    Attributes:
        max_n_samples (Optional[int]): The maximum number of samples to consider when making decisions,
                                       helping to limit the computation during the minimax process.
        render_steps (int): The number of intermediate steps to visually render moves,
                            enhancing the user experience during gameplay.
    """

    max_n_samples: int = 10000
    render_steps: int = 30

    @staticmethod
    def init_worker():
        """
        Initialize the worker for multiprocessing. This method sets the behavior for SIGINT (interrupt signal) 
        within worker processes to be ignored. This is done to ensure that the main process can handle 
        the interrupt signal appropriately during parallel execution.
        """
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    @staticmethod
    def generate_possible_moves(board: Board) -> list[tuple[int | None, "Node", int]]:
        """Generate all possible moves for the agent based on the current game board state.

        This method inspects the board and generates possible moves depending on the current phase
        of the game, such as placing, moving, and capturing phases.

        Args:
            board (Board): The board instance to generate moves for, which contains the current state.

        Returns:
            list[tuple[int | None, Node, int]]: A list of all possible moves where each move is represented
                                                as a tuple containing the piece ID (or None), the target Node,
                                                and the type of move ('move' or 'remove').
        """
        generated_moves = []

        # Handle placing phase where pieces are initially placed on the board.
        if board.phase == Phase.placing:
            # Find a piece that has not moved yet and is thus eligible for placement.
            piece_to_place = [
                piece for piece in board.pieces[board.turn] if piece.first_move
            ][0]

            if board.available_nodes is not None:
                for node in board.available_nodes:
                    # Check the legality of placing the piece at the node.
                    legality = piece_to_place.check_legal_move(
                        board=board, new_node=node, just_check=True
                    )
                    if legality in [Action.move, Action.remove]:
                        # If the move is legal, add it to the list of generated moves.
                        generated_moves.append((piece_to_place.id, node, legality))

        # Handle move generation during the 'moving' phase of the game.
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

        # Handle move generation during the 'capturing' phase of the game.
        elif board.phase == Phase.capturing:
            other_turn = Player.orange if board.turn == Player.white else Player.white
            for piece in board.pieces[other_turn]:
                if not piece.first_move:
                    if piece.removable(board): # Check if the piece can be removed.
                        generated_moves.append((None, piece.piece.node, Action.remove))

        return generated_moves # Return the list of generated moves.

    @staticmethod
    def evaluate(
        board: Board,
        evaluation_coefficients: dict[str, dict[str, float]] = EVALUATION_COEFFICIENTS,
        training_parameters: dict[str, Any] = TRAINING_PARAMETERS,
        node_lookup: dict["Node", list["Node"]] = NODE_LOOKUP,
    ) -> float:
        """
        Evaluate the board state to compute a score that reflects the current advantage or disadvantage on the board.
    
        This method applies various heuristics based on the current game phase (for example: placing, moving, flying) to assess the board. 
        It considers factors such as piece distribution, control of mills,
        and potential mobility, adjusting for game-specific parameters to determine the overall score of the board state.

        Args:
            board (Board): The current board state to be evaluated.
            evaluation_coefficients (dict[str, float]): Coefficients used for scoring various aspects of the board.
            training_parameters (dict[str, Any]): Parameters that influence the evaluation, such as whether to consider sparsity, entropy, etc.
            node_lookup (dict[Node, list[Node]]): A lookup to determine node connectivity for mobility assessment.

        Returns:
            float: A numerical score representing the evaluated state of the board. 
            A higher score favors the maximizing player ('orange'), and a lower score favors the minimizing player ('white'), which is bascally the concept of Minimax algorithm.
        """

        # Determine the current game phase based on the number of pieces and movement.
        game_phase = "placing"
        if board.started_moving:
            game_phase = "moving"
            if len(board.pieces[board.turn]) <= 3:
                game_phase = "flying"

        # Retrieve the coefficients for evaluating the board based on the current game phase.
        coefs = evaluation_coefficients[game_phase]

        # Calculate sparsity evaluation if it's enabled in training parameters.
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
        # Normalize the sparsity evaluation to be within [-1, 1].
        sparsity_eval = sparsity_eval / 36.0  # in the range [-1, 1]

        # Evaluate the difference in the number of pieces between players, normalized to [-1, 1].
        n_pieces_eval = (
            len(board.pieces[Player.orange]) - len(board.pieces[Player.white])
        ) / 9.0  # in the range [-1, 1]

        # Immediately return extreme values if a game-ending condition is met.
        if board.started_moving:
            if len(board.pieces[Player.orange]) <= 2:
                return -np.inf
            if len(board.pieces[Player.white]) <= 2:
                return np.inf

        # Evaluate the number of mills for each player and adjust the score accordingly.
        if board.current_mills is None or board.piece_mapping is None:
            return 0
        
        # Calculate the difference in the number of mills controlled by each player, also normalized to [-1, 1].
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

        # Normalize the difference in mills to [-1, 1].
        n_mills_eval = (
            len(orange_mills) - len(white_mills)
        ) / 4.0  # in the range [-1, 1]

        # Compute entropy as a random factor based on the 'STUPIDITY' parameter, normalized to [-1, 1].
        # We called it 'STUPIDITY' because it adds randomness to the evaluation, making the agent less logical in its decisions
        # but this can be useful to explore different strategies or to avoid getting stuck in a local optimum.
        entropy = 0
        if training_parameters["STUPIDITY"] > 0:
            entropy = (
                np.random.normal(0, training_parameters["STUPIDITY"])
                / training_parameters["STUPIDITY"]
            )  # in the range [-1, 1]

        # Combine all evaluation aspects using their respective weights to get the final board evaluation.
        return (
            coefs["sparsity"] * sparsity_eval
            + coefs["n_pieces"] * n_pieces_eval
            + coefs["n_mills"] * n_mills_eval
            + coefs["entropy"] * entropy
        )

    def make_move(
        self, board: Board, move: tuple[int | None, "Node", int], render: bool = True
    ) -> Optional[bool]:
        """
        Execute a move on the board as specified by the move tuple. This method handles both moving and capturing actions, 
        updating the board state accordingly.

        Args:
            board (Board): The game board where the move will be executed.
            move (tuple[int | None, Node, int]): A tuple representing the move to be made, where:
                - The first element is the piece's ID or None if it's a capture move.
                - The second element is the Node to which the piece is moved or from which it is removed.
                - The third element is unused in this method but may represent additional state or flags related to the move.
            render (bool): If True, the move will be visually simulated step-by-step.

        Returns:
            Optional[bool]: Returns True if the move leads to a change in game phase (for example: from moving to capturing), 
            otherwise returns False. Returns None if the move tuple is empty or invalid, indicating an immediate end 
            of the game with the opposite player declared as the winner.

        """

        # Check if the move is valid; if not, end the game and declare the other player as the winner.
        if not move:
            board.winner = Player.orange if board.turn == Player.white else Player.white
            return

        # Extract details from the move tuple.
        moved_piece_id, move_node, _ = move

        # Find the piece corresponding to the moved_piece_id.
        moved_piece = (
            [piece for piece in board.pieces[board.turn] if piece.id == moved_piece_id][
                0
            ]
            if moved_piece_id is not None
            else None
        )

        # Determine the opponent's turn.
        other_turn = Player.orange if board.turn == Player.white else Player.white

        # If a piece is moved, simulate the move and update the board state accordingly.
        if moved_piece is not None:

            # Backup the original starting node of the piece
            backup_start_node = deepcopy(moved_piece.piece.node)

            # If rendering is enabled, simulate the move visually, this makes the game more interactive with real-time moving effects.
            if render:
                start_node = deepcopy(moved_piece.piece.node)
                end_node = deepcopy(move_node)
                vector = end_node - start_node
                current_node = deepcopy(start_node)

                # Incrementally update the piece's position to simulate motion
                for i in range(self.render_steps):
                    current_node = Node.from_coords(
                        start_node.x + vector[0] / self.render_steps * (i + 1),
                        start_node.y + vector[1] / self.render_steps * (i + 1),
                    )
                    moved_piece.piece.node = current_node
                    time.sleep(0.02)

            # Restore the original node after simulation.
            moved_piece.piece.node = backup_start_node
            # Execute the move and check the result.
            move_result = moved_piece.move(move_node, board)

            # If the move results in a piece removal, switch to the capturing phase.
            if move_result == Action.remove:
                board.phase = Phase.capturing
            else:
                board.turn = other_turn
        else:
            # If no piece was moved, handle capturing a piece directly.
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
            return True # Return True indicating the successful capture and phase change.

        return False # Return False indicating the move was processed without a phase change.

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
        """
        Perform the Minimax algorithm with optional alpha-beta pruning and parallel processing enhancements.
        
        This function recursively evaluates possible game moves to find the optimal move for the current player. 
        It uses alpha-beta pruning to reduce the number of nodes evaluated and can operate in parallel 
        to enhance performance.

        Args:
            board (Board): The game board to analyze.
            depth (int): The maximum depth to search in the game tree.
            alpha (float): The alpha cutoff value for alpha-beta pruning.
            beta (float): The beta cutoff value for alpha-beta pruning.
            fanning (Optional[int]): The number of moves to sample at each depth, reduces breadth of search if set.
            cumulative_n_samples (float): The cumulative product of samples considered at each recursive call.
            multicore (int): Number of processor cores to use for parallel processing. If -1, uses all but two cores.
            first_call (bool): Indicates if this is the initial call to the function (affects fanning logic).
            evaluation_coefficients (dict[str, float]): Coefficients for evaluating the board state.
            training_parameters (dict[str, Any]): Parameters influencing the evaluation function.
            node_lookup (dict[Node, list[Node]]): Lookup table for node relationships, used in move generation.

        Returns:
            tuple[Any, float]: The best move determined and its evaluation value found in the decision tree search.
        """

        # Update movable pieces based on the current board state.
        board.update_draggable_pieces()

        # Base case: if depth is 0 or the game is over, evaluate the board state and return.
        if depth == 0 or board.game_over:
            return None, self.evaluate(
                board, evaluation_coefficients, training_parameters, node_lookup
            )

        # Determine if the current player is maximizing or minimizing.
        maximizing_player = board.turn == Player.orange

        # Generate all possible moves from the current board state.
        possible_moves = self.generate_possible_moves(board)

        # If fanning is enabled, calculate the number of moves to consider based on depth and past samples.
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

            # Randomly sample moves to consider if fanning is applied.
            samples_idx = np.random.choice(
                len(possible_moves), n_samples, replace=False
            )
            possible_moves = [possible_moves[i] for i in samples_idx]

        # If no possible moves are available, return an extreme value depending on the player.
        if len(possible_moves) == 0:
            return None, float("-inf") if maximizing_player else float("inf")

        # Initialize variables for finding the best move.
        extreme_value = float("-inf") if maximizing_player else float("inf")
        best_move = None

        # Choose between parallel and sequential processing based on multicore settings.
        if multicore == 1 or depth < 4 or len(possible_moves) / cpu_count() < 0.5:
            for move in possible_moves:
                # Evaluate each move and update alpha-beta values accordingly.
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

                # If the alpha cutoff exceeds beta, prune the remaining branches.
                if beta <= alpha:
                    break
        else:
            # Parallel processing using multiprocessing.
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
                    # Collect results from all processes and determine the best move.
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
                    # Handle keyboard interrupts to terminate processes cleanly.
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
        """
        Evaluate a single move's impact on the board state within the Minimax algorithm, updating alpha and beta values as needed.

        This method simulates the move on a copy of the board, then recursively calls the minimax function to evaluate the resulting board state. It updates the alpha and beta values based on the move's evaluation and determines if this move should be considered as the new best move.

        Args:
            board (Board): The current board state to evaluate.
            move (tuple[int | None, Node, int]): The move to evaluate, described as a tuple containing:
                - The piece's ID if the move is a regular move, or None if it's a capture.
                - The node to which the piece moves or from which it is captured.
                - An integer representing additional state or flags related to the move.
            depth (int): The current depth in the Minimax search tree.
            extreme_value (float): The best value found so far at this level of the tree.
            alpha (float): The current alpha value for alpha-beta pruning.
            beta (float): The current beta value for alpha-beta pruning.
            maximizing_player (bool): True if the current player is maximizing; False if minimizing.
            next_n_fanning (Optional[int]): The number of nodes to fan out in the next level of recursion.
            cumulative_n_samples (int): The cumulative number of nodes considered in the search path.
            best_move (Any): The current best move found in the search.
            evaluation_coefficients (dict[str, float]): Coefficients used to evaluate board states.
            training_parameters (dict[str, Any]): Parameters that influence the evaluation logic.
            node_lookup (dict[Node, list[Node]]): Lookup for node connectivity, used in move generation.

        Returns:
            tuple[Any, float, float, float]: A tuple containing:
                - The best move found after evaluating this move.
                - The new extreme value.
                - The updated alpha value.
                - The updated beta value.
        """

        # Create a copy of the board to simulate the move without affecting the original board.
        board_copy = board.ai_copy()
        try:
            # Attempt to make the move on the board copy and recursively call minimax to evaluate the result.
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
            # Handle keyboard interrupts to ensure the process can be safely terminated.
            print("Keyboard interrupt received. Stopping processes...")
            return best_move, extreme_value, alpha, beta

        # Update the extreme value and best move if this move results in a better evaluation.
        if (
            (maximizing_player and value > extreme_value)
            or (not maximizing_player and value < extreme_value)
            or best_move is None
        ):
            extreme_value = value
            best_move = move

        # Update alpha or beta values based on whether the current player is maximizing or minimizing.
        if maximizing_player:
            alpha = max(alpha, extreme_value)
        else:
            beta = min(beta, extreme_value)

        # Return the potentially updated best move and the corresponding alpha and beta values.
        return best_move, extreme_value, alpha, beta
