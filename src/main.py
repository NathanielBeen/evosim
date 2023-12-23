from simulation import Simulation
from graph import Graph

simul = Simulation()
simul.createGeneration()

graph = Graph(simul.grid)

simul.executeSimStep()