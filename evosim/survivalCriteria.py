from PIL import ImageDraw

from .organism import Organism
from config import Config


class SurvivalCriteria:
    def survived(self, organism: Organism) -> bool:
        pass
    
    def draw(self, context: ImageDraw):
        pass


class SideSurvivalType:
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3


# when used, organisms will survive if they are within a certain distance
# of one of the boundary, with the distance and which boundary to use
# being configurable
class SideSurvialCriteria:
    def __init__(self, type: SideSurvivalType, distance: int):
        self.type = type
        self.distance = distance
        self.width = Config.get(Config.GRID_WIDTH)
        self.height = Config.get(Config.GRID_HEIGHT)
        self.scaling = Config.get(Config.IMAGE_SCALING)
    
    def survived(self, organism: Organism) -> bool:
        if self.type == SideSurvivalType.LEFT:
            return organism.loc.x <= self.distance
        if self.type == SideSurvivalType.RIGHT:
            return organism.loc.x >= self.width - self.distance
        if self.type == SideSurvivalType.TOP:
            return organism.loc.y <= self.distance
        if self.type == SideSurvivalType.BOTTOM:
            return organism.loc.y >= self.height - self.distance
        return False
    
    # draw this boundary on the output image in yellow. Note that all values need to be scaled by 
    # IMAGE_SCALING, as the image has larger dimensions than the size of the grid for improved clarity
    def draw(self, context: ImageDraw):
        coords = (0, 0, 0, 0)
        if self.type == SideSurvivalType.LEFT:
            coords = (0, 0, self.distance * self.scaling, self.height * self.scaling)
        elif self.type == SideSurvivalType.RIGHT:
            coords = ((self.width - self.distance) * self.scaling, 0, self.width * self.scaling, self.height * self.scaling)
        elif self.type == SideSurvivalType.TOP:
            coords = (0, 0, self.width * self.scaling, self.distance * self.scaling)
        elif self.type == SideSurvivalType.BOTTOM:
            coords = (0, (self.height - self.distance) * self.scaling, self.height * self.scaling)

        context.rectangle(coords, fill="#00FF00")


# when used, organisms will survive if they are within a certain distance to one of the corners
class CornerSurvivalCriteria:
    def __init__(self, distance: int):
        self.distance = distance
        self.width = Config.get(Config.GRID_WIDTH)
        self.height = Config.get(Config.GRID_HEIGHT)
        self.scaling = Config.get(Config.IMAGE_SCALING)
    
    def survived(self, organism: Organism) -> bool:
        return organism.loc.x + organism.loc.y < self.distance \
            or organism.loc.x + self.height - organism.loc.y < self.distance \
            or self.width - organism.loc.x + organism.loc.y < self.distance \
            or self.width - organism.loc.x + self.height - organism.loc.y < self.distance
    
    # draw triangles in the four corners of the grid in yellow. Note that all values need to be scaled by IMAGE_SCALING
    def draw(self, context: ImageDraw):
        cornerX = self.width * self.scaling
        closeX = self.distance * self.scaling
        farX = (self.width - self.distance) * self.scaling

        cornerY = self.height * self.scaling
        closeY = self.distance * self.scaling
        farY = (self.height - self.distance) * self.scaling

        context.polygon([(0,0), (closeX, 0), (0, closeY)], fill="#00FF00")
        context.polygon([(0, cornerY), (closeX, cornerY), (0, farY)], fill="#00FF00")
        context.polygon([(cornerX, 0), (cornerX, closeY), (farX, 0)], fill="#00FF00")
        context.polygon([(cornerX, cornerY), (farX, cornerY), (cornerX, farY)], fill="#00FF00")