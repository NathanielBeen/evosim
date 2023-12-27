from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from organism import Organism

class Coord:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")

        return Coord(self.x + other.x, self.y + other.y)
    
    def __radd__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")

        return Coord(self.x + other.x, self.y + other.y)
    
    def __iadd__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")

        self.x += other.x
        self.y += other.y
        return self
    
    def __eq__(self, other):
        return isinstance(other, Coord) and self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))


class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.organisms: List[Organism] = []

    
    def locIsValidForMove(self, loc: Coord) -> bool:
        if (loc.x < 0 or loc.x >= self.width or loc.y < 0 or loc.y >= self.height):
            return False
        for organism in self.organisms:
            if organism.loc == loc:
                return False
        return True