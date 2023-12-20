from typing import List

from brain import Brain
from genome import Genome
from grid import Coord, Grid

class SenseTypes:
    DISTANCE_FROM_NEAREST_EDGE = 0
    DISTANCE_FROM_NEAREST_X_EDGE = 1
    DISTANCE_FROM_NEAREST_Y_EDGE = 2

class ActionTypes:
    MOVE_POS_X = 0
    MOVE_NEG_X = 1
    MOVE_POS_Y = 2
    MOVE_NEG_Y = 3

class Organism:
    def __init__(self, grid: Grid, genome: Genome):
        self.brain = Brain(genome)
        self.loc = Coord(0, 0)
        self.grid = grid

    @staticmethod
    def gen_random(grid: Grid):
        genome = Genome.gen_random()
        return Organism(grid, genome)
    
    @staticmethod
    def gen_from_parents(grid: Grid, parent: 'Organism', parent2: 'Organism'):
        genome = Genome.gen_from_parents(parent.brain.genome, parent2.brain.genome)
        return Organism(grid, genome)

    def getSenseValue(self, senseId: int) -> float:
        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_EDGE:
            nearestX = min(self.loc.x, self.grid.width - self.loc.x) / (self.grid.width / 2)
            nearestY = min(self.loc.y, self.grid.height - self.loc.y) / (self.grid.height / 2)
            return min(nearestX, nearestY)

        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_X_EDGE:
            return min(self.loc.x, self.grid.width - self.loc.x) / (self.grid.width / 2)

        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_Y_EDGE:
            return min(self.loc.y, self.grid.height - self.loc.y) / (self.grid.height / 2)

    def executeActions(self, actionIds: List[int]):
        moveActions = [id for id in actionIds if self.actionIsMoveAction(id)]
        if len(moveActions) > 0:
            self.executeMoveActions(moveActions)

    def executeMoveActions(self, actionIds: List[int]):
        proposedMoveDir = Coord(0, 0)
        for id in actionIds:
            if id == ActionTypes.MOVE_POS_X:
                proposedMoveDir.x += 1
            elif id == ActionTypes.MOVE_NEG_X:
                proposedMoveDir.x -= 1
            elif id == ActionTypes.MOVE_POS_Y:
                proposedMoveDir.y += 1
            elif id == ActionTypes.MOVE_NEG_Y:
                proposedMoveDir.y -= 1
        
        proposedMove = self.loc + proposedMoveDir
        if self.grid.locIsValidForMove(proposedMove):
            self.loc = proposedMove


    def actionIsMoveAction(self, actionId: int) -> bool:
        return actionId == ActionTypes.MOVE_NEG_X or actionId == ActionTypes.MOVE_NEG_Y \
            or actionId == ActionTypes.MOVE_POS_X or actionId == ActionTypes.MOVE_POS_Y