from typing import List
import random

from runConfig import GRID_HEIGHT, GRID_WIDTH, NUM_ORGANISMS
from grid import Grid, Coord
from organism import Organism

class Simulation:
    def __init__(self):
        self.grid = Grid(GRID_WIDTH, GRID_HEIGHT)
        self.simStep = 0
        self.organisms: List[Organism] = []
    
    # creates a set of organsisms (either with random genes or based on parents)
    # and places then randomly in the grid
    def createGeneration(self):
        newOrganisms: List[Organism] = []
        if self.simStep == 0:
            newOrganisms = [Organism.gen_random(self.grid) for _ in range(NUM_ORGANISMS)]
        else:
            for _ in range(NUM_ORGANISMS):
                # select random parents for each organism. There's opportunity here for a more
                # sophisticated "mating" system that uses proximity or score or something instead
                parent = self.organisms[random.randint(0, len(self.organisms) - 1)]
                parent2 = self.organisms[random.randint(0, len(self.organisms) - 1)]
                newOrganisms.append(Organism.gen_from_parents(parent, parent2))
        
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