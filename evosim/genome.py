import random
from config import Config
from .node import NodeType, ActionTypes, SenseTypes

class Gene:
    # we convert a "code" of 24 bits into a set of integers that will determine the type
    # of connection that the gene will construct. This code is comprised of the following:
    #   - inputType: 0 if the output will be an SENSE node, 1 if it will be an INTERNAL node
    #   - inputId: the id of the input node (we will use a modulo in the brain to make sure it points to a real node)
    #   - outputType: 0 if the output will be an INNER node, 0 for a ACTION node
    #   - outputId: the id of the output node (we will also use a modulo here)
    #   - weight: a float from -4 to 4 that indicates the strength of this connection
    def __init__(self, code: str):
        self.code = code

        self.setInputType()
        self.setOutputType()
        self.setInputId()
        self.setOutputId()

        self.weight = (int(code[16:], 2) / 32 - 4)

    def setInputType(self):
        codeInputType = int(self.code[0], 2)
        self.inputType = NodeType.SENSE if codeInputType == 0 else NodeType.INNER

    def setOutputType(self):
        codeOutputType = int(self.code[8], 2)
        self.outputType = NodeType.INNER if codeOutputType else NodeType.ACTION

    def setInputId(self):
        codeInputId = int(self.code[1:7], 2)
        self.inputId = codeInputId % SenseTypes.count() if self.inputType == NodeType.SENSE else codeInputId % Config.get(Config.NUM_INTERNAL_NODES)
    
    def setOutputId(self):
        codeOutputId = int(self.code[9:15], 2)
        self.outputId = codeOutputId % Config.get(Config.NUM_INTERNAL_NODES) if self.outputType == NodeType.INNER else codeOutputId % ActionTypes.count()


    # for the first generation there are no parents, so we must generate a random bit string
    @staticmethod
    def gen_random():
        return Gene(f'{random.getrandbits(24):=024b}')


    # creates a new gene based on two parent genes (representated as a string of binary).
    # we do this by copying one gene and then splicing a random segment from the other gene into the middle. 
    # After this has been completed we may perform a point mutation on the gene
    @staticmethod
    def gen_from_parents(parentGene: 'Gene', parent2Gene: 'Gene'):
        baseCode = parentGene.code if random.randint(0, 1) == 0 else parent2Gene.code
        codeToInsert = parentGene.code if baseCode == parent2Gene.code else parent2Gene.code

        startInsertIndex = random.randint(0, len(baseCode))
        endInsertIndex = random.randint(0, len(baseCode))

        if startInsertIndex > endInsertIndex:
            startInsertIndex, endInsertIndex = endInsertIndex, startInsertIndex
        
        code = baseCode[:startInsertIndex] + codeToInsert[startInsertIndex:endInsertIndex] + baseCode[endInsertIndex:]
        return Gene(Gene.mutateCode(code))
    
    # perform a point mutation on the gene by flipping one bit in the string. We first check whether we should perform
    # a mutation by generating a random number from 0 to 1 and seeing if it is less than the mutation chance
    @staticmethod
    def mutateCode(code: str):
        if random.random() < Config.get(Config.MUTATE_CHANCE):
            bitToFlip = random.randint(0, len(code) - 1)
            code = code[:bitToFlip] + ("1" if code[bitToFlip] == "0" else "0") + code[bitToFlip+1:]

        return code


class Genome:
    def __init__(self, genes: list[Gene]):
        self.genes = genes

    @staticmethod
    def gen_random():    
        return Genome([Gene.gen_random() for _ in range(Config.get(Config.GENES))])

    @staticmethod
    def gen_from_parents(parentGenome: 'Genome', parent2Genome: 'Genome'):
        return Genome([
            Gene.gen_from_parents(parentGene, parent2Gene) 
            for parentGene, parent2Gene in zip(parentGenome.genes, parent2Genome.genes)
        ])
