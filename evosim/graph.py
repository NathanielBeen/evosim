from PIL import Image, ImageDraw
import cv2
import os
import re

from grid import Grid
from runConfig import NUM_GENERATIONS

ASSET_FOLDER = "/home/nathaniel/Dev/evosim_assets"

class Graph:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.numImages = 0
        self.cleanImages()
        self.cleanVideos()

    def willRecordGeneration(self, genNumber):
        return genNumber == 0 or genNumber == NUM_GENERATIONS - 1 or genNumber % 10 == 0

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

        frame = Image.new('RGB', (self.grid.width * 4, self.grid.height * 4), "#ffffff")
        context = ImageDraw.Draw(frame)

        for org in self.grid.organisms:
            context.rectangle((org.loc.x * 4, org.loc.y * 4, org.loc.x * 4 + 4, org.loc.y * 4 + 4), fill="#000000")

        imagePath = f"/home/nathaniel/Dev/evosim_assets/image_{self.numImages}.png"
        frame.save(imagePath)
        self.numImages += 1

    def saveVideo(self, genNumber):
        if not self.willRecordGeneration(genNumber):
            return

        videoName = f"{ASSET_FOLDER}/output_{genNumber}.avi"

        video = cv2.VideoWriter(videoName, 0, 10, (self.grid.width * 4, self.grid.height * 4))

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
