# SUDOKU (Bramble's game), always 9 x 9, a new random puzzle every time (it can't be learned by heart).
#   "think" - few numbers given (hard), no time limit, but 3 MISTAKES = you lose
#   "speed" - many numbers given, short time limit, every MISTAKE costs 15 s
# A mistake = writing a number that is not the solution of that cell (the cell turns red and is cleared).
# Controls: mouse click or arrows / WASD = pick a cell, 1-9 = write, Backspace / Delete = erase,
#           Esc = give up (counts as a loss).
# Numbers that break a rule (same number twice in a row / column / box) are shown red.

import random
import pygame
from game.minigames.base import Minigame

MODES = {
    "think": {"givens": 26, "time": None, "name": "Thinking", "max_mistakes": 3, "mistake_seconds": 0},
    "speed": {"givens": 50, "time": 150, "name": "Speed", "max_mistakes": None, "mistake_seconds": 15},
}
WRONG_FLASH = 30            # frames a wrong number stays red before it is cleared


def _full_grid(rnd):
    grid = [[0] * 9 for _ in range(9)]
    def fill(k):
        if k == 81:
            return True
        r, c = divmod(k, 9)
        nums = list(range(1, 10))
        rnd.shuffle(nums)
        for n in nums:
            if _allowed(grid, r, c, n):
                grid[r][c] = n
                if fill(k + 1):
                    return True
        grid[r][c] = 0
        return False
    fill(0)
    return grid


def _allowed(grid, r, c, n):
    if any(grid[r][x] == n for x in range(9)) or any(grid[y][c] == n for y in range(9)):
        return False
    br, bc = r // 3 * 3, c // 3 * 3
    return not any(grid[y][x] == n for y in range(br, br + 3) for x in range(bc, bc + 3))


def _count_solutions(grid, limit=2):
    # backtracking from the cell with the fewest options; stops at `limit`
    best, options = None, None
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                opts = [n for n in range(1, 10) if _allowed(grid, r, c, n)]
                if not opts:
                    return 0
                if options is None or len(opts) < len(options):
                    best, options = (r, c), opts
    if best is None:
        return 1
    r, c = best
    count = 0
    for n in options:
        grid[r][c] = n
        count += _count_solutions(grid, limit - count)
        if count >= limit:
            break
    grid[r][c] = 0
    return count


def make_puzzle(givens, rnd=None):
    """(puzzle, solution) with exactly one solution and about `givens` numbers shown."""
    rnd = rnd or random.Random()
    solution = _full_grid(rnd)
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(9) for c in range(9)]
    rnd.shuffle(cells)
    shown = 81
    for r, c in cells:
        if shown <= givens:
            break
        keep = puzzle[r][c]
        puzzle[r][c] = 0
        if _count_solutions([row[:] for row in puzzle]) != 1:
            puzzle[r][c] = keep                     # removing it would allow two solutions
        else:
            shown -= 1
    return puzzle, solution


class Sudoku(Minigame):
    hide_board_in_countdown = True          # no peeking at the puzzle before "GO!"

    def __init__(self, screen, background, mode="think", volume=1.0):
        super().__init__(screen, background, volume)
        self.mode = MODES[mode]
        self.title = f"Bramble's Sudoku - {self.mode['name']}"
        self.puzzle, self.solution = make_puzzle(self.mode["givens"])
        self.grid = [row[:] for row in self.puzzle]
        self.cursor = (4, 4)
        self.frames_left = self.mode["time"] * 60 if self.mode["time"] else None
        self.cell_rects = {}
        self.mistakes = 0
        self.wrong = {}                     # cell -> frames left of the red flash

    def lose_text(self):
        if self.frames_left is not None and self.frames_left <= 0:
            return "Time's up!"
        if self.mode["max_mistakes"] and self.mistakes >= self.mode["max_mistakes"]:
            return "Three mistakes!"
        return "You gave up."

    def on_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for cell, rect in self.cell_rects.items():
                    if rect.collidepoint(e.pos):
                        self.cursor = cell
            elif e.type == pygame.KEYDOWN:
                r, c = self.cursor
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    c = (c - 1) % 9
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    c = (c + 1) % 9
                elif e.key in (pygame.K_UP, pygame.K_w):
                    r = (r - 1) % 9
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    r = (r + 1) % 9
                elif e.key == pygame.K_ESCAPE:
                    self.end(False)
                elif self.puzzle[r][c] == 0:
                    digit = None
                    if pygame.K_1 <= e.key <= pygame.K_9:
                        digit = e.key - pygame.K_0
                    elif pygame.K_KP1 <= e.key <= pygame.K_KP9:
                        digit = e.key - pygame.K_KP1 + 1
                    elif e.key in (pygame.K_BACKSPACE, pygame.K_DELETE):     # (0 does nothing - author)
                        digit = 0
                    if digit is not None:
                        self.grid[r][c] = digit
                        if digit and digit != self.solution[r][c]:
                            self.mistake((r, c))
                        elif digit:
                            self.play("write")
                        if self.grid == self.solution:
                            self.end(True)
                self.cursor = (r, c)

    def mistake(self, cell):
        self.mistakes += 1
        self.wrong[cell] = WRONG_FLASH
        self.play("wrong")
        if self.frames_left is not None:
            self.frames_left -= self.mode["mistake_seconds"] * 60
        if self.mode["max_mistakes"] and self.mistakes >= self.mode["max_mistakes"]:
            self.end(False)

    def on_update(self):
        for cell in list(self.wrong):
            self.wrong[cell] -= 1
            if self.wrong[cell] <= 0:
                del self.wrong[cell]
                r, c = cell
                if self.grid[r][c] != self.solution[r][c]:
                    self.grid[r][c] = 0            # the wrong number disappears
        if self.frames_left is not None:
            self.frames_left -= 1
            if self.frames_left <= 0:
                self.end(False)

    def _conflict(self, r, c):
        n = self.grid[r][c]
        if not n:
            return False
        self.grid[r][c] = 0
        bad = not _allowed(self.grid, r, c, n)
        self.grid[r][c] = n
        return bad

    def on_draw(self):
        sw, sh = self.screen.get_size()
        hint = "1-9 write   Backspace erase   Esc give up"
        if self.frames_left is None:
            self.draw_header(hint + f"   Mistakes: {self.mistakes} / {self.mode['max_mistakes']}")
        else:
            self.draw_header(hint + f"   (a mistake costs {self.mode['mistake_seconds']} s)", self.frames_left / 60, self.mode["time"])
        size = int(sh * 0.07)
        left, top = sw // 2 - size * 9 // 2, int(sh * 0.19)
        board = pygame.Rect(left, top, size * 9, size * 9)
        pygame.draw.rect(self.screen, (245, 240, 230), board)
        cr, cc = self.cursor
        self.cell_rects = {}
        for r in range(9):
            for c in range(9):
                rect = pygame.Rect(left + c * size, top + r * size, size, size)
                self.cell_rects[(r, c)] = rect
                if (r, c) in self.wrong:
                    pygame.draw.rect(self.screen, (255, 150, 150), rect)
                elif (r, c) == self.cursor:
                    pygame.draw.rect(self.screen, (255, 230, 120), rect)
                elif r == cr or c == cc or (r // 3 == cr // 3 and c // 3 == cc // 3):
                    pygame.draw.rect(self.screen, (230, 225, 205), rect)
                n = self.grid[r][c]
                if n:
                    given = self.puzzle[r][c] != 0
                    color = (200, 30, 30) if (r, c) in self.wrong or self._conflict(r, c) else ((20, 20, 25) if given else (40, 90, 200))
                    img = self.font.render(str(n), True, color)
                    self.screen.blit(img, img.get_rect(center=rect.center))
        for k in range(10):
            w = 4 if k % 3 == 0 else 1
            pygame.draw.line(self.screen, (20, 20, 25), (left + k * size, top), (left + k * size, top + 9 * size), w)
            pygame.draw.line(self.screen, (20, 20, 25), (left, top + k * size), (left + 9 * size, top + k * size), w)
