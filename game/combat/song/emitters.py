# EMITTERS: what puts BULLETS into a song fight. Every bullet flies straight on and out of the arena (none stays
# long on the screen - new ones keep coming in instead).
#   Spinner - rotating beams made of bullets: `arms` streams from the mascot, turning round as the song goes.
#   Ring    - one full ring of bullets from the mascot, on the beat.
#   Walls   - a row of bullets comes in from one edge and goes right across to the other; one gap to slip through.
#             (marks on the edge show where it comes from before it does)
# Each one: update(beat, origin) -> new bullets; draw(layer, beat) -> its warning, if it has one; done(beat).

import math

import pygame

from game.combat.projectile import projectile
from game.combat.song.hazards import PINK

BULLET_DAMAGE = 1               # you can't die in a song fight - a hit is only counted
BULLET_REACH = 26               # px between the centres for a hit (smaller than in normal fights: 32)
FRAME_MS = 1000 / 60
WALL_SPACING = 46               # px between the bullets in a wall
WALL_MARK = 34                  # px: the warning marks on the edge


def bullet(x, y, angle, speed, width, kind, info, arena, damage=BULLET_DAMAGE, reach=BULLET_REACH):
    """One bullet flying from (x, y) at `angle` (radians); it lives just long enough to cross the arena.
    (10.11) Other fights (Milo) give it real `damage` and reach=None (the normal hitbox)."""
    a = math.cos(angle), math.sin(angle)
    crossing_ms = (arena[0] + arena[1]) / max(1e-6, speed) * FRAME_MS
    shot = projectile(x, y, x + a[0] * 1000, y + a[1] * 1000, speed, damage, "enemy", width,
                      crossing_ms, info, [kind])
    shot.fixed_reach = reach
    return shot


class Spinner:
    def __init__(self, start, end, spec, info, arena):
        self.end = end
        self.spec, self.info, self.arena = spec, info, arena
        self.next_shot = start
        self.start = start

    def angle_at(self, beat):
        s = self.spec
        return math.radians(s.get("start", 0) + s["turn"] * (beat - self.start))

    def update(self, beat, origin):
        out = []
        s = self.spec
        step = 1 / s["rate"]
        while self.next_shot <= min(beat, self.end):
            base = self.angle_at(self.next_shot)
            for arm in range(s["arms"]):
                a = base + arm * math.tau / s["arms"]
                out.append(bullet(*origin, a, s["speed"], s["width"], s["kind"], self.info, self.arena,
                                  s.get("damage", BULLET_DAMAGE), s.get("reach", BULLET_REACH)))
            self.next_shot += step
        return out

    def draw(self, layer, beat):
        pass

    def done(self, beat):
        return beat >= self.end


class Ring:
    def __init__(self, at, spec, info, arena):
        self.at, self.spec, self.info, self.arena = at, spec, info, arena
        self.fired = False

    def update(self, beat, origin):
        if self.fired or beat < self.at:
            return []
        self.fired = True
        s = self.spec
        start = math.radians(s.get("start", 0))
        return [bullet(*origin, start + i * math.tau / s["bullets"], s["speed"], s["width"], s["kind"],
                       self.info, self.arena, s.get("damage", BULLET_DAMAGE), s.get("reach", BULLET_REACH))
                for i in range(s["bullets"])]

    def draw(self, layer, beat):
        pass

    def done(self, beat):
        return self.fired


class Walls:
    """`side` = where it comes in from ("left", "right", "top", "bottom"); `gap_at` = px along the edge."""

    def __init__(self, at, side, gap_at, spec, info, arena):
        self.at, self.side, self.gap_at = at, side, gap_at
        self.spec, self.info, self.arena = spec, info, arena
        self.fired = False

    def spots(self):
        """(position along the edge, start point, flying angle) of every bullet in the row."""
        w, h = self.arena
        along = h if self.side in ("left", "right") else w
        out = []
        for i in range(int(along // WALL_SPACING) + 1):
            p = WALL_SPACING / 2 + i * WALL_SPACING
            if abs(p - self.gap_at) < self.spec["gap"] / 2:
                continue
            start, angle = {"left": ((0, p), 0.0), "right": ((w, p), math.pi),
                            "top": ((p, 0), math.pi / 2), "bottom": ((p, h), -math.pi / 2)}[self.side]
            out.append((p, start, angle))
        return out

    def update(self, beat, origin):
        if self.fired or beat < self.at:
            return []
        self.fired = True
        s = self.spec
        return [bullet(*start, angle, s["speed"], s["width"], s["kind"], self.info, self.arena)
                for _, start, angle in self.spots()]

    def draw(self, layer, beat):
        if self.fired:
            return
        alpha = 90 if int(beat * 4) % 2 else 200                 # blinks
        for _, (x, y), angle in self.spots():
            end = (x + math.cos(angle) * WALL_MARK, y + math.sin(angle) * WALL_MARK)
            pygame.draw.line(layer, PINK + (alpha,), (x, y), end, 5)

    def done(self, beat):
        return self.fired
