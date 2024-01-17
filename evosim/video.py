from PIL import Image, ImageDraw
import cv2
import os
import re
import pygraphviz as pgv

from .organism import Organism
from .grid import Grid
from .survivalCriteria import SurvivalCriteria
from .runConfig import IMAGE_SCALING

ASSET_FOLDER = "/home/nathaniel/Dev/evosim_assets"

class Video:
    def __init__(self, grid: Grid, survivalCriteria: SurvivalCriteria):
        self.grid = grid
        self.survivalCriteria = survivalCriteria
        self.numImages = 0
        self.cleanFolder()

    def cleanIntermediaryImages(self):
        for f in os.listdir(ASSET_FOLDER):
            if f.startswith('image') and f.endswith(".png"):
                os.remove(os.path.join(ASSET_FOLDER, f))
        self.numImages = 0

    def cleanFolder(self):
        for f in os.listdir(ASSET_FOLDER):
            if f.endswith(".mp4") or f.endswith(".png"):
                os.remove(os.path.join(ASSET_FOLDER, f))

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

    def saveGenerationOutput(self, organisms: list[Organism], genNumber: int):
        self.saveVideo(genNumber)
        self.drawGraph(organisms, genNumber)

    def saveVideo(self, genNumber):
        videoName = f"{ASSET_FOLDER}/output_{genNumber}.mp4"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(videoName, fourcc, 10, (self.grid.width * IMAGE_SCALING, self.grid.height * IMAGE_SCALING))

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
