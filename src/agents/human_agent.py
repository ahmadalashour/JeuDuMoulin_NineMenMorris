from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game_env.board import Board
    import pygame


class HumanAgent:
    remove_piece = False

    def move(self, event: "pygame.event.Event", board: "Board"):
        if not self.remove_piece:
            # Handle events for draggable pieces
            for piece in board.pieces[board.turn]:
                legality = piece.handle_event(event, board)
                if legality == "remove":
                    self.remove_piece = True
                    board.latest_phase = board.phase
                    board.phase = "capturing"
                    break
                if legality == "move":
                    board.turn = "orange" if board.turn == "white" else "white"
                    break
        else:
            other_turn = "orange" if board.turn == "white" else "white"
            removed = False
            for piece in board.pieces[other_turn]:
                if piece.handle_remove_event(event, board):
                    removed = True
                    board.pieces[other_turn].remove(piece)
                    board.available_nodes.append(piece.piece.node)
                    break
            if removed:
                self.remove_piece = False
                board.turn = "orange" if board.turn == "white" else "white"
                board.phase = board.latest_phase
