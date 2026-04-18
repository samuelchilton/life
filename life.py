import numpy as np


class Cell:
    def __init__(self, alive=False, color='green'):
        self.alive = alive
        self.color = color

    def __repr__(self):
        return "█" if self.alive else "·"


class Board:
    def __init__(self, size=10, cells=None):
        self.size = size
        if cells is not None:
            self.cells = cells
        else:
            self.cells = [Cell() for _ in range(size * size)]

    def get(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.cells[row * self.size + col]
        return None

    def next_generation(self):
        size = self.size

        # Convert cell list to two 2D numpy arrays — one per color.
        # List comprehensions build the flat arrays in one pass, then reshape
        # into (size x size) grids. This replaces the per-cell Python loops.
        green = np.array(
            [1 if c.alive and c.color == 'green' else 0 for c in self.cells],
            dtype=np.int8
        ).reshape(size, size)

        red = np.array(
            [1 if c.alive and c.color == 'red' else 0 for c in self.cells],
            dtype=np.int8
        ).reshape(size, size)

        # Count same-color neighbors for every cell simultaneously using array
        # slicing. Each of the 8 shifts adds the contribution of one neighbor
        # direction across the whole grid in a single C-level operation, rather
        # than calling get() 8 times per cell in Python.
        def count_neighbors(g):
            n = np.zeros((size, size), dtype=np.int8)
            n[1:,  1:]  += g[:-1, :-1]  # top-left
            n[1:,  :]   += g[:-1, :]    # top
            n[1:,  :-1] += g[:-1, 1:]   # top-right
            n[:,   1:]  += g[:,   :-1]  # left
            n[:,   :-1] += g[:,   1:]   # right
            n[:-1, 1:]  += g[1:,  :-1]  # bottom-left
            n[:-1, :]   += g[1:,  :]    # bottom
            n[:-1, :-1] += g[1:,  1:]   # bottom-right
            return n

        green_n = count_neighbors(green)
        red_n   = count_neighbors(red)

        # Apply Game of Life rules across the entire grid at once using boolean
        # array operations — no Python loop, no branching per cell.
        survive_green = green.astype(bool) & ((green_n == 2) | (green_n == 3))
        survive_red   = red.astype(bool)   & ((red_n   == 2) | (red_n   == 3))

        dead = ~green.astype(bool) & ~red.astype(bool)
        born_green = dead & (green_n == 3) & (red_n != 3)
        born_red   = dead & (red_n   == 3) & (green_n != 3)

        new_green = survive_green | born_green
        new_red   = survive_red   | born_red

        # Write results back to the cell list. This loop is unavoidable given
        # the current Cell-object design, but it's simple assignment with no
        # neighbor lookups so it's fast in practice.
        flat_green = new_green.ravel()
        flat_red   = new_red.ravel()
        new_cells = []
        for i in range(size * size):
            if flat_green[i]:
                new_cells.append(Cell(True, 'green'))
            elif flat_red[i]:
                new_cells.append(Cell(True, 'red'))
            else:
                new_cells.append(Cell(False))
        self.cells = new_cells
