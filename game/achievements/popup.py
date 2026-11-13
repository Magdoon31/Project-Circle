# "ACHIEVEMENT UNLOCKED" (13.11): a small card that slides down at the top of the screen with the icon, a title
# and the name; one at a time, from the book's queue. Game draws it on the map, the main menu draws it there -
# never in a fight (the queue just waits).

import os
import random

import pygame

from game.achievements.book import BOOK
from game.achievements.data import BY_ID
from game.achievements.icons import icon
from game.menu import fancy_text as FANCY

SHOW_FRAMES = 210                 # 3.5 s on the screen ...
SLIDE_FRAMES = 18                 # ... of it sliding in / out
CARD = (0.32, 0.095)              # share of the screen (width, height)
BACK, EDGE = (24, 16, 38), (190, 160, 230)
SOUND = "achievement"             # the old single sound (assets/sfx/UI/achievement.wav) if none of these is there:
SOUND_DIR = os.path.join("assets", "sfx", "achievements")
SOUNDS = ["adv_1.mp3", "adv_2.mp3", "adv_3.mp3"]          # (13.11, Filip's) one at random ...
SECRET_SOUND = "secret_adv.mp3"                             # ... a hidden achievement: this one


class AchievementPopup:
    def __init__(self, sfx=None):
        self.sfx = sfx
        self.current, self.frames = None, 0
        self.name_cache = None
        self.sounds = self.load_sounds(SOUNDS)
        self.secret_sounds = self.load_sounds([SECRET_SOUND])

    def load_sounds(self, files):
        """The names (in the sfx manager) of the files that are there."""
        names = []
        for file in files:
            name = "achievement_" + os.path.splitext(file)[0]
            path = os.path.join(SOUND_DIR, file)
            if self.sfx is None or not os.path.exists(path):
                continue
            if name not in self.sfx.sfx:
                try:
                    self.sfx.load_sfx(name, path)
                except pygame.error:
                    continue
            names.append(name)
        return names

    def update_and_draw(self, screen):
        if self.current is None:
            self.current = BOOK.next_note()
            self.frames = 0
            if self.current is None:
                return
            self.play_sound()
        self.frames += 1
        self.draw(screen)
        if self.frames >= SHOW_FRAMES:
            self.current = None

    def play_sound(self):
        if self.sfx is None:
            return
        hidden = BY_ID[self.current].get("hidden")
        choices = (self.secret_sounds if hidden else []) or self.sounds
        name = random.choice(choices) if choices else SOUND if SOUND in self.sfx.sfx else None
        if name:
            self.sfx.play(name)

    def name_picture(self, width, size):
        if self.name_cache is None or self.name_cache[0] != (self.current, width, size):
            self.name_cache = ((self.current, width, size), fitted(BY_ID[self.current]["name"], width, size))
        return self.name_cache[1]

    def draw(self, screen):
        sw, sh = screen.get_size()
        w, h = int(sw * CARD[0]), int(sh * CARD[1])
        slide = min(1.0, self.frames / SLIDE_FRAMES, (SHOW_FRAMES - self.frames) / SLIDE_FRAMES)
        card = pygame.Rect(0, 0, w, h)
        card.midtop = (sw // 2, int(-h + (h + sh * 0.02) * ease(slide)))
        pygame.draw.rect(screen, BACK, card, 0, h // 5)
        pygame.draw.rect(screen, EDGE, card, 3, h // 5)
        size = int(h * 0.8)
        picture = icon(self.current, size)
        screen.blit(picture, picture.get_rect(midleft=(card.left + int(h * 0.12), card.centery)))
        left = card.left + int(h * 0.12) + size + int(h * 0.15)
        title = FANCY.font(int(h * 0.22)).render("Achievement unlocked", True, (190, 175, 215))
        name = self.name_picture(card.right - left - int(h * 0.15), int(h * 0.34))
        screen.blit(title, (left, card.top + int(h * 0.14)))
        screen.blit(name, (left, card.top + int(h * 0.42)))


def fitted(text, width, size):
    """(13.11) The name in the menus' letters, as big as `size` but no wider than `width`."""
    picture = FANCY.fancy(text, size)
    if picture.get_width() > width:
        picture = FANCY.fancy(text, max(8, int(size * width / picture.get_width())))
    return picture


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3
