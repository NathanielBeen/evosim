class Config:
  GENERATIONS = "generations"
  STEPS = "steps"
  ORGANSISMS = "organisms"
  GENES = "genes"

  MUTATE_CHANCE = "mutateChance"
  NUM_INTERNAL_NODES = "numInternalNodes"

  GRID_WIDTH = "gridWidth"
  GRID_HEIGHT = "gridHeight"
  OBSTACLES = "obstacles"

  IMAGE_SCALING = "imageScaling"

  SENSE_DISTANCE = "senseDistance"
  MATING_STRATEGY = "matingStrategy"

  RECORD_FREQUENCY = "recordFrequency"

  configValues = {
    GENERATIONS: 1200,
    STEPS: 200,
    ORGANSISMS: 100,
    GENES: 10,
    MUTATE_CHANCE: .01,
    NUM_INTERNAL_NODES: 4,
    GRID_WIDTH: 140,
    GRID_HEIGHT: 140,
    IMAGE_SCALING: 4,
    OBSTACLES: [],
    SENSE_DISTANCE: 5,
    MATING_STRATEGY: 1, # 0 for random mating, 1 for mating based on genetic similarity, 2 for mating based on location
    RECORD_FREQUENCY: 200
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
