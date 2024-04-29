from typing import TYPE_CHECKING
from src.globals import Player, Phase, Action

if TYPE_CHECKING:
    from src.game_env.board import Board
    import pygame


class HumanAgent:
    """Class to represent a human agent."""

    _remove_piece = False

    def move(self, event: "pygame.event.Event", board: "Board"):
        """Method to handle the human agent's move.

        Args:
            event (pygame.event.Event): The event to handle.
            board (Board): The board to play on.
        """

        if not self._remove_piece:
            # Handle events for draggable pieces
            for piece in board.pieces[board.turn]:
                legality = piece.handle_event(event, board)
                if legality == Action.remove:
                    self._remove_piece = True
                    board.latest_phase = board.phase
                    board.phase = Phase.capturing
                    break
                if legality == Action.move:
                    board.turn = (
                        Player.orange if board.turn == Player.white else Player.white
                    )
                    break

            if legality in [Action.move, Action.remove]:
                return False

        else:
            other_turn = Player.orange if board.turn == Player.white else Player.white
            removed = False
            if board.available_nodes is None:
                return False
            for piece in board.pieces[other_turn]:
                if piece.handle_remove_event(event, board):
                    removed = True
                    board.pieces[other_turn].remove(piece)
                    board.available_nodes.append(piece.piece.node)
            if removed:
                self._remove_piece = False
                board.turn = (
                    Player.orange if board.turn == Player.white else Player.white
                )
                board.phase = board.latest_phase
                return True
