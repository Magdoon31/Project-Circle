# THE CORE FIGHT'S PARTS (10.11, Milo): the beating heart, Milo's mines and the lines he says over the fight. Only these pieces live here - the order of the fight is core_fight.py.

import math
import os
import random

import pygame


# --- the heart -----------------------------------------------------------------------------------------------
HEART_BPM = (60, 140)            # BPM with Milo at full HP .. at 0 HP (it speeds up as he loses)
HEART_BPM_BROKEN = (140, 175)    # after Milo falls: fast and uneven
HEART_PULSE = 0.15               # the heart grows this share of its size on a beat
HEART_VOLUME = (0.55, 1.0)       # the beat's sound: quieter when slow .. loud when fast


class Heart:
    """Counts the heart's beats. `beat` is a float (whole numbers = the beats); tick() says if one just came."""

    def __init__(self):
        self.beat = 0.0
        self.bpm = HEART_BPM[0]
        self.stopped = False
        self.broken = False

    def set_pace(self, hp_share):
        if self.broken:
            self.bpm = random.uniform(*HEART_BPM_BROKEN)
        else:
            low, high = HEART_BPM
            self.bpm = low + (high - low) * (1 - max(0.0, min(1.0, hp_share)))

    def tick(self):
        """One frame on; True when a beat falls on this frame."""
        if self.stopped:
            return False
        before = math.floor(self.beat)
        self.beat += self.bpm / 3600
        return math.floor(self.beat) > before

    def volume(self):
        low, high = HEART_BPM
        share = max(0.0, min(1.0, (self.bpm - low) / (high - low)))
        return HEART_VOLUME[0] + (HEART_VOLUME[1] - HEART_VOLUME[0]) * share

    def pulse(self):
        """How much bigger the heart is drawn now (1 = normal)."""
        if self.stopped:
            return 1.0
        return 1 + HEART_PULSE * (1 - self.beat % 1) ** 3


# --- Milo's mines ("patches") ----------------------------------------------------------------------------------
MINE_RADIUS = 16


class Mine:
    """Dropped where Milo stands; on beat `goes_off` it bursts into a ring of bullets."""

    def __init__(self, pos, goes_off):
        self.pos = pos
        self.goes_off = goes_off

    def due(self, beat):
        return beat >= self.goes_off

    def draw(self, screen, beat):
        left = self.goes_off - beat
        blink = int(left * 4) % 2 == 0 or left < 1
        colour = (255, 70, 70) if blink else (120, 40, 40)
        pygame.draw.circle(screen, colour, (int(self.pos[0]), int(self.pos[1])), MINE_RADIUS)
        pygame.draw.circle(screen, (30, 20, 20), (int(self.pos[0]), int(self.pos[1])), MINE_RADIUS, 3)


# --- what Milo says over the fight ---------------------------------------------------------------------------
SUBTITLE_FRAMES = 200
VOICE_FILE = "assets/voice/milo_fight_{}.ogg"     # a recorded line, if there is one (later: voice lines)


class Subtitles:
    """One line at a time at the bottom of the screen (fades out). A recording plays too if its file exists."""

    def __init__(self, font, volume=1.0):
        self.font = font
        self.volume = volume
        self.text = ""
        self.left = 0

    def say(self, key, text):
        self.text, self.left = text, SUBTITLE_FRAMES
        path = VOICE_FILE.format(key)
        if os.path.exists(path):
            voice = pygame.mixer.Sound(path)
            voice.set_volume(self.volume)
            voice.play()

    def draw(self, screen):
        if self.left <= 0:
            return
        self.left -= 1
        alpha = min(255, self.left * 6)
        line = self.font.render(self.text, True, (255, 236, 200))
        plate = pygame.Surface((line.get_width() + 40, line.get_height() + 18), pygame.SRCALPHA)
        plate.fill((0, 0, 0, min(170, alpha)))
        line.set_alpha(alpha)
        w, h = screen.get_size()
        rect = plate.get_rect(midbottom=(w // 2, h - h // 14))
        screen.blit(plate, rect)
        screen.blit(line, line.get_rect(center=rect.center))
