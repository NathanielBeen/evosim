from typing import List
import random
from datetime import datetime

from config import Config
from .grid import Grid
from .organism import Organism
from .output import Output
from .survivalCriteria import SideSurvialCriteria, SideSurvivalType
from .genome_similarity import calcGenerationSimiarity

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
            newOrganisms = [Organism.gen_random(id, self.grid) for id in range(Config.get(Config.ORGANSISMS))]
        elif Config.get(Config.MATING_STRATEGY) == 0:
            newOrganisms = self.randomMating(self.organisms)
        else:
            newOrganisms = self.geneticSimilarityMating(self.organisms)
        
        calcGenerationSimiarity(newOrganisms, 3)
        self.organisms = newOrganisms
        # the grid will place new organisms in a random starting location
        self.grid.initGeneration(self.organisms)

    # generate a new set of organisms by randomly selecting survivors and splicing their genomes together
    def randomMating(self, survivors: list[Organism]) -> list[Organism]:
        newOrganisms = []
        for id in range(Config.get(Config.ORGANSISMS)):
                parent = survivors[random.randint(0, len(survivors) - 1)]
                parent2 = survivors[random.randint(0, len(survivors) - 1)]
                newOrganisms.append(Organism.gen_from_parents(id, self.grid, parent, parent2))
        return newOrganisms

    # generate a new set of organisms by matching survivors that are genetically similar to each other
    # and then splicing their genomes together
    def geneticSimilarityMating(self, survivors: list[Organism]) -> list[Organism]:
        pairedSurvivors = {}
        survivorPairs = []

        for survivor in survivors:
            # we will only end up going through around half of the survivors, as the other half
            # will be matched, so exit early if we have found all the pairs
            if len(survivorPairs) * 2 >= len(survivors) - 1:
                break

            if not survivor.id in pairedSurvivors:
                match = None
                matchDifference = None

                # find the organism that has not already been matched that is most genetically
                # similar to the current survivor
                for potentialMatch in survivors:
                    if not potentialMatch.id in pairedSurvivors and potentialMatch != survivor:
                        difference = survivor.similarity.getWeightedDifference(potentialMatch.similarity)
                        if not matchDifference or difference < matchDifference:
                            match = potentialMatch
                            matchDifference = difference

                pairedSurvivors[survivor.id] = True
                pairedSurvivors[match.id] = True
                survivorPairs.append([survivor, match])
        
        newOrganisms = []
        for id in range(Config.get(Config.ORGANSISMS)):
            index = id % len(survivorPairs)
            newOrganisms.append(Organism.gen_from_parents(id, self.grid, survivorPairs[index][0], survivorPairs[index][1]))
                
        return newOrganisms

    def determineSurvivors(self):
        return [org for org in self.organisms if self.survivalStrategy.survived(org)]