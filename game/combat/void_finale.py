# THE VOID'S LAST MOMENTS (11.11): how the boss looks at the very end - void_fight.py says when.
#   Glitch     - the interlude, after its last word: it breaks up (blinks, jumps, wrong colours, ghosts beside it),
#                more and more, until the end starts - then it stands in its new form (bigger, dark, a bright edge).
#   Dying      - after your shot, to the music (final_scene, ms from its start): it shakes harder and harder and
#                swells on every beat; at the music's last peak it bursts and
#                shrinks to nothing as the music dies away, its pieces drifting off. Nothing is left.
#   FadeOut    - 2 s after the music: the screen goes black (or white, if you used the lore items).

import math
import random

import pygame

GLITCH_COLOURS = [(255, 60, 120), (80, 255, 230), (255, 255, 255), (20, 10, 30)]
FORM_COLOUR = (34, 18, 58)        # its new form ...
FORM_EDGE = (225, 190, 255)       # ... and its bright edge
FORM_SIZE = 1.35                  # x its usual size


def form_width(boss):
    return int(boss.base_width * FORM_SIZE)


def draw_form_edge(screen, boss, timer):
    """The new form's bright edge (Combat draws the dark body)."""
    if getattr(boss, "hidden", False) or boss.width < 2:
        return
    glow = 3 + int(2 * math.sin(timer * 0.2))
    pygame.draw.circle(screen, FORM_EDGE, (int(boss.x), int(boss.y)), boss.width + glow, 4)


# --- the interlude: it breaks up -----------------------------------------------------------------------------------
class Glitch:
    def __init__(self, spot, frames):
        self.spot = spot                          # where it stands (it jumps round this, never drifts away)
        self.frames = frames                      # until the end starts
        self.timer = 0
        self.ghosts = []                          # [(dx, dy, colour)] drawn beside it this frame

    @property
    def strength(self):
        return min(1.0, self.timer / max(1, self.frames))

    def update(self, boss):
        self.timer += 1
        k = self.strength
        broken = random.random() < 0.15 + 0.6 * k
        boss.hidden = broken and random.random() < 0.25 * k
        jump = 30 * k if broken else 0
        boss.x = self.spot[0] + random.uniform(-jump, jump)
        boss.y = self.spot[1] + random.uniform(-jump * 0.4, jump * 0.4)
        boss.color = random.choice(GLITCH_COLOURS) if broken else (FORM_COLOUR if random.random() < k else boss.color)
        grow = boss.base_width + (form_width(boss) - boss.base_width) * k
        boss.width = int(grow * (random.uniform(0.85, 1.2) if broken else 1))
        self.ghosts = [(random.uniform(-40, 40) * k, random.uniform(-8, 8), random.choice(GLITCH_COLOURS[:2]))
                       for _ in range(int(3 * k) if broken else 0)]

    def draw(self, screen, boss):
        for dx, dy, colour in self.ghosts:
            pygame.draw.circle(screen, colour, (int(boss.x + dx), int(boss.y + dy)), boss.width, 3)


def settle_in_form(boss, spot):
    """The end starts: the glitching stops, it stands in its new form."""
    boss.hidden = False
    boss.x, boss.y = spot
    boss.color = FORM_COLOUR
    boss.width = form_width(boss)


# --- after your shot: it dies to the music --------------------------------------------------------------------------
SHOT_MS = 28770                   # your shot hits (final_scene)
BURST_MS = 41800                  # the music's last peak: it bursts and starts to shrink ...
GONE_MS = 56500                   # ... and is gone as the music dies away
MUSIC_END_MS = 58500              # the music is silent from here
FIRST_BEAT_MS = 75
BEAT_MS = 60_000 / 138
SWELL = 0.14                      # it swells this much on a beat
PIECES = 28


class Dying:
    def __init__(self, boss, camera):
        self.boss, self.camera = boss, camera
        self.spot = (boss.x, boss.y)
        self.width = boss.width
        self.beat = -1
        self.swell = 0.0
        self.burst = False
        self.t = SHOT_MS

    def update(self, t):
        """t: ms into final_scene."""
        self.t = t
        self.on_beats(t)
        self.swell *= 0.85
        if t < BURST_MS:
            self.shake(t)
            self.boss.width = int(self.width * (1 + SWELL * self.swell))
            return
        if not self.burst:
            self.burst = True
            self.camera.kick(zoom=0.15, turn=3.0)
        self.shrink(t)

    def on_beats(self, t):
        beat = int((t - FIRST_BEAT_MS) // BEAT_MS)
        while self.beat < beat:
            self.beat += 1
            if t < BURST_MS:
                self.swell = 1.0
                if self.beat % 8 == 0:
                    self.camera.kick(zoom=0.06, turn=1.5 if (self.beat // 8) % 2 else -1.5)
                elif self.beat % 2 == 0:
                    self.camera.kick(zoom=0.025)

    def shake(self, t):
        k = (t - SHOT_MS) / (BURST_MS - SHOT_MS)
        force = 3 + 14 * k
        self.boss.x = self.spot[0] + random.uniform(-force, force)
        self.boss.y = self.spot[1] + random.uniform(-force, force)

    def shrink_share(self, t):
        return min(1.0, max(0.0, (t - BURST_MS) / (GONE_MS - BURST_MS)))

    def shrink(self, t):
        k = self.shrink_share(t)
        self.boss.x, self.boss.y = self.spot[0] + random.uniform(-3, 3) * (1 - k), self.spot[1]
        self.boss.width = int(self.width * (1 - k) ** 1.4)
        self.boss.hidden = self.boss.width < 2
        if k >= 0.7:
            self.camera.zoom_to(1.0)
        if self.boss.hidden:
            self.camera.look(None)

    def draw(self, screen):
        if self.t >= BURST_MS:
            self.draw_pieces(screen)

    def draw_pieces(self, screen):
        """Pieces drift away from where it was and get smaller until nothing is left."""
        k = self.shrink_share(self.t)
        size = int(12 * (1 - k))
        if size < 1:
            return
        for i in range(PIECES):
            a = i * math.tau / PIECES + k * 1.5
            r = 30 + k * 700 * (0.6 + 0.4 * ((i * 7) % 5) / 4)
            pygame.draw.circle(screen, FORM_EDGE, (int(self.spot[0] + math.cos(a) * r),
                                                   int(self.spot[1] + math.sin(a) * r)), size)

    @property
    def fade_starts_ms(self):
        return MUSIC_END_MS + 2000


# --- the screen goes black / white ---------------------------------------------------------------------------------
FADE_MS = 2500


class FadeOut:
    def __init__(self, light):
        self.colour = (255, 255, 255) if light else (0, 0, 0)
        self.share = 0.0

    def update(self, ms_since_start):
        self.share = max(0.0, min(1.0, ms_since_start / FADE_MS))

    @property
    def done(self):
        return self.share >= 1.0

    def draw(self, screen):
        if self.share <= 0:
            return
        veil = pygame.Surface(screen.get_size())
        veil.fill(self.colour)
        veil.set_alpha(int(255 * self.share))
        screen.blit(veil, (0, 0))
