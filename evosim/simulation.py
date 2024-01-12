from typing import List
import random
import math
from datetime import datetime

from .runConfig import GRID_HEIGHT, GRID_WIDTH, NUM_ORGANISMS, NUM_STEPS_PER_GENERATION, NUM_GENERATIONS
from .grid import Grid, Coord
from .organism import Organism
from .genome import genome_similarity
from .video import Video
from .survivalCriteria import CornerSurvivalCriteria
from .graph import drawGraph

class Simulation:
    def __init__(self):
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT)
        self.survivalStrategy = CornerSurvivalCriteria(20)
        self.video = Video(self.grid, self.survivalStrategy)
        self.organisms: List[Organism] = []

    def runSimulation(self):
        start = datetime.now()
        for gen in range(NUM_GENERATIONS):
            self.createGeneration(gen)

            willRecord = self.willRecordGeneration(gen)
            if willRecord:
                self.determineOrganismColors()
                self.video.drawFrame()

            for _ in range(NUM_STEPS_PER_GENERATION):
                for organism in self.organisms:
                    organism.performStep()
                if willRecord:
                    self.video.drawFrame()

            if willRecord:
                self.video.saveVideo(gen)
                drawGraph(self.organisms, gen)

            self.organisms = self.determineSurvivors()
            print(f'Number of survivors {len(self.organisms)}')
        end = datetime.now()
        print(f'Total time {end - start}')
        
    
    def willRecordGeneration(self, genNumber):
        return genNumber == NUM_GENERATIONS - 1 or genNumber % 100 == 0
    
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

    def determineOrganismColors(self):
        redBenchmark = self.grid.organisms[random.randint(0, len(self.grid.organisms) - 1)]
        greenBenchmark = redBenchmark
        blueBenchmark = redBenchmark

        for org in self.grid.organisms:
            similarity = genome_similarity(redBenchmark.brain.genome, org.brain.genome)
            org.color.red = math.floor(similarity * 255)

            if org.color.red < greenBenchmark.color.red:
                greenBenchmark = org
        
        for org in self.grid.organisms:
            similarity = genome_similarity(greenBenchmark.brain.genome, org.brain.genome)
            org.color.green = math.floor(similarity * 255)

            if org.color.red + org.color.green < blueBenchmark.color.red + blueBenchmark.color.green:
                blueBenchmark = org
            
        for org in self.grid.organisms:
            similarity = genome_similarity(blueBenchmark.brain.genome, org.brain.genome)
            org.color.blue = math.floor(similarity * 255)