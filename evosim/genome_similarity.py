import random
import math

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .organism import Organism

from .genome import Gene, Genome

class NFactorGeneticSimilary:
    def __init__(self):
        self.factors = []

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


def calcGenerationSimiarity(organisms: list['Organism'], numFactors: int):
    for org in organisms:
        org.similarity = NFactorGeneticSimilary()

    benchmark = organisms[random.randint(0, len(organisms) - 1)]
    for i in range(numFactors):
        newBenchmark: Organism | None = None

        for org in organisms:
            similarity = genome_similarity(benchmark.brain.genome, org.brain.genome)
            similarityInt = math.floor(similarity * 255)
            org.similarity.addSimilarityFactor(similarityInt)

            if not newBenchmark or similarityInt < newBenchmark.similarity.getSimilarityFactor(i):
                newBenchmark = org
        
        benchmark = newBenchmark


# return the average similarity of the genes in two genomes. Currently we just compare the xth gene from the first
# genome to the xth gene from the second genome as sexual reproduction always is between those genes, but this will
# need to be adjsuted if gene duplication/irregular gene lengths is added
def genome_similarity(genome: Genome, genome2: Genome) -> float:
    return sum(gene_similarity(gene, gene2) for gene, gene2 in zip(genome.genes, genome2.genes)) / len(genome.genes)

# gives a score from 0 to 1 based on how similar two genes are. This is calculated as follows:
#     +.15 if the input types are the same
#     +.15 if the output types are the same
#     +.3 if the input type and id is the same (.1 if it is only off by one, as similar actions/senses tend to have similar ids)
#     +.3 if the output type and id is the same (.1 if it is only off by one)
#     +.05 if the weight of the genes are both + or both -
#     +0-.05 based on how similar the weights are
def gene_similarity(gene: Gene, gene2: Gene) -> float:
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