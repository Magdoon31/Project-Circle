# DECOY - the Mascot Plush (trinket effect "decoy": [seconds]).
# At the start of every fight the plush drops onto the battlefield, a bit away from the player.
# While it is alive ALL enemies go for it: they walk to it and aim their shots at it (combat.py target()).
# It only has a little HP: the AVERAGE damage per second of the enemies in this fight x seconds (3).
# When its HP runs out it is gone for the rest of the fight. It can't be healed or moved.

import math, random
import pygame

MIN_HP = 20                 # even against very weak enemies it takes a few hits
CONTACT_PER_SECOND = 2      # how often contact damage is counted in the estimate (a touch every ~0.5 s)
SPIRAL_HITS = 3             # of a ring of bullets only a few reach one target
HIT_FLASH = 8
IMM_FRAMES = 15             # after a hit the plush can't be hurt for this long (blinks, like the player)
SPRITE_SCALE = 1.3           # the sprite is a bit bigger than the hit circle (ears, legs)


def attack_dps(enemy):
    """A rough damage-per-second of one enemy aimed at one target (bullets + touching)."""
    dps = 0.0
    for name, info in enemy.attacks.items():
        if "death" in name or "damage" not in info or not info.get("cooldown"):
            continue
        stop = info.get("stop_move") or (0, 0)
        cycle = info["cooldown"] + (stop[0] + stop[1]) / 60
        if name in ("spiral", "pulse"):
            hits = min(SPIRAL_HITS, info.get("bullets", 1))
        elif name == "sprinkler":
            hits = SPIRAL_HITS
            cycle += info.get("duration", 0)
        elif name in ("line", "wave"):
            hits = info.get("bullets", 1)
        elif name == "wall":
            hits = 1
        elif name == "shotgun":
            hits = info.get("bullets", 1)
        elif name == "minigun":
            hits = info.get("burst_max", 1)
            cycle += info.get("burst_delay", 0) * hits
        else:
            hits = 1
        times = info.get("repeat", [1])[0]                  # a series
        dps += info["damage"] * enemy.damage * hits * times / cycle
    return dps + enemy.contact_dmg * CONTACT_PER_SECOND


class Decoy:
    type = "player"            # enemy bullets hit it (they skip their own type)

    def __init__(self, x, y, width, hp, image=None):
        self.x, self.y, self.width = x, y, width
        self.hp = self.max_hp = hp
        self.image = image
        self.scaled = self.scaled_flash = None
        self.flash = 0
        self.imm = 0
        self.wobble = random.uniform(0, math.tau)

    @classmethod
    def drop(cls, screen, player, enemies, seconds, image=None):
        """The plush for this fight: away from the player, inside the screen."""
        sw, sh = screen.get_size()
        width = player.width
        hp = max(MIN_HP, round(sum(attack_dps(e) for e in enemies) / max(1, len(enemies)) * seconds))
        angle = random.uniform(0, math.tau)
        dist = min(sw, sh) * random.uniform(0.25, 0.35)
        x = min(sw - width * 2, max(width * 2, player.x + math.cos(angle) * dist))
        y = min(sh - width * 2, max(width * 2, player.y + math.sin(angle) * dist))
        return cls(x, y, width, hp, image)

    @property
    def alive(self):
        return self.hp > 0

    def take_damage(self, amount, effects=None):
        if self.imm > 0:
            return False                # still blinking: the shot goes through it without damage
        self.hp = max(0, self.hp - amount)
        self.flash = HIT_FLASH
        self.imm = IMM_FRAMES
        return [True]

    def draw(self, screen, timer):
        if not self.alive:
            return
        if self.imm > 0:
            self.imm -= 1
        if self.imm > 0 and not self.flash and (self.imm // 5) % 2 == 1:
            return                      # blinking while it can't be hurt
        bob = math.sin(timer / 12 + self.wobble) * 3
        centre = (int(self.x), int(self.y + bob))
        w = self.width
        if self.image:
            if self.scaled is None:     # pixel art (assets/img/combat/decoy.png): sharp scaling, once
                size = w * 2 * SPRITE_SCALE
                iw, ih = self.image.get_size()
                self.scaled = pygame.transform.scale(self.image, (round(size * iw / max(iw, ih)), round(size * ih / max(iw, ih))))
                self.scaled_flash = self.scaled.copy()
                self.scaled_flash.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MAX)
            pic = self.scaled_flash if self.flash else self.scaled
            screen.blit(pic, pic.get_rect(center=centre))
        else:
            # placeholder plush: a round pink body with two ears
            body = (255, 255, 255) if self.flash else (245, 150, 190)
            for side in (-1, 1):
                pygame.draw.circle(screen, body, (centre[0] + side * w * 0.6, centre[1] - w * 0.8), w * 0.4)
                pygame.draw.circle(screen, (60, 40, 60), (centre[0] + side * w * 0.6, centre[1] - w * 0.8), w * 0.4, 2)
            pygame.draw.circle(screen, body, centre, w)
            pygame.draw.circle(screen, (60, 40, 60), centre, w, 3)
            for side in (-1, 1):
                pygame.draw.circle(screen, (40, 30, 40), (centre[0] + side * w * 0.35, centre[1] - w * 0.15), max(2, w // 7))
        if self.flash:
            self.flash -= 1
        # its HP bar
        bar_w, bar_h = w * 2, 6
        left, top = centre[0] - w, centre[1] + int(w * (SPRITE_SCALE if self.image else 1)) + 6
        pygame.draw.rect(screen, (120, 30, 40), (left, top, bar_w, bar_h))
        pygame.draw.rect(screen, (250, 170, 210), (left, top, int(bar_w * self.hp / self.max_hp), bar_h))
