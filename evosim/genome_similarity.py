import random
import math
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .organism import Organism

from .genome import Gene, Genome

class NFactorGeneticSimilary:
    def __init__(self):
        self.factors = []
        self.colorCode = '#000000'

    def totalSimilarity(self):
        return sum(self.factors)

    def getSimilarityFactor(self, index: int):
        return self.factors[index]

    def addSimilarityFactor(self, similarity: int):
        self.factors.append(similarity)

    def getWeightedDifference(self, other: 'NFactorGeneticSimilary') -> int:
        difference = 0
        for simFactor, otherSimFactor in zip(self.factors, other.factors):
            difference += abs(simFactor - otherSimFactor) ** 2
        return difference


# this assigns each organism a color based upon its similarity to other organisms. If an organism is part of a group where all of the members are at least 90% genetically
# similar to a particular "center organism", then that group will get its own color. All other organisms will be colored black by default.
def calcGenerationColors(organisms: list['Organism']):
    colorOptions = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#42d4f4', '#f032e6', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#000075', '#a9a9a9']
    similarityFactors = np.zeros((len(organisms), len(organisms)))

    # compute the similarity of all organisms against all others. This seems like a lot but actually is not very computationally expensive
    for i in range(len(organisms)):
        for j in range(i + 1, len(organisms)):
            similarity = genomeSimilarity(organisms[i].brain.genome, organisms[j].brain.genome)
            similarityFactors[i][j] = similarity
            similarityFactors[j][i] = similarity

    groupedSimilaritiesMap = {}

    # organisms will be considered "in a group" if they are 90% similar to each other, so for each organism get a listing
    # of all the organisms that are at least 90% simmilar 
    indicies = np.where(similarityFactors > .9)

    for centerIndex, orgIndex in zip(indicies[0], indicies[1]):
        if not centerIndex in groupedSimilaritiesMap:
            groupedSimilaritiesMap[centerIndex] = {
                'center': centerIndex,
                'orgs': [centerIndex, orgIndex]
            }
        else:
            groupedSimilaritiesMap[centerIndex]['orgs'].append(orgIndex)

    if not groupedSimilaritiesMap:
        return

    largestGroup = max(groupedSimilaritiesMap.values(), key=lambda g: len(g['orgs']))

    # assign organisms colors based on which group they are a part of.
    # start with the largest group and move towards smaller groups.
    groupNum = 0
    while largestGroup is not None and groupNum < len(colorOptions):
        for index in largestGroup['orgs']:
            organisms[index].similarity.colorCode = colorOptions[groupNum]

            # remove all other groups that have one of the organisms in this group at the center
            if index in groupedSimilaritiesMap:
                del groupedSimilaritiesMap[index]
        
        # filter all of the organisms that have just been assinged a color out of all other groups,
        # then find the next largest to repeat the process
        newLargestGroup = None
        for group in groupedSimilaritiesMap.values():
            group['orgs'] = [org for org in group['orgs'] if org not in largestGroup['orgs']]
            
            if not newLargestGroup or len(group['orgs']) > len(newLargestGroup['orgs']):
                newLargestGroup = group

        groupNum += 1

        # a group must have at least 3 members to get their own color, so if we have run out of large enough
        # groups set largestGroup to None and exit the group coloring loop
        largestGroup = newLargestGroup if newLargestGroup and len(newLargestGroup['orgs']) > 2 else None

# determine the genetic similarity of a list of organisms. A comprehensive method
# would require comparing every organism to every other one, which is far too expensive,
# so instead we do 'numFactors' number of comparisons for each. This is accomplished by picking 
# a benchmark organism and comparing all other organisms to it, calculating a score from 0 to 100.
# The first benchmark is random, but after that the new benchmark is the organism most
# dissimilar to the last one
def calcGenerationSimiarity(organisms: list['Organism'], numFactors: int):
    for org in organisms:
        org.similarity = NFactorGeneticSimilary()

    benchmark = organisms[random.randint(0, len(organisms) - 1)]
    for _ in range(numFactors):
        similarityMap = {}

        minSimilarity = 1
        for org in organisms:
            similarity = genomeSimilarity(benchmark.brain.genome, org.brain.genome)
            similarityMap[org.id] = similarity
            
            minSimilarity = min(minSimilarity, similarity)
  
        newBenchmark: Organism = organisms[0]
        for org in organisms:
            similarity = math.floor((similarityMap[org.id] - minSimilarity) / (1 - minSimilarity) * 100)
            org.similarity.addSimilarityFactor(similarity)
            if org.similarity.totalSimilarity() < newBenchmark.similarity.totalSimilarity():
                newBenchmark = org
        
        benchmark = newBenchmark


# return the average similarity of the genes in two genomes. Currently we just compare the xth gene from the first
# genome to the xth gene from the second genome as sexual reproduction always is between those genes, but this will
# need to be adjusted if gene duplication/irregular gene lengths is added
def genomeSimilarity(genome: Genome, genome2: Genome) -> float:
    if genome == genome2:
        return 1

    availableMatches = [*genome2.genes]
    totalSimilarity = 0
    for gene in genome.genes:
        similarities = [(i, geneSimilarity(gene, potential)) for i, potential in enumerate(availableMatches)]
        mostSimilar = max(similarities, key=lambda s: s[1])

        del availableMatches[mostSimilar[0]]
        totalSimilarity += mostSimilar[1]

    return totalSimilarity / len(genome.genes)

# gives a score from 0 to 1 based on how similar two genes are. This is calculated as follows:
#     +.15 if the input types are the same
#     +.15 if the output types are the same
#     +.3 if the input type and id is the same (.1 if it is only off by one, as similar actions/senses tend to have similar ids)
#     +.3 if the output type and id is the same (.1 if it is only off by one)
#     +.05 if the weight of the genes are both + or both -
#     +0-.05 based on how similar the weights are
def geneSimilarity(gene: Gene, gene2: Gene) -> float:
    score = 0
    if gene.inputType == gene2.inputType:
        score += .15

        if gene.inputId == gene2.inputId:
            score += .3
        elif abs(gene.inputId - gene2.inputId) == 1:
            score += .1

    if gene.outputType == gene2.outputType:
        score += .15

        if gene.outputId == gene2.outputId:
            score += .3
        elif abs(gene.outputId - gene2.outputId):
            score += .1

    if gene.weight > 0 == gene2.weight > 0:
        score += .05
    score += (1 - abs(gene.weight - gene2.weight) / 8) * .05
    return score