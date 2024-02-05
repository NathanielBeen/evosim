from typing import List

from config import Config
from .brain import Brain, Action
from .genome import Genome
from .grid import Grid
from .coord import Coord
from .node import SenseTypes, ActionTypes

import random

class OrganismColor:
    def __init__(self):
        self.red = 0
        self.green = 0
        self.blue = 0
    
    def hex(self):
        return '#{:02x}{:02x}{:02x}'.format(self.red, self.green, self.blue)


class Organism:
    def __init__(self, grid: Grid, genome: Genome):
        self.brain = Brain(genome)
        self.loc = Coord(0, 0)
        self.lastMove = ActionTypes.MOVE_NEG_X
        self.age = 0
        
        self.grid = grid
        self.color = OrganismColor()

    @staticmethod
    def gen_random(grid: Grid):
        genome = Genome.gen_random()
        return Organism(grid, genome)
    
    @staticmethod
    def gen_from_parents(grid: Grid, parent: 'Organism', parent2: 'Organism'):
        genome = Genome.gen_from_parents(parent.brain.genome, parent2.brain.genome)
        return Organism(grid, genome)
    
    # perform one complete cycle: reset all the brain nodes, populate sense data, apply all
    # the node connections to generate actions, and execute those actions
    def performStep(self):
        self.age += 1
        self.brain.clearNodes()
        for node in self.brain.senseNodes:
            node.value = self.getSenseValue(node.id)

        actions = self.brain.determineAction()
        self.executeActions(actions)

    # return a value between 0 and 1 that determines how strong a particular node's signal is.
    # for example, if the organism is close to the right edge and we are checking the DISTANCE_FROM_NEAREST_X_EDGE
    # sense, it will return a value close to 0, but if the organism is close to the center it will return 1
    def getSenseValue(self, senseId: int) -> float:
        if senseId == SenseTypes.X_LOC:
            return self.loc.x / self.grid.width
        
        if senseId == SenseTypes.Y_LOC:
            return self.loc.y / self.grid.height

        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_EDGE:
            nearestX = min(self.loc.x, self.grid.width - self.loc.x) / (self.grid.width / 2)
            nearestY = min(self.loc.y, self.grid.height - self.loc.y) / (self.grid.height / 2)
            return min(nearestX, nearestY)

        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_X_EDGE:
            return min(self.loc.x, self.grid.width - self.loc.x) / (self.grid.width / 2)

        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_Y_EDGE:
            return min(self.loc.y, self.grid.height - self.loc.y) / (self.grid.height / 2)
        
        if senseId == SenseTypes.DISTANCE_FROM_FORWARD_EDGE:
            if self.lastMove == ActionTypes.MOVE_NEG_X:
                return self.loc.x
            if self.lastMove == ActionTypes.MOVE_POS_X:
                return self.grid.width - self.loc.x
            if self.lastMove == ActionTypes.MOVE_NEG_Y:
                return self.loc.y
            return self.grid.height - self.loc.y
        
        if senseId == SenseTypes.DISTANCE_FROM_LR_EDGE:
            if self.lastMove == ActionTypes.MOVE_NEG_X or self.lastMove == ActionTypes.MOVE_POS_X:
                return min(self.loc.y, self.grid.height - self.loc.y) / (self.grid.height / 2)
            
            return min(self.loc.x, self.grid.width - self.loc.x) / (self.grid.width / 2)
        
        if senseId == SenseTypes.DISTANCE_FROM_FORWARD_BOUNDARY:
            return self.grid.getBoundaryDistance(self.loc, Config.get(Config.SENSE_DISTANCE), self.lastMove)
        
        if senseId == SenseTypes.DISTANCE_FROM_LR_BOUNDARY:
            return min(
                self.grid.getBoundaryDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.leftDir(self.lastMove)),
                self.grid.getBoundaryDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.rightDir(self.lastMove))
            )
        
        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_X_BOUNDARY:
            return min(
                self.grid.getBoundaryDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.MOVE_NEG_X),
                self.grid.getBoundaryDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.MOVE_POS_X)
            )

        if senseId == SenseTypes.DISTANCE_FROM_NEAREST_Y_BOUNDARY:
            return min(
                self.grid.getBoundaryDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.MOVE_NEG_Y),
                self.grid.getBoundaryDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.MOVE_POS_Y)
            )
        
        if senseId == SenseTypes.POPULATION_CLOSE:
            return self.grid.getDensityWithinDistance(self.loc, Config.get(Config.SENSE_DISTANCE))
        
        if senseId == SenseTypes.POPULATION_FORWARD:
            return self.grid.getDensityWithinDistanceDirected(self.loc, Config.get(Config.SENSE_DISTANCE), self.lastMove)
        
        if senseId == SenseTypes.DISTANCE_FROM_FORWARD_ORGANISM:
            return self.grid.getOccupiedDistance(self.loc, Config.get(Config.SENSE_DISTANCE), self.lastMove)
        
        if senseId == SenseTypes.DISTANCE_FROM_LR_ORGANISM:
            return min(
                self.grid.getOccupiedDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.leftDir(self.lastMove)),
                self.grid.getOccupiedDistance(self.loc, Config.get(Config.SENSE_DISTANCE), ActionTypes.rightDir(self.lastMove))
            )
        
        if senseId == SenseTypes.AGE:
            return self.age / Config.get(Config.STEPS)
 
    def executeActions(self, actionIds: List[Action]):
        moveActions = [action for action in actionIds if self.actionIsMoveAction(action)]
        if len(moveActions) > 0:
            self.executeMoveActions(moveActions)

    # combine all the move actions together to create a new proposed location and move to it
    # (as long as that location is in bounds and unoccupied)
    def executeMoveActions(self, actions: List[Action]):
        proposedMoveDir = Coord(0, 0)

        # simplify the more complicated move actions (ex: move forward) into XY move actions for easier calculations
        simpleActions = []
        for action in actions:

            # if we need to take a random move then generate one of the other move actions and add it to the list
            if action.id == ActionTypes.MOVE_RANDOM:
                simpleActions.append(Action(random.randint(0, 3), 0))

            # if we need to take a forward move then generate a move action based on whatever the organism did last
            elif action.id == ActionTypes.MOVE_FORWARD:
                simpleActions.append(Action(self.lastMove, 0))

            elif action.id == ActionTypes.MOVE_LEFT:
                simpleActions.append(Action(ActionTypes.leftDir(self.lastMove), 0))

            elif action.id == ActionTypes.MOVE_RIGHT:
                simpleActions.append(Action(ActionTypes.rightDir(self.lastMove), 0))
            
            else:
                simpleActions.append(simpleActions)

        for action in actions:
            if action.id == ActionTypes.MOVE_POS_X:
                proposedMoveDir.x += 1
                self.lastMove = action.id

            elif action.id == ActionTypes.MOVE_NEG_X:
                proposedMoveDir.x -= 1
                self.lastMove = action.id

            elif action.id == ActionTypes.MOVE_POS_Y:
                proposedMoveDir.y += 1
                self.lastMove = action.id

            elif action.id == ActionTypes.MOVE_NEG_Y:
                proposedMoveDir.y -= 1
                self.lastMove = action.id

        proposedMove = self.loc + proposedMoveDir
        if self.grid.locIsAvailable(proposedMove):
            self.grid.updateLoc(self, proposedMove)


    def actionIsMoveAction(self, action: Action) -> bool:
        return action.id == ActionTypes.MOVE_NEG_X or action.id == ActionTypes.MOVE_NEG_Y \
            or action.id == ActionTypes.MOVE_POS_X or action.id == ActionTypes.MOVE_POS_Y \
            or action.id == ActionTypes.MOVE_RANDOM or action.id == ActionTypes.MOVE_FORWARD \
            or action.id == ActionTypes.MOVE_LEFT or action.id == ActionTypes.MOVE_RIGHT