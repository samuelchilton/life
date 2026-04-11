import pygame
import sys
from life import Board, Cell

SIZE = 10
CELL_SIZE = 40

ALIVE_COLOR = (74, 222, 128)
DEAD_COLOR = (42, 42, 62)
GRID_COLOR = (0, 0, 0)
BG_COLOR = (30, 30, 46)
BTN_COLOR = (49, 50, 68)
BTN_HOVER_COLOR = (69, 71, 90)
TEXT_COLOR = (205, 214, 244)
HINT_COLOR = (108, 112, 134)

MARGIN = 10
CANVAS_SIZE = SIZE * CELL_SIZE
PANEL_H = 90
WIN_W = CANVAS_SIZE + MARGIN * 2
WIN_H = CANVAS_SIZE + PANEL_H + MARGIN * 2
SPEED = 200  # ms between auto-steps


def make_glider(board, row=1, col=1):
    pattern = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    for dr, dc in pattern:
        cell = board.get(row + dr, col + dc)
        if cell:
            cell.alive = True


class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label

    def draw(self, surface, font, mouse_pos):
        color = BTN_HOVER_COLOR if self.rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        text = font.render(self.label, True, TEXT_COLOR)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Conway's Game of Life")

        self.font = pygame.font.SysFont("Helvetica", 14)
        self.small_font = pygame.font.SysFont("Helvetica", 11)

        self.board = Board(size=SIZE)
        make_glider(self.board)
        self.generation = 0
        self.running = False
        self.last_step = 0

        panel_y = CANVAS_SIZE + MARGIN * 2 + 8
        self.btn_step = Button((MARGIN, panel_y, 80, 28), "Step ->")
        self.btn_run = Button((MARGIN + 88, panel_y, 80, 28), "Run")
        self.btn_reset = Button((MARGIN + 176, panel_y, 80, 28), "Reset")
        self.buttons = [self.btn_step, self.btn_run, self.btn_reset]

    def draw(self):
        self.screen.fill(BG_COLOR)

        for row in range(SIZE):
            for col in range(SIZE):
                x = MARGIN + col * CELL_SIZE
                y = MARGIN + row * CELL_SIZE
                cell = self.board.get(row, col)
                color = ALIVE_COLOR if cell.alive else DEAD_COLOR
                pygame.draw.rect(self.screen, color, (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))
                pygame.draw.rect(self.screen, GRID_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 1)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(self.screen, self.font, mouse_pos)

        gen_surf = self.font.render(f"Generation: {self.generation}", True, TEXT_COLOR)
        self.screen.blit(gen_surf, (MARGIN, CANVAS_SIZE + MARGIN * 2 + 44))

        hint_surf = self.small_font.render("Click cells to toggle  |  Arrow keys to step  |  Space to run", True, HINT_COLOR)
        self.screen.blit(hint_surf, (MARGIN, CANVAS_SIZE + MARGIN * 2 + 66))

        pygame.display.flip()

    def step(self):
        self.board.next_generation()
        self.generation += 1

    def toggle_run(self):
        self.running = not self.running
        self.btn_run.label = "Pause" if self.running else "Run"

    def reset(self):
        self.running = False
        self.btn_run.label = "Run"
        self.board.cells = [Cell() for _ in range(self.board.size ** 2)]
        make_glider(self.board)
        self.generation = 0

    def on_click(self, pos):
        if self.btn_step.hit(pos):
            self.step()
            return
        if self.btn_run.hit(pos):
            self.toggle_run()
            return
        if self.btn_reset.hit(pos):
            self.reset()
            return
        gx, gy = pos[0] - MARGIN, pos[1] - MARGIN
        if 0 <= gx < CANVAS_SIZE and 0 <= gy < CANVAS_SIZE:
            cell = self.board.get(gy // CELL_SIZE, gx // CELL_SIZE)
            if cell:
                cell.alive = not cell.alive

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                        self.step()
                    elif event.key == pygame.K_SPACE:
                        self.toggle_run()

            if self.running:
                now = pygame.time.get_ticks()
                if now - self.last_step >= SPEED:
                    self.step()
                    self.last_step = now

            self.draw()
            clock.tick(60)


if __name__ == "__main__":
    GameUI().run()
