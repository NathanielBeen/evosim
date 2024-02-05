from typing import List

class SenseTypes:
    X_LOC = 0
    Y_LOC = 1

    DISTANCE_FROM_NEAREST_EDGE = 2
    DISTANCE_FROM_NEAREST_X_EDGE = 3
    DISTANCE_FROM_NEAREST_Y_EDGE = 4
    DISTANCE_FROM_FORWARD_EDGE = 5
    DISTANCE_FROM_LR_EDGE = 6

    DISTANCE_FROM_FORWARD_BOUNDARY = 7
    DISTANCE_FROM_LR_BOUNDARY = 8
    DISTANCE_FROM_NEAREST_X_BOUNDARY = 9
    DISTANCE_FROM_NEAREST_Y_BOUNDARY = 10

    POPULATION_CLOSE = 11
    POPULATION_FORWARD = 12

    DISTANCE_FROM_FORWARD_ORGANISM = 13
    DISTANCE_FROM_LR_ORGANISM = 14

    AGE = 15

    @staticmethod
    def count():
        return SenseTypes.AGE + 1
    
    @staticmethod
    def name(type: 'SenseTypes'):
        if type == SenseTypes.X_LOC:
            return 'xL'
        if type == SenseTypes.Y_LOC:
            return 'yL'
        if type == SenseTypes.DISTANCE_FROM_NEAREST_EDGE:
            return 'dE'
        if type == SenseTypes.DISTANCE_FROM_NEAREST_X_EDGE:
            return 'dXE'
        if type == SenseTypes.DISTANCE_FROM_NEAREST_Y_EDGE:
            return 'dYE'
        if type == SenseTypes.DISTANCE_FROM_FORWARD_EDGE:
            return 'dFE'
        if type == SenseTypes.DISTANCE_FROM_LR_EDGE:
            return 'dLRE'
        if type == SenseTypes.DISTANCE_FROM_FORWARD_BOUNDARY:
            return 'dFB'
        if type == SenseTypes.DISTANCE_FROM_LR_BOUNDARY:
            return 'dLRB'
        if type == SenseTypes.DISTANCE_FROM_NEAREST_X_BOUNDARY:
            return 'dXB'
        if type == SenseTypes.DISTANCE_FROM_NEAREST_Y_BOUNDARY:
            return 'dYB'
        if type == SenseTypes.POPULATION_CLOSE:
            return 'pC'
        if type == SenseTypes.POPULATION_FORWARD:
            return 'pF'
        if type == SenseTypes.DISTANCE_FROM_FORWARD_ORGANISM:
            return 'fO'
        if type == SenseTypes.DISTANCE_FROM_LR_ORGANISM:
            return 'lrO'
        if type == SenseTypes.AGE:
            return 'A'
        return 'unknown'


class ActionTypes:
    MOVE_POS_X = 0
    MOVE_NEG_X = 1
    MOVE_POS_Y = 2
    MOVE_NEG_Y = 3
    MOVE_FORWARD = 4
    MOVE_LEFT = 5
    MOVE_RIGHT = 6
    MOVE_RANDOM = 7

    @staticmethod
    def count():
        return ActionTypes.MOVE_RANDOM + 1
    
    @staticmethod
    def name(type: 'ActionTypes'):
        if type == ActionTypes.MOVE_NEG_X:
            return 'm-X'
        if type == ActionTypes.MOVE_POS_X:
            return 'm+X'
        if type == ActionTypes.MOVE_NEG_Y:
            return 'm-Y'
        if type == ActionTypes.MOVE_POS_Y:
            return 'm+Y'
        if type == ActionTypes.MOVE_RANDOM:
            return 'mR'
        if type == ActionTypes.MOVE_FORWARD:
            return 'mF'
        if type == ActionTypes.MOVE_LEFT:
            return 'mL'
        if type == ActionTypes.MOVE_RIGHT:
            return 'mR'
        return 'unknown'
    
    @staticmethod
    def leftDir(type: 'ActionTypes'):
        if type == ActionTypes.MOVE_NEG_X:
            return ActionTypes.MOVE_NEG_Y
        if type == ActionTypes.MOVE_POS_X:
            return ActionTypes.MOVE_POS_Y
        if type == ActionTypes.MOVE_NEG_Y:
            return ActionTypes.MOVE_NEG_X
        if type == ActionTypes.MOVE_POS_Y:
            return ActionTypes.MOVE_POS_X
        
    @staticmethod
    def rightDir(type: 'ActionTypes'):
        if type == ActionTypes.MOVE_NEG_X:
            return ActionTypes.MOVE_POS_Y
        if type == ActionTypes.MOVE_POS_X:
            return ActionTypes.MOVE_NEG_Y
        if type == ActionTypes.MOVE_NEG_Y:
            return ActionTypes.MOVE_POS_X
        if type == ActionTypes.MOVE_POS_Y:
            return ActionTypes.MOVE_NEG_X

class NodeType:
    SENSE = 0
    INNER = 1
    ACTION = 2


class Node:
    def __init__(self, type: NodeType, id: int):
        self.type = type
        self.id = id
        self.connections: List[NodeConnection] = []
        self.value = 0
        self.willDelete = False

    def hasOutput(self):
        return any(conn.output != self and not conn.output.willDelete for conn in self.connections)
    
    def hasInput(self):
        return any(conn.input != self and not conn.input.willDelete for conn in self.connections)
    
    def applyConnections(self):
        for conn in self.connections:
            if conn.output == self:
                conn.applyConnection()

    def removeConnections(self):
        for conn in self.connections:
            conn.remove()
    
    def reset(self):
        self.value = 0

    def name(self):
        if self.type == NodeType.SENSE:
            return SenseTypes.name(self.id)
        if self.type == NodeType.ACTION:
            return ActionTypes.name(self.id)
        return str(self.id)
    
    def color(self):
        if self.type == NodeType.SENSE:
            return "black"
        if self.type == NodeType.ACTION:
            return "gold"
        if self.type == NodeType.INNER:
            return "grey"


class NodeConnection:
    def __init__(self, input: Node, output: Node, weight: int):
        self.input = input
        self.output = output
        self.weight = weight
    
    def remove(self):
        self.input.connections = [conn for conn in self.input.connections if conn != self]
        self.output.connections = [conn for conn in self.output.connections if conn != self]

    
    def applyConnection(self):
        self.output.value += self.input.value * self.weight

    def width(self):
        return max(abs(self.weight), .5)

    def color(self):
        return "blue" if self.weight > 0 else "red"