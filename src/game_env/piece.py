from src.game_env.node import Node
import pygame
import numpy as np
import dataclasses as dc
from src.globals import INITIAL_POSITIONS, ICONS, NODES, EDGES, CELL_SIZE, MARGIN, Action, NODE_LOOKUP, is_mill
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP
from typing import TYPE_CHECKING, Optional
from copy import deepcopy

if TYPE_CHECKING:
    from src.game_env.board import Board


@dc.dataclass
class Piece:
    player: str
    node: Node

    def __post_init__(self):
        if not self.node:
            self.node = Node(INITIAL_POSITIONS[self.player])

    def surface(self, cell_size: int):
        surface = pygame.image.load(str(ICONS[self.player]))
        return pygame.transform.scale(surface, (cell_size, cell_size))


@dc.dataclass
class DraggablePiece:
    piece: Piece
    id: int
    interactable: bool = True
    first_move: bool = True

    dragging: bool = False
    starting_node: Optional[Node] = None
    cell_size: int = CELL_SIZE
    margin: int = MARGIN
    mill_count: int = 0

    def copy_ai(self):
        return DraggablePiece(
            piece=deepcopy(self.piece),
            id=self.id,
            interactable=False,
            first_move=self.first_move,
        )

    def removable(self, board: "Board") -> bool:
        return self.mill_count == 0 or all([piece.mill_count > 0 for piece in board.pieces[self.piece.player]])

    def handle_remove_event(self, event: pygame.event.Event, board: "Board") -> bool:
        if not self.first_move:
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                piece_x = self.piece.node.x * self.cell_size + self.margin  # type: ignore
                piece_y = self.piece.node.y * self.cell_size  # type: ignore
                piece_rect = self.piece.surface(self.cell_size).get_rect(topleft=(piece_x, piece_y))
                if piece_rect.collidepoint(mouse_x, mouse_y):
                    if self.removable(board):

                        for x, y, z in board.current_mills:
                            if self in [x, y, z]:
                                board.formed_mills.remove([x, y, z])
                                board.current_mills.remove([x, y, z])

                        self.update_mills(board)
                        return True
        return False

    def handle_event(self, event: pygame.event.Event, board: "Board"):
        if not self.interactable:
            return
        if (board.phase == "placing" and self.first_move) or board.phase == "moving":
            if not self.dragging:
                self.starting_node = self.piece.node

            if self.piece.player != board.turn:
                return

            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                piece_x = self.piece.node.x * self.cell_size + self.margin  # type: ignore
                piece_y = self.piece.node.y * self.cell_size  # type: ignore
                piece_rect = self.piece.surface(self.cell_size).get_rect(topleft=(piece_x, piece_y))
                if piece_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging = True

            elif event.type == MOUSEBUTTONUP and self.dragging:
                self.dragging = False
                # Snap the piece to the nearest grid cell if dropped outside
                x_index = np.clip(
                    round((pygame.mouse.get_pos()[0] - self.margin - self.cell_size // 2) / self.cell_size),
                    0,
                    6,
                )
                y_index = np.clip(
                    round((pygame.mouse.get_pos()[1] - self.cell_size // 2) / self.cell_size),
                    0,
                    6,
                )
                new_node = Node(f"{chr(x_index + 97)}{6 - y_index}")
                return self.move(new_node, board)

    def move(self, new_node: Node, board: "Board") -> Action:
        legality = self.check_legal_move(board, new_node)
        if new_node in NODES and legality in ["move", "remove"]:

            self.piece.node = new_node
            if self.first_move:
                self.first_move = False
            board.available_nodes.remove(new_node)
            if self.starting_node in NODES:
                board.available_nodes.append(self.starting_node)
            return legality
        else:
            self.piece.node = self.starting_node  # type: ignore
            return "undo"

    def update_position(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.piece.node = Node(
                f"{chr(np.clip(round((mouse_x - self.margin -  self.cell_size // 2) /  self.cell_size), 0, 6) + 97)}{6 - np.clip(round((mouse_y -  self.cell_size // 2) /  self.cell_size), 0, 6)}"
            )

    def update_mills(self, board: "Board") -> None:
        for x, y, z in board.current_mills:
            if self in [x, y, z]:
                board.current_mills.remove([x, y, z])
                x.mill_count -= 1
                y.mill_count -= 1
                z.mill_count -= 1

    def check_legal_move(self, board: "Board", new_node: Node, just_check: bool = False) -> Action:

        if not self.interactable:
            self.starting_node = self.piece.node

        if new_node == self.starting_node:
            return "undo"

        if not just_check:
            # in this case we need to update the board formed mills
            self.update_mills(board)
        node_occupied = False
        for player_pieces in board.pieces.values():
            for piece in player_pieces:
                if piece != self:
                    if piece.piece.node == new_node:
                        node_occupied = True

        if node_occupied:
            return "undo"
        else:
            player_controlled_nodes = [piece.piece.node for piece in board.pieces[self.piece.player]]

            # Check if edge is legal
            if not self.first_move and len(player_controlled_nodes) > 3 and (self.starting_node, new_node) not in EDGES and (new_node, self.starting_node) not in EDGES:
                return "undo"

            new_mills = []
            for second_node in NODE_LOOKUP[new_node]:
                if second_node in player_controlled_nodes and second_node != self.starting_node:
                    for third_node in NODE_LOOKUP[second_node] + NODE_LOOKUP[new_node]:
                        if third_node in player_controlled_nodes and third_node != self.starting_node and third_node != new_node and third_node != second_node:
                            if is_mill((new_node, second_node, third_node)):
                                second_piece = [piece for piece in board.pieces[self.piece.player] if piece.piece.node == second_node][0]
                                third_piece = [piece for piece in board.pieces[self.piece.player] if piece.piece.node == third_node][0]

                                new_mill = [self, second_piece, third_piece]

                                # Sort the mill
                                new_mill.sort()
                                if new_mill not in new_mills:
                                    if new_mill not in board.formed_mills or len(board.pieces[board.turn]) == 3:
                                        new_mills.append(new_mill)
                                        if not just_check:
                                            board.formed_mills.append(new_mill)

                                    if not just_check:
                                        board.current_mills.append(new_mill)
                                        for piece in new_mill:
                                            piece.mill_count += 1

            if new_mills:
                return "remove"

        return "move"

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self) -> str:
        return f"{self.piece.player} piece at {self.piece.node} with id {self.id} and state {self.first_move}"
