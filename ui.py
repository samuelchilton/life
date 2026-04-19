import pygame
import sys
import json
import os
import random
from life import Board, Cell

ALIVE_COLOR     = (74, 222, 128)
RED_COLOR       = (243, 139, 168)
DEAD_COLOR      = (42, 42, 62)
GRID_COLOR      = (0, 0, 0)
BG_COLOR        = (30, 30, 46)
PANEL_COLOR     = (24, 24, 37)
BTN_COLOR       = (49, 50, 68)
BTN_HOVER_COLOR = (69, 71, 90)
TEXT_COLOR      = (205, 214, 244)
HINT_COLOR      = (108, 112, 134)

PANEL_H         = 80
SPEED           = 0
MAX_GENERATIONS = 100
MIN_CELL        = 3.0
MAX_CELL        = 80.0
ZOOM_STEP       = 1.15

HERE = os.path.dirname(os.path.abspath(__file__))
GREEN_FILE = os.path.join(HERE, 'green.json')
RED_FILE   = os.path.join(HERE, 'red.json')


def make_glider(board, row=1, col=1, color='green'):
    pattern = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
    for dr, dc in pattern:
        cell = board.get(row + dr, col + dc)
        if cell:
            cell.alive = True
            cell.color = color


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
    def __init__(self, size):
        self.size = size

        pygame.init()
        info = pygame.display.Info()
        self.win_w = info.current_w - 40
        self.win_h = info.current_h - 80
        self.canvas_h = self.win_h - PANEL_H

        self.cell_size = max(MIN_CELL, min(MAX_CELL, min(self.win_w / size, self.canvas_h / size)))
        board_px = size * self.cell_size
        self.offset_x = (self.win_w - board_px) / 2
        self.offset_y = (self.canvas_h - board_px) / 2

        self.screen = pygame.display.set_mode((self.win_w, self.win_h))
        pygame.display.set_caption("Conway's Game of Life")

        self.font       = pygame.font.SysFont("Helvetica", 14)
        self.small_font = pygame.font.SysFont("Helvetica", 11)

        self.board       = Board(size=size)
        self.generation  = 0
        self.place_color = 'green'
        self.render_live = False
        self.status_msg  = ''

        self.dragging   = False
        self.drag_start = None
        self.drag_pos   = None

        panel_y = self.canvas_h + 12
        x = 16
        def btn(label, w=88):
            nonlocal x
            b = Button((x, panel_y, w, 28), label)
            x += w + 8
            return b

        self.btn_step         = btn("Step ->", 80)
        self.btn_run          = btn("Run", 80)
        self.btn_reset        = btn("Reset", 80)
        self.btn_glider       = btn("Glider", 80)
        self.btn_random       = btn("Random 10x10", 110)
        self.btn_random_fill  = btn("Random Fill", 100)
        self.btn_export       = btn("Export JSON", 100)
        self.btn_import       = btn("Import JSON", 100)
        self.btn_color        = btn("Place: Green", 108)
        self.btn_render       = btn("Render: Final", 112)

        self.buttons = [
            self.btn_step, self.btn_run, self.btn_reset, self.btn_glider,
            self.btn_random, self.btn_random_fill, self.btn_export,
            self.btn_import, self.btn_color, self.btn_render,
        ]

    def zoom(self, factor, mouse_pos):
        mx, my = mouse_pos
        old = self.cell_size
        new = max(MIN_CELL, min(MAX_CELL, old * factor))
        ratio = new / old
        self.offset_x = mx - (mx - self.offset_x) * ratio
        self.offset_y = my - (my - self.offset_y) * ratio
        self.cell_size = new

    def draw(self):
        self.screen.fill(BG_COLOR)

        cs = self.cell_size
        ox, oy = self.offset_x, self.offset_y

        col_start = max(0, int(-ox / cs))
        col_end   = min(self.size, int((self.win_w - ox) / cs) + 1)
        row_start = max(0, int(-oy / cs))
        row_end   = min(self.size, int((self.canvas_h - oy) / cs) + 1)

        self.screen.set_clip((0, 0, self.win_w, self.canvas_h))
        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                x = int(ox + col * cs)
                y = int(oy + row * cs)
                w = int(ox + (col + 1) * cs) - x
                h = int(oy + (row + 1) * cs) - y
                cell = self.board.get(row, col)
                if cell.alive:
                    color = ALIVE_COLOR if cell.color == 'green' else RED_COLOR
                else:
                    color = DEAD_COLOR
                if cs > 5:
                    pygame.draw.rect(self.screen, color, (x + 1, y + 1, w - 2, h - 2))
                    pygame.draw.rect(self.screen, GRID_COLOR, (x, y, w, h), 1)
                else:
                    pygame.draw.rect(self.screen, color, (x, y, w, h))
        self.screen.set_clip(None)

        pygame.draw.rect(self.screen, PANEL_COLOR, (0, self.canvas_h, self.win_w, PANEL_H))

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(self.screen, self.font, mouse_pos)

        green_count = sum(1 for c in self.board.cells if c.alive and c.color == 'green')
        red_count   = sum(1 for c in self.board.cells if c.alive and c.color == 'red')

        right_x = self.win_w - 16
        self.screen.blit(self.font.render(f"Generation: {self.generation}", True, TEXT_COLOR),
                         (right_x - self.font.size(f"Generation: {self.generation}")[0], self.canvas_h + 10))
        self.screen.blit(self.font.render(f"Red: {red_count}", True, RED_COLOR),
                         (right_x - self.font.size(f"Red: {red_count}")[0], self.canvas_h + 30))
        self.screen.blit(self.font.render(f"Green: {green_count}", True, ALIVE_COLOR),
                         (right_x - self.font.size(f"Green: {green_count}")[0], self.canvas_h + 50))

        if self.status_msg:
            status = self.small_font.render(self.status_msg, True, HINT_COLOR)
            self.screen.blit(status, (16, self.canvas_h + PANEL_H - 18))

        pygame.display.flip()

    def step(self):
        self.board.next_generation()
        self.generation += 1

    def toggle_run(self):
        if self.render_live:
            for _ in range(MAX_GENERATIONS):
                self.board.next_generation()
                self.generation += 1
                self.draw()
        else:
            self.draw()
            for _ in range(MAX_GENERATIONS):
                self.board.next_generation()
                self.generation += 1

    def toggle_render_mode(self):
        self.render_live = not self.render_live
        self.btn_render.label = "Render: Live" if self.render_live else "Render: Final"

    def reset(self):
        self.board.cells = [Cell() for _ in range(self.board.size ** 2)]
        self.generation = 0

    def spawn_glider(self):
        make_glider(self.board, row=1, col=1, color=self.place_color)

    def spawn_random(self):
        mid = self.size // 2 - 5
        for dr in range(10):
            for dc in range(10):
                cell = self.board.get(mid + dr, mid + dc)
                if cell:
                    cell.alive = random.random() < 0.5
                    cell.color = random.choice(['green', 'red'])

    def spawn_random_fill(self):
        for row in range(self.size):
            for col in range(self.size):
                cell = self.board.get(row, col)
                if cell:
                    cell.alive = random.random() < 0.5
                    cell.color = random.choice(['green', 'red'])

    def export_json(self):
        green_coords = [[r, c] for r in range(self.size) for c in range(self.size)
                        if self.board.get(r, c).alive and self.board.get(r, c).color == 'green']
        red_coords   = [[r, c] for r in range(self.size) for c in range(self.size)
                        if self.board.get(r, c).alive and self.board.get(r, c).color == 'red']
        with open(GREEN_FILE, 'w') as f:
            json.dump(green_coords, f, indent=2)
        with open(RED_FILE, 'w') as f:
            json.dump(red_coords, f, indent=2)
        self.status_msg = f"Exported to {GREEN_FILE} and {RED_FILE}"

    def import_json(self):
        try:
            with open(GREEN_FILE) as f:
                green_coords = json.load(f)
            with open(RED_FILE) as f:
                red_coords = json.load(f)
            for cell in self.board.cells:
                cell.alive = False
            for r, c in green_coords:
                cell = self.board.get(r, c)
                if cell:
                    cell.alive = True
                    cell.color = 'green'
            for r, c in red_coords:
                cell = self.board.get(r, c)
                if cell:
                    cell.alive = True
                    cell.color = 'red'
            self.status_msg = "Imported successfully"
        except FileNotFoundError:
            self.status_msg = "No JSON files found — export first"
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            self.status_msg = f"Import error: {e}"

    def toggle_place_color(self):
        self.place_color = 'red' if self.place_color == 'green' else 'green'
        self.btn_color.label = f"Place: {self.place_color.capitalize()}"

    def on_canvas_click(self, pos):
        x, y = pos
        col = int((x - self.offset_x) / self.cell_size)
        row = int((y - self.offset_y) / self.cell_size)
        cell = self.board.get(row, col)
        if cell:
            if cell.alive:
                cell.alive = False
            else:
                cell.alive = True
                cell.color = self.place_color

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.drag_start = event.pos
                    self.drag_pos   = event.pos
                    self.dragging   = False

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if not self.dragging and self.drag_start:
                        pos = self.drag_start
                        hit = next((b for b in self.buttons if b.hit(pos)), None)
                        if hit:
                            if hit is self.btn_step:        self.step()
                            elif hit is self.btn_run:       self.toggle_run()
                            elif hit is self.btn_reset:     self.reset()
                            elif hit is self.btn_glider:    self.spawn_glider()
                            elif hit is self.btn_random:    self.spawn_random()
                            elif hit is self.btn_random_fill: self.spawn_random_fill()
                            elif hit is self.btn_export:    self.export_json()
                            elif hit is self.btn_import:    self.import_json()
                            elif hit is self.btn_color:     self.toggle_place_color()
                            elif hit is self.btn_render:    self.toggle_render_mode()
                        elif pos[1] < self.canvas_h:
                            self.on_canvas_click(pos)
                    self.dragging   = False
                    self.drag_start = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.drag_start and event.buttons[0]:
                        dx = event.pos[0] - self.drag_pos[0]
                        dy = event.pos[1] - self.drag_pos[1]
                        if abs(event.pos[0] - self.drag_start[0]) + abs(event.pos[1] - self.drag_start[1]) > 4:
                            self.dragging = True
                        if self.dragging:
                            self.offset_x += dx
                            self.offset_y += dy
                        self.drag_pos = event.pos

                elif event.type == pygame.MOUSEWHEEL:
                    factor = ZOOM_STEP if event.y > 0 else 1 / ZOOM_STEP
                    self.zoom(factor, pygame.mouse.get_pos())

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.step()
                    elif event.key == pygame.K_SPACE:
                        self.toggle_run()

            self.draw()
            clock.tick(60)


if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    GameUI(size).run()
