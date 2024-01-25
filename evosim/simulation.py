from typing import List
import random
from datetime import datetime

from .runConfig import GRID_HEIGHT, GRID_WIDTH, NUM_ORGANISMS, NUM_STEPS_PER_GENERATION, NUM_GENERATIONS
from .grid import Grid, Coord
from .organism import Organism
from .output import Output
from .survivalCriteria import CornerSurvivalCriteria

class Simulation:
    def __init__(self):
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT)
        self.survivalStrategy = CornerSurvivalCriteria(20)
        self.output = Output(self.grid, self.survivalStrategy)
        self.organisms: List[Organism] = []

    def runSimulation(self):
        start = datetime.now()
        for gen in range(NUM_GENERATIONS):
            self.createGeneration(gen)
            self.output.stepComplete(gen)

            for _ in range(NUM_STEPS_PER_GENERATION):
                for organism in self.organisms:
                    organism.performStep()
                self.output.stepComplete(gen)

            survivors = self.determineSurvivors()
            self.output.generationComplete(self.organisms, len(survivors), gen)

            self.organisms = survivors

        self.output.simulationComplete()
        end = datetime.now()
        print(f'Total time {end - start}')
    
    # creates a set of organsisms (either with random genes or based on parents)
    # and places then randomly in the grid
    def createGeneration(self, generationNumber):
        newOrganisms: List[Organism] = []
        if generationNumber == 0:
            newOrganisms = [Organism.gen_random(self.grid) for _ in range(NUM_ORGANISMS)]
        else:
            for _ in range(NUM_ORGANISMS):
                # select random parents for each organism. There's opportunity here for a more
                # sophisticated "mating" system that uses proximity or score or something instead
                parent = self.organisms[random.randint(0, len(self.organisms) - 1)]
                parent2 = self.organisms[random.randint(0, len(self.organisms) - 1)]
                newOrganisms.append(Organism.gen_from_parents(self.grid, parent, parent2))
        
        self.organisms = newOrganisms

        usedLocations = set()
        for organism in self.organisms:
            proposedLoc = Coord(
                random.randint(0, self.grid.width - 1), 
                random.randint(0, self.grid.height - 1)
            )
            attempts = 0
            # generate locations randomly until we come across one that is not occupied
            # it is possible that this could become extremely expensive or even loop forever,
            # but as long as there is a relatively low population density we shouldn't expect
            # many repeat locations
            while proposedLoc in usedLocations:
                attempts += 1
                proposedLoc = Coord(
                    random.randint(0, self.grid.width - 1), 
                    random.randint(0, self.grid.height - 1)
                )
            
            organism.loc = proposedLoc
            usedLocations.add(proposedLoc)
        
        self.grid.initGeneration(newOrganisms)

    def determineSurvivors(self):
        return [org for org in self.organisms if self.survivalStrategy.survived(org)]