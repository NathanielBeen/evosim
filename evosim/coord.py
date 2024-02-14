class Coord:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def mapString(self):
        return f'{self.x}_{self.y}'
    
    def weightedDifference(self, other: 'Coord'):
        return abs(self.x - other.x) ** 2 + abs(self.y - other.y) ** 2
    
    def __add__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")

        return Coord(self.x + other.x, self.y + other.y)
    
    __radd__ = __add__
    
    def __sub__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")
        return Coord(self.x - other.x, self.y - other.y)
    
    __rsub__ = __sub__
    
    def __iadd__(self, other):
        if not isinstance(other, Coord):
            raise ValueError(f"{other} must be a Coord object")

        self.x += other.x
        self.y += other.y
        return self
    
    def __eq__(self, other):
        return isinstance(other, Coord) and self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
