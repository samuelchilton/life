import sys
import tty
import termios


class Cell:
    def __init__(self, alive=False):
        self.alive = alive

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

    def count_live_neighbors(self, row, col):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                neighbor = self.get(row + dr, col + dc)
                if neighbor and neighbor.alive:
                    count += 1
        return count

    def next_generation(self):
        new_cells = []
        for row in range(self.size):
            for col in range(self.size):
                cell = self.get(row, col)
                neighbors = self.count_live_neighbors(row, col)
                if cell.alive:
                    alive = neighbors in (2, 3)
                else:
                    alive = neighbors == 3
                new_cells.append(Cell(alive))
        self.cells = new_cells

    def display(self, generation):
        print(f"\033[H\033[J", end="")  # clear screen
        print(f"Conway's Game of Life  |  Generation: {generation}")
        print(f"Press any arrow key to advance, Q to quit\n")
        for row in range(self.size):
            row_str = "  ".join(str(self.get(row, col)) for col in range(self.size))
            print(row_str)


def read_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return "arrow"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def make_glider(board, row=1, col=1):
    pattern = [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2)
    ]
    for dr, dc in pattern:
        cell = board.get(row + dr, col + dc)
        if cell:
            cell.alive = True


if __name__ == "__main__":
    board = Board(size=10)
    make_glider(board)

    generation = 0
    board.display(generation)

    while True:
        key = read_key()
        if key in ("q", "Q", "\x03"):
            print("\nBye!")
            break
        elif key == "arrow":
            board.next_generation()
            generation += 1
            board.display(generation)
