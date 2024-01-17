# EvoSim
An exploration of evolution using Python and a hand-coded NN!

![evosim_image](https://github.com/NathanielBeen/evosim/assets/39103518/4c09af47-7f4d-4f79-97e5-f6396b30d065)

I got the idea for this project from https://github.com/davidrmiller/biosim4, and a lot of the core methodology remains the same, although I have deviated significantly from Miller's implemntation strategy for many compononents.

## What it does

EvoSim explores the basic principles of evolution by simulating generations of individual organisms and seeing how many meet the given survival criteria. In summary, each generation is made up of a number of individuals, each of which has a "genome" consisting of a certain number of binary genes. At the start of the generation these genes are converted into connections in a simple nueral network, which contains sense nodes (distance from the nearest boundary, for example), inner nodes, and action nodes (move forward, for example). The simulation is run for a certain number of steps, with each individual taking actions based upon the calculated values in its own NN. At the end of the generation, survivors are determined based upon some survival criteria (get within 5 units of the left wall, for example) and a new generation is created based upon the genomes of those survivors. Along the way the program will generate videos of certain generations (which look like the image linked above), and a graph showing the average genome of an individual within the generation.

![example_nueral_net](https://github.com/NathanielBeen/evosim/assets/39103518/ee920ba4-7c6a-4fa0-9555-20d20876e8a2)


## Getting Started

In order to run EvoSim you will need to have poetry installed on your local machine. Once you have downloaded this repo run `poetry install`. Once you have done that, the program can be run with `poetry run python main.py`

Note: currently the program will output result files to a hard-coded folder (`ASSET_FOLDER` in `video.py`), so you will need to alter said attribute to point to your desired output folder. This will be improved in future updates

Additionally, parameters related to the simulation, such as the number of generations or how often to take snapshots, can be edited in `runConfig.py`


