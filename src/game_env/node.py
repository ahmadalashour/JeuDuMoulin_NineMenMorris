import dataclasses as dc


@dc.dataclass
class Node:
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
