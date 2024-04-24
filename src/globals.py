from pathlib import Path
from src.game_env.node import Node
from typing import Literal
from collections import defaultdict

ICONS = {
    "orange": Path("assets/orangeplayer.png"),
    "white": Path("assets/whiteplayer.png"),
}

INITIAL_POSITIONS = {"orange": "h2", "white": "h4"}
Turn = Literal["orange", "white"]
Action = Literal["move", "remove", "undo"]
CELL_SIZE = 80
MARGIN = 50

NODES = [
    Node("a0"),
    Node("d0"),
    Node("g0"),
    Node("b1"),
    Node("d1"),
    Node("f1"),
    Node("c2"),
    Node("d2"),
    Node("e2"),
    Node("a3"),
    Node("b3"),
    Node("c3"),
    Node("e3"),
    Node("f3"),
    Node("g3"),
    Node("c4"),
    Node("d4"),
    Node("e4"),
    Node("b5"),
    Node("d5"),
    Node("f5"),
    Node("a6"),
    Node("d6"),
    Node("g6"),
]

EDGES = [
    # Horizontal edges
    (Node("a0"), Node("d0")),
    (Node("d0"), Node("g0")),
    (Node("b1"), Node("d1")),
    (Node("d1"), Node("f1")),
    (Node("c2"), Node("d2")),
    (Node("d2"), Node("e2")),
    (Node("a3"), Node("b3")),
    (Node("b3"), Node("c3")),
    (Node("e3"), Node("f3")),
    (Node("f3"), Node("g3")),
    (Node("c4"), Node("d4")),
    (Node("d4"), Node("e4")),
    (Node("b5"), Node("d5")),
    (Node("d5"), Node("f5")),
    (Node("a6"), Node("d6")),
    (Node("d6"), Node("g6")),
    # Vertical edges
    (Node("a0"), Node("a3")),
    (Node("a3"), Node("a6")),
    (Node("b1"), Node("b3")),
    (Node("b3"), Node("b5")),
    (Node("c2"), Node("c3")),
    (Node("c3"), Node("c4")),
    (Node("d0"), Node("d1")),
    (Node("d1"), Node("d2")),
    (Node("d4"), Node("d5")),
    (Node("d5"), Node("d6")),
    (Node("e2"), Node("e3")),
    (Node("e3"), Node("e4")),
    (Node("f1"), Node("f3")),
    (Node("f3"), Node("f5")),
    (Node("g0"), Node("g3")),
    (Node("g3"), Node("g6")),
]

# Create a lookup table
NODE_LOOKUP = defaultdict(list)
for edge in EDGES:
    NODE_LOOKUP[edge[0]].append(edge[1])
    NODE_LOOKUP[edge[1]].append(edge[0])

TRAINING_PARAMETERS = dict(
    # Global variables
    RENDER=True,
    INTERACTABLES=[],
    DIFFICULTY=5,
    STUPIDITY=0.0,
    USE_SPARSITY=False,
    MAX_N_OPERATIONS=None,
)


def is_mill(nodes: tuple[Node, Node, Node]) -> bool:
    edge_check = (
        (nodes[0] in NODE_LOOKUP[nodes[1]] and nodes[1] in NODE_LOOKUP[nodes[0]])
        or (nodes[1] in NODE_LOOKUP[nodes[2]] and nodes[2] in NODE_LOOKUP[nodes[1]])
        or (nodes[0] in NODE_LOOKUP[nodes[2]] and nodes[2] in NODE_LOOKUP[nodes[0]])
    )
    return edge_check and (nodes[0].x == nodes[1].x == nodes[2].x or nodes[0].y == nodes[1].y == nodes[2].y)
