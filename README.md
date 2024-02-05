# EvoSim
An exploration of evolution using Python and a hand-coded NN!

![evosim_image](https://github.com/NathanielBeen/evosim/assets/39103518/4c09af47-7f4d-4f79-97e5-f6396b30d065)

I got the idea for this project from https://github.com/davidrmiller/biosim4, and a lot of the core methodology remains the same, although I have deviated significantly from Miller's implementation strategy for many components.

## What it does

EvoSim explores the basic principles of evolution by simulating generations of individual organisms and seeing how many meet the given survival criteria. The simulation is founded upon a series of "generations", where individual organisms will be created and navigate their world in an attempt to survive and pass on their genes to the next generation. Each generation consists of a set number of "steps", and during each step the organism will receive a variety of data through its "senses" and will determine what actions to take via a simple Neural Network brain, consisting of a number of connections between nodes. These connections are encoded by the organism's "genome", a set of binary strings that can be passed to its offspring, thus allowing the whole population to gradually adapt to the environment and survive at greater and greater rates.

## How it works

### The Arena

EvoSim places all organisms into an "arena", a grid of spaces that they must navigate in order to survive. The grid is a specified height and width (configurable by changing the appropriate values in `config.py`) and has a certain area that is designated the "survival zone" (colored yellow in all screenshots). If an organism reaches this zone then they are considered a survivor and are eligible to pass on their genes to the next generation. There are currently two possible configurations for survival
 - Side: get within X spaces of a specified side of the grid
 - Corner: get within X spaces of one of the four corners of the grid (pictured above)

In addition to the survival criteria, barriers can be added to impede the movement of organisms. These are rectangles of blocked off spaces configured in the `OBSTACLES` parameter in `config.py`. For example, the following simulation placed a barrier directly in front of the survival area, requiring organisms to move around it to survive

![evosim_barriers](https://github.com/NathanielBeen/evosim/assets/39103518/7ee2a978-7dbf-489e-8fbc-2db44802f146)

### Genomes and Brains

The genome of each individual contains a number of genes, each of which is a string of 24 binary bits. For the first generation of individuals these genomes are generated randomly, but for all subsequent generations two surviving genomes are selected and spliced together (with a chance of a random mutation - simulated by flipping a random bit in the gene) to form new genomes.

Each individual also has a brain - a set of connected nodes that will help it interpret its world and decide what actions to take. There are three types of nodes: sense nodes, inner nodes, and action nodes. At the start of a new generation each individual's brain will be "wired" with connections based upon its genome, with each gene creating one connection based on the following conversion

![evosim_genome](https://github.com/NathanielBeen/evosim/assets/39103518/6e139d17-c32b-4b16-962b-5d3892e73da4)

The connection weight is scaled to always be between -4 and 4, and we use node type bools and `nodeId % NUM_NODES_OF_TYPE` values to point to specific input and output nodes. After all genes are converted into connections, the individual's brain may look something like this 

![example_nueral_net](https://github.com/NathanielBeen/evosim/assets/39103518/ee920ba4-7c6a-4fa0-9555-20d20876e8a2)

During each step of the simulation, individuals will have an opportunity to take 1 or more actions in order to try to survive. First, all sense nodes (with a brain connection) will calculate their values based upon the surrounding environment. There are currently eight difference sense nodes implemented, which will all return a value between 0 and 1:
- **Distance from Nearest Edge** - how far an individual is from the nearest boundary
- **Distance from Nearest X Edge** - how far an individual is from the left or right boundary, whichever is closest
- **Distance from Nearest Y Edge** - how far an individual is from the top of bottom boundary, whichever is closest
- **Distance from Forward Edge** - how far an individual is from the edge in front of them ("forward" is always in the direction of the last movement taken)
- **Population Close** - how many other individuals are within a certain distance of this one
- **Population Forward** - how many other individuals are within a cone in front of this one
- **Forward Occupied** - whether the space directly in front of the individual is occupied by another
- **Forward Available** - whether the space directly in front of the individual is empty and within the boundaries

These are then fed forward to inner (or action) nodes, with the sense value being multiplied by the weight of the connection. Inner nodes are similarly fed forward to action nodes until each connected action node has a value. These values are clamped to [0,1] using a `tanh` function, with the resulting value being the percent chance the individual will take said action. There are currently six different actions:
- **Move Positive X** - move one unit right
- **Move Negative X** - move one unit left
- **Move Positive Y** - move one unit down
- **Move Negative Y** - move one unit up
- **Move Forward** - move in the direction of the last move
- **Move Randomly** - imitates one of the first four moves.

Once all action likelihoods have been calculated, random values are generated to determine which will actually be carried out.

### Output

At the end of the simulation, a number of graphs and charts will be generated to provide more information about the results of the simulation. The first is a graph showing the genetic similarity and # of survivors in each generation

![evosim_survivor_graph](https://github.com/NathanielBeen/evosim/assets/39103518/813ac671-b474-473c-aa26-1efb2414c8b2)

Additionally, during specific generations additional output will be generated (currently configured to every 300 generations, including the first and last ones). The first of these outputs is a video showing what happened during each step of the generation. All of the images of the arena that you have seen here are screenshots of these videos. Additionally, the simulation will output a directed graph of the "most average" brain in the generation to get an idea of how they are solving the problem.

## Getting Started

In order to run EvoSim you will need to have poetry installed on your local machine. Once you have downloaded this repo run `poetry install`. Once you have done that, the program can be run with `poetry run evosim [PATH_TO_OUTPUT_FOLDER]`. The output folder is where all generated graphs and videos will be saved to.

Important: evosim will clear the given folder of .png and .mp4 files before each run to ensure that only the results of that run are saved. As such I highly recommend you create a completely new folder for this program instead of reusing an existing one.

A number of parameters can be passed into the command line to change the number of organisms per generation, the number of generations, etc. All of these flags can be found by running `poetry run evosim --help`. These configuration parameters (and other, lesser-used ones) can also be changed in the `config.py` file in the root directory. Note that a parameter passed in with a flag will always override the one found in the `config.py`.

