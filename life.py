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

    def count_live_neighbors(self, row, col, color):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                neighbor = self.get(row + dr, col + dc)
                if neighbor and neighbor.alive and neighbor.color == color:
                    count += 1
        return count

    def next_generation(self):
        new_cells = []
        for row in range(self.size):
            for col in range(self.size):
                cell = self.get(row, col)
                if cell.alive:
                    neighbors = self.count_live_neighbors(row, col, cell.color)
                    new_cells.append(Cell(neighbors in (2, 3), cell.color))
                else:
                    green_n = self.count_live_neighbors(row, col, 'green')
                    red_n = self.count_live_neighbors(row, col, 'red')
                    if green_n == 3 and red_n != 3:
                        new_cells.append(Cell(True, 'green'))
                    elif red_n == 3 and green_n != 3:
                        new_cells.append(Cell(True, 'red'))
                    else:
                        new_cells.append(Cell(False))
        self.cells = new_cells
