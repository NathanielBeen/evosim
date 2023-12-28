import pygraphviz as pgv

from brain import Brain

ASSET_FOLDER = "/home/nathaniel/Dev/evosim_assets"

def drawGraph(brain: Brain):
    graph = pgv.AGraph(strict=False, directed=True, rankdir="LR")

    for node in [*brain.senseNodes, *brain.innerNodes, *brain.actionNodes]:
        graph.add_node(node.name())

        for conn in node.connections:
                if conn.input == node:
                    graph.add_edge(node.name(), conn.output.name())

    graph.layout("dot")
    graph.draw(f"{ASSET_FOLDER}/graph.png")
