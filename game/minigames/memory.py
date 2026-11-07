# MEMORY (Dot's game): 4 x 5 cards = 10 pairs, find them all before the time runs out.
# Mouse: click a card.  Keyboard: arrows / WASD + Space or Enter.

import math, random
import pygame
from game.minigames.base import Minigame

ROWS, COLS = 4, 5
TIME_LIMIT = 30             # seconds - hard but doable (author: 20 s less than the first 50)
MISMATCH_FRAMES = 35        # how long two wrong cards stay face up (the clock keeps running)

# 10 different pictures: shape + colour
SYMBOLS = [("circle", (255, 90, 90)), ("square", (90, 160, 255)), ("triangle", (120, 220, 120)),
           ("diamond", (255, 210, 60)), ("star", (230, 120, 255)), ("cross", (255, 150, 60)),
           ("ring", (90, 230, 230)), ("hexagon", (250, 130, 190)), ("heart", (220, 60, 90)), ("moon", (200, 200, 220))]


class Memory(Minigame):
    title = "Dot's Memory"

    def __init__(self, screen, background, volume=1.0):
        super().__init__(screen, background, volume)
        cards = list(range(len(SYMBOLS))) * 2
        random.shuffle(cards)
        self.cards = cards                    # symbol index per card, reading order
        self.found = set()                    # card indexes already matched
        self.open = []                        # 1-2 cards face up right now
        self.mismatch = 0
        self.cursor = 0
        self.frames_left = TIME_LIMIT * 60
        self.rects = []

    def on_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, r in enumerate(self.rects):
                    if r.collidepoint(e.pos):
                        self.cursor = i
                        self.flip(i)
            elif e.type == pygame.KEYDOWN:
                r, c = divmod(self.cursor, COLS)
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    c = (c - 1) % COLS
                elif e.key in (pygame.K_RIGHT, pygame.K_d):
                    c = (c + 1) % COLS
                elif e.key in (pygame.K_UP, pygame.K_w):
                    r = (r - 1) % ROWS
                elif e.key in (pygame.K_DOWN, pygame.K_s):
                    r = (r + 1) % ROWS
                elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.flip(self.cursor)
                self.cursor = r * COLS + c

    def flip(self, i):
        if self.mismatch or i in self.found or i in self.open:
            return
        self.open.append(i)
        self.play("flip")
        if len(self.open) == 2:
            a, b = self.open
            if self.cards[a] == self.cards[b]:
                self.found.update(self.open)
                self.open = []
                self.play("match")
                if len(self.found) == len(self.cards):
                    self.end(True)
            else:
                self.mismatch = MISMATCH_FRAMES
                self.play("wrong")

    def on_update(self):
        self.frames_left -= 1
        if self.frames_left <= 0:
            self.end(False)
        if self.mismatch:
            self.mismatch -= 1
            if not self.mismatch:
                self.open = []

    def on_draw(self):
        sw, sh = self.screen.get_size()
        self.draw_header("Find all pairs.  Mouse or arrows + Space", self.frames_left / 60, TIME_LIMIT)
        size = int(min(sw * 0.6 / COLS, sh * 0.68 / ROWS))
        gap = size // 8
        card = size - gap
        left = sw // 2 - (COLS * size) // 2
        top = int(sh * 0.2)
        self.rects = []
        for i, symbol in enumerate(self.cards):
            r, c = divmod(i, COLS)
            rect = pygame.Rect(left + c * size, top + r * size, card, card)
            self.rects.append(rect)
            face_up = i in self.found or i in self.open
            if face_up:
                pygame.draw.rect(self.screen, (245, 240, 230) if i not in self.found else (190, 190, 180), rect, 0, 12)
                self.draw_symbol(SYMBOLS[symbol], rect)
            else:
                pygame.draw.rect(self.screen, (120, 80, 50), rect, 0, 12)           # bread-brown backs (Dot is a baker)
                pygame.draw.rect(self.screen, (170, 120, 80), rect.inflate(-card // 5, -card // 5), 3, 10)
            if i == self.cursor:
                pygame.draw.rect(self.screen, (255, 230, 60), rect.inflate(8, 8), 4, 14)

    def draw_symbol(self, symbol, rect):
        shape, color = symbol
        cx, cy = rect.center
        r = rect.width * 0.3
        s = self.screen
        if shape == "circle":
            pygame.draw.circle(s, color, (cx, cy), r)
        elif shape == "ring":
            pygame.draw.circle(s, color, (cx, cy), r, max(4, int(r * 0.3)))
        elif shape == "square":
            pygame.draw.rect(s, color, pygame.Rect(cx - r, cy - r, 2 * r, 2 * r), 0, 6)
        elif shape == "triangle":
            pygame.draw.polygon(s, color, [(cx, cy - r), (cx + r, cy + r * 0.8), (cx - r, cy + r * 0.8)])
        elif shape == "diamond":
            pygame.draw.polygon(s, color, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)])
        elif shape == "star":
            pts = [(cx + math.cos(math.pi / 2 + k * math.pi / 5) * (r if k % 2 == 0 else r * 0.45),
                    cy - math.sin(math.pi / 2 + k * math.pi / 5) * (r if k % 2 == 0 else r * 0.45)) for k in range(10)]
            pygame.draw.polygon(s, color, pts)
        elif shape == "cross":
            w = r * 0.55
            pygame.draw.rect(s, color, pygame.Rect(cx - w / 2, cy - r, w, 2 * r))
            pygame.draw.rect(s, color, pygame.Rect(cx - r, cy - w / 2, 2 * r, w))
        elif shape == "hexagon":
            pygame.draw.polygon(s, color, [(cx + math.cos(k * math.pi / 3) * r, cy + math.sin(k * math.pi / 3) * r) for k in range(6)])
        elif shape == "heart":
            pygame.draw.circle(s, color, (cx - r * 0.45, cy - r * 0.25), r * 0.5)
            pygame.draw.circle(s, color, (cx + r * 0.45, cy - r * 0.25), r * 0.5)
            pygame.draw.polygon(s, color, [(cx - r * 0.93, cy - r * 0.05), (cx + r * 0.93, cy - r * 0.05), (cx, cy + r)])
        elif shape == "moon":
            pygame.draw.circle(s, color, (cx, cy), r)
            pygame.draw.circle(s, (245, 240, 230), (cx + r * 0.45, cy - r * 0.2), r * 0.85)
