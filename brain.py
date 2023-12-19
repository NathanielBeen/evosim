from typing import List
import random
import math

from genome import Genome
from node import NodeType, Node, NodeConnection

class Brain:
    def __init__(self):
        self.genome = None
        self.senseNodes: List[Node] = []
        self.innerNodes: List[Node] = []
        self.actionNodes: List[Node] = []
    
    def create_brain(self):
        nodeMap = self.generateNodes()
        self.removeUselessConnections(nodeMap)

        self.senseNodes = nodeMap[NodeType.SENSE]
        self.innerNodes = nodeMap[NodeType.INNER]
        self.actionNodes = nodeMap[NodeType.SENSE]

    def generateNodes(self):
        nodes = {
            NodeType.SENSE: {},
            NodeType.INNER: {},
            NodeType.ACTION: {}
        }
        for gene in self.genome.genes:
            inputNodeType = NodeType.SENSE if gene.inputType == 0 else NodeType.INNER
            outputNodeType = NodeType.INNER if gene.outputType == 0 else NodeType.ACTION

            if not gene.inputNum in nodes[inputNodeType]:
                nodes[inputNodeType][gene.inputNum] = Node(inputNodeType, gene.inputNum)

            if not gene.outputNum in nodes[outputNodeType]:
                nodes[outputNodeType][gene.outputNum] = Node(outputNodeType, gene.outputNum)
            
            inputNode: Node = nodes[inputNodeType][gene.inputNum]
            outputNode: Node = nodes[outputNodeType][gene.outputNum]

            connection = NodeConnection(inputNode, outputNode, gene.weight)
            inputNode.connections.append(connection)
            outputNode.connections.append(connection)
        
        return nodes
    
    def removeUselessConnections(nodes):
        # output nodes cannot be created if they dont have an input so we don't need to check them
        # inner nodes can, so we should remove any that dont have outputs (it is possible one inner node
        # leads to another that has no output, so after we remove a node we should re-check the rest)
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

    def determineAction(self):
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
                    actions.append({
                        'id': node.id,
                        'value': triggerChance
                    })

        for node in [*self.innerNodes, *self.actionNodes]:
            node.reset()
        