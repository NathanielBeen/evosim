import click
import evosim.simulation as sim
from config import Config

@click.command()
@click.argument('folder', required=True)
@click.option("--generations", '-g', type=int, default=Config.get(Config.GENERATIONS), required=False, 
                help=f"the number of generations to simulate (defaults to {Config.get(Config.GENERATIONS)})")
@click.option("--steps", '-s', type=int, default=Config.get(Config.STEPS), required=False,
                help=f"the number of steps in each generation (defaults to {Config.get(Config.STEPS)})")
@click.option("--organisms", '-o', type=int, default=Config.get(Config.ORGANSISMS), required=False, 
                help=f"the number of organisms in each generation (defaults to {Config.get(Config.ORGANSISMS)})")
@click.option("--genes", '-ge', type=int, default=Config.get(Config.GENES), 
                help=f"the number of genes in each organism's genome (the number of connections in each organism's name - defaults to {Config.get(Config.GENES)})")
def cli(folder: str, generations: int, steps: int, organisms: int, genes: int):
    Config.set(Config.GENERATIONS, generations)
    Config.set(Config.STEPS, steps)
    Config.set(Config.ORGANSISMS, organisms)
    Config.set(Config.GENES, genes)

    simul = sim.Simulation(folder)
    simul.runSimulation()
