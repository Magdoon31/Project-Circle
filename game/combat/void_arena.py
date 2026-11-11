# THE VOID'S ARENA (11.11, the last boss): islands over the abyss, joined by bridges - 2 x 2 screens, the camera
# follows you. A big island in the middle, 8 smaller ones round it. Between the phases some bridges crumble and
# others grow (LAYOUTS). F5 (11.11): a warning (everything but the middle blinks), then the outer islands and every
# bridge fall away (you too, if you stand there); the middle island grows and the outer ones come back closer - out
# of reach, only stands for the turrets (void_turrets.py). Off the islands and bridges = the abyss (VoidFight: you
# fall - a hit and back onto the nearest island).
# Only the shape lives here (where the ground is, drawing it); the fight is void_fight.py.

import math

import pygame

ROOM = (2, 2)                     # the arena in screens
CENTRE_R = 330                    # px: the middle island
OUTER = (1350, 780, 220)          # the 8 outer islands: how far across / down from the middle, their radius
BRIDGE_WIDTH = 120
DROP_WARN = 4 * 60                # F5: the outer islands blink this long before they fall ...
DROP_FALL = 60                    # ... then fall away (shrink to nothing) over this long
WARN_EDGE = (255, 90, 120)
BELT_SPEED = 2.2                  # (11.11) F3: px per frame a conveyor-belt bridge carries you
CHEVRON_EVERY = 70                # px between the arrows drawn on a belt
CHANGE_FRAMES = 90                # a bridge crumbles / grows this long (it blinks while crumbling - still there)
BELT_COLOUR, BELT_ARROW = (72, 72, 82), (130, 130, 145)
COLOURS = {"abyss": (14, 8, 24), "island": (58, 40, 88), "edge": (125, 95, 175), "bridge": (78, 58, 110),
           "pale_abyss": (226, 226, 232), "pale_island": (250, 250, 252), "pale_edge": (196, 196, 204),
           "pale_bridge": (240, 240, 244), "far_island": (40, 28, 62), "far_edge": (95, 70, 140),
           "pale_far_island": (236, 236, 240), "pale_far_edge": (200, 200, 208)}

# which bridges stand in each phase: "spokes" = from the middle to these outer islands (0 = right, then clockwise
# every 45 degrees), "ring" = between neighbouring outer islands (n joins n and n+1); "outer" = their size share
ALL = tuple(range(8))
LAYOUTS = [
    {"spokes": ALL, "ring": ALL, "outer": 1.0},                   # F1
    {"spokes": ALL, "ring": (0, 2, 4, 6), "outer": 1.0},          # F2
    {"spokes": ALL, "ring": (), "outer": 1.0, "belts": True, "width": 190},   # F3: the bridges are wide belts
    {"spokes": (1, 3, 5, 7), "ring": ALL, "outer": 1.0},          # F4
    {"spokes": (), "ring": (), "outer": 0.75, "centre": 420, "near": (920, 700), "drop": True},   # F5, the interlude
]                                                                 # and the end: no bridges, the outer ones out of reach


class VoidArena:
    def __init__(self, screen_size):
        sw, sh = screen_size
        self.size = (sw * ROOM[0], sh * ROOM[1])
        self.centre = (self.size[0] / 2, self.size[1] / 2)
        self.outer_share = 1.0
        self.centre_r = self.centre_goal = CENTRE_R
        self.outer_solid = True           # F5: the outer islands are only stands (you can't be on them)
        self.drop = None                  # F5's fall: [stage ("warn" / "fall"), frames left]
        self.drop_layout = None
        self.bridges = {}                 # key -> frames left of a change (0 = steady); key: ("spoke", n) / ("ring", n)
        self.leaving = {}                 # bridges crumbling away: key -> frames left
        self.place_outer(OUTER[:2])
        self.set_layout(0, instant=True)

    def place_outer(self, reach):
        self.outer = [(self.centre[0] + math.cos(math.radians(45 * k)) * reach[0],
                       self.centre[1] + math.sin(math.radians(45 * k)) * reach[1]) for k in range(8)]

    # --- the shape ----------------------------------------------------------------------------------------------
    def islands(self):
        """(x, y, radius) of every island you can stand on."""
        solid = self.outer_solid and not self.collapsing          # (a falling island takes you down at once)
        return [(*self.centre, self.centre_r)] + (self.outer_islands() if solid else [])

    def outer_islands(self):
        r = OUTER[2] * self.outer_share
        return [(x, y, r) for x, y in self.outer]

    @property
    def warning(self):
        """F5: the outer islands are about to fall (they blink; VoidFight says so)."""
        return bool(self.drop) and self.drop[0] == "warn"

    @property
    def collapsing(self):
        """F5: the outer islands are falling right now (you fall with them, even when you can't be hurt)."""
        return bool(self.drop) and self.drop[0] == "fall"

    def ends(self, key):
        kind, n = key
        if kind == "spoke":
            return self.centre, self.outer[n]
        return self.outer[n], self.outer[(n + 1) % 8]

    def set_layout(self, phase, instant=False):
        layout = LAYOUTS[min(phase, len(LAYOUTS) - 1)]
        if layout.get("drop") and not instant:
            if self.drop is None and self.outer_solid:
                self.drop, self.drop_layout = ["warn", DROP_WARN], layout       # the bridges go when the islands do
            return
        self.drop = None
        self.apply_layout(layout, instant)
        if instant:
            self.outer_share = self.outer_goal
            self.centre_r = self.centre_goal
            self.outer_solid = not layout.get("drop")
            self.place_outer(layout.get("near", OUTER[:2]))

    def apply_layout(self, layout, instant):
        wanted = {("spoke", n) for n in layout["spokes"]} | {("ring", n) for n in layout["ring"]}
        for key in list(self.bridges):
            if key not in wanted:
                del self.bridges[key]
                if not instant:
                    self.leaving[key] = CHANGE_FRAMES
        for key in wanted:
            if key not in self.bridges:
                self.bridges[key] = 0 if instant else CHANGE_FRAMES
                self.leaving.pop(key, None)
        self.outer_goal = layout["outer"]
        self.centre_goal = layout.get("centre", CENTRE_R)
        self.belts = layout.get("belts", False)
        self.bridge_width = layout.get("width", BRIDGE_WIDTH)

    def update_drop(self):
        """F5: blink (warn) -> fall away (shrink, the bridges with them) -> back closer, out of reach."""
        stage, left = self.drop
        self.drop[1] -= 1
        if stage == "fall":
            self.outer_share = self.fall_from * (left - 1) / DROP_FALL
        if left > 1:
            return
        if stage == "warn":
            self.bridges, self.leaving = {}, {}
            self.drop, self.fall_from = ["fall", DROP_FALL], self.outer_share
            self.centre_goal = self.drop_layout.get("centre", CENTRE_R)          # the middle grows meanwhile
            return
        self.drop = None
        self.outer_solid = False
        self.place_outer(self.drop_layout["near"])
        self.outer_share = 0.0
        self.apply_layout(self.drop_layout, instant=True)

    def update(self):
        if self.drop:
            self.update_drop()
        else:
            self.outer_share += (self.outer_goal - self.outer_share) * 0.02
        self.centre_r += (self.centre_goal - self.centre_r) * 0.03
        for key in list(self.bridges):
            self.bridges[key] = max(0, self.bridges[key] - 1)
        for key in list(self.leaving):
            self.leaving[key] -= 1
            if self.leaving[key] <= 0:
                del self.leaving[key]
        self.belt_offset = (getattr(self, "belt_offset", 0) + BELT_SPEED) % CHEVRON_EVERY

    # --- the ground ---------------------------------------------------------------------------------------------
    def on_ground(self, x, y, margin=0):
        """Is (x, y) on an island or a bridge? margin = (11.11) a body this big still touching the ground counts."""
        if self.on_island(x, y, margin):
            return True
        standing = [k for k, grow in self.bridges.items() if grow < CHANGE_FRAMES // 2] + list(self.leaving)
        return any(self.near_segment((x, y), *self.ends(k)) <= self.bridge_width / 2 + margin for k in standing)

    def on_island(self, x, y, margin=0):
        return any(math.dist((x, y), (ix, iy)) <= r + margin for ix, iy, r in self.islands())

    # --- F3: the belts ------------------------------------------------------------------------------------------
    @staticmethod
    def belt_way(key):
        """Which way a belt runs: out from the middle on even spokes, in on odd ones."""
        return 1 if key[1] % 2 == 0 else -1

    def belt_push(self, x, y):
        """(dx, dy) a belt moves you this frame (nothing on the islands or with no belts)."""
        if not self.belts or self.on_island(x, y):
            return 0.0, 0.0
        for key in self.bridges:
            a, b = self.ends(key)
            if self.near_segment((x, y), a, b) <= self.bridge_width / 2:
                d = math.dist(a, b) or 1
                k = self.belt_way(key) * BELT_SPEED
                return (b[0] - a[0]) / d * k, (b[1] - a[1]) / d * k
        return 0.0, 0.0

    def push_bullets(self, bullets):
        """(11.11) F3: the belts carry the bullets on them too."""
        if not self.belts:
            return
        for b in bullets:
            dx, dy = self.belt_push(b.x, b.y)
            b.x, b.y = b.x + dx, b.y + dy

    def keep_inside_ring(self, body):
        """(11.11) The boss never goes out past the ring of the outer islands (an ellipse through their middles)."""
        dx, dy = body.x - self.centre[0], body.y - self.centre[1]
        k = math.hypot(dx / OUTER[0], dy / OUTER[1])
        if k > 1:
            body.x, body.y = self.centre[0] + dx / k, self.centre[1] + dy / k

    @staticmethod
    def near_segment(p, a, b):
        ax, ay = a
        dx, dy = b[0] - ax, b[1] - ay
        t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy or 1)))
        return math.dist(p, (ax + dx * t, ay + dy * t))

    def nearest_island(self, x, y):
        """The middle of the nearest island (where you come back after falling)."""
        ix, iy, _ = min(self.islands(), key=lambda i: math.dist((x, y), i[:2]) - i[2])
        return ix, iy

    def far_island(self, x, y, at_least):
        """An outer island at least this far away (where a lost weapon lands)."""
        far = [p for p in self.outer if math.dist(p, (x, y)) >= at_least]
        return max(far or self.outer, key=lambda p: math.dist(p, (x, y)))

    # --- drawing ------------------------------------------------------------------------------------------------
    def draw(self, screen, pale, timer):
        c = (lambda name: COLOURS["pale_" + name]) if pale else (lambda name: COLOURS[name])
        screen.fill(c("abyss"))
        blink = self.warning and (timer // 8) % 2 == 0          # F5: about to fall
        for key, grow in self.bridges.items():
            self.draw_bridge(screen, key, 1 - grow / CHANGE_FRAMES,
                             WARN_EDGE if blink else BELT_COLOUR if self.belts else c("bridge"))
            if self.belts and not grow:
                self.draw_chevrons(screen, key)
        for key, left in self.leaving.items():
            if (timer // 6) % 2 == 0:                          # crumbling: it blinks
                self.draw_bridge(screen, key, 1.0, c("edge"))
        far = not self.outer_solid
        for x, y, r in self.outer_islands():
            if r >= 1:
                self.draw_island(screen, (x, y, r), c("far_island" if far else "island"),
                                 WARN_EDGE if blink else c("far_edge" if far else "edge"))
        self.draw_island(screen, (*self.centre, self.centre_r), c("island"), c("edge"))

    @staticmethod
    def draw_island(screen, island, colour, edge):
        x, y, r = island
        pygame.draw.circle(screen, colour, (int(x), int(y)), int(r))
        pygame.draw.circle(screen, edge, (int(x), int(y)), int(r), 6)

    def draw_bridge(self, screen, key, share, colour):
        (ax, ay), (bx, by) = self.ends(key)
        bx, by = ax + (bx - ax) * share, ay + (by - ay) * share       # growing out from its first end
        d = math.hypot(bx - ax, by - ay) or 1
        nx, ny = -(by - ay) / d * self.bridge_width / 2, (bx - ax) / d * self.bridge_width / 2
        pygame.draw.polygon(screen, colour, [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)])

    def draw_chevrons(self, screen, key):
        """Arrows moving along a belt (which way it carries you)."""
        (ax, ay), (bx, by) = self.ends(key)
        d = math.hypot(bx - ax, by - ay) or 1
        ux, uy = (bx - ax) / d, (by - ay) / d
        way = self.belt_way(key)
        half = self.bridge_width * 0.3
        t = self.belt_offset if way > 0 else CHEVRON_EVERY - self.belt_offset
        while t < d:
            cx, cy = ax + ux * t, ay + uy * t
            tip = (cx + ux * 14 * way, cy + uy * 14 * way)
            back = (cx - ux * 14 * way, cy - uy * 14 * way)
            pygame.draw.lines(screen, BELT_ARROW, False, [(back[0] - uy * half, back[1] + ux * half), tip,
                                                          (back[0] + uy * half, back[1] - ux * half)], 5)
            t += CHEVRON_EVERY
