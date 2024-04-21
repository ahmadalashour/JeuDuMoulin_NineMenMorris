from pathlib import Path
from node import Node
from typing import Literal

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
