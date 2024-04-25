# This is a base class for the board of the game (Nine men's Moris ). It is a 2D array of cells.
import pygame
import time
from typing import Literal, TYPE_CHECKING
from src.game_env.piece import DraggablePiece, Piece  # type: ignore

if TYPE_CHECKING:
    from src.game_env.node import Node
from src.globals import EDGES, NODES, Turn
import contextlib


class Board:
    """Class to represent the board of the game.

    Args:
        interactables (list[str], optional): List of players that can interact with the board. Defaults to None.

    Attributes:
        pieces (dict[str, list[DraggablePiece]]): Dictionary of player pieces.
        available_pieces (dict[str, int]): Dictionary of available pieces for each player.
        timers (dict[str, float]): Dictionary of timers for each operation.
        formed_mills (list[list[DraggablePiece]]): List of formed mills.
        current_mills (list[list[DraggablePiece]]): List of current mills.
        turn (Turn): Current turn.
        phase (Literal["placing", "moving", "capturing"]): Current phase.
        latest_phase (Literal["placing", "moving", "capturing"]): Latest phase.
        interactables (list[str]): List of players that can interact with the board.
        available_nodes (list[Node]): List of available nodes.
        winner (Literal["orange", "white"]): Winner of the game.
        sid (int): Id of the next piece to be added to the board.
        is_draw (bool): Whether the game is a draw.
    """

    formed_mills = []
    current_mills = []
    turn: Turn = "orange"
    phase: Literal["placing", "moving", "capturing"] = "placing"
    latest_phase: Literal["placing", "moving", "capturing"] = "placing"
    interactables: list[Literal["orange", "white"]] | None = None
    available_nodes: list["Node"] = NODES.copy()
    winner: Literal["orange", "white"] | None = None
    sid: int = 0
    is_draw: bool = False

    def __init__(self, interactables: list[Literal["orange", "white"]] | None = None):
        self.interactables = interactables or []
        self.pieces = {
            "orange": [
                DraggablePiece(
                    Piece("orange", None),  # type: ignore
                    interactable="orange" in self.interactables,
                    id=self.sid,
                )
            ],
            "white": [
                DraggablePiece(
                    Piece("white", None),  # type: ignore
                    interactable="white" in self.interactables,
                    id=self.sid + 1,
                )
            ],
        }
        self.sid += 2

        self.available_pieces = {"orange": 8, "white": 8}
        self.timers = {}

    @property
    def game_over(self):
        """Check if the game is over."""
        return self.winner is not None or self._check_game_over() or self.is_draw

    def ai_copy(self):
        """Create a copy of the board for the AI to use."""
        new_board = Board([])
        new_board.pieces = {player: [piece.copy_ai() for piece in self.pieces[player]] for player in self.pieces}
        id_piece_map = {piece.id: piece for player in new_board.pieces.values() for piece in player}

        new_board.available_pieces = {player: self.available_pieces[player] for player in self.available_pieces}
        new_board.turn = self.turn
        new_board.phase = self.phase
        new_board.sid = self.sid
        new_board.winner = self.winner
        new_board.is_draw = self.is_draw

        new_board.formed_mills = []

        for a, b, c in self.formed_mills:
            with contextlib.suppress(KeyError):
                a_corr = id_piece_map[a.id]
                b_corr = id_piece_map[b.id]
                c_corr = id_piece_map[c.id]
                new_board.formed_mills.append([a_corr, b_corr, c_corr])

        new_board.current_mills = []
        for a, b, c in self.current_mills:
            with contextlib.suppress(KeyError):
                a_corr = id_piece_map[a.id]
                b_corr = id_piece_map[b.id]
                c_corr = id_piece_map[c.id]
                new_board.current_mills.append([a_corr, b_corr, c_corr])

        new_board.available_nodes = self.available_nodes.copy()
        return new_board

    def update_draggable_pieces(self):
        """Update the position of the draggable pieces on the board."""
        self._start_timer("update_draggable_pieces")
        moving_phase = True
        for player_pieces in self.pieces.values():
            empty_slot = True
            for piece in player_pieces:
                piece.update_position()
                if piece.first_move:
                    empty_slot = False
            if empty_slot and self.available_pieces[player_pieces[0].piece.player] > 0:
                self.pieces[player_pieces[0].piece.player].append(
                    DraggablePiece(
                        Piece(player_pieces[0].piece.player, None),  # type: ignore
                        interactable=player_pieces[0].interactable,
                        id=self.sid,
                    )
                )
                self.sid += 1
                self.available_pieces[player_pieces[0].piece.player] -= 1

            if any(piece.first_move for piece in player_pieces):
                moving_phase = False

        if moving_phase and self.phase == "placing":
            self.phase = "moving"
        self._end_timer("update_draggable_pieces")

    def draw(self, screen, cell_size: int, margin: int):
        """Draw the board on the screen.

        Args:
            screen (pygame.Surface): The screen to draw the board on.
            cell_size (int): The size of each cell.
            margin (int): The margin around the board.
        """
        self._start_timer("draw")
        # Load background image
        background = pygame.image.load("assets/background.jpg")
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
        screen.blit(background, (0, 0))

        # Draw edges, legal nodes, numbers, and letters
        for edge in EDGES:
            pygame.draw.line(
                screen,
                (0, 0, 0),
                (
                    edge[0].x * cell_size + cell_size // 2 + margin,
                    edge[0].y * cell_size + cell_size // 2,
                ),
                (
                    edge[1].x * cell_size + cell_size // 2 + margin,
                    edge[1].y * cell_size + cell_size // 2,
                ),
                2,
            )

        # Draw legal nodes over the edges
        for node in NODES:
            # Draw a small circle centered at the node's position
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (
                    node.x * cell_size + cell_size // 2 + margin,
                    node.y * cell_size + cell_size // 2,
                ),
                cell_size // 8,
            )
        # Draw pieces that are not being dragged
        for player in self.pieces:
            for piece in self.pieces[player]:
                if piece.piece.node is not None and not piece.dragging:
                    # Make the icons a little smaller
                    smaller_icon = pygame.transform.scale(
                        piece.piece.surface(cell_size),
                        (int(cell_size * 0.8), int(cell_size * 0.8)),
                    )
                    screen.blit(
                        smaller_icon,
                        (
                            piece.piece.node.x * cell_size + margin + cell_size * 0.1,
                            piece.piece.node.y * cell_size + cell_size * 0.1,
                        ),
                    )

        # Draw pieces that are being dragged
        for player in self.pieces:
            for piece in self.pieces[player]:
                if piece.piece.node is not None and piece.dragging:
                    # Make the icons a little smaller
                    smaller_icon = pygame.transform.scale(
                        piece.piece.surface(cell_size),
                        (int(cell_size * 0.8), int(cell_size * 0.8)),
                    )
                    screen.blit(
                        smaller_icon,
                        (
                            piece.piece.node.x * cell_size + margin + cell_size * 0.1,
                            piece.piece.node.y * cell_size + cell_size * 0.1,
                        ),
                    )

        # Draw numbers on the left side with bigger and white font
        for i in range(7):
            number = str(i)
            text = pygame.font.Font(None, 48).render(number, True, (255, 255, 255))
            screen.blit(text, (3 * margin // 4, (6 - i) * cell_size + cell_size // 2 - 10))

        # Draw letters at the bottom with bigger and white font
        for i, letter in enumerate("ABCDEFG"):
            text = pygame.font.Font(None, 48).render(letter, True, (255, 255, 255))
            screen.blit(text, (i * cell_size + cell_size // 2 + margin - 10, 7 * cell_size))

        # Display score and turn with smaller font and appropriate colors
        score_text = f"Orange: {8 - self.available_pieces['orange']}  White: {8 - self.available_pieces['white']}"
        score_display = pygame.font.Font(None, 36).render(score_text, True, (255, 255, 255))
        screen.blit(score_display, (screen.get_width() - score_display.get_width() - 10, 10))

        turn_text = f"Turn: {self.turn.capitalize()}"
        player_color = (255, 255, 255) if self.turn == "white" else (255, 165, 0)
        turn_display = pygame.font.Font(None, 36).render(turn_text, True, player_color)
        screen.blit(
            turn_display,
            (
                screen.get_width() - turn_display.get_width() - 10,
                screen.get_height() - 40,
            ),
        )

        # Display phase with smaller font and appropriate colors
        phase_text = f"Phase: {self.phase.capitalize()}"
        phase_color = (255, 255, 255) if self.phase == "capturing" else (0, 255, 0)
        phase_display = pygame.font.Font(None, 36).render(phase_text, True, phase_color)
        screen.blit(
            phase_display,
            (
                screen.get_width() - phase_display.get_width() - 10,
                screen.get_height() // 2 - phase_display.get_height() // 2,
            ),
        )

        # Check if the game is over and display game over screen
        if self.game_over:
            if self.is_draw:
                game_over_text = pygame.font.Font(None, 72).render("Game Over: Draw!", True, (255, 255, 255))
            else:
                winner = self.winner or ("Orange" if self.turn == "white" else "White")
                game_over_text = pygame.font.Font(None, 72).render("Game Over: " + winner + " wins!", True, (255, 255, 255))
            screen.blit(
                game_over_text,
                (
                    screen.get_width() // 2 - game_over_text.get_width() // 2,
                    screen.get_height() // 2 - game_over_text.get_height() // 2,
                ),
            )
        # Display "Thinking" next to non-interactable pieces during their turn
        for player in self.pieces:
            if player not in self.interactables and self.turn == player:  # type: ignore
                thinking_text = pygame.font.Font(None, 24).render("Thinking", True, (255, 255, 255))
                # display text to right of the screen, up if white, down if orange
                screen.blit(
                    thinking_text,
                    (
                        screen.get_width() - thinking_text.get_width() - 10,
                        screen.get_height() - 2 * margin if player == "orange" else 2 * margin,
                    ),
                )
        # Update the display
        pygame.display.flip()
        self._end_timer("draw")

    def _start_timer(self, key):
        self.timers[key] = time.time()

    def _end_timer(self, key):
        pass
        # time.time() - self.timers[key]
        # uncomment to display times
        # print(f"Time taken for {key}: {elapsed_time} seconds")

    def __repr__(self):
        return f"Board(turn={self.turn}, phase={self.phase})"

    def _check_game_over(self):
        return self.available_pieces["orange"] == 0 and self.available_pieces["white"] == 0 and (len(self.pieces["orange"]) < 3 or len(self.pieces["white"]) < 3)
