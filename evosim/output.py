from PIL import Image, ImageDraw
import cv2
import os
import re
import random
import math
import pygraphviz as pgv
import matplotlib.pyplot as plt
import numpy as np

from .organism import Organism
from .grid import Grid
from .survivalCriteria import SurvivalCriteria
from .genome import genome_similarity
from .runConfig import IMAGE_SCALING, NUM_GENERATIONS

ASSET_FOLDER = "/home/nathaniel/Dev/evosim_assets"

class Output:
    def __init__(self, grid: Grid, survivalCriteria: SurvivalCriteria):
        self.cleanFolder()

        self.video = OutputVideo(grid, survivalCriteria)
        self.graph = OutputGraph()
        self.stats = OutputStats()

    def cleanFolder(self):
        for f in os.listdir(ASSET_FOLDER):
            if f.endswith(".mp4") or f.endswith(".png"):
                os.remove(os.path.join(ASSET_FOLDER, f))

    def willRecordGeneration(self, genNumber: int) -> bool:
        return genNumber == NUM_GENERATIONS - 1 or genNumber % 100 == 0
    
    def stepComplete(self, genNumber: int):
        if self.willRecordGeneration(genNumber):
            self.video.drawFrame()

    def generationComplete(self, organisms: list[Organism], survivors: int, genNumber: int):
        self.stats.addStats(survivors)

        if self.willRecordGeneration(genNumber):
            self.determineOrganismColors(organisms)
            self.video.saveVideo(genNumber)
            self.graph.drawGraph(organisms, genNumber)

    def simulationComplete(self):
        self.stats.drawGraph()

    def determineOrganismColors(self, organisms: list[Organism]):
        redBenchmark = organisms[random.randint(0, len(organisms) - 1)]
        greenBenchmark = redBenchmark
        blueBenchmark = redBenchmark

        for org in organisms:
            similarity = genome_similarity(redBenchmark.brain.genome, org.brain.genome)
            org.color.red = math.floor(similarity * 255)

            if org.color.red < greenBenchmark.color.red:
                greenBenchmark = org
        
        for org in organisms:
            similarity = genome_similarity(greenBenchmark.brain.genome, org.brain.genome)
            org.color.green = math.floor(similarity * 255)

            if org.color.red + org.color.green < blueBenchmark.color.red + blueBenchmark.color.green:
                blueBenchmark = org
            
        for org in organisms:
            similarity = genome_similarity(blueBenchmark.brain.genome, org.brain.genome)
            org.color.blue = math.floor(similarity * 255)


class OutputVideo:
    def __init__(self, grid: Grid, criteria: SurvivalCriteria):
        self.grid = grid
        self.survivalCriteria = criteria
        self.numImages = 0

    def drawFrame(self):
        frame = Image.new('RGB', (self.grid.width * IMAGE_SCALING, self.grid.height * IMAGE_SCALING), "#ffffff")
        context = ImageDraw.Draw(frame)

        self.survivalCriteria.draw(context)

        for org in self.grid.organisms:
            context.rectangle((
                org.loc.x * IMAGE_SCALING, org.loc.y * IMAGE_SCALING, org.loc.x * IMAGE_SCALING + IMAGE_SCALING, org.loc.y * IMAGE_SCALING + IMAGE_SCALING
            ), fill=org.color.hex())

        imagePath = f"/home/nathaniel/Dev/evosim_assets/image_{self.numImages}.png"
        frame.save(imagePath)
        self.numImages += 1

    def saveVideo(self, genNumber):
        videoName = f"{ASSET_FOLDER}/output_{genNumber}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(videoName, fourcc, 15, (self.grid.width * IMAGE_SCALING, self.grid.height * IMAGE_SCALING))

        imagePaths = []
        for img in os.listdir(ASSET_FOLDER):
            if img.endswith(".png"):
                stepNum = int(re.match(f"\D*(\d+)\D*", img).group(1))
                imagePaths.append({
                    'name': img,
                    'step': stepNum
                })
        imagePaths.sort(key=lambda x: x['step'])

        for imagePath in imagePaths:
            video.write(cv2.imread(os.path.join(ASSET_FOLDER, imagePath['name'])))

        cv2.destroyAllWindows()
        video.release()

        self.cleanIntermediaryImages()

    def cleanIntermediaryImages(self):
        for f in os.listdir(ASSET_FOLDER):
            if f.startswith('image') and f.endswith(".png"):
                os.remove(os.path.join(ASSET_FOLDER, f))
        self.numImages = 0


class OutputGraph:
    def __init__(self):
        pass

    def drawGraph(self, organisms: list[Organism], genNumber: int):

        # find the most average organism to graph (defined by having the highest average similarity)
        averageOrg: Organism = None
        highestSim = 0

        for org in organisms:
            similarity = org.color.red + org.color.green + org.color.blue
            if similarity > highestSim:
                averageOrg = org

        graph = pgv.AGraph(strict=False, directed=True, rankdir="LR")

        for node in [*averageOrg.brain.senseNodes, *averageOrg.brain.innerNodes, *averageOrg.brain.actionNodes]:
            graph.add_node(node.name(), color=node.color())

            for conn in node.connections:
                    if conn.input == node:
                        graph.add_edge(node.name(), conn.output.name(), penwidth=conn.width(), color=conn.color(), len=2)

        graph.layout()
        graph.draw(f"{ASSET_FOLDER}/graph_{genNumber}.png")

class OutputStats:
    def __init__(self):
        self.survivors = []

        self.averageWindow = 20
        self.survivorAverage = []

    def addStats(self, survivors: int):
        self.survivors.append(survivors)

        if len(self.survivors) < self.averageWindow:
            self.survivorAverage.append(np.nan)
        else:
            averageStart = len(self.survivors) - self.averageWindow - 1
            average = np.mean(self.survivors[averageStart:])
            self.survivorAverage.append(average)
    
    def drawGraph(self):
        x = np.arange(NUM_GENERATIONS)
        plt.plot(x, self.survivors)
        plt.plot(x, self.survivorAverage)
        plt.savefig(f"{ASSET_FOLDER}/stats.png")

