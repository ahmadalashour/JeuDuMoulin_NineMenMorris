import dataclasses as dc


@dc.dataclass
class Node:
    """
    Represents a node on a board. The node is represented by a string, like 'a1', where 'a' is the row and '1' is the column.

    Attributes:
        str_repr (str): The string representation of the node, like 'a1', where 'a' is the column and '1' is the row.
        _x (int): The x-coordinate, calculated from str_repr, private and not initialized directly.
        _y (int): The y-coordinate, calculated from str_repr, private and not initialized directly.
    """

    str_repr: str
    _x: int = dc.field(init=False)
    _y: int = dc.field(init=False)

    def __post_init__(self):
        """Converts the string representation to numerical coordinates after the object's initialization."""
        self._x = ord(self.str_repr[0]) - 97
        self._y = 6 - int(self.str_repr[1])

    @property
    def x(self):
        """Getter for the x-coordinate. provided to other classes in a safe read-only way."""
        return self._x

    @property
    def y(self):
        """Getter for the y-coordinate. provided to other classes in a safe read-only way."""
        return self._y

    @classmethod
    def from_coords(cls, x: int, y: int) -> "Node":
        """
        Method to create a Node instance from x, y coordinates.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.

        Returns:
            Node: A new Node object initialized from the specified coordinates.
        """
        try:
            # Attempt to create a Node using calculated string representation from coordinates
            return cls(str_repr=chr(x + 97) + str(6 - y))
        except TypeError:
            # Handele any errors by creating a dummy node.
            new_cls = cls(str_repr="a0")  # Dummy node
            new_cls._x = x
            new_cls._y = y
            return new_cls

    def __repr__(self):
        """Defines the "official" string representation of the object."""
        return self.str_repr

    def __eq__(self, other):
        """Check equality based on the string representation."""
        return self.str_repr == other.str_repr

    def __hash__(self):
        """Return the hash based on the string representation."""
        return hash(self.str_repr)

    def __sub__(self, other):
        """Define subtraction to find the vector difference between two nodes."""
        return (self.x - other.x, self.y - other.y)

    def __abs__(self):
        """Return the Manhattan distance (absolute value) between two nodes."""
        return abs(self.x) + abs(self.y)

    def __gt__(self, other):
        """Greater than comparison based on x and then y coordinates."""
        return self.x > other.x or (self.x == other.x and self.y > other.y)

    def __lt__(self, other):
        """Less than comparison based on x and then y coordinates."""
        return self.x < other.x or (self.x == other.x and self.y <= other.y)

    def __ge__(self, other):
        """Greater than or equal to comparison based on x and then y coordinates."""
        return self.x >= other.x and self.y >= other.y
