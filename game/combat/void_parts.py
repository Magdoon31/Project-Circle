# THE VOID FIGHT'S PARTS (11.11): the boss's broken name, the shot that knocks your weapon away, the weapon lying
# somewhere, Milo's memory (helps a little, says nothing) and the boss's few words (broken letters that get clear).
# The order of the fight is void_fight.py.

import math
import random

import pygame

GLITCH = "#%&?!/\\|_=+*<>~^"


# --- the name over the bar --------------------------------------------------------------------------------------
class GlitchName:
    """Never the same twice: a few broken signs, changing every few frames."""

    def __init__(self, every=6):
        self.every = every
        self.text = ""

    def update(self, timer):
        if timer % self.every == 0 or not self.text:
            self.text = "".join(random.choice(GLITCH) for _ in range(random.randint(5, 8)))
        return self.text


def broken(text, share):
    """`text` with this share of its letters swapped for broken signs (spaces stay)."""
    return "".join(ch if ch == " " or random.random() >= share else random.choice(GLITCH) for ch in text)


# --- the weapon -------------------------------------------------------------------------------------------------
DISARM_SPEED = 6.5
DISARM_RADIUS = 20
DISARM_COLOUR = (190, 90, 255)
DISARM_TURN = math.radians(0.6)   # (11.11) it follows you, very slightly (radians per frame)
PICK_UP = 46                      # px: walking this close picks the weapon up


class DisarmShot:
    """A big, slow, glowing shot: if it hits you, your weapon flies away."""

    def __init__(self, start, target):
        self.x, self.y = start
        d = math.dist(start, target) or 1
        self.vx, self.vy = (target[0] - start[0]) / d * DISARM_SPEED, (target[1] - start[1]) / d * DISARM_SPEED
        self.life = 60 * 9

    def update(self, target):
        """Flies on, turning a little towards the target."""
        heading = math.atan2(self.vy, self.vx)
        wanted = math.atan2(target[1] - self.y, target[0] - self.x)
        turn = (wanted - heading + math.pi) % math.tau - math.pi
        heading += max(-DISARM_TURN, min(DISARM_TURN, turn))
        self.vx, self.vy = math.cos(heading) * DISARM_SPEED, math.sin(heading) * DISARM_SPEED
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def hits(self, player):
        return math.dist((self.x, self.y), (player.x, player.y)) < DISARM_RADIUS + player.width * 0.8

    def draw(self, screen, timer):
        glow = DISARM_RADIUS + 6 + 4 * math.sin(timer * 0.3)
        pygame.draw.circle(screen, DISARM_COLOUR, (int(self.x), int(self.y)), int(glow), 3)
        pygame.draw.circle(screen, (235, 210, 255), (int(self.x), int(self.y)), DISARM_RADIUS)


class LostWeapon:
    """Your weapon, lying on a far island; walk onto it to take it back."""

    def __init__(self, pos):
        self.pos = pos

    def picked_up(self, player):
        return math.dist(self.pos, (player.x, player.y)) < PICK_UP

    def draw(self, screen, timer):
        x, y = int(self.pos[0]), int(self.pos[1] - 6 * abs(math.sin(timer * 0.08)))
        pygame.draw.rect(screen, (40, 40, 48), (x - 22, y - 7, 44, 14), 0, 4)
        pygame.draw.rect(screen, (255, 230, 140), (x - 22, y - 7, 44, 14), 2, 4)


# --- Milo's memory ----------------------------------------------------------------------------------------------
MILO_GHOST = (170, 210, 255)
GUARD_EVERY = 7 * 60              # frames he needs to be ready again (a ring round him fills up meanwhile)
GUARD_TRIGGER = 80                # px: when ready, a bullet this close to you makes him catch ...
GUARD_RADIUS = 115                # ... every bullet this close to you
CATCH_FRAMES = 22                 # a caught bullet: a line from Milo to it and a spark, this long


class MiloMemory:
    """Floats near you; when your weapon is lost he goes to it. (11.11) When he is ready he glows; the moment a
    bullet comes close to you he catches it (and the ones round it) - a line from him to each and a spark - and then
    he needs a while again."""

    def __init__(self, pos):
        self.x, self.y = pos
        self.timer = 0
        self.charge = 0                           # frames since he last caught (ready at GUARD_EVERY)
        self.caught = []                          # [x, y, frames left] the sparks of the bullets he just caught

    @property
    def ready(self):
        return self.charge >= GUARD_EVERY

    def update(self, player, weapon_at, bullets):
        self.timer += 1
        goal = weapon_at if weapon_at else (player.x - 70, player.y - 60)
        k = 0.05 if weapon_at else 0.08
        self.x += (goal[0] - self.x) * k
        self.y += (goal[1] - self.y) * k
        self.charge = min(GUARD_EVERY, self.charge + 1)
        for spark in self.caught:
            spark[2] -= 1
        self.caught = [s for s in self.caught if s[2] > 0]
        if self.ready and any(self.near(b, player, GUARD_TRIGGER) for b in bullets):
            self.guard(player, bullets)

    @staticmethod
    def near(bullet, player, reach):
        return math.dist((bullet.x, bullet.y), (player.x, player.y)) < reach

    def guard(self, player, bullets):
        near = [b for b in bullets if self.near(b, player, GUARD_RADIUS)]
        bullets[:] = [b for b in bullets if b not in near]
        self.caught += [[b.x, b.y, CATCH_FRAMES] for b in near]
        self.charge = 0

    def draw(self, screen, player, weapon_at):
        ghost = pygame.Surface((100, 100), pygame.SRCALPHA)
        glow = 0.5 + 0.5 * math.sin(self.timer * 0.15) if self.ready else 0
        pygame.draw.circle(ghost, MILO_GHOST + (int(110 + 90 * glow),), (50, 50), 18)
        if self.ready:                                      # ready: he glows
            pygame.draw.circle(ghost, MILO_GHOST + (int(70 + 80 * glow),), (50, 50), 28 + int(4 * glow), 4)
        else:                                               # getting ready: a ring round him fills up
            share = self.charge / GUARD_EVERY
            pygame.draw.arc(ghost, MILO_GHOST + (90,), (22, 22, 56, 56), math.pi / 2, math.pi / 2 + math.tau * share, 3)
        screen.blit(ghost, (int(self.x) - 50, int(self.y) - 50))
        if weapon_at:                                       # a faint line from you to your weapon
            pygame.draw.line(screen, MILO_GHOST, (player.x, player.y), weapon_at, 2)
        for x, y, left in self.caught:                      # what he just caught
            k = left / CATCH_FRAMES
            if k > 0.5:
                pygame.draw.line(screen, MILO_GHOST, (self.x, self.y), (x, y), 2)
            r = int(4 + 10 * (1 - k))
            for i in range(4):
                a = i * math.pi / 2 + math.pi / 4
                pygame.draw.line(screen, MILO_GHOST, (x + math.cos(a) * r * 0.4, y + math.sin(a) * r * 0.4),
                                 (x + math.cos(a) * r, y + math.sin(a) * r), 2)


# --- the boss's few words ---------------------------------------------------------------------------------------
CLEAR_FRAMES = 90                 # the broken letters become the real ones over this long
LINE_FRAMES = 270


class BrokenWords:
    """One line at a time in the middle of the screen: broken signs at first, then clear, then it fades."""

    def __init__(self, font):
        self.font = font
        self.text, self.age = "", LINE_FRAMES

    def say(self, text):
        self.text, self.age = text, 0

    @property
    def done(self):
        """The last line has faded away."""
        return self.age >= LINE_FRAMES

    def draw(self, screen):
        if self.age >= LINE_FRAMES:
            return
        self.age += 1
        share = max(0.0, 1 - self.age / CLEAR_FRAMES)
        img = self.font.render(broken(self.text, share), True, (230, 220, 255))
        img.set_alpha(min(255, (LINE_FRAMES - self.age) * 6))
        w, h = screen.get_size()
        screen.blit(img, img.get_rect(center=(w // 2, int(h * 0.72))))
