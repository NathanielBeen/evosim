from typing import List
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .organism import Organism

from .node import ActionTypes

class Coord:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def mapString(self):
        return f'{self.x}_{self.y}'
    
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
        self.organisms: list[Organism] = []
        self.organismLocs: dict[str, Organism] = {}

    def initGeneration(self, organisms: list['Organism']):
        self.organisms = organisms
        self.organismLocs = {f'{org.loc.x}_{org.loc.y}': org for org in self.organisms}

    def updateLoc(self, org: 'Organism', loc: Coord):
        del self.organismLocs[org.loc.mapString()]
        org.loc = loc
        self.organismLocs[loc.mapString()] = org

    def locIsValidForMove(self, loc: Coord) -> bool:
        if (loc.x < 0 or loc.x >= self.width or loc.y < 0 or loc.y >= self.height):
            return False
        return not self.locOccupied(loc)

    def locOccupied(self, loc: Coord) -> bool:
        return loc.mapString() in self.organismLocs
    
    # given a location and a distance, return the desnity of organisms within that distance.
    def getDensityWithinDistance(self, loc: Coord, distance: int) -> bool:
        condition = lambda org: abs(loc.x - org.loc.x) + abs(loc.y - org.loc.y) <= distance
        return self.getDensity(condition, 100)
    
    # return the density of organisms in a cone in front of an organism. The "front" is determined
    # by the last most that organism took.
    def getDensityWithinDistanceDirected(self, loc: Coord, distance: int, dir: ActionTypes):
        check = lambda _: False

        if dir == ActionTypes.MOVE_NEG_X:
            newX = loc.x - distance
            newLoc = Coord(newX, loc.y)
            check = lambda org: org.loc.x >= newX and abs(newLoc.x - org.loc.x) + abs(newLoc.y - org.loc.y) <= distance

        elif dir == ActionTypes.MOVE_POS_X:
            newX = loc.x + distance
            newLoc = Coord(newX, loc.y)
            check = lambda org: org.loc.x <= newX and abs(newLoc.x - org.loc.x) + abs(newLoc.y - org.loc.y) <= distance

        elif dir == ActionTypes.MOVE_NEG_Y:
            newY = loc.y + distance
            newLoc = Coord(loc.x, newY)
            check = lambda org: org.loc.y <= newY and abs(newLoc.x - org.loc.x) + abs(newLoc.y - org.loc.y) <= distance

        elif dir == ActionTypes.MOVE_POS_Y:
            newY = loc.y - distance
            newLoc = Coord(loc.x, newY)
            check = lambda org: org.loc.y >= newY and abs(newLoc.x - org.loc.x) + abs(newLoc.y - org.loc.y) <= distance

        return self.getDensity(check, 100)
    
    def getDensity(self, condition, totalPossible):
        return len([org for org in self.organisms if condition(org)]) / totalPossible