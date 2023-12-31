from typing import List

class SenseTypes:
    DISTANCE_FROM_NEAREST_EDGE = 0
    DISTANCE_FROM_NEAREST_X_EDGE = 1
    DISTANCE_FROM_NEAREST_Y_EDGE = 2

class ActionTypes:
    MOVE_POS_X = 0
    MOVE_NEG_X = 1
    MOVE_POS_Y = 2
    MOVE_NEG_Y = 3

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
            if self.id == SenseTypes.DISTANCE_FROM_NEAREST_EDGE:
                return 'dE'
            if self.id == SenseTypes.DISTANCE_FROM_NEAREST_X_EDGE:
                return 'dXE'
            if self.id == SenseTypes.DISTANCE_FROM_NEAREST_Y_EDGE:
                return 'dYE'
        if self.type == NodeType.ACTION:
            if self.id == ActionTypes.MOVE_NEG_X:
                return 'm-X'
            if self.id == ActionTypes.MOVE_POS_X:
                return 'm+X'
            if self.id == ActionTypes.MOVE_NEG_Y:
                return 'm-Y'
            if self.id == ActionTypes.MOVE_POS_Y:
                return 'm+Y'
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