import pygraphviz as pgv

from .organism import Organism

ASSET_FOLDER = "/home/nathaniel/Dev/evosim_assets"

def drawGraph(organisms: list[Organism], genNumber: int):

    # find the most average organism to graph (defined by having the highest average similarity)
    averageOrg: Organism = None
    highestSim = 0

    for org in organisms:
         similarity = org.color.red + org.color.green + org.color.blue
         if similarity > highestSim:
              averageOrg = org

    graph = pgv.AGraph(strict=False, directed=True, rankdir="LR")

    for node in [*averageOrg.brain.senseNodes, *averageOrg.brain.innerNodes, *averageOrg.brain.actionNodes]:
        graph.add_node(node.name(), color=node.color())

        for conn in node.connections:
                if conn.input == node:
                    graph.add_edge(node.name(), conn.output.name(), penwidth=conn.width(), color=conn.color(), len=2)

    graph.layout()
    graph.draw(f"{ASSET_FOLDER}/graph_{genNumber}.png")
