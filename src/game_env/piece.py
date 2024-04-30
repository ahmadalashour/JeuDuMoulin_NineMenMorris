from src.game_env.node import Node
import numpy as np
import dataclasses as dc
from src.globals import (
    INITIAL_POSITIONS,
    ICONS,
    NODES,
    EDGES,
    CELL_SIZE,
    MARGIN,
    Action,
    NODE_LOOKUP,
    Phase,
    Player,
)
from typing import TYPE_CHECKING, Optional
from copy import deepcopy

if TYPE_CHECKING:
    from src.game_env.board import Board
    import pygame


@dc.dataclass
class Piece:
    """Class to represent a piece on the board.

    Args:
        player (str): The player that owns the piece.
        node (Node, optional): The node the piece is on. Defaults to None.

    Attributes:
        player (str): The player that owns the piece.
        node (Node): The node the piece is on.
    """

    player: Player
    node: Node

    def __post_init__(self):
        if not self.node:
            """Set the initial position of the piece."""
            self.node = Node(INITIAL_POSITIONS[self.player])

    def surface(self):
        """Get the surface of the piece, which represents the piece icon on the board."""
        return str(ICONS[self.player])


@dc.dataclass
class DraggablePiece:
    """Class to represent a piece that can be dragged around the board.

    Args:
        piece (Piece): The piece object to be represented.
        id (int): A unique identifier for the piece.
        interactable (bool, optional): Whether the piece can be interacted with. Defaults to True.
        first_move (bool, optional): Whether the piece has moved yet. Defaults to True.

        Attributes:
        dragging (bool): Whether the piece is currently being dragged.
        starting_node (Optional[Node]): The node the piece was on before being dragged.
        cell_size (int): The size of each cell on the board.
        margin (int): The margin around the board.
        mill_count (int): The number of mills the piece is part of.
    """

    piece: Piece
    id: int
    interactable: bool = True
    first_move: bool = True
    available_moves: list[Node] = dc.field(default_factory=list)

    dragging: bool = False
    starting_node: Optional[Node] = None
    cell_size: int = CELL_SIZE
    margin: int = MARGIN
    mill_count: int = 0

    @staticmethod
    def is_mill(nodes: tuple[Node, Node, Node]) -> bool:
        """Check if the given nodes form a mill.

        Args:
            nodes (tuple[Node, Node, Node]): The nodes to check.

        Returns:
            bool: Whether the nodes form a mill.
        """

        # Check if the nodes are connected to each other
        edge_check = (
            (nodes[0] in NODE_LOOKUP[nodes[1]] and nodes[1] in NODE_LOOKUP[nodes[0]])
            or (nodes[1] in NODE_LOOKUP[nodes[2]] and nodes[2] in NODE_LOOKUP[nodes[1]])
            or (nodes[0] in NODE_LOOKUP[nodes[2]] and nodes[2] in NODE_LOOKUP[nodes[0]])
        )

        # Check if the nodes are in a straight line, either horizontally or vertically
        return edge_check and (
            nodes[0].x == nodes[1].x == nodes[2].x
            or nodes[0].y == nodes[1].y == nodes[2].y
        )

    def copy_ai(self):
        """Create a copy of the piece for the AI to use."""
        return DraggablePiece(
            piece=deepcopy(self.piece),
            id=self.id,
            interactable=False,
            first_move=self.first_move,
        )

    def removable(self, board: "Board") -> bool:
        """Check if the piece can be removed from the board."""
        return self.mill_count == 0 or all(
            [
                piece.mill_count > 0
                for piece in board.pieces[self.piece.player]
                if not piece.first_move
            ]
        )

    def handle_remove_event(self, event: "pygame.event.Event", board: "Board") -> bool:
        """Handle the event of removing the piece from the board."""
        from pygame.locals import MOUSEBUTTONDOWN
        import pygame

        # Check if the piece can be removed. First, check if the first move has been made.
        if not self.first_move:
            if event.type == MOUSEBUTTONDOWN:
                # Get the mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                piece_x = self.piece.node.x * self.cell_size + self.margin  # type: ignore
                piece_y = self.piece.node.y * self.cell_size  # type: ignore
                surface_path = self.piece.surface()
                # Load the piece surface
                surface = pygame.image.load(surface_path)

                # Scale the surface to the cell size
                surface = pygame.transform.scale(
                    surface, (self.cell_size, self.cell_size)
                )

                # Get the rectangle of the piece
                piece_rect = surface.get_rect(topleft=(piece_x, piece_y))
                # If there's no current mills, return False
                if board.current_mills is None:
                    return False
                # If the mouse is on the piece, and the piece can be removed:
                if piece_rect.collidepoint(mouse_x, mouse_y):
                    if self.removable(board):
                        for mill in board.current_mills:
                            x, y, z = mill[0]
                            # Allows the piece to be removed if there's a mill
                            if self.id in [x, y, z]:
                                board.current_mills.remove(mill)

                        # Remove the piece from the board
                        self.remove_mill_containing_piece(board)
                        return True
        # if the piece can't be removed, because it's the first move or the piece is part of a mill,
        return False

    def handle_event(
        self, event: "pygame.event.Event", board: "Board"
    ) -> Action | None:
        """Handle the event of moving the piece on the board."""
        from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP
        import pygame

        # If the piece is not interactable, do nothing
        if not self.interactable:
            return

        # If the piece is interactable, check the event in phases like placing and moving
        if (
            board.phase == Phase.placing and self.first_move
        ) or board.phase == Phase.moving:
            if not self.dragging:
                self.starting_node = self.piece.node

            if self.piece.player != board.turn:
                return

            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                piece_x = self.piece.node.x * self.cell_size + self.margin  # type: ignore
                piece_y = self.piece.node.y * self.cell_size  # type: ignore
                surface_path = self.piece.surface()
                surface = pygame.image.load(surface_path)
                surface = pygame.transform.scale(
                    surface, (self.cell_size, self.cell_size)
                )

                # Get the rectangle of the piece
                piece_rect = surface.get_rect(topleft=(piece_x, piece_y))
                if piece_rect.collidepoint(mouse_x, mouse_y):
                    self.dragging = True

            elif event.type == MOUSEBUTTONUP and self.dragging:
                self.dragging = False
                # Snap the piece to the nearest grid cell if dropped outside
                x_index = np.clip(
                    round(
                        (pygame.mouse.get_pos()[0] - self.margin - self.cell_size // 2)
                        / self.cell_size
                    ),
                    0,
                    6,
                )
                y_index = np.clip(
                    round(
                        (pygame.mouse.get_pos()[1] - self.cell_size // 2)
                        / self.cell_size
                    ),
                    0,
                    6,
                )
                new_node = Node(f"{chr(x_index + 97)}{6 - y_index}")
                return self.move(new_node, board)

    def move(self, new_node: Node, board: "Board") -> Action:
        """Move the piece to the given node on the board.

        Args:
            new_node (Node): The node to move the piece to.
            board (Board): The board object.

        Returns:
            Action: The action taken.
        """

        # Check if the move is legal on the board before moving the piece
        legality = self.check_legal_move(board, new_node)

        # If the move is legal, update the piece's position and the board's available nodes
        if new_node in NODES and legality in [Action.move, Action.remove]:
            self.piece.node = new_node
            if self.first_move:
                self.first_move = False
            if board.available_nodes is None:
                return Action.undo
            board.available_nodes.remove(new_node)
            if self.starting_node in NODES:
                board.available_nodes.append(self.starting_node)
            return legality
        # If the move is not legal, return the piece to its starting position
        else:
            self.piece.node = self.starting_node  # type: ignore
            # If the move is not legal, the action is to undo the move
            return Action.undo

    def update_position(self):
        import pygame

        """Update the position of the piece on the board."""
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.piece.node = Node(
                f"{chr(np.clip(round((mouse_x - self.margin -  self.cell_size // 2) /  self.cell_size), 0, 6) + 97)}{6 - np.clip(round((mouse_y -  self.cell_size // 2) /  self.cell_size), 0, 6)}"
            )

    def remove_mill_containing_piece(self, board: "Board"):
        """Update the mills formed by the piece on the board."""
        if board.current_mills is None:
            return
        for mill in board.current_mills:
            x, y, z = mill[0]
            if self.id in [x, y, z]:
                board.current_mills.remove(mill)

    def check_legal_move(
        self, board: "Board", new_node: Node, just_check: bool = False
    ) -> Action:
        """Check if the move to the given node is legal.

        Args:
            board (Board): The board object.
            new_node (Node): The node to move the piece to.
            just_check (bool, optional): Whether to only check the legality. Defaults to False.

        Returns:
            Action: The action taken.
        """

        if not self.interactable:
            self.starting_node = self.piece.node

        if new_node == self.starting_node:
            return Action.undo

        if not just_check:
            # in this case we need to update the board formed mills
            self.remove_mill_containing_piece(board)

        # Check if the node is occupied by another piece
        node_occupied = False
        for player_pieces in board.pieces.values():
            for piece in player_pieces:
                if piece != self:
                    if piece.piece.node == new_node:
                        node_occupied = True

        # if the node is occupied, the action is to undo the move
        if node_occupied:
            return Action.undo
        # If the node is not occupied, check if the move is legal
        else:
            player_controlled_nodes = [
                piece.piece.node for piece in board.pieces[self.piece.player]
            ]

            # Check if edge is legal
            if (
                not self.first_move
                and len(player_controlled_nodes) > 3
                and (self.starting_node, new_node) not in EDGES
                and (new_node, self.starting_node) not in EDGES
            ):
                return Action.undo

            new_mills = []
            # Check if the move forms a mill by checking all possible mills formed by three nodes and starting from the new node
            for second_node in NODE_LOOKUP[new_node]:
                if (
                    second_node in player_controlled_nodes
                    and second_node != self.starting_node
                ):
                    for third_node in NODE_LOOKUP[second_node] + NODE_LOOKUP[new_node]:
                        if (
                            third_node in player_controlled_nodes
                            and third_node != self.starting_node
                            and third_node != new_node
                            and third_node != second_node
                        ):
                            # if the three nodes form a mill, add the mill to the list of new mills
                            if self.is_mill((new_node, second_node, third_node)):
                                second_piece = [
                                    piece
                                    for piece in board.pieces[self.piece.player]
                                    if piece.piece.node == second_node
                                ][0]
                                third_piece = [
                                    piece
                                    for piece in board.pieces[self.piece.player]
                                    if piece.piece.node == third_node
                                ][0]

                                new_mill: list[list[int | Node]] = [
                                    [self.id, second_piece.id, third_piece.id],
                                    [
                                        deepcopy(new_node),
                                        deepcopy(second_node),
                                        deepcopy(third_node),
                                    ],
                                ]

                                # Sort the mill
                                new_mill[0].sort()
                                new_mill[1].sort()

                                if board.current_mills is None:
                                    return Action.undo

                                # Check if the mill is already formed or not, if not add it to the list of new mills
                                if new_mill not in new_mills:
                                    if (
                                        new_mill not in board.formed_mills  # type: ignore
                                        # or len(board.pieces[board.turn]) == 3 # Un comment to allow mills to be reformed with same 3 pieces
                                    ):
                                        new_mills.append(new_mill)
                                        if not just_check:
                                            board.formed_mills.append(new_mill)  # type: ignore
                                    if new_mill not in board.current_mills:
                                        if not just_check:
                                            board.current_mills.append(new_mill)
            if len(new_mills) > 0:
                return Action.remove

        return Action.move

    def __lt__(self, other):
        """Less than comparison based on the piece id."""
        return self.id < other.id

    def __eq__(self, other):
        """Check equality based on the piece id."""
        return self.id == other.id

    def __repr__(self) -> str:
        """Defines the "official" string representation of the object."""
        return f"{self.piece.player} piece at {self.piece.node} with id {self.id} and state {self.first_move}"
