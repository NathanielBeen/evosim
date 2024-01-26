class Config:
  GENERATIONS = "generations"
  STEPS = "steps"
  ORGANSISMS = "organisms"
  GENES = "genes"

  MUTATE_CHANCE = "mutateChance"
  NUM_INTERNAL_NODES = "numInternalNodes"

  GRID_WIDTH = "gridWidth"
  GRID_HEIGHT = "gridHeight"

  IMAGE_SCALING = "imageScaling"

  configValues = {
    GENERATIONS: 1000,
    STEPS: 100,
    ORGANSISMS: 100,
    GENES: 10,
    MUTATE_CHANCE: .05,
    NUM_INTERNAL_NODES: 4,
    GRID_WIDTH: 128,
    GRID_HEIGHT: 128,
    IMAGE_SCALING: 4
  }

  @staticmethod
  def get(name):
    return Config.configValues[name]

  @staticmethod
  def set(name, value):
    if name in Config.configValues:
      Config.configValues[name] = value
    else:
      raise NameError(f"Can only override one of the following")
