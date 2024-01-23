# EvoSim
An exploration of evolution using Python and a hand-coded NN!

![evosim_image](https://github.com/NathanielBeen/evosim/assets/39103518/4c09af47-7f4d-4f79-97e5-f6396b30d065)

I got the idea for this project from https://github.com/davidrmiller/biosim4, and a lot of the core methodology remains the same, although I have deviated significantly from Miller's implementation strategy for many components.

## What it does

EvoSim explores the basic principles of evolution by simulating generations of individual organisms and seeing how many meet the given survival criteria. In summary, each generation is made up of a number of individuals, each of which has a "genome" consisting of a certain number of genes. At the start of the generation these genes are converted into connections in a simple neural network, which will gather data from the environment via senses and then calculate actions to perform. The simulation is run for a certain number of steps, with each individual taking actions based upon the calculated values in its own NN. At the end of the generation, survivors are determined based upon some survival criteria (get within 5 units of the left wall, for example) and a new generation is created based upon the genomes of those survivors. Along the way the program will generate videos of certain generations (which look like the image linked above), and a graph showing the average genome of an individual within the generation.

## How it works

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

At the beginning of each generation, individuals are placed randomly on a grid, and after 100 steps of movement (this can be configured in `runConfig.py`) a survival criteria is used to determine which individuals will get to pass on their genetic information to the next generation. Currently the implemented survival criteria are simple: one requires individuals be within a certain distance of a specific edge to survive and another requires individuals be within a certain distance of one of the corners to survive.

## Getting Started

In order to run EvoSim you will need to have poetry installed on your local machine. Once you have downloaded this repo run `poetry install`. Once you have done that, the program can be run with `poetry run python main.py`

Note: currently the program will output result files to a hard-coded folder (`ASSET_FOLDER` in `video.py`), so you will need to alter said attribute to point to your desired output folder. This will be improved in future updates

Additionally, parameters related to the simulation, such as the number of generations or how often to take snapshots, can be edited in `runConfig.py`

