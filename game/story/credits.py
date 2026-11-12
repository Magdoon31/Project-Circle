# CREDITS (12.11): the names roll up a black screen after every ending, over the end_credits music
# (assets/music/end_credits.mp3). The text is game/story/credits.txt:
#   "# Heading" - a big line      "@ assets/img/credits/x.png" - a picture (a missing file is left out)
#   text        - a normal line   (empty line) - a gap
#   the LAST line of the file is not rolled: when everything has gone up, it comes alone in the middle of an empty
#   screen ("Thank you for playing"), the music still playing; then the music fades and the screen goes dark.
# Space / Enter held = faster.

import os

import pygame

from game.menu import fancy_text as FANCY

TEXT_FILE = "game/story/credits.txt"
BACKGROUND = (0, 0, 0)
INK = (235, 232, 240)
SPEED = 0.9                       # px a frame at 1080 px high (scaled with the screen)
FAST = 5                          # x SPEED while Space / Enter is held
HEADING_SIZE, LINE_SIZE = 0.05, 0.03      # shares of the screen's height
PICTURE_SIZE = 0.35               # a picture's height, share of the screen's height
GAP = 0.6                         # an empty line = this share of a normal line's height
FINAL_FADE_IN, FINAL_HOLD, FINAL_FADE_OUT = 90, 300, 150     # frames of the last screen
FADE_MS = FINAL_FADE_OUT * 1000 // 60                          # the music fades with the last screen


def read_lines(path=TEXT_FILE):
    """[(kind, text)]: "heading" / "line" / "picture" / "gap"."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read().splitlines()
    except OSError:
        raw = ["# Thank you for playing"]
    out = []
    for line in raw:
        if line.startswith(";"):
            continue
        if not line.strip():
            out.append(("gap", ""))
        elif line.startswith("#"):
            out.append(("heading", line.lstrip("#").strip()))
        elif line.startswith("@"):
            out.append(("picture", line[1:].strip()))
        else:
            out.append(("line", line.strip()))
    while out and out[0][0] == "gap":
        out.pop(0)
    while out and out[-1][0] == "gap":
        out.pop()
    return out


class Credits:
    def __init__(self, screen):
        self.screen = screen
        w, h = screen.get_size()
        self.speed = SPEED * h / 1080
        lines = read_lines()
        self.final = self.render(lines[-1:], h)[0][0] if lines else None     # the last line: its own screen
        self.images = self.render(lines[:-1], h)
        self.y = float(h)                                    # the top of the text, coming up from below
        self.final_frames = 0
        self.finished = False

    @staticmethod
    def render(lines, h):
        """[(picture or None, height)] - None = a gap."""
        font = pygame.font.Font("assets/font/Nexa-ExtraLight.ttf", int(h * LINE_SIZE))
        out = []
        for kind, text in lines:
            if kind == "gap":
                out.append((None, int(h * LINE_SIZE * GAP)))
            elif kind == "heading":
                img = FANCY.fancy(text, int(h * HEADING_SIZE))
                out.append((img, img.get_height()))
            elif kind == "picture":
                img = load_picture(text, int(h * PICTURE_SIZE))
                if img is not None:
                    out.append((img, int(img.get_height() * 1.1)))
            else:
                img = font.render(text, True, INK)
                out.append((img, int(img.get_height() * 1.25)))
        return out

    @property
    def rolled_away(self):
        """Everything has gone off the top of the screen."""
        return self.y + sum(height for _, height in self.images) < 0

    @property
    def fading_out(self):
        """The last screen is fading (Game / EndingScene fades the music then)."""
        return self.final_frames > FINAL_FADE_IN + FINAL_HOLD

    def update(self, fast):
        if not self.rolled_away:
            self.y -= self.speed * (FAST if fast else 1)
            return
        self.final_frames += 1
        self.finished = self.final_frames >= FINAL_FADE_IN + FINAL_HOLD + FINAL_FADE_OUT

    def draw(self):
        self.screen.fill(BACKGROUND)
        if self.rolled_away:
            self.draw_final()
            return
        w = self.screen.get_width()
        y = self.y
        for img, height in self.images:
            if img is not None and -height < y < self.screen.get_height():
                self.screen.blit(img, img.get_rect(midtop=(w // 2, int(y))))
            y += height

    def draw_final(self):
        if self.final is None:
            return
        t = self.final_frames
        if t < FINAL_FADE_IN:
            alpha = 255 * t // FINAL_FADE_IN
        elif t < FINAL_FADE_IN + FINAL_HOLD:
            alpha = 255
        else:
            alpha = max(0, 255 - 255 * (t - FINAL_FADE_IN - FINAL_HOLD) // FINAL_FADE_OUT)
        img = self.final.copy()
        img.set_alpha(alpha)
        self.screen.blit(img, img.get_rect(center=self.screen.get_rect().center))


def load_picture(path, height):
    if not os.path.exists(path):
        return None
    try:
        raw = pygame.image.load(path).convert_alpha()
    except pygame.error:
        return None
    return pygame.transform.smoothscale(raw, (max(1, raw.get_width() * height // raw.get_height()), height))
