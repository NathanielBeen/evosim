from simulation import Simulation
from graph import Graph

simul = Simulation()
simul.createGeneration()

graph = Graph(simul.grid)
graph.drawFrame()

for i in range(100):
    simul.executeSimStep()
    graph.drawFrame()

graph.saveVideo()