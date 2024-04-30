"""
This module contains the HumanAgent class, which is used to represent a human player in the game.
It includes a method 'move' to handle human player moves and an attribute '_remove_piece' to manage piece removal.
"""

from typing import TYPE_CHECKING
from src.globals import Player, Phase, Action

if TYPE_CHECKING:
    from src.game_env.board import Board
    import pygame


class HumanAgent:
    """Class to represent a human agent that interacts with the game board via user input."""

    _remove_piece = False

    def move(self, event: "pygame.event.Event", board: "Board"):
        """Handle the human agent's move based on pygame events.

        Args:
            event (pygame.event.Event): The current event to process, such as mouse clicks or key presses.
            board (Board): The game board object where the game is being played.

        Returns:
            bool: Returns False if the move is in progress or True if the move completes successfully.
        """

        # If no piece needs to be removed, process normal piece movements.
        if not self._remove_piece:
            # Check all pieces of the current player's turn for possible actions.
            for piece in board.pieces[board.turn]:
                # Handle the current event for the piece and update the board according to the legality of the move.
                legality = piece.handle_event(event, board)
                if legality == Action.remove:
                    # Transition to the capturing phase if a piece is marked for removal.
                    self._remove_piece = True
                    board.latest_phase = board.phase
                    board.phase = Phase.capturing
                    break
                if legality == Action.move:
                    # Change the turn to the other player after a move.
                    board.turn = (
                        Player.orange if board.turn == Player.white else Player.white
                    )
                    break

            # Return False to indicate that the current player's action has been processed, 
            # but the turn has not concluded because further actions might be required.
            if legality in [Action.move, Action.remove]:
                return False

        # If a piece needs to be removed, handle the removing process.
        else:
            other_turn = Player.orange if board.turn == Player.white else Player.white
            removed = False
            # Check all pieces of the opposing player (opponent) for possible removal.
            if board.available_nodes is None:
                return False
            for piece in board.pieces[other_turn]:
                if piece.handle_remove_event(event, board):
                    removed = True
                    # Remove the piece from the board and update available nodes.
                    board.pieces[other_turn].remove(piece)
                    # Add the removed piece's node to the available nodes list.
                    board.available_nodes.append(piece.piece.node)

            # If a piece has just been removed, switch the turn and return to the previous phase.
            if removed:
                self._remove_piece = False
                board.turn = (
                    Player.orange if board.turn == Player.white else Player.white
                )
                board.phase = board.latest_phase
                # Return True to indicate the removal was successful and the turn is complete.
                return True
