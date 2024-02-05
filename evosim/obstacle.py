from PIL import ImageDraw

from config import Config
from .coord import Coord

class Obstacle:
    def __init__(self, left: int, right: int, top: int, bottom: int):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def getBlockedSpaces(self):
        return [Coord(x, y) for x in range(self.left, self.right + 1) for y in range(self.top, self.bottom + 1)]

    def blocked(self, loc: Coord):
        return loc.x >= self.left and loc.x <= self.right \
            and loc.y >= self.top and loc.y <= self.bottom
    
    # draw this boundary on the output image in yellow. Note that all values need to be scaled by 
    # IMAGE_SCALING, as the image has larger dimensions than the size of the grid for improved clarity
    def draw(self, context: ImageDraw):
        scaling = Config.get(Config.IMAGE_SCALING)

        context.rectangle((self.left * scaling, self.top * scaling, self.right * scaling, self.bottom * scaling), fill="#3b3b3b")