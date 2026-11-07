# WHEEL OF FORTUNE (Lucky, in the lunapark). You pay the stake (in the dialogue: 10 / 50 / 100$), Space spins.
# The wheel slows down and stops on a field: x0, x0.5, x1, x2, x3 or the JACKPOT x6.
# On average a bit less comes back than you paid (~90%) - the house always wins, a little.
# Sometimes it "almost" stops on the jackpot and creeps one field further (Lucky's favourite moment).
# No countdown, the lunapark music keeps playing. The gold that comes back is in .reward (Game pays it out).
# (7.11) Until you have the Haggler sigil one x0 field is a "?" - it pays nothing, but gives the sigil (.won_sigil).

import math, random
import pygame
from game.minigames.base import Minigame

# the fields around the wheel, in order (20 fields -> expected return 18/20 = 0.9 of the stake)
FIELDS = [0, 2, 0, 0.5, 1, 0, 0.5, 0, 3, 0, 1, 0.5, 0, 2, 0, 0.5, 1, 0, 6, 0]
SIGIL_FIELD = 9                # this x0 field is the "?" while the sigil isn't yours yet
COLORS = {"?": (150, 90, 230), 0: (90, 80, 100), 0.5: (120, 170, 230), 1: (240, 240, 240), 2: (120, 220, 130), 3: (250, 200, 70), 6: (240, 90, 160)}
SPIN_FRAMES = (150, 220)       # how long it spins
NEAR_MISS = 0.35               # chance that a losing spin crawls past the jackpot at the end


class Wheel(Minigame):
    title = "Lucky's Wheel"
    use_countdown = False
    keep_music = True

    def __init__(self, screen, background, stake=10, volume=1.0, sigil=None):
        super().__init__(screen, background, volume)
        self.fields = list(FIELDS)
        self.sigil = sigil
        self.won_sigil = None
        if sigil:
            self.fields[SIGIL_FIELD] = "?"
        self.stake = stake
        self.angle = random.uniform(0, 360)       # where the wheel stands (degrees, field 0 at the top)
        self.spinning = False
        self.result_field = None
        self.reward = 0
        self.tick = 0

    def field_at(self, angle):
        return int(((-angle) % 360) / (360 / len(self.fields)))       # the field under the pointer at the top

    def on_events(self, events):
        if self.spinning or self.result_field is not None:
            return
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.spin()

    def spin(self):
        self.spinning = True
        f = self.fields
        self.target = random.randrange(len(f))
        jackpot = f.index(6)
        if f[self.target] == 0 and random.random() < NEAR_MISS and f[(jackpot + 1) % len(f)] == 0:
            self.target = (jackpot + 1) % len(f)                       # "so close!" - one field after the jackpot
        size = 360 / len(f)
        stop = -(self.target * size + random.uniform(0.2, 0.8) * size)     # angle that puts the target under the pointer
        turns = random.randint(4, 6) * 360
        self.start_angle = self.angle
        self.total = (stop - self.angle) % 360 + turns
        self.frames = random.randint(*SPIN_FRAMES)
        self.t = 0
        self.play("flip")

    def on_update(self):
        if not self.spinning:
            return
        self.t += 1
        p = min(1.0, self.t / self.frames)
        eased = 1 - (1 - p) ** 3                                  # fast at first, slowly to a stop
        before = self.field_at(self.angle)
        self.angle = self.start_angle + self.total * eased
        if self.field_at(self.angle) != before:
            self.tick += 1
            if self.tick % 2 == 0:
                self.play("write")                               # click-click-click
        if p >= 1.0:
            self.spinning = False
            self.result_field = self.field_at(self.angle)
            mult = self.fields[self.result_field]
            if mult == "?":                                       # the sigil field: no gold, the sigil
                self.won_sigil = self.sigil
                self.end(True, "jackpot")
                return
            self.reward = int(round(self.stake * mult))
            self.end(mult >= 1, "jackpot" if mult == 6 else None)

    def win_text(self):
        if self.result_field is None:
            return "You win!"
        mult = self.fields[self.result_field]
        if mult == "?":
            return "? - something for you!"
        return f"JACKPOT! +{self.reward}$" if mult == 6 else f"x{mult:g}  +{self.reward}$"

    def lose_text(self):
        if self.result_field is None:
            return "Nothing!"
        mult = self.fields[self.result_field]
        return "Nothing!" if mult == 0 else f"x0.5  +{self.reward}$"

    def on_draw(self):
        sw, sh = self.screen.get_size()
        self.draw_header(f"Stake: {self.stake}$" + ("" if self.spinning or self.result_field is not None else "   -   Space: spin!"))
        cx, cy = sw // 2, int(sh * 0.56)
        r = int(min(sw, sh) * 0.33)
        size = 360 / len(self.fields)
        for i, mult in enumerate(self.fields):
            a0 = math.radians(-90 + self.angle + i * size)
            a1 = math.radians(-90 + self.angle + (i + 1) * size)
            pts = [(cx, cy)] + [(cx + r * math.cos(a0 + (a1 - a0) * k / 6), cy + r * math.sin(a0 + (a1 - a0) * k / 6)) for k in range(7)]
            pygame.draw.polygon(self.screen, COLORS[mult], pts)
            pygame.draw.polygon(self.screen, (30, 25, 35), pts, 3)
            mid = (a0 + a1) / 2
            label = "?" if mult == "?" else "x6!" if mult == 6 else ("x0" if mult == 0 else f"x{mult:g}")   # x6 = jackpot
            img = self.font_small.render(label, True, (20, 20, 25) if mult and mult != "?" else (230, 230, 240))
            img = pygame.transform.rotate(img, -math.degrees(mid) - 90)
            pos = (cx + r * 0.72 * math.cos(mid), cy + r * 0.72 * math.sin(mid))
            self.screen.blit(img, img.get_rect(center=pos))
        pygame.draw.circle(self.screen, (30, 25, 35), (cx, cy), r, 8)
        pygame.draw.circle(self.screen, (250, 210, 80), (cx, cy), r // 9)
        pygame.draw.circle(self.screen, (30, 25, 35), (cx, cy), r // 9, 4)
        # the pointer at the top
        tip = (cx, cy - r + 18)
        pygame.draw.polygon(self.screen, (240, 70, 70), [tip, (cx - 22, cy - r - 30), (cx + 22, cy - r - 30)])
        pygame.draw.polygon(self.screen, (30, 25, 35), [tip, (cx - 22, cy - r - 30), (cx + 22, cy - r - 30)], 4)
