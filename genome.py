import random
import runConfig

class Gene:
    def __init__(self, code: str):
        self.code = code
        self.inputType = int(code[0])
        self.inputNum = int(code[1:7])
        self.outputType = int(code[8])
        self.outputNum = int(code[9:15])
        self.weight = (int(code[16:]) / 32 - 4) # generate -4 to 4 range

    @staticmethod
    def gen_random():
        return Gene(f'{random.getrandbits(24):=024b}')


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