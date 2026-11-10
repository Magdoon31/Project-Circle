# HAZARDS: the shapes of a song fight that are not bullets - lasers across the whole arena and pulsing shapes.
# Each one is first a warning (a faint outline, getting stronger), then for a short while it hurts (solid),
# then it fades away (no longer hurts). All times are in beats (see clock.py).

import math

import pygame

PINK = (255, 46, 136)            # what hurts
WARN_ALPHA = (30, 110)           # the warning: from faint to clear
HIT_ALPHA = 235
FADE_BEATS = 0.35                # it fades away this long after it stops hurting
FLARE_BEATS = 0.15               # right when it starts hurting it is a bit bigger (a "pop" on the beat)
FLARE = 1.25


class Hazard:
    sound = ""                                      # its sound when it lands (on the beat)

    def __init__(self, warn_from, hit_at, hold):
        self.warn_from = warn_from
        self.hit_at = hit_at
        self.hit_end = hit_at + hold
        self.landed = False

    def lands_now(self, beat):
        """True once: on the first frame it hurts (for its sound)."""
        if self.landed or beat < self.hit_at:
            return False
        self.landed = True
        return True

    def hurts(self, beat):
        return self.hit_at <= beat < self.hit_end

    def gone(self, beat):
        return beat >= self.hit_end + FADE_BEATS

    def alpha(self, beat):
        if beat < self.hit_at:
            share = (beat - self.warn_from) / max(1e-6, self.hit_at - self.warn_from)
            return int(WARN_ALPHA[0] + (WARN_ALPHA[1] - WARN_ALPHA[0]) * min(1.0, max(0.0, share)))
        if beat < self.hit_end:
            return HIT_ALPHA
        return int(HIT_ALPHA * max(0.0, 1 - (beat - self.hit_end) / FADE_BEATS))

    def size_share(self, beat):
        """How much of its full size it shows now: thin while warning, a pop on the beat, then full."""
        if beat < self.hit_at:
            return 0.25
        if beat < self.hit_at + FLARE_BEATS:
            return FLARE
        return 1.0


class Laser(Hazard):
    """A straight beam right across the arena: through (x, y) at `angle` degrees (0 = across, 90 = down)."""
    sound = "laser"

    def __init__(self, x, y, angle, width, warn_from, hit_at, hold):
        super().__init__(warn_from, hit_at, hold)
        self.x, self.y, self.width = x, y, width
        a = math.radians(angle)
        self.dx, self.dy = math.cos(a), math.sin(a)

    def touches(self, px, py, radius, beat):
        if not self.hurts(beat):
            return False
        across = abs((px - self.x) * self.dy - (py - self.y) * self.dx)     # distance from the beam's middle line
        return across < self.width / 2 + radius

    def draw(self, layer, beat):
        reach = layer.get_width() + layer.get_height()
        half = self.width * self.size_share(beat) / 2
        nx, ny = -self.dy * half, self.dx * half
        ax, ay = self.x - self.dx * reach, self.y - self.dy * reach
        bx, by = self.x + self.dx * reach, self.y + self.dy * reach
        points = [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)]
        pygame.draw.polygon(layer, PINK + (self.alpha(beat),), points)
        if beat < self.hit_at:                              # the warning also shows how wide it will be
            full = [(ax - self.dy * self.width / 2, ay + self.dx * self.width / 2),
                    (bx - self.dy * self.width / 2, by + self.dx * self.width / 2),
                    (bx + self.dy * self.width / 2, by - self.dx * self.width / 2),
                    (ax + self.dy * self.width / 2, ay - self.dx * self.width / 2)]
            pygame.draw.polygon(layer, PINK + (self.alpha(beat) // 2,), full, 2)


class Shape(Hazard):
    """A circle or a square (`size` = radius / half the side) that pops on the beat."""

    def __init__(self, x, y, kind, size, warn_from, hit_at, hold):
        super().__init__(warn_from, hit_at, hold)
        self.x, self.y, self.kind, self.size = x, y, kind, size
        self.sound = kind                           # "circle" / "square"

    def touches(self, px, py, radius, beat):
        if not self.hurts(beat):
            return False
        if self.kind == "circle":
            return math.dist((px, py), (self.x, self.y)) < self.size + radius
        return abs(px - self.x) < self.size + radius and abs(py - self.y) < self.size + radius

    def draw(self, layer, beat):
        warning = beat < self.hit_at
        size = self.size if warning else self.size * self.size_share(beat)
        colour = PINK + (self.alpha(beat),)
        edge = 3 if warning else 0                         # the warning is just the outline
        if self.kind == "circle":
            pygame.draw.circle(layer, colour, (int(self.x), int(self.y)), int(size), edge)
        else:
            rect = pygame.Rect(0, 0, int(size * 2), int(size * 2))
            rect.center = (int(self.x), int(self.y))
            pygame.draw.rect(layer, colour, rect, edge)
        if warning:                                         # ... and a filling middle: how soon it hits
            share = (beat - self.warn_from) / max(1e-6, self.hit_at - self.warn_from)
            inner = int(self.size * min(1.0, max(0.0, share)))
            if inner > 0:
                if self.kind == "circle":
                    pygame.draw.circle(layer, PINK + (50,), (int(self.x), int(self.y)), inner)
                else:
                    rect = pygame.Rect(0, 0, inner * 2, inner * 2)
                    rect.center = (int(self.x), int(self.y))
                    pygame.draw.rect(layer, PINK + (50,), rect)
