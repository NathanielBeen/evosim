import matplotlib.pyplot as plt

from grid import Grid

class Graph:
    def __init__(self, grid: Grid):
        self.grid = grid

    def drawFrame(self):    
        _, ax = plt.subplots()
        ax.set_xlim(0, self.grid.width)
        ax.set_ylim(0, self.grid.height)

        print(f'X values: ${[org.loc.x for org in self.grid.organisms]}')
        print(f'Y values: ${[org.loc.y for org in self.grid.organisms]}')

        ax.scatter(
            [org.loc.x for org in self.grid.organisms],
            [org.loc.y for org in self.grid.organisms]
        )

        plt.show()