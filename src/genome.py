import random
import runConfig

class Gene:
    # we convert a "code" of 24 bits into a set of integers that will determine the type
    # of connection that the gene will construct. This code is comprised of the following:
    #   - inputType: 0 if the output will be an SENSE node, 1 if it will be an INTERNAL node
    #   - inputNum: the id of the input node (we will use a modulo in the brain to make sure it points to a real node)
    #   - outputType: 0 if the output will be an INNER node, 0 for a ACTION node
    #   - outputNum: the id of the output node (we will also use a modulo here)
    #   - weight: a float from -4 to 4 that indicates the strength of this connection
    def __init__(self, code: str):
        self.code = code
        self.inputType = int(code[0], 2)
        self.inputNum = int(code[1:7], 2)
        self.outputType = int(code[8], 2)
        self.outputNum = int(code[9:15], 2)
        self.weight = (int(code[16:], 2) / 32 - 4)

    # for the first generation there are no parents, so we must generate a random bit string
    @staticmethod
    def gen_random():
        return Gene(f'{random.getrandbits(24):=024b}')


    # creates a new gene based on two parent genes (representated as a string of binary).
    # we do this by copying one gene and then splicing a random segment from the other gene into the middle. 
    # After this has been completed we may perform a point mutation on the gene
    @staticmethod
    def gen_from_parents(parentCode, parent2Code):
        baseCode = parentCode if random.randint(0, 1) == 0 else parent2Code
        codeToInsert = parentCode if baseCode == parent2Code else parent2Code

        startInsertIndex = random.randint(0, len(parentCode))
        endInsertIndex = random.randint(0, len(parentCode))

        if startInsertIndex > endInsertIndex:
            startInsertIndex, endInsertIndex = endInsertIndex, startInsertIndex
        
        code = baseCode[:startInsertIndex] + codeToInsert[startInsertIndex:endInsertIndex] + baseCode[endInsertIndex:]
        return Gene(Gene.mutateCode(code))
    
    # perform a point mutation on the gene by flipping one bit in the string. We first check whether we should perform
    # a mutation by generating a random number from 0 to 1 and seeing if it is less than the mutation chance
    @staticmethod
    def mutateCode(code: str):
        if random.random() < runConfig.MUTATE_CHANCE:
            bitToFlip = random.randint(0, len(code) - 1)
            code[bitToFlip] = "1" if code[bitToFlip] == "0" else "0"



class Genome:
    def __init__(self, genes):
        self.genes = genes

    @staticmethod
    def gen_random():    
        return Genome([Gene.gen_random() for _ in range(runConfig.NUM_GENES)])

    @staticmethod
    def gen_from_parents(self, parentGenome, parent2Genome):
        return Genome([
            Gene.gen_from_parents(parentCode, parent2Code) 
            for parentCode, parent2Code in zip(parentGenome.genes, parent2Genome.genes)
        ])