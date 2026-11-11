# DAMAGE NUMBERS (11.11, Settings -> Gameplay): how much you hit an enemy for, rising over it and fading. It only
# watches the enemies' HP (whatever took it - a bullet, an explosion, a burn - it shows), and hits close together
# on one enemy add up into one number.

import pygame

LIFE = 45                         # frames a number shows
RISE = 0.9                        # px a frame it goes up
MERGE = 8                         # frames: a new hit this soon after the last one adds to its number
COLOUR, EDGE = (255, 236, 160), (60, 30, 20)


def short(amount):
    """1234 -> 1234, 12345 -> 12.3k"""
    return f"{amount / 1000:.1f}k" if amount >= 10_000 else str(int(round(amount)))


class DamageNumbers:
    def __init__(self, font):
        self.font = font
        self.last_hp = {}                         # enemy -> its HP last frame
        self.numbers = []                         # [enemy, x, y, amount, age]

    def update(self, enemies):
        for e in enemies:
            before = self.last_hp.get(e)
            self.last_hp[e] = e.hp
            if before is not None and e.hp < before and not getattr(e, "hidden", False):
                self.add(e, before - e.hp)
        for n in self.numbers:
            n[2] -= RISE
            n[4] += 1
        self.numbers = [n for n in self.numbers if n[4] < LIFE]
        if len(self.last_hp) > 4 * len(enemies) + 16:                # forget the dead ones now and then
            self.last_hp = {e: hp for e, hp in self.last_hp.items() if e in enemies}

    def add(self, enemy, amount):
        recent = next((n for n in reversed(self.numbers) if n[0] is enemy and n[4] < MERGE), None)
        if recent:
            recent[3] += amount
        else:
            self.numbers.append([enemy, enemy.x, enemy.y - enemy.width - 10, amount, 0])

    def draw(self, screen):
        for _, x, y, amount, age in self.numbers:
            text = short(amount)
            img = self.font.render(text, True, COLOUR)
            edge = self.font.render(text, True, EDGE)
            alpha = 255 if age < LIFE * 0.6 else int(255 * (LIFE - age) / (LIFE * 0.4))
            word = pygame.Surface((img.get_width() + 2, img.get_height() + 2), pygame.SRCALPHA)
            for dx, dy in ((0, 0), (2, 0), (0, 2), (2, 2)):
                word.blit(edge, (dx, dy))
            word.blit(img, (1, 1))
            word.set_alpha(alpha)
            screen.blit(word, word.get_rect(center=(int(x), int(y))))
