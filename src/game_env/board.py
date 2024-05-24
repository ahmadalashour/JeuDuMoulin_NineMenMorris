# This is a base class for the board of the game (Nine men's Moris ). It is a 2D array of cells.
import time
from src.game_env.piece import DraggablePiece, Piece
from typing import Optional, TYPE_CHECKING
from src.game_env.node import Node
from src.globals import EDGES, NODES, Phase, Player
from copy import deepcopy

if TYPE_CHECKING:
    import pygame


class Board:
    """Class to represent the board of the game.

    Args:
        interactables (list[str], optional): List of players that can interact with the board. Defaults to None.

    Attributes:

        screen (pygame.Surface): The screen to draw the board on.
        cell_size (int): The size of each cell.
        margin (int): The margin around the board.
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

    formed_mills: Optional[list[list[list[int | Node]]]] = None
    current_mills: Optional[list[list[list[int | Node]]]] = None
    turn: Player = Player.orange
    phase: Phase = Phase.placing
    latest_phase: Phase = Phase.placing
    interactables: list[Player] | None = None
    available_nodes: Optional[list["Node"]] = None
    winner: Player | None = None
    sid: int = 0
    is_draw: bool = False
    piece_mapping: Optional[dict[int, DraggablePiece]] = None
    started_moving: bool = False
    time: float = 0

    def __init__(
        self,
        cell_size: int,
        margin: int,
        screen: Optional["pygame.Surface"] = None,
        interactables: Optional[list[Player]] = None,
    ):
        self.formed_mills = self.formed_mills or []
        self.current_mills = self.current_mills or []
        self.available_nodes = deepcopy(NODES)
        self.screen = screen
        self.cell_size = cell_size
        self.margin = margin
        self.interactables = interactables or []
        self.time = time.time()
        self.pieces = {
            Player.orange: [
                DraggablePiece(
                    Piece(Player.orange, None),  # type: ignore
                    interactable=Player.orange in self.interactables,
                    id=self.sid,
                )
            ],
            Player.white: [
                DraggablePiece(
                    Piece(Player.white, None),  # type: ignore
                    interactable=Player.white in self.interactables,
                    id=self.sid + 1,
                )
            ],
        }
        self.piece_mapping = {
            piece.id: piece for player in self.pieces.values() for piece in player
        }

        self.sid += 2

        self.available_pieces = {Player.orange: 8, Player.white: 8}
        self.timers = {}

    @property
    def time_display_string(self) -> str:
        """Return the time taken to make a move as a string."""
        time_diff = time.time() - self.time
        hours = int(time_diff // 3600)
        minutes = int((time_diff % 3600) // 60)
        seconds = int(time_diff % 60)
        return (
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            if hours > 0
            else f"{minutes:02d}:{seconds:02d}"
        )

    @property
    def game_over(self) -> bool:
        """Check if the game is over."""
        return self.winner is not None or self._check_game_over() or self.is_draw

    def ai_copy(self) -> "Board":
        """Create a copy of the board for the AI to use."""
        new_board = Board(cell_size=self.cell_size, margin=self.margin)
        new_board.pieces = {
            player: [piece.copy_ai() for piece in self.pieces[player]]
            for player in self.pieces
        }

        new_board.available_pieces = deepcopy(self.available_pieces)
        new_board.piece_mapping = {
            piece.id: piece for player in new_board.pieces.values() for piece in player
        }
        ids = list(new_board.piece_mapping.keys())
        new_board.turn = deepcopy(self.turn)
        new_board.phase = deepcopy(self.phase)
        new_board.sid = deepcopy(self.sid)
        new_board.winner = deepcopy(self.winner)
        new_board.is_draw = deepcopy(self.is_draw)
        new_board.started_moving = deepcopy(self.started_moving)

        new_board.formed_mills = deepcopy(self.formed_mills)
        new_board.current_mills = deepcopy(self.current_mills)

        if new_board.formed_mills is None or new_board.current_mills is None:
            return new_board
        # remove mills that have ids that are not in the new board
        new_board.formed_mills = [
            mill
            for mill in new_board.formed_mills
            if all(pid in ids for pid in mill[0])
        ]
        new_board.current_mills = [
            mill
            for mill in new_board.current_mills
            if all(pid in ids for pid in mill[0])
        ]

        self._update_mill_count(new_board)
        new_board.available_nodes = deepcopy(self.available_nodes)

        return new_board

    def update_draggable_pieces(self):
        """Update the position of the draggable pieces on the board."""
        self.started_moving = True
        for player_pieces in self.pieces.values():
            empty_slot = True
            for piece in player_pieces:
                if self.screen:
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
                if self.piece_mapping:
                    self.piece_mapping[self.sid] = self.pieces[
                        player_pieces[0].piece.player
                    ][-1]
                self.sid += 1
                self.available_pieces[player_pieces[0].piece.player] -= 1

            if any(piece.first_move for piece in player_pieces):
                self.started_moving = False

        if self.started_moving and self.phase == Phase.placing:
            self.phase = Phase.moving

        self._update_mill_count(self)


    def draw(self):
        """Draw the board on the screen.

        Args:

        """
        import pygame

        if self.screen is None:
            return
        # Load background image
        background = pygame.image.load("assets/background.jpg")
        background = pygame.transform.scale(
            background, (self.screen.get_width(), self.screen.get_height())
        )
        self.screen.blit(background, (0, 0))

        # Draw edges, legal nodes, numbers, and letters
        for edge in EDGES:
            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (
                    edge[0].x * self.cell_size + self.cell_size // 2 + self.margin,
                    edge[0].y * self.cell_size + self.cell_size // 2,
                ),
                (
                    edge[1].x * self.cell_size + self.cell_size // 2 + self.margin,
                    edge[1].y * self.cell_size + self.cell_size // 2,
                ),
                2,
            )

        # Draw legal nodes over the edges
        for node in NODES:
            # Draw a small circle centered at the node's position
            pygame.draw.circle(
                self.screen,
                (0, 0, 0),
                (
                    node.x * self.cell_size + self.cell_size // 2 + self.margin,
                    node.y * self.cell_size + self.cell_size // 2,
                ),
                self.cell_size // 8,
            )
        # Draw pieces that are not being dragged
        for player in self.pieces:
            for piece in self.pieces[player]:
                if piece.piece.node is not None and not piece.dragging:
                    surface_path = piece.piece.surface()
                    surface = pygame.image.load(surface_path)
                    surface = pygame.transform.scale(
                        surface, (self.cell_size, self.cell_size)
                    )
                    # Make the icons a little smaller
                    smaller_icon = pygame.transform.scale(
                        surface,
                        (int(self.cell_size * 0.8), int(self.cell_size * 0.8)),
                    )
                    self.screen.blit(
                        smaller_icon,
                        (
                            piece.piece.node.x * self.cell_size
                            + self.margin
                            + self.cell_size * 0.1,
                            piece.piece.node.y * self.cell_size + self.cell_size * 0.1,
                        ),
                    )

        # Draw pieces that are being dragged
        for player in self.pieces:
            for piece in self.pieces[player]:
                if piece.piece.node is not None and piece.dragging:
                    surface_path = piece.piece.surface()
                    surface = pygame.image.load(surface_path)
                    surface = pygame.transform.scale(
                        surface, (self.cell_size, self.cell_size)
                    )

                    # Make the icons a little smaller
                    smaller_icon = pygame.transform.scale(
                        surface,
                        (int(self.cell_size * 0.8), int(self.cell_size * 0.8)),
                    )
                    self.screen.blit(
                        smaller_icon,
                        (
                            piece.piece.node.x * self.cell_size
                            + self.margin
                            + self.cell_size * 0.1,
                            piece.piece.node.y * self.cell_size + self.cell_size * 0.1,
                        ),
                    )

        # Draw numbers on the left side with bigger and white font
        for i in range(7):
            number = str(i)
            text = pygame.font.Font(None, 48).render(number, True, (255, 255, 255))
            self.screen.blit(
                text,
                (
                    3 * self.margin // 4,
                    (6 - i) * self.cell_size + self.cell_size // 2 - 10,
                ),
            )

        # Draw letters at the bottom with bigger and white font
        for i, letter in enumerate("ABCDEFG"):
            text = pygame.font.Font(None, 48).render(letter, True, (255, 255, 255))
            self.screen.blit(
                text,
                (
                    i * self.cell_size + self.cell_size // 2 + self.margin - 10,
                    7 * self.cell_size,
                ),
            )

        # Display the time taken to make a move
        time_text = f"Time: {self.time_display_string}"
        score_display = pygame.font.Font(None, 36).render(
            time_text, True, (255, 255, 255)
        )
        score_rect = pygame.Rect(
            0, 0, score_display.get_width(), score_display.get_height()
        )
        # Scale the score_rect by 1.5
        score_rect.topleft = (
            self.screen.get_width() - score_display.get_width() - 50,
            10,
        )

        # Draw black box with rounded edges
        pygame.draw.rect(self.screen, (0, 0, 0), score_rect, border_radius=10)

        # Draw the score display on the black box
        self.screen.blit(score_display, score_rect.topleft)

        turn_text = f"Turn: {str(self.turn).capitalize()}"
        player_color = (255, 255, 255) if self.turn == Player.white else (255, 165, 0)
        turn_display = pygame.font.Font(None, 36).render(turn_text, True, player_color)
        self.screen.blit(
            turn_display,
            (
                self.screen.get_width() - turn_display.get_width() - 50,
                self.screen.get_height() - 80,
            ),
        )

        # Display phase with smaller font and appropriate colors
        phase_text = f"{str(self.phase).capitalize()}"
        match self.phase:
            case Phase.placing:
                phase_color = (255, 254, 222)
            case Phase.moving:
                phase_color = (100, 100, 255)
            case Phase.capturing:
                phase_color = (255, 0, 0)

        phase_display = pygame.font.Font(None, 36).render(phase_text, True, phase_color)
        self.screen.blit(
            phase_display,
            (
                self.screen.get_width() - phase_display.get_width() - 80,
                ((self.screen.get_height() - self.margin) // 2)
                - phase_display.get_height() // 2,
            ),
        )

        # Check if the game is over and display game over self.screen
        if self.game_over:
            if self.is_draw:
                game_over_text = pygame.font.Font(None, 72).render(
                    "Game Over: Draw!", True, (255, 255, 255)
                )
            else:
                winner = self.winner or (
                    "Orange" if self.turn == Player.white else "White"
                )
                game_over_text = pygame.font.Font(None, 72).render(
                    "Game Over: " + str(winner) + " wins!", True, (255, 255, 255)
                )
            self.screen.blit(
                game_over_text,
                (
                    self.screen.get_width() // 2 - game_over_text.get_width() // 2,
                    self.screen.get_height() // 2 - game_over_text.get_height() // 2,
                ),
            )
        # Display "Thinking" next to non-interactable pieces during their turn
        for player in self.pieces:
            if player not in self.interactables and self.turn == player:  # type: ignore
                thinking_text = pygame.font.Font(None, 24).render(
                    "Thinking" + "." * int(time.time() % 3), True, (255, 255, 255)
                )
                # display text to right of the self.screen, up if white, down if orange
                self.screen.blit(
                    thinking_text,
                    (
                        self.screen.get_width() - thinking_text.get_width() - 80,
                        self.screen.get_height() - 3 * self.margin
                        if player == Player.orange
                        else 2 * self.margin,
                    ),
                )
        # Update the display
        pygame.display.flip()

    def __repr__(self):
        return f"Board(turn={self.turn}, phase={self.phase})"

    def _check_game_over(self):
        game_over_result = (
            self.available_pieces[Player.orange] == 0
            and self.available_pieces[Player.white] == 0
            and (
                len(self.pieces[Player.orange]) < 3
                or len(self.pieces[Player.white]) < 3
            )
        )

        if game_over_result:
            self.winner = (
                Player.orange if len(self.pieces[Player.white]) < 3 else Player.white
            )

        return game_over_result

    @staticmethod
    def _update_mill_count(board: "Board"):
        if board.piece_mapping is None:
            return
        for piece in board.piece_mapping.values():
            piece.mill_count = 0

        if board.current_mills is None:
            return

        for mill in board.current_mills:
            for pid in mill[0]:
                if pid in board.piece_mapping:
                    board.piece_mapping[pid].mill_count += 1
                else:
                    board.current_mills.remove(mill)
                    break
