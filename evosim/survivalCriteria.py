from PIL import ImageDraw

from organism import Organism
from runConfig import GRID_HEIGHT, GRID_WIDTH, IMAGE_SCALING

class SideSurvivalType:
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

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
