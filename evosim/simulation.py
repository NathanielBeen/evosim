from typing import List
import random
from datetime import datetime

from config import Config
from .grid import Grid
from .coord import Coord
from .organism import Organism
from .output import Output
from .survivalCriteria import SideSurvialCriteria, SideSurvivalType

class Simulation:
    def __init__(self, outputFolder):
        self.grid = Grid(Config.get(Config.GRID_WIDTH), Config.get(Config.GRID_HEIGHT), Config.get(Config.OBSTACLES))
        self.survivalStrategy = SideSurvialCriteria(SideSurvivalType.RIGHT, 10)
        self.output = Output(outputFolder, self.grid, self.survivalStrategy)
        self.organisms: List[Organism] = []

    def runSimulation(self):
        start = datetime.now()
        for gen in range(Config.get(Config.GENERATIONS)):
            self.createGeneration(gen)
            self.output.generationStarted(self.organisms, gen)

            for _ in range(Config.get(Config.STEPS)):
                for organism in self.organisms:
                    organism.performStep()
                self.output.stepComplete()

            survivors = self.determineSurvivors()
            self.output.generationComplete(len(survivors))

            self.organisms = survivors

        self.output.simulationComplete()
        end = datetime.now()
        print(f'Total time {end - start}')
    
    # creates a set of organsisms (either with random genes or based on parents)
    # and places then randomly in the grid
    def createGeneration(self, generationNumber):
        newOrganisms: List[Organism] = []
        if generationNumber == 0:
            newOrganisms = [Organism.gen_random(self.grid) for _ in range(Config.get(Config.ORGANSISMS))]
        else:
            for _ in range(Config.get(Config.ORGANSISMS)):
                # select random parents for each organism. There's opportunity here for a more
                # sophisticated "mating" system that uses proximity or score or something instead
                parent = self.organisms[random.randint(0, len(self.organisms) - 1)]
                parent2 = self.organisms[random.randint(0, len(self.organisms) - 1)]
                newOrganisms.append(Organism.gen_from_parents(self.grid, parent, parent2))
        
        self.organisms = newOrganisms
        # the grid will place new organisms in a random starting location
        self.grid.initGeneration(self.organisms)

    def determineSurvivors(self):
        return [org for org in self.organisms if self.survivalStrategy.survived(org)]