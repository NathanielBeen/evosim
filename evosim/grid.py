import random

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .organism import Organism

from .node import ActionTypes
from .coord import Coord
from .obstacle import Obstacle

class Grid:
    def __init__(self, width: int, height: int, obstacles: list[dict[str, int]]):
        self.width = width
        self.height = height
        self.organisms: list[Organism] = []
        self.organismLocs: dict[str, Organism] = {}

        self.obstacles = [Obstacle(obs[0], obs[1], obs[2], obs[3]) for obs in obstacles]

        # this creates a map of every space on the grid blocked by an obstacle. While this is an expensive call,
        # checking a location is valid for a move happens around NUM_ORGANISMS * NUM_STEPS * NUM_GENERATIONS times,
        # so ensuring a fast lookup there is more important
        self.blockedLocs = {}
        for obs in self.obstacles:
            for loc in obs.getBlockedSpaces():
                self.blockedLocs[loc.mapString()] = True

    def initGeneration(self, organisms: list['Organism']):
        self.organisms = organisms
        self.organismLocs = {}

        for organism in self.organisms:
            proposedLoc = Coord(
                random.randint(0, self.width - 1), 
                random.randint(0, self.height - 1)
            )
            proposedMapString = proposedLoc.mapString()

            # generate locations randomly until we come across one that is not occupied
            # it is possible that this could become extremely expensive or even loop forever,
            # but as long as there is a relatively low population density we shouldn't expect
            # many repeat locations
            while proposedMapString in self.organismLocs or proposedMapString in self.blockedLocs:
                proposedLoc = Coord(
                    random.randint(0, self.width - 1), 
                    random.randint(0, self.height - 1)
                )
                proposedMapString = proposedLoc.mapString()
            
            organism.loc = proposedLoc
            self.organismLocs[proposedMapString] = organism

    def updateLoc(self, org: 'Organism', loc: Coord):
        del self.organismLocs[org.loc.mapString()]
        org.loc = loc
        self.organismLocs[loc.mapString()] = org

    def locIsAvailable(self, loc: Coord) -> bool:
        if (loc.x < 0 or loc.x >= self.width or loc.y < 0 or loc.y >= self.height):
            return False
        mapStr = loc.mapString()
        return not mapStr in self.organismLocs and not mapStr in self.blockedLocs
    
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
    
    def getDensity(self, condition, totalPossible: int):
        return len([org for org in self.organisms if condition(org)]) / totalPossible


    # get the distance to the nearest boundary in the given direction, up to the max distance
    def getBoundaryDistance(self, loc: Coord, maxDistance: int, dir: ActionTypes):
        check = lambda loc: loc.mapString() in self.blockedLocs
        val = self.getLocConditionWithinDirectedDistance(check, loc, maxDistance, dir)
        return val
    
    # get the distance to the nearest organism in the given direction, up to the max distance
    def getOccupiedDistance(self, loc: Coord, maxDistance: int, dir: ActionTypes):
        check = lambda loc: loc.mapString() in self.organismLocs
        return self.getLocConditionWithinDirectedDistance(check, loc, maxDistance, dir)
    
    def getLocConditionWithinDirectedDistance(self, condition, loc: Coord, distance: int, dir: ActionTypes):
        dirCoord = Coord(0, 0)
        if dir == ActionTypes.MOVE_NEG_X:
            dirCoord.x = -1
        elif dir == ActionTypes.MOVE_POS_X:
            dirCoord.x = 1
        elif dir == ActionTypes.MOVE_NEG_Y:
            dirCoord.y = -1
        elif dir == ActionTypes.MOVE_POS_Y:
            dirCoord.y = 1

        testCoord = Coord(loc.x, loc.y)
        for i in range(distance):
            testCoord += dirCoord
            if testCoord.mapString() in self.blockedLocs:
                return i / distance
        
        return 1