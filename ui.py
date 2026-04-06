import tkinter as tk
from life import Board, Cell


CELL_SIZE = 40
ALIVE_COLOR = "#4ade80"
DEAD_COLOR = "#1e1e2e"
GRID_COLOR = "#2e2e3e"
BG_COLOR = "#1e1e2e"
TEXT_COLOR = "#cdd6f4"


def make_glider(board, row=1, col=1):
    pattern = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    for dr, dc in pattern:
        cell = board.get(row + dr, col + dc)
        if cell:
            cell.alive = True


class GameUI:
    def __init__(self, root, board):
        self.root = root
        self.board = board
        self.generation = 0
        self.running = False
        self.speed = 200  # ms between auto-steps

        root.title("Conway's Game of Life")
        root.configure(bg=BG_COLOR)
        root.resizable(False, False)

        canvas_size = board.size * CELL_SIZE
        self.canvas = tk.Canvas(
            root,
            width=canvas_size,
            height=canvas_size,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(10, 0))
        self.canvas.bind("<Button-1>", self.on_cell_click)

        controls = tk.Frame(root, bg=BG_COLOR)
        controls.pack(pady=10)

        btn_style = {"bg": "#313244", "fg": TEXT_COLOR, "relief": "flat",
                     "padx": 12, "pady": 6, "cursor": "hand2"}

        self.step_btn = tk.Button(controls, text="Step →", command=self.step, **btn_style)
        self.step_btn.pack(side="left", padx=4)

        self.run_btn = tk.Button(controls, text="Run ▶", command=self.toggle_run, **btn_style)
        self.run_btn.pack(side="left", padx=4)

        reset_btn = tk.Button(controls, text="Reset", command=self.reset, **btn_style)
        reset_btn.pack(side="left", padx=4)

        self.gen_label = tk.Label(
            root, text="Generation: 0", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)
        )
        self.gen_label.pack(pady=(0, 10))

        hint = tk.Label(
            root, text="Click cells to toggle  •  Arrow keys to step",
            bg=BG_COLOR, fg="#6c7086", font=("Helvetica", 10)
        )
        hint.pack(pady=(0, 8))

        root.bind("<Right>", lambda e: self.step())
        root.bind("<Down>", lambda e: self.step())
        root.bind("<space>", lambda e: self.toggle_run())

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        size = self.board.size
        for row in range(size):
            for col in range(size):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                cell = self.board.get(row, col)
                color = ALIVE_COLOR if cell.alive else DEAD_COLOR
                self.canvas.create_rectangle(
                    x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                    fill=color, outline=GRID_COLOR
                )
        self.gen_label.config(text=f"Generation: {self.generation}")

    def step(self):
        self.board.next_generation()
        self.generation += 1
        self.draw()

    def toggle_run(self):
        self.running = not self.running
        self.run_btn.config(text="Pause ⏸" if self.running else "Run ▶")
        if self.running:
            self._auto_step()

    def _auto_step(self):
        if self.running:
            self.step()
            self.root.after(self.speed, self._auto_step)

    def reset(self):
        self.running = False
        self.run_btn.config(text="Run ▶")
        self.board.cells = [Cell() for _ in range(self.board.size ** 2)]
        make_glider(self.board)
        self.generation = 0
        self.draw()

    def on_cell_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        cell = self.board.get(row, col)
        if cell:
            cell.alive = not cell.alive
            self.draw()


if __name__ == "__main__":
    board = Board(size=10)
    make_glider(board)

    root = tk.Tk()
    GameUI(root, board)
    root.mainloop()
