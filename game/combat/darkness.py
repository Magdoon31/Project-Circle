# DARKNESS (8.11, Night Bloom's arena): the fight is dark - you only see a small circle round yourself.
#
#   arena "darkness": {"light": px round you,
#                      "fog": share (optional, 1 = fully dark; less = you can still make things out a little),
#                      "seed": {"every": frames, "life": frames, "time": frames, "player": px, "boss": px,
#                               "spots": n, "spot_r": px},
#                      "storm": {"every": frames, "flicker": [lit, dark, lit, ...] frames, "fade": frames}}
#   ("seed" and "storm" are both optional)
#   - a light seed comes up every `every` frames at a random spot (it glows, you can always see it) and goes after
#     `life` frames; walk over it -> for `time` frames a big circle round you, round the boss and `spots` random
#     spots light up.
#   - things that give light by themselves: thrown lanterns (bullets with .light).
#   - storm: every `every` frames lightning flickers (lit / dark / lit ...), then the dark fades back in over `fade`
#     frames (no damage; Combat plays a thunder sound when it strikes).
#
# Combat owns one Darkness; it calls update() every frame and draw() after the world, before the HUD.

import math
import random

import pygame

FOG = (6, 8, 14)              # the colour of the dark
FOG_ALPHA = 252               # how dark (255 = nothing at all)
CLEAR_CORE = 0.45             # (8.11) the inner share of a light's radius is fully clear; out from there the dark
                              # comes back in a smooth gradient to the edge
SEED_PICK = 46                # px: walking this close picks a seed up
SEED_RADIUS = 14
SEED_GLOW = (255, 236, 150)
JAR_LIGHT = 60                 # px more light round you with the Firefly Jar


class Darkness:
    def __init__(self):
        self.spec = None
        self.seed = None          # (x, y, frames left) - one seed at a time
        self.next_seed = 0
        self.lit = 0              # frames the seed's light still lasts
        self.spots = []           # (x, y) lit by the seed
        self.storm_t = None       # frames since the last lightning (None = no storm)

    @property
    def active(self):
        return self.spec is not None

    # --- update ----------------------------------------------------------------------------------------------
    def update(self, spec, player, size, timer):
        """Returns True on the frame lightning strikes (for the thunder sound)."""
        self.spec = spec
        if not spec:
            return False
        if spec.get("seed"):
            self.update_seed(spec["seed"], player, size, timer)
        else:
            self.seed, self.lit = None, 0
        return self.update_storm(spec.get("storm"), timer)

    def update_seed(self, seed, player, size, timer):
        if self.lit > 0:
            self.lit -= 1
        if self.seed is None and timer >= self.next_seed:
            self.seed = (*self.random_spot(size, away_from=(player.x, player.y)), seed["life"])
        if self.seed is None:
            return
        x, y, left = self.seed
        if math.dist((x, y), (player.x, player.y)) < SEED_PICK:
            self.light_up(seed, size)
            self.seed, self.next_seed = None, timer + seed["every"]
        elif left <= 1:
            self.seed, self.next_seed = None, timer + seed["every"] // 2
        else:
            self.seed = (x, y, left - 1)

    def light_up(self, seed, size):
        self.lit = seed["time"]
        self.spots = [self.random_spot(size) for _ in range(seed["spots"])]

    def update_storm(self, storm, timer):
        if not storm:
            self.storm_t = None
            return False
        self.storm_t = timer % storm["every"]
        return self.storm_t == 0

    @staticmethod
    def random_spot(size, away_from=None):
        w, h = size
        for _ in range(50):
            p = (random.uniform(120, w - 120), random.uniform(160, h - 100))
            if away_from is None or math.dist(p, away_from) > 300:
                return p
        return (w / 2, h / 2)

    # --- draw ------------------------------------------------------------------------------------------------
    def draw(self, screen, player, boss, projectiles):
        if not self.active:
            return
        fog = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        dark = int(FOG_ALPHA * self.spec.get("fog", 1.0) * self.darkness_share())
        fog.fill(FOG + (dark,))
        if dark > 0:                                        # (in a lightning flash there is nothing to cut)
            self.cut_lights(fog, self.lights(player, boss, projectiles), dark)
        screen.blit(fog, (0, 0))
        self.draw_seed(screen)

    def darkness_share(self):
        """1 = fully dark, 0 = lit by lightning: it flickers, then the dark fades back in."""
        storm = self.spec.get("storm") if self.spec else None
        if storm is None or self.storm_t is None:
            return 1.0
        t = self.storm_t
        for i, frames in enumerate(storm["flicker"]):
            if t < frames:
                return 0.0 if i % 2 == 0 else 1.0
            t -= frames
        return min(1.0, t / max(1, storm["fade"]))

    def lights(self, player, boss, projectiles):
        spec = self.spec
        seed = spec.get("seed") or {}
        own = (seed["player"] if self.lit else spec["light"]) + (JAR_LIGHT if "light" in player.trinket_effect else 0)
        out = [((player.x, player.y), own)]
        if self.lit:
            if boss is not None:
                out.append(((boss.x, boss.y), seed["boss"]))
            out += [(spot, seed["spot_r"]) for spot in self.spots]
        out += [((p.x, p.y), p.light) for p in projectiles if getattr(p, "light", 0)]
        return out

    def cut_lights(self, fog, lights, dark):
        """Soft holes in the fog. Each light is a picture with a radial gradient of darkness (clear in the middle,
        `dark` at the edge), put on with 'keep the smaller alpha' - so lights add up nicely and a light is never
        darker than the fog round it (e.g. when lightning has almost cleared the dark)."""
        for (x, y), r in lights:
            glow = self.light_picture(int(r), dark)
            fog.blit(glow, (int(x) - glow.get_width() // 2, int(y) - glow.get_height() // 2),
                     special_flags=pygame.BLEND_RGBA_MIN)

    _pictures = {}

    @classmethod
    def light_picture(cls, r, dark):
        """A (2r x 2r) picture: alpha 0 inside CLEAR_CORE x r, then smoothly up to `dark` at r (and outside)."""
        key = (r, dark // 8)                                # a few shades of dark are enough (cache stays small)
        if key not in cls._pictures:
            pic = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
            pic.fill(FOG + (dark,))
            steps = 24
            for i in range(steps):                          # outside in: each ring a bit clearer
                k = 1 - i / steps                           # 1 .. ~0 of the gradient's width
                radius = r * (CLEAR_CORE + (1 - CLEAR_CORE) * k)
                share = k * k * (3 - 2 * k)                 # smoothstep: soft at both ends
                pygame.draw.circle(pic, FOG + (int(dark * share),), (r, r), int(radius))
            pygame.draw.circle(pic, FOG + (0,), (r, r), int(r * CLEAR_CORE))
            cls._pictures[key] = pic
        return cls._pictures[key]

    def draw_seed(self, screen):
        if self.seed is None:
            return
        x, y, left = self.seed
        pulse = 1 + 0.2 * math.sin(left * 0.15)
        pygame.draw.circle(screen, (255, 210, 90), (int(x), int(y)), int(SEED_RADIUS * 2.2 * pulse), 2)
        pygame.draw.circle(screen, SEED_GLOW, (int(x), int(y)), SEED_RADIUS)
