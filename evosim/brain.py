from typing import List
import random
import math

from .node import NodeType, Node, NodeConnection
from .genome import Genome, Gene

class Action:
    def __init__(self, id: int, value: float):
        self.id = id
        self.value = value

class Brain:
    def __init__(self, genome: Genome):
        self.genome = genome

        nodeMap = self.generateNodes()

        self.senseNodes = list(nodeMap[NodeType.SENSE].values())
        self.innerNodes = list(nodeMap[NodeType.INNER].values())
        self.actionNodes = list(nodeMap[NodeType.ACTION].values())

        self.removeUselessConnections()

    # given a set of genes create a network of sense, inner, and action nodes with node connections
    # between them. 
    def generateNodes(self) -> dict[NodeType, dict[int, Node]]:
        nodes = {
            NodeType.SENSE: {},
            NodeType.INNER: {},
            NodeType.ACTION: {}
        }
        for gene in self.genome.genes:
            if not gene.inputId in nodes[gene.inputType]:
                nodes[gene.inputType][gene.inputId] = Node(gene.inputType, gene.inputId)

            if not gene.outputId in nodes[gene.outputType]:
                nodes[gene.outputType][gene.outputId] = Node(gene.outputType, gene.outputId)
            
            inputNode: Node = nodes[gene.inputType][gene.inputId]
            outputNode: Node = nodes[gene.outputType][gene.outputId]

            connection = NodeConnection(inputNode, outputNode, gene.weight)
            inputNode.connections.append(connection)
            outputNode.connections.append(connection)
        
        return nodes
    
    # it is possible to end up generating a brain where internal nodes have inputs but no outputs,
    # so remove these useless nodes/connections if they exist. Note that because internal nodes can lead to
    # each other we need to re-check all the inner nodes each time we remove one
    def removeUselessConnections(self):
        innerNodesCleaned = False
        while not innerNodesCleaned:
            innerNodesCleaned = True
            for node in self.innerNodes:
                if not node.willDelete and (not node.hasOutput() or not node.hasInput()):
                    node.removeConnections()
                    node.willDelete = True
                    innerNodesCleaned = False
        
        # if some inner nodes were deleted it is possible that sense nodes have no outputs, so remove if so
        for node in self.senseNodes:
            if not node.hasOutput():
                node.willDelete = True

        for node in self.actionNodes:
            if not node.hasInput():
                node.willDelete = True

        self.innerNodes = [node for node in self.innerNodes if not node.willDelete]
        self.senseNodes = [node for node in self.senseNodes if not node.willDelete]
        self.actionNodes = [node for node in self.actionNodes if not node.willDelete]


    # determine which actions this individual will take given the NodeConnections and 
    # populated sense nodes. Each action node will end up generating a value between 0 and 1,
    # which is the probability that action will be taken.
    def determineAction(self) -> list[Action]:
        actions = []

        for node in [*self.innerNodes, *self.actionNodes]:
            node.applyConnections()

        actions: List[int] = []
        for node in self.actionNodes:
            # convert the node value to a value between 0 and 1
            triggerChance = ( math.tanh(node.value) + 1 ) / 2

            # some actions are binary (either occur or don't), but others change float values on
            # the individual so we need to pass back both the id and the value
            if random.random() < triggerChance:
                actions.append(Action(node.id, triggerChance))

        return actions
    
    # reset all node values to 0
    def clearNodes(self):
        for node in [*self.senseNodes, *self.innerNodes, *self.actionNodes]:
            node.reset()