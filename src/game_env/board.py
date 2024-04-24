# This is a base class for the board of the game (Nine men's Moris ). It is a 2D array of cells.
import pygame
import time
from typing import Literal, TYPE_CHECKING
from src.game_env.piece import DraggablePiece, Piece

if TYPE_CHECKING:
    from src.game_env.node import Node
from src.globals import EDGES, NODES, Turn


class Board:
    formed_mills = []
    turn: Turn = "orange"
    phase: Literal["placing", "moving", "capturing"] = "placing"
    latest_phase: Literal["placing", "moving", "capturing"] = "placing"
    interactables: list[Literal["orange", "white"]] | None = None
    available_nodes: list["Node"] = NODES.copy()
    winner: Literal["orange", "white"] | None = None
    sid: int = 0

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

    def ai_copy(self):
        new_board = Board([])
        new_board.pieces = {player: [piece.copy_ai() for piece in self.pieces[player]] for player in self.pieces}

        new_board.available_pieces = {player: self.available_pieces[player] for player in self.available_pieces}
        new_board.turn = self.turn
        new_board.phase = self.phase
        new_board.sid = self.sid

        new_board.formed_mills = []

        for a, b, c in self.formed_mills:
            try:
                a_corr = [p for p in new_board.pieces[a.piece.player] if p.id == a.id][0]
                b_corr = [p for p in new_board.pieces[b.piece.player] if p.id == b.id][0]
                c_corr = [p for p in new_board.pieces[c.piece.player] if p.id == c.id][0]
                new_board.formed_mills.append([a_corr, b_corr, c_corr])
            except:
                pass

        new_board.available_nodes = self.available_nodes.copy()
        return new_board

    # Add a method to update the position of draggable pieces
    def update_draggable_pieces(self):
        self.start_timer("update_draggable_pieces")
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
        self.end_timer("update_draggable_pieces")

    def start_timer(self, key):
        self.timers[key] = time.time()

    def end_timer(self, key):
        pass
        # time.time() - self.timers[key]
        # uncomment to display times
        # print(f"Time taken for {key}: {elapsed_time} seconds")

    def __repr__(self):
        return f"Board(turn={self.turn}, phase={self.phase})"

    def add_piece(self, piece: DraggablePiece):
        self.pieces[piece.piece.player].append(piece)

    @property
    def game_over(self):
        return self.winner is not None or self.check_game_over()

    def check_game_over(self):
        return self.available_pieces["orange"] == 0 and self.available_pieces["white"] == 0 and (len(self.pieces["orange"]) < 3 or len(self.pieces["white"]) < 3)

    def draw(self, screen, cell_size: int, margin: int):
        self.start_timer("draw")
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
            winner = self.winner or ("Orange" if self.turn == "white" else "White")
            game_over_text = pygame.font.Font(None, 72).render("Game Over " + winner + " wins!", True, (255, 255, 255))
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
        self.end_timer("draw")