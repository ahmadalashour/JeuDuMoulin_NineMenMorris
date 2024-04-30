"""
This file defines various constants and configurations used in the game environment and AI evaluation.
"""



from pathlib import Path
from src.game_env.node import Node
from collections import defaultdict
from enum import Enum


class Player(Enum):
    orange = "orange"
    white = "white"

    def __str__(self) -> str:
        return self.value


class Phase(Enum):
    placing = "placing"
    moving = "moving"
    capturing = "capturing"

    def __str__(self) -> str:
        return self.value


class Action(Enum):
    move = "move"
    remove = "remove"
    undo = "undo"

    def __str__(self) -> str:
        return self.value


# Paths to player icons
ICONS = {
    Player.orange: Path("assets/orangeplayer.png"),
    Player.white: Path("assets/whiteplayer.png"),
}

# Initial positions for players
INITIAL_POSITIONS = {Player.orange: "h2", Player.white: "h4"}

# Constants for grid cell size and margin
CELL_SIZE = 80
MARGIN = 50

# Minimum number of moves required for a draw
MIN_DRAW_MOVES = 50

# Define the nodes (points) on the game board
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

# Define the edges (connections between nodes) on the game board
EDGES: list[tuple[Node, Node]] = [
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


# Create a lookup table for quick access to node connections
NODE_LOOKUP = defaultdict(list[Node])
for edge in EDGES:
    NODE_LOOKUP[edge[0]].append(edge[1])
    NODE_LOOKUP[edge[1]].append(edge[0])

# Training parameters for AI and game settings
TRAINING_PARAMETERS = dict(
    # Global variables
    RENDER=True,
    INTERACTABLES=[],
    DIFFICULTY={
        Player.orange: 5,
        Player.white: 5,
    },
    STUPIDITY=1.0,
    USE_SPARSITY=True,
    MAX_N_OPERATIONS=None,
    N_PROCESS=-1,
)

# Evaluation coefficients for different game phases
EVALUATION_COEFFICIENTS = {
    "placing": {
        "sparsity": 0.3,
        "n_pieces": 0.1,
        "n_mills": 0.9,
        "entropy": 0.2,
    },
    "moving": {
        "sparsity": 0.0,
        "n_pieces": 0.1,
        "n_mills": 0.9,
        "entropy": 0.2,
    },
    "flying": {
        "sparsity": 0.0,
        "n_pieces": 0.1, 
        "n_mills": 0.9,
        "entropy": 0.2,
    },
}


N_REPITITIONS = 55
