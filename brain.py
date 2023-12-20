from typing import List
import random
import math

from runConfig import NUM_SENSE, NUM_INTERNAL, NUM_ACTIONS
from node import NodeType, Node, NodeConnection
from genome import Genome

class Brain:
    def __init__(self, genome: Genome):
        self.genome = genome
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
        