from PIL import Image, ImageDraw
import cv2
import os
import re
import random
import math

from .grid import Grid
from .genome import genome_similarity
from .survivalCriteria import SideSurvialCriteria
from .runConfig import NUM_GENERATIONS, IMAGE_SCALING

ASSET_FOLDER = "/home/nathaniel/Dev/evosim_assets"

class Graph:
    def __init__(self, grid: Grid, survivalCriteria: SideSurvialCriteria):
        self.grid = grid
        self.survivalCriteria = survivalCriteria
        self.numImages = 0
        self.cleanImages()
        self.cleanVideos()

    def willRecordGeneration(self, genNumber):
        return genNumber == NUM_GENERATIONS - 1 or genNumber % 100 == 0

    def cleanImages(self):
        for f in os.listdir(ASSET_FOLDER):
            if f.endswith(".png"):
                os.remove(os.path.join(ASSET_FOLDER, f))
        self.numImages = 0

    def cleanVideos(self):
        for f in os.listdir(ASSET_FOLDER):
            if f.endswith(".avi"):
                os.remove(os.path.join(ASSET_FOLDER, f))

    def drawFrame(self, genNumber):
        if not self.willRecordGeneration(genNumber):
            return

        frame = Image.new('RGB', (self.grid.width * IMAGE_SCALING, self.grid.height * IMAGE_SCALING), "#ffffff")
        context = ImageDraw.Draw(frame)

        self.survivalCriteria.draw(context)

        if self.numImages == 0:
            self.determineOrganismColors()

        for org in self.grid.organisms:
            context.rectangle((
                org.loc.x * IMAGE_SCALING, org.loc.y * IMAGE_SCALING, org.loc.x * IMAGE_SCALING + IMAGE_SCALING, org.loc.y * IMAGE_SCALING + IMAGE_SCALING
            ), fill=org.color.hex())

        imagePath = f"/home/nathaniel/Dev/evosim_assets/image_{self.numImages}.png"
        frame.save(imagePath)
        self.numImages += 1

    def saveVideo(self, genNumber):
        if not self.willRecordGeneration(genNumber):
            return

        videoName = f"{ASSET_FOLDER}/output_{genNumber}.avi"

        video = cv2.VideoWriter(videoName, 0, 10, (self.grid.width * IMAGE_SCALING, self.grid.height * IMAGE_SCALING))

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

        self.cleanImages()

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

        similarity = sum((org.color.red + org.color.green + org.color.blue) / 3 for org in self.grid.organisms) / len(self.grid.organisms)
        print(similarity)

