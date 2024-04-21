# This is a base class for the board of the game (Nine men's Moris ). It is a 2D array of cells.
import dataclasses as dc
from typing import List
from pathlib import Path
import pygame
from pygame.locals import *
import numpy as np
import time
from typing import Literal

ICONS = {
    "orange": Path("assets/orangeplayer.png"),
    "white": Path("assets/whiteplayer.png")
        }

INITIAL_POSITIONS = {   
    "orange":"h2",
    "white":"h4"
}

CELL_SIZE = 50
MARGIN = 20


@dc.dataclass
class Node:
    str_repr: str
    _x : int = dc.field(init=False)
    _y : int = dc.field(init=False)
    def __post_init__(self):
        self._x = ord(self.str_repr[0]) - 97
        self._y = 6 - int(self.str_repr[1])
        # assert 0 <= self._x < 7, f"Invalid x coordinate {self._x}"
        # assert 0 <= self._y < 7, f"Invalid y coordinate {self._y}"

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    def __repr__(self):
        return self.str_repr
    
    def __eq__(self, other):
        return self.str_repr == other.str_repr
    
    def __hash__(self):
        return hash(self.str_repr)

NODES = [
    Node("a0"), Node("d0"), Node("g0"),
    Node("b1"), Node("d1"), Node("f1"),
    Node("c2"), Node("d2"), Node("e2"),
    Node("a3"), Node("b3"), Node("c3"), 
    Node("e3"), Node("f3"), Node("g3"),
    Node("c4"), Node("d4"), Node("e4"),
    Node("b5"), Node("d5"), Node("f5"),
    Node("a6"), Node("d6"), Node("g6")
]

EDGES = [
    # Horizontal edges
    (Node("a0"), Node("d0")), (Node("d0"), Node("g0")),
    (Node("b1"), Node("d1")), (Node("d1"), Node("f1")),
    (Node("c2"), Node("d2")), (Node("d2"), Node("e2")),
    (Node("a3"), Node("b3")), (Node("b3"), Node("c3")),
    (Node("e3"), Node("f3")), (Node("f3"), Node("g3")),
    (Node("c4"), Node("d4")), (Node("d4"), Node("e4")),
    (Node("b5"), Node("d5")), (Node("d5"), Node("f5")),
    (Node("a6"), Node("d6")), (Node("d6"), Node("g6")),
    # Vertical edges
    (Node("a0"), Node("a3")), (Node("a3"), Node("a6")),
    (Node("b1"), Node("b3")), (Node("b3"), Node("b5")),
    (Node("c2"), Node("c3")), (Node("c3"), Node("c4")),
    (Node("d0"), Node("d1")), (Node("d1"), Node("d2")),
    (Node("d4"), Node("d5")), (Node("d5"), Node("d6")),
    (Node("e2"), Node("e3")), (Node("e3"), Node("e4")),
    (Node("f1"), Node("f3")), (Node("f3"), Node("f5")),
    (Node("g0"), Node("g3")), (Node("g3"), Node("g6")),

]




@dc.dataclass   
class Piece: 
    player: str
    node: Node | None = None
    def __post_init__(self):
        if not self.node:
            self.node = Node(INITIAL_POSITIONS[self.player])
    def surface(self, cell_size: int):
        surface = pygame.image.load(str(ICONS[self.player]))
        return pygame.transform.scale(surface, (cell_size, cell_size))



@dc.dataclass
class DraggablePiece:
    piece: Piece
    dragging: bool = False
    starting_node: Node | None = None
    cell_size: int = CELL_SIZE
    margin: int = MARGIN
    def handle_event(self, event: pygame.event.Event, pieces: List[Piece]):
        
        if not self.dragging:
            self.starting_node = self.piece.node 

        if event.type == MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            piece_x = self.piece.node.x * self.cell_size + self.margin
            piece_y = self.piece.node.y * self.cell_size
            piece_rect = self.piece.surface(self.cell_size).get_rect(topleft=(piece_x, piece_y))
            if piece_rect.collidepoint(mouse_x, mouse_y):
                self.dragging = True
                
        elif event.type == MOUSEBUTTONUP and self.dragging:
            self.dragging = False
            # Snap the piece to the nearest grid cell if dropped outside
            x_index = np.clip(round((pygame.mouse.get_pos()[0] - self.margin - self.cell_size // 2) / self.cell_size), 0, 6)
            y_index = np.clip(round((pygame.mouse.get_pos()[1] -  self.cell_size // 2) /  self.cell_size), 0, 6)
            new_node = Node(f"{chr(x_index + 97)}{6 - y_index}")
            node_occupied = False
            for player_pieces in pieces.values():
                for draggable_piece in player_pieces:
                    if not draggable_piece == self:
                        if draggable_piece.piece.node == new_node:
                            node_occupied = True
            if new_node in NODES and not node_occupied:
                self.piece.node = new_node
            else:
                self.piece.node = self.starting_node


    def update_position(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.piece.node = Node(
                f"{chr(np.clip(round((mouse_x - self.margin -  self.cell_size // 2) /  self.cell_size), 0, 6) + 97)}{6 - np.clip(round((mouse_y -  self.cell_size // 2) /  self.cell_size), 0, 6)}"
            )


Turn = Literal["orange", "white"]
Action = Literal["move", "remove"]

class Board:
    turn: Turn = "orange"
    action: Action = "move"
    def __init__(self):
        self.pieces = {
            "orange": [DraggablePiece(Piece("orange"))],
            "white": [DraggablePiece(Piece("white"))]
        }
        self.available_pieces = {
            "orange": 9,
            "white": 9
        }
        self.timers = {}



    # Add a method to update the position of draggable pieces
    def update_draggable_pieces(self):
        self.start_timer("update_draggable_pieces")
        for player_pieces in self.pieces.values():
            empty_slot = True
            for piece in player_pieces:
                piece.update_position()
                if piece.piece.node.str_repr == INITIAL_POSITIONS[piece.piece.player] or piece.dragging:
                    empty_slot = False
            if empty_slot and self.available_pieces[player_pieces[0].piece.player] > 0:
                self.pieces[player_pieces[0].piece.player].append(DraggablePiece(Piece(player_pieces[0].piece.player)))
                self.available_pieces[player_pieces[0].piece.player] -= 1
        self.end_timer("update_draggable_pieces")

    def start_timer(self, key):
        self.timers[key] = time.time()

    def end_timer(self, key):
        elapsed_time = time.time() - self.timers[key]
        # uncomment to display times
        # print(f"Time taken for {key}: {elapsed_time} seconds")


    def __repr__(self):
        return "\n".join("".join(str(cell) for cell in row) for row in self.cells)

    def add_piece(self, piece: Piece):
        self.pieces[piece.player].append(piece)

    @classmethod
    def from_repr(cls, repr):
        cells = [[int(cell) for cell in row] for row in repr.split("\n")]
        return cls(cells)
    
    def draw(self, screen, cell_size: int, margin: int):
        self.start_timer("draw")
        # Set background color to white
        screen.fill((255, 255, 255))
        
        # Draw edges
        for edge in EDGES:
            pygame.draw.line(screen, (0, 0, 0), (edge[0].x * cell_size + cell_size // 2 + margin, edge[0].y * cell_size + cell_size // 2), (edge[1].x * cell_size + cell_size // 2 + margin, edge[1].y * cell_size + cell_size // 2), 2)

        # Draw legal nodes over the edges
        for node in NODES:
            # Draw a small circle centered at the node's position
            pygame.draw.circle(screen, (0, 0, 0), (node.x * cell_size + cell_size // 2 + margin, node.y * cell_size + cell_size // 2), cell_size // 8)

        # Draw numbers on the left side
        for i in range(7):
            number = str(i)
            text = pygame.font.Font(None, 24).render(number, True, (0, 0, 0))
            screen.blit(text, (margin // 2, (6-i) * cell_size + cell_size // 2 - 5))

        # Draw letters at the bottom
        for i, letter in enumerate("ABCDEFG"):
            text = pygame.font.Font(None, 24).render(letter, True, (0, 0, 0))
            screen.blit(text, (i * cell_size + cell_size // 2 + margin - 5, 7 * cell_size))
            
        # Draw pieces that are not being dragged
        for player in self.pieces:
            for piece in self.pieces[player]:
                if piece.piece.node is not None and not piece.dragging:
                    screen.blit(piece.piece.surface(cell_size),
                                (piece.piece.node.x * cell_size + margin, piece.piece.node.y * cell_size))
                    
        # Draw pieces that are being dragged
        for player in self.pieces:
            for piece in self.pieces[player]:
                if piece.piece.node is not None and piece.dragging:
                    screen.blit(piece.piece.surface(cell_size),
                                (piece.piece.node.x * cell_size + margin, piece.piece.node.y * cell_size))
        # Update the display
        pygame.display.flip()
        self.end_timer("draw")
