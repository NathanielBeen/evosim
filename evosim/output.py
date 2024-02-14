from PIL import Image, ImageDraw
import cv2
import os
import re
import random
import pygraphviz as pgv
import matplotlib.pyplot as plt
import numpy as np

from .organism import Organism
from .grid import Grid
from .survivalCriteria import SurvivalCriteria
from .genome_similarity import genomeSimilarity, calcGenerationColors
from config import Config

class Output:
    def __init__(self, outputFolder: str, grid: Grid, survivalCriteria: SurvivalCriteria):
        self.outputFolder = outputFolder
        self.cleanFolder()

        self.organisms: list[Organism] = []
        self.genNumber: int = 0

        self.video = OutputVideo(outputFolder, grid, survivalCriteria)
        self.graph = OutputGraph(outputFolder)
        self.stats = OutputStats(outputFolder)

    def cleanFolder(self):
        for f in os.listdir(self.outputFolder):
            if f.endswith(".mp4") or f.endswith(".png"):
                os.remove(os.path.join(self.outputFolder, f))

    def generationStarted(self, organisms: list[Organism], genNumber: int):
        self.organisms = organisms
        self.genNumber = genNumber
        if self.willRecordGeneration():
            calcGenerationColors(self.organisms)
            self.video.drawFrame()

    def willRecordGeneration(self) -> bool:
        return self.genNumber == Config.get(Config.GENERATIONS) - 1 or self.genNumber % Config.get(Config.RECORD_FREQUENCY) == 0
    
    def stepComplete(self):
        if self.willRecordGeneration():
            self.video.drawFrame()

    def generationComplete(self, survivors: int):
        self.stats.addStats(self.organisms, survivors)

        if self.willRecordGeneration():
            self.video.saveVideo(self.genNumber)
            self.graph.drawGraph(self.organisms, self.genNumber)

    def simulationComplete(self):
        self.stats.drawGraph()
        self.stats.drawSimilarityGraph()


class OutputVideo:
    def __init__(self, outputFolder: str, grid: Grid, criteria: SurvivalCriteria):
        self.outputFolder = outputFolder
        self.grid = grid
        self.survivalCriteria = criteria
        self.numImages = 0

    def drawFrame(self):
        scaling = Config.get(Config.IMAGE_SCALING)
        frame = Image.new('RGB', (self.grid.width * scaling, self.grid.height * scaling), "#ffffff")
        context = ImageDraw.Draw(frame)

        self.survivalCriteria.draw(context)
        for obs in self.grid.obstacles:
            obs.draw(context)

        for org in self.grid.organisms:
            context.rectangle((
                org.loc.x * scaling, org.loc.y * scaling, org.loc.x * scaling + scaling, org.loc.y * scaling + scaling
            ), fill=org.similarity.colorCode)

        imagePath = f"{self.outputFolder}/image_{self.numImages}.png"
        frame.save(imagePath)
        self.numImages += 1

    def saveVideo(self, genNumber):
        scaling = Config.get(Config.IMAGE_SCALING)
        videoName = f"{self.outputFolder}/output_{genNumber}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(videoName, fourcc, 15, (self.grid.width * scaling, self.grid.height * scaling))

        imagePaths = []
        for img in os.listdir(self.outputFolder):
            if img.endswith(".png"):
                stepNum = int(re.match(f"\D*(\d+)\D*", img).group(1))
                imagePaths.append({
                    'name': img,
                    'step': stepNum
                })
        imagePaths.sort(key=lambda x: x['step'])

        for imagePath in imagePaths:
            video.write(cv2.imread(os.path.join(self.outputFolder, imagePath['name'])))

        cv2.destroyAllWindows()
        video.release()

        self.cleanIntermediaryImages()

    def cleanIntermediaryImages(self):
        for f in os.listdir(self.outputFolder):
            if f.startswith('image') and f.endswith(".png"):
                os.remove(os.path.join(self.outputFolder, f))
        self.numImages = 0


class OutputGraph:
    def __init__(self, outputFolder):
        self.outputFolder = outputFolder

    def drawGraph(self, organisms: list[Organism], genNumber: int):

        # find the most average organism to graph (defined by having the highest average similarity)
        averageOrg: Organism = None
        highestSim = 0

        for org in organisms:
            if org.similarity.totalSimilarity() > highestSim:
                averageOrg = org
                highestSim = org.similarity.totalSimilarity()

        graph = pgv.AGraph(strict=False, directed=True, rankdir="LR")

        for node in [*averageOrg.brain.senseNodes, *averageOrg.brain.innerNodes, *averageOrg.brain.actionNodes]:
            graph.add_node(node.name(), color=node.color())

            for conn in node.connections:
                    if conn.input == node:
                        graph.add_edge(node.name(), conn.output.name(), penwidth=conn.width(), color=conn.color(), len=2)

        graph.layout()
        graph.draw(f"{self.outputFolder}/graph_{genNumber}.png")


class OutputStats:
    def __init__(self, outputFolder):
        self.outputFolder = outputFolder
        self.survivors = []
        self.similarity = []

        self.averageWindow = 20
        self.survivorAverage = []
        self.similarityAverage = []

        self.similarityFactors = []

    def addStats(self, organisms: list[Organism], survivors: int):
        self.survivors.append(survivors)
        self.similarity.append(self.calculateAvgSimilarity(organisms))

        if len(self.survivors) < self.averageWindow:
            self.survivorAverage.append(np.nan)
            self.similarityAverage.append(np.nan)
        else:
            averageStart = len(self.survivors) - self.averageWindow - 1
            survivorAverage = np.mean(self.survivors[averageStart:])
            similarityAverage = np.mean(self.similarity[averageStart:])

            self.survivorAverage.append(survivorAverage)
            self.similarityAverage.append(similarityAverage)

        for org in organisms:
            self.similarityFactors += org.similarity.factors

    def calculateAvgSimilarity(self, organsisms: list[Organism]) -> float:
        similarity = []
        for _ in range(30):
            first_genome = organsisms[random.randint(0, len(organsisms) - 1)].brain.genome
            second_genome = organsisms[random.randint(0, len(organsisms) - 1)].brain.genome
            similarity.append(genomeSimilarity(first_genome, second_genome))
        
        return np.mean(similarity)
    
    def drawSimilarityGraph(self):
        plt.figure(2)
        plt.hist(self.similarityFactors, bins=64)
        plt.savefig(f"{self.outputFolder}/factorDist.png")
    
    def drawGraph(self):
        x = np.arange(Config.get(Config.GENERATIONS))

        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()

        ax1.set_xlabel('generation')
        ax1.set_ylabel('# of survivors')
        ax2.set_ylabel('genetic similarity %')

        surv = ax1.plot(x, self.survivors, color='#a0d9ef', label='survivors')
        sim = ax2.plot(x, self.similarity, color='#ff7b7b', label='similarity')

        survAvg = ax1.plot(x, self.survivorAverage, color='#1c96c5', label='survivor moving avg.')
        simAvg = ax2.plot(x, self.similarityAverage, color='#ff0000', label='similarity moving avg.')

        lines = surv + survAvg + sim + simAvg
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc=0)

        fig.tight_layout()
        plt.savefig(f"{self.outputFolder}/stats.png")
