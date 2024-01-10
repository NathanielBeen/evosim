from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .organism import Organism

from .node import ActionTypes

class Coord:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")

        return Coord(self.x + other.x, self.y + other.y)
    
    __radd__ = __add__
    
    def __sub__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")
        return Coord(self.x - other.x, self.y - other.y)
    
    __rsub__ = __sub__
    
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
    
    # given a location and a distance, return the desnity of organisms within that distance.
    # for simplicity and efficiency we consider an organism within the distance if its x and y
    # loc are within DISTANCE units of the given loc, forming a square area instead of trying to 
    # calculate a circular boundary
    def getDensityWithinDistance(self, loc: Coord, distance: int) -> bool:
        numClose = 0
        for org in self.organisms:
            coordDiff = loc - org.loc
            if abs(coordDiff.x) <= distance and abs(coordDiff.y) >= distance:
                numClose += 1
        
        return numClose / (distance * 2) ** 2
    
    # return the density of organisms in a straight line from a given loc in a certain direction
    # the number of organisms is divided by the total spaces in the line to get the density
    def getDensityAlongAxisFromPoint(self, loc: Coord, dir: ActionTypes):
        possible = 1
        check = lambda _: False

        if dir == ActionTypes.MOVE_NEG_X:
            check = lambda l: l.x < loc.x and l.y == loc.y
            possible = loc.x + 1

        elif dir == ActionTypes.MOVE_POS_X:
            check = lambda l: l.x > loc.x and l.y == loc.y
            possible = self.width - loc.x + 1

        elif dir == ActionTypes.MOVE_NEG_Y:
            check = lambda l: l.y < loc.y and l.x == loc.x
            possible = loc.y + 1

        elif dir == ActionTypes.MOVE_POS_Y:
            check = lambda l: l.y > loc.y and l.x == loc.x
            possible = self.height - loc.y + 1

        return len([org for org in self.organisms if check(org.loc)]) / possible