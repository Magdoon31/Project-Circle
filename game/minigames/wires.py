# WIRES (Hal's antennas): connect every wire on the left to the wire of the SAME colour on the right.
# Like the wire task in Among Us, but keyboard only:
#   W/S or arrows = move,  Space / Enter = take a wire / plug it in,  A or Left / Esc = put the wire back.
# A wrong plug sparks (sound) and the wire drops back. Run out of time = lose (no cost, just try again).

import random
import pygame
from game.minigames.base import Minigame

TIME_LIMIT = 20             # seconds, the same for every antenna (more wires = harder)
WRONG_FRAMES = 18           # how long the wrong plug flashes red
# colour + a small mark at the end of each wire (so the colours can be told apart without the colour too)
WIRE_COLORS = [((230, 60, 60), "R"), ((70, 130, 255), "B"), ((250, 220, 50), "Y"),
               ((70, 200, 90), "G"), ((220, 90, 230), "P"), ((255, 150, 40), "O")]


class Wires(Minigame):
    title = "Hal's Antenna"

    def __init__(self, screen, background, count=4, volume=1.0):
        super().__init__(screen, background, volume)
        self.count = max(2, min(count, len(WIRE_COLORS)))
        colors = list(range(self.count))
        self.left = colors[:]
        random.shuffle(self.left)
        self.right = colors[:]
        while self.right == self.left:          # never already in the right order
            random.shuffle(self.right)
        self.done = set()                       # colours already connected
        self.side = 0                           # 0 = choosing on the left, 1 = plugging in on the right
        self.cursor = [0, 0]
        self.held = None                        # left index of the wire in hand
        self.wrong = 0
        self.wrong_at = None
        self.frames_left = TIME_LIMIT * 60

    def _step(self, d):
        col = self.left if self.side == 0 else self.right
        i = self.cursor[self.side]
        for _ in range(self.count):             # skip wires that are already connected
            i = (i + d) % self.count
            if col[i] not in self.done:
                break
        self.cursor[self.side] = i

    def on_events(self, events):
        for e in events:
            if e.type != pygame.KEYDOWN:
                continue
            if e.key in (pygame.K_UP, pygame.K_w):
                self._step(-1)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self._step(1)
            elif e.key in (pygame.K_LEFT, pygame.K_a, pygame.K_ESCAPE) and self.side == 1:
                self.side, self.held = 0, None
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT, pygame.K_d):
                if self.side == 0:
                    if self.left[self.cursor[0]] not in self.done:
                        self.held = self.cursor[0]
                        self.side = 1
                        if self.right[self.cursor[1]] in self.done:
                            self._step(1)
                        self.play("flip")
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.plug()

    def plug(self):
        color = self.left[self.held]
        if self.right[self.cursor[1]] == color:
            self.done.add(color)
            self.play("match")
            self.side, self.held = 0, None
            if len(self.done) == self.count:
                self.end(True)
            elif self.left[self.cursor[0]] in self.done:
                self._step(1)
        else:
            self.wrong, self.wrong_at = WRONG_FRAMES, (self.held, self.cursor[1])
            self.play("wrong")
            self.side, self.held = 0, None

    def on_update(self):
        self.frames_left -= 1
        if self.frames_left <= 0:
            self.end(False)
        if self.wrong:
            self.wrong -= 1

    def lose_text(self):
        return "Time's up! The wires slipped out."

    def on_draw(self):
        sw, sh = self.screen.get_size()
        self.draw_header("Match the colours.  W/S move, Space take / plug in, A put back",
                         self.frames_left / 60, TIME_LIMIT)
        box = pygame.Rect(0, 0, int(sw * 0.5), int(sh * 0.66))
        box.midtop = (sw // 2, int(sh * 0.2))
        pygame.draw.rect(self.screen, (55, 60, 70), box, 0, 16)           # the junction box
        pygame.draw.rect(self.screen, (150, 155, 165), box, 5, 16)
        gap = box.height / (self.count + 1)
        plug_w, plug_h = box.width // 9, max(16, int(gap * 0.4))
        lx, rx = box.left + plug_w, box.right - plug_w
        ys = [int(box.top + gap * (i + 1)) for i in range(self.count)]
        left_pos = [(lx, y) for y in ys]
        right_pos = [(rx, y) for y in ys]
        # connected wires
        for i, c in enumerate(self.left):
            if c in self.done:
                j = self.right.index(c)
                pygame.draw.line(self.screen, WIRE_COLORS[c][0], left_pos[i], right_pos[j], max(6, plug_h // 3))
        # wire in hand: from its socket to the right-side cursor
        if self.held is not None:
            c = self.left[self.held]
            pygame.draw.line(self.screen, WIRE_COLORS[c][0], left_pos[self.held], right_pos[self.cursor[1]], max(4, plug_h // 4))
        if self.wrong and self.wrong_at:
            a, b = self.wrong_at
            pygame.draw.line(self.screen, (255, 255, 255) if self.wrong % 6 < 3 else (255, 60, 60),
                             left_pos[a], right_pos[b], 3)
        for side, (col, pos) in enumerate(((self.left, left_pos), (self.right, right_pos))):
            for i, c in enumerate(col):
                color, mark = WIRE_COLORS[c]
                x, y = pos[i]
                rect = pygame.Rect(0, 0, plug_w, plug_h)
                rect.center = (x - plug_w // 2, y) if side == 0 else (x + plug_w // 2, y)
                pygame.draw.rect(self.screen, color, rect, 0, 6)
                label = self.font_small.render(mark, True, (20, 20, 20))
                self.screen.blit(label, label.get_rect(center=rect.center))
                active = (side == self.side and i == self.cursor[side] and c not in self.done) or \
                         (side == 0 and i == self.held)
                if active:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect.inflate(10, 10), 4, 8)
