# THE VOID'S COPIES (11.11, F4 in the Pale World - like the Brain of Cthulhu in Terraria): the boss and 3 copies
# stand in a rhombus round you, all as far from you; the rhombus follows you and turns. Now and then they all fade
# away and come back somewhere else round you (in new places). Only the real one casts a shadow. Every one of them
# shoots at you, but the shots are about as many as before - only from different places. Only the real one can be
# hit (and only while it is there): the copies are pictures, your bullets fly through them.
# Here: where they are, how they fade, who shoots and the drawing (all 4 - Combat doesn't draw the boss in F4);
# void_fight.py moves the real boss and says when it can be hit.

import math
import random

import pygame

from game.combat.song.emitters import bullet

BODIES = 4                        # the real one + 3 copies
REACH = 520                       # px from you
REACH_BREATH = 60                 # ... going in and out by this much
FOLLOW = 0.05                     # how quickly the rhombus's middle follows you (share per frame)
GLIDE = 0.06                      # how quickly a body goes to its place (share per frame)
TURN = math.radians(0.25)         # the rhombus turns this much a frame
STAY = 5 * 60                     # frames they stay before they fade away ...
FADE = 36                         # ... fade out / in this long (in between: new places)
EDGE = 100                        # px: they stay this far inside the arena (your bullets must reach them)
SOLID = 0.6                       # the real one can be hit when it's at least this much there
SHADOW = (150, 150, 162)          # the real one's shadow (the Pale World is white)

# the shots (F4's own attacks were these - spiral, a burst of 3, a sprinkler - now each from a random body; about
# as many bullets as the boss alone shot, since it used one attack at a time)
SPIRAL = {"every": 200, "bullets": 16, "speed": 5, "damage": 5500, "width": 13, "kind": "spore"}
BURST = {"every": 150, "shots": 3, "gap": 12, "speed": 9, "damage": 6000, "width": 14, "kind": "flower_white"}
SPRINKLER = {"every": 600, "streams": 4, "frames": 120, "step": 6, "turn": 8, "speed": 6, "damage": 5000,
             "width": 12, "kind": "flower_pink"}


class VoidCopies:
    def __init__(self, boss_pos, player_pos, bullet_info, arena_size):
        self.info, self.arena_size = bullet_info, arena_size
        self.middle = list(player_pos)
        self.turn = math.atan2(boss_pos[1] - player_pos[1], boss_pos[0] - player_pos[0])
        self.bodies = [list(boss_pos) for _ in range(BODIES)]      # [0] is the real one
        self.places = list(range(BODIES))                          # body -> its corner of the rhombus
        self.timer = 0
        self.stage, self.left = "out", FADE                        # at first: it fades from where it stood
        self.shooting = []                                         # [(body, pattern, frames left, its own state)]

    # --- moving and fading ----------------------------------------------------------------------------------
    def update(self, player_pos):
        """One frame on: the rhombus follows you and turns; the bodies glide to their corners or fade.
        -> new bullets"""
        self.timer += 1
        self.middle[0] += (player_pos[0] - self.middle[0]) * FOLLOW
        self.middle[1] += (player_pos[1] - self.middle[1]) * FOLLOW
        self.turn += TURN
        self.update_stage()
        if self.stage != "out":
            for body, place in zip(self.bodies, self.places):
                gx, gy = self.corner(place)
                body[0] += (gx - body[0]) * GLIDE
                body[1] += (gy - body[1]) * GLIDE
        return self.shoot(player_pos) if self.stage == "stay" else []

    def update_stage(self):
        self.left -= 1
        if self.left > 0:
            return
        if self.stage == "stay":
            self.stage, self.left = "out", FADE
            self.shooting = []
        elif self.stage == "out":
            self.come_back_elsewhere()
            self.stage, self.left = "in", FADE
        else:
            self.stage, self.left = "stay", STAY

    def come_back_elsewhere(self):
        """New places: the rhombus turned somewhere else, and who stands where - mixed up."""
        self.turn += random.uniform(0.6, math.tau - 0.6)
        random.shuffle(self.places)
        for body, place in zip(self.bodies, self.places):
            body[0], body[1] = self.corner(place)

    def corner(self, place):
        reach = REACH + REACH_BREATH * math.sin(self.timer * 0.02)
        a = self.turn + place * math.tau / BODIES
        x, y = self.middle[0] + math.cos(a) * reach, self.middle[1] + math.sin(a) * reach
        w, h = self.arena_size
        return min(max(EDGE, x), w - EDGE), min(max(EDGE, y), h - EDGE)

    @property
    def shown(self):
        """How much they are there (0 = gone, 1 = all there)."""
        if self.stage == "stay":
            return 1.0
        k = self.left / FADE
        return k if self.stage == "out" else 1 - k

    @property
    def solid(self):
        """The real one can be hit now."""
        return self.shown >= SOLID

    @property
    def real(self):
        return tuple(self.bodies[0])

    # --- shooting -------------------------------------------------------------------------------------------
    def shoot(self, target):
        for pattern in (SPIRAL, BURST, SPRINKLER):
            if self.timer % pattern["every"] == 0:
                frames = pattern.get("frames", pattern.get("shots", 1) * pattern.get("gap", 1))
                self.shooting.append([random.randrange(BODIES), pattern, frames, random.uniform(0, math.tau)])
        out = []
        for shot in self.shooting:
            out += self.fire(shot, target)
            shot[2] -= 1
        self.shooting = [s for s in self.shooting if s[2] > 0]
        return out

    def fire(self, shot, target):
        body, pattern, left, angle = shot
        x, y = self.bodies[body]
        aim = math.atan2(target[1] - y, target[0] - x)
        if pattern is SPIRAL:
            if left != 1:
                return []
            n = pattern["bullets"]
            return [self.bullet(x, y, angle + i * math.tau / n, pattern) for i in range(n)]
        if pattern is BURST:
            return [self.bullet(x, y, aim, pattern)] if left % pattern["gap"] == 0 else []
        if left % pattern["step"]:                                   # the sprinkler
            return []
        turn = math.radians(pattern["turn"]) * (pattern["frames"] - left) / pattern["step"]
        n = pattern["streams"]
        return [self.bullet(x, y, angle + turn + i * math.tau / n, pattern) for i in range(n)]

    def bullet(self, x, y, angle, pattern):
        return bullet(x, y, angle, pattern["speed"], pattern["width"], pattern["kind"], self.info, self.arena_size,
                      pattern["damage"], None)

    # --- drawing --------------------------------------------------------------------------------------------
    def draw(self, screen, boss):
        """All 4 look just like the boss, fading together; only the real one has a shadow."""
        alpha = int(255 * self.shown)
        if alpha <= 0:
            return
        r = boss.width
        picture = pygame.Surface((r * 2 + 4, int(r * 2.6)), pygame.SRCALPHA)
        shadow = pygame.Rect(0, 0, int(r * 1.8), int(r * 0.6))
        shadow.center = (r + 2, int(r * 1.95))
        for i, (x, y) in enumerate(self.bodies):
            picture.fill((0, 0, 0, 0))
            if i == 0:
                pygame.draw.ellipse(picture, SHADOW + (alpha,), shadow)
            pygame.draw.circle(picture, tuple(boss.color[:3]) + (alpha,), (r + 2, r + 2), r)
            screen.blit(picture, (int(x) - r - 2, int(y) - r - 2))
