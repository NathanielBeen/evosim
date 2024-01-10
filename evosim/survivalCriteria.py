from PIL import ImageDraw

from .organism import Organism
from .runConfig import GRID_HEIGHT, GRID_WIDTH, IMAGE_SCALING


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
    
    def survived(self, organism: Organism) -> bool:
        if self.type == SideSurvivalType.LEFT:
            return organism.loc.x <= self.distance
        if self.type == SideSurvivalType.RIGHT:
            return organism.loc.x >= GRID_WIDTH - self.distance
        if self.type == SideSurvivalType.TOP:
            return organism.loc.y <= self.distance
        if self.type == SideSurvivalType.BOTTOM:
            return organism.loc.y >= GRID_HEIGHT - self.distance
        return False
    
    # draw this boundary on the output image in yellow. Note that all values need to be scaled by 
    # IMAGE_SCALING, as the image has larger dimensions than the size of the grid for improved clarity
    def draw(self, context: ImageDraw):
        coords = (0, 0, 0, 0)
        if self.type == SideSurvivalType.LEFT:
            coords = (0, 0, self.distance * IMAGE_SCALING, GRID_HEIGHT * IMAGE_SCALING)
        elif self.type == SideSurvivalType.RIGHT:
            coords = ((GRID_WIDTH - self.distance) * IMAGE_SCALING, 0, GRID_WIDTH * IMAGE_SCALING, GRID_HEIGHT * IMAGE_SCALING)
        elif self.type == SideSurvivalType.TOP:
            coords = (0, 0, GRID_WIDTH * IMAGE_SCALING, self.distance * IMAGE_SCALING)
        elif self.type == SideSurvivalType.BOTTOM:
            coords = (0, (GRID_HEIGHT - self.distance) * IMAGE_SCALING, GRID_HEIGHT * IMAGE_SCALING)

        context.rectangle(coords, fill="#00FF00")


# when used, organisms will survive if they are within a certain distance to one of the corners
class CornerSurvivalCriteria:
    def __init__(self, distance: int):
        self.distance = distance
    
    def survived(self, organism: Organism) -> bool:
        return organism.loc.x + organism.loc.y < self.distance \
            or organism.loc.x + GRID_HEIGHT - organism.loc.y < self.distance \
            or GRID_WIDTH - organism.loc.x + organism.loc.y < self.distance \
            or GRID_WIDTH - organism.loc.x + GRID_HEIGHT - organism.loc.y < self.distance
    
    # draw triangles in the four corners of the grid in yellow. Note that all values need to be scaled by IMAGE_SCALING
    def draw(self, context: ImageDraw):
        cornerX = GRID_WIDTH * IMAGE_SCALING
        closeX = self.distance * IMAGE_SCALING
        farX = (GRID_WIDTH - self.distance) * IMAGE_SCALING

        cornerY = GRID_HEIGHT * IMAGE_SCALING
        closeY = self.distance * IMAGE_SCALING
        farY = (GRID_HEIGHT - self.distance) * IMAGE_SCALING

        context.polygon([(0,0), (closeX, 0), (0, closeY)], fill="#00FF00")
        context.polygon([(0, cornerY), (closeX, cornerY), (0, farY)], fill="#00FF00")
        context.polygon([(cornerX, 0), (cornerX, closeY), (farX, 0)], fill="#00FF00")
        context.polygon([(cornerX, cornerY), (farX, cornerY), (cornerX, farY)], fill="#00FF00")