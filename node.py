from typing import List


class NodeType:
    SENSE = 0
    INNER = 1
    ACTION = 2


class Node:
    def _init__(self, type: NodeType, id: int):
        self.type = type
        self.id = id
        self.connections: List[NodeConnection] = []
        self.value = 0

    def hasOutput(self):
        return any(conn.output != self for conn in self.connections)
    
    def applyConnections(self):
        for conn in self.connections:
            if conn.output == self:
                conn.applyConnection()

    def removeConnections(self):
        for conn in self.connections:
            conn.remove()
    
    def reset(self):
        self.value = 0


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