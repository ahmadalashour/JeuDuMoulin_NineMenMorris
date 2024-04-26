import dataclasses as dc


@dc.dataclass
class Node:
    """Class to represent a node in the board.

    Args:
        str_repr (str): The string representation of the node.
    """

    str_repr: str
    _x: int = dc.field(init=False)
    _y: int = dc.field(init=False)

    def __post_init__(self):
        self._x = ord(self.str_repr[0]) - 97
        self._y = 6 - int(self.str_repr[1])

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @classmethod
    def from_coords(cls, x: int, y: int) -> "Node":  # Bad habit
        """Method to create a node from coordinates.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.

        Returns:
            Node: The node created.
        """
        try:
            return cls(str_repr=chr(x + 97) + str(6 - y))
        except TypeError:
            new_cls = cls(str_repr="a0")
            new_cls._x = x
            new_cls._y = y
            return new_cls

    def __repr__(self):
        return self.str_repr

    def __eq__(self, other):
        return self.str_repr == other.str_repr

    def __hash__(self):
        return hash(self.str_repr)

    def __sub__(self, other):
        return (self.x - other.x, self.y - other.y)

    def __abs__(self):
        return abs(self.x) + abs(self.y)

    def __gt__(self, other):
        return self.x > other.x or (self.x == other.x and self.y > other.y)

    def __lt__(self, other):
        return self.x < other.x or (self.x == other.x and self.y < other.y)

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __ge__(self, other):
        return self.x >= other.x and self.y >= other.y
