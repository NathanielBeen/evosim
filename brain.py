from typing import List
import random
import math

from runConfig import NUM_SENSE, NUM_INTERNAL, NUM_ACTIONS
from node import NodeType, Node, NodeConnection
from genome import Genome

class Action:
    def __init__(self, id: int, value: float):
        self.id = id
        self.value = value

class Brain:
    def __init__(self, genome: Genome):
        self.genome = genome

        nodeMap = self.generateNodes()
        self.removeUselessConnections(nodeMap)

        self.senseNodes = list(nodeMap[NodeType.SENSE].values())
        self.innerNodes = list(nodeMap[NodeType.INNER].values())
        self.actionNodes = list(nodeMap[NodeType.SENSE].values())

    # given a set of genes create a network of sense, inner, and action nodes with node connections
    # between them. 
    def generateNodes(self) -> dict[NodeType, dict[int, Node]]:
        nodes = {
            NodeType.SENSE: {},
            NodeType.INNER: {},
            NodeType.ACTION: {}
        }
        for gene in self.genome.genes:
            inputNodeType = NodeType.SENSE if gene.inputType == 0 else NodeType.INNER
            outputNodeType = NodeType.INNER if gene.outputType == 0 else NodeType.ACTION

            # a gene's input and output ids can be 0 to 999, so use a modulo to convert that value into one that's
            # garunteed to actually point to a node
            inputId = gene.inputNum % NUM_SENSE if inputNodeType == NodeType.SENSE else gene.inputNum % NUM_INTERNAL
            outputId = gene.outputNum % NUM_INTERNAL if inputNodeType == NodeType.INNER else gene.outputNum % NUM_ACTIONS

            if not gene.inputNum in nodes[inputNodeType]:
                nodes[inputNodeType][inputId] = Node(inputNodeType, inputId)

            if not outputId in nodes[outputNodeType]:
                nodes[outputNodeType][outputId] = Node(outputNodeType, outputId)
            
            inputNode: Node = nodes[inputNodeType][inputId]
            outputNode: Node = nodes[outputNodeType][outputId]

            connection = NodeConnection(inputNode, outputNode, gene.weight)
            inputNode.connections.append(connection)
            outputNode.connections.append(connection)
        
        return nodes
    
    # it is possible to end up generating a brain where internal nodes have inputs but no outputs,
    # so remove these useless nodes/connections if they exist. Note that because internal nodes can lead to
    # each other we need to re-check all the inner nodes each time we remove one
    def removeUselessConnections(nodes):
        innerNodesCleaned = False
        while not innerNodesCleaned:
            innerNodesCleaned = True
            for id, node in nodes[NodeType.INNER].items():
                if not node.hasOutput():
                    node.removeConnections()
                    del nodes[NodeType.INNER][id]
                    innerNodesCleaned = False
        
        # if some inner nodes were deleted it is possible that sense nodes have no outputs, so remove if so
        for id, node in nodes[NodeType.SENSE].items():
            if not node.hasOutput():
                del nodes[NodeType.SENSE][id]

    # determine which actions this individual will take given the NodeConnections and 
    # populated sense nodes. Each action node will end up generating a value between 0 and 1,
    # which is the probability that action will be taken.
    def determineAction(self) -> list[Action]:
        actions = []
        
        for node in [*self.innerNodes, *self.actionNodes]:
            node.applyConnections()
        
        actions: List[int] = []
        for node in self.nodes:
            if node.type == NodeType.ACTION:
                # convert the node value to a value between 0 and 1
                triggerChance = math.tanh(node.value) / 2 + 1

                # some actions are binary (either occur or don't), but others change float values on
                # the individual so we need to pass back both the id and the value
                if random.random() < triggerChance:
                    actions.append(Action(node.id, triggerChance))
    
    # reset all node values to 0
    def clearNodes(self):
        for node in [*self.senseNodes, *self.innerNodes, *self.actionNodes]:
            node.reset()