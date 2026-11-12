# THE VOID'S TURRETS (11.11, F5): small turrets come up out of the outer islands (out of your reach there), shoot
# once - a spiral, a sprinkler or a line at you - and go back down at once. Here: when and where they come up, what
# they shoot and how they look; void_fight.py only calls update() and draw().

import math
import random

import pygame

from game.combat.song.emitters import bullet
from game import difficulty as DIFF

EVERY = 150                       # frames between two turrets coming up
HARD_EVERY = 100                  # (12.11) hard mode: more of them
RISE = 36                         # frames it comes up (you see it coming) ...
HIDE = 24                         # ... and goes down after its shot
SIZE = 26                         # px: half its width
COLOUR, EDGE, BARREL = (120, 96, 170), (40, 28, 60), (230, 210, 255)
DAMAGE = 5000

# what a turret shoots (frames it shoots for; on which of them; how)
PATTERNS = {
    "spiral": {"frames": 48, "step": 3, "arms": 2, "turn": 17, "speed": 6, "width": 12, "kind": "ghost_bullet"},
    "sprinkler": {"frames": 60, "step": 6, "arms": 4, "turn": 9, "speed": 6, "width": 12, "kind": "flower_pink"},
    "line": {"frames": 25, "step": 5, "arms": 1, "turn": 0, "speed": 13, "width": 13, "kind": "bullet_red"},
}


class Turret:
    def __init__(self, island, pattern, spec):
        self.x, self.y = island
        self.pattern, self.spec = pattern, spec                   # its name ("line" aims) and PATTERNS[name]
        self.stage, self.left = "rise", RISE
        self.angle = random.uniform(0, math.tau)

    @property
    def gone(self):
        return self.stage == "gone"

    def height(self):
        """How far out it is (0 = down in its island, 1 = all the way up)."""
        if self.stage == "rise":
            return 1 - self.left / RISE
        if self.stage == "hide":
            return self.left / HIDE
        return 1.0

    def update(self, target, info, arena_size):
        self.left -= 1
        shots = self.fire(target, info, arena_size) if self.stage == "shoot" else []
        if self.left <= 0:
            self.stage, self.left = {"rise": ("shoot", self.spec["frames"]),
                                     "shoot": ("hide", HIDE), "hide": ("gone", 0)}[self.stage]
        return shots

    def fire(self, target, info, arena_size):
        p = self.spec
        if self.left % p["step"]:
            return []
        if self.pattern == "line":
            self.angle = math.atan2(target[1] - self.y, target[0] - self.x)
        else:
            self.angle += math.radians(p["turn"])
        return [bullet(self.x, self.y, self.angle + i * math.tau / p["arms"], p["speed"], p["width"], p["kind"],
                       info, arena_size, DAMAGE, None) for i in range(p["arms"])]

    def draw(self, screen):
        k = self.height()
        half = max(1, int(SIZE * k))
        box = pygame.Rect(0, 0, half * 2, half * 2)
        box.center = (int(self.x), int(self.y))
        pygame.draw.rect(screen, COLOUR, box, 0, 6)
        pygame.draw.rect(screen, EDGE, box, 4, 6)
        if k > 0.5:
            end = (self.x + math.cos(self.angle) * half * 1.6, self.y + math.sin(self.angle) * half * 1.6)
            pygame.draw.line(screen, BARREL, (self.x, self.y), end, 6)


class Turrets:
    """F5's turrets: one comes up out of a random outer island every EVERY frames."""

    def __init__(self, bullet_info, arena_size, hard=False, easy=False):
        self.info, self.arena_size = bullet_info, arena_size
        self.patterns = {name: easy_pattern(p) for name, p in PATTERNS.items()} if easy else PATTERNS
        self.every = HARD_EVERY if hard else EVERY
        self.timer = 0
        self.up = []

    def update(self, islands, target):
        """islands: [(x, y, r)] the outer ones. -> new bullets"""
        self.timer += 1
        if self.timer % self.every == 0 and islands:
            free = [i for i in islands if all(math.dist(i[:2], (t.x, t.y)) > 1 for t in self.up)]
            x, y, _ = random.choice(free or islands)
            name = random.choice(list(self.patterns))
            self.up.append(Turret((x, y), name, self.patterns[name]))
        out = []
        for turret in self.up:
            out += turret.update(target, self.info, self.arena_size)
        self.up = [t for t in self.up if not t.gone]
        return out

    def draw(self, screen):
        for turret in self.up:
            turret.draw(screen)


def easy_pattern(p):
    """(12.11) "I Have a Job": fewer arms - or, with one arm, fewer shots (a longer step between them)."""
    if p["arms"] > 1:
        return dict(p, arms=DIFF.fewer(p["arms"]))
    return dict(p, step=round(p["step"] / DIFF.EASY_BULLETS))
