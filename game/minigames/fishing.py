# FISHING (Oliver's ice hole) - like DeeDee's Fishing Hole in FNaF World.
# 5 rows under the ice. Everything swims left <-> right and bounces off the sides of the hole:
#   row 1: 5 fish (1$)   row 2: 4 fish (5$)   row 3: 3 fish (30$)   row 4: 2 fish (50$)   row 5: the PEARL (250$)
# Aim the line at the top (A/D or arrows), Space / Enter = drop it. It sinks STRAIGHT down and the hook catches
# the FIRST thing it touches - to get the pearl you have to time the drop through the gaps.
# 30 s to aim, then the line drops by itself. No countdown and no minigame music (the Tundra music keeps playing).
# One cast per payment (game.py MINIGAME_PRICES) and then a break (game.py MINIGAME_COOLDOWNS).
# Catching anything = "win", the gold is in .reward (Game pays it out).

import os, random
import pygame
from game.minigames.base import Minigame

IMAGE_DIR = "assets/img/minigames"
AIM_SECONDS = 30            # time to aim; then the line drops by itself
AIM_SPEED = 0.012           # how fast the aim moves (share of the pond width per frame)
SINK_SPEED = 0.024         # how fast the hook sinks (share of the pond height per frame)
# rows from the top: (picture, how many, value in $, width as a share of the pond width, speed range)
ROWS = [("fish1.png", 5, 1,   0.085, (0.0020, 0.0040)),
        ("fish2.png", 4, 5,   0.085, (0.0025, 0.0045)),
        ("fish3.png", 3, 30,  0.085, (0.0030, 0.0055)),
        ("fish4.png", 2, 50,  0.085, (0.0035, 0.0065)),
        ("pearl.png", 1, 250, 0.05,  (0.0030, 0.0050))]
PEARL_ROW = len(ROWS) - 1
_images = {}
_scaled = {}          # (picture, width, flipped) -> scaled picture


def _image(name):
    if name not in _images:
        path = os.path.join(IMAGE_DIR, name)
        try:
            _images[name] = pygame.image.load(path).convert_alpha() if os.path.exists(path) else None
        except pygame.error:
            _images[name] = None
    return _images[name]


class Swimmer:
    """A fish (or the pearl) in a row. x = centre, 0..1 of the pond width."""
    def __init__(self, row, x, speed):
        self.row, self.x, self.speed = row, x, speed
        picture, _, self.value, self.width, _ = ROWS[row]
        self.picture = picture

    def move(self):
        self.x += self.speed
        half = self.width / 2
        if self.x < half or self.x > 1 - half:          # bounces off the side of the hole
            self.x = max(half, min(1 - half, self.x))
            self.speed = -self.speed


class Fishing(Minigame):
    title = "Oliver's Ice Hole"
    use_countdown = False           # Game: no 3-2-1 and no minigame music for this one
    keep_music = True

    def __init__(self, screen, background, volume=1.0):
        super().__init__(screen, background, volume)
        self.countdown = 0
        self.swimmers = []
        for row, (_, count, _, width, (slow, fast)) in enumerate(ROWS):
            lane = (1 - width) / count                     # spread them out over the row at the start
            for k in range(count):
                x = width / 2 + lane * (k + random.uniform(0.1, 0.9))
                self.swimmers.append(Swimmer(row, x, random.uniform(slow, fast) * random.choice((-1, 1))))
        self.aim = 0.5
        self.hook_y = None                      # None = still aiming, else 0..1 depth of the hook
        self.frames_left = AIM_SECONDS * 60
        self.caught = None                      # the Swimmer that bit
        self.reward = 0
        self.wait_after = 0

    # --- input / logic ----------------------------------------------------------------------------
    def on_events(self, events):
        if self.hook_y is not None:
            return
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_s, pygame.K_DOWN):
                self.drop()

    def drop(self):
        self.hook_y = 0.0
        self.play("flip")

    def on_update(self):
        for s in self.swimmers:
            if s is not self.caught:
                s.move()
        if self.caught is not None:
            self.wait_after -= 1
            if self.wait_after <= 0:
                self.end(True)
            return
        if self.hook_y is None:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.aim = max(0.02, self.aim - AIM_SPEED)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.aim = min(0.98, self.aim + AIM_SPEED)
            self.frames_left -= 1
            if self.frames_left <= 0:
                self.drop()
            return
        self.hook_y += SINK_SPEED
        for s in self.swimmers:
            if abs(self.row_y(s.row) - self.hook_y) < 0.03 and abs(s.x - self.aim) < s.width / 2:
                self.caught, self.reward = s, s.value
                self.wait_after = 30            # a moment to see what bit
                self.play("match")
                return
        if self.hook_y >= 1.0:
            self.end(False)

    @staticmethod
    def row_y(row):
        return 0.2 + row * 0.17                 # depth of a row, 0..1

    def win_text(self):
        return f"A pearl! +{self.reward}$" if self.caught.row == PEARL_ROW else f"Caught a fish! +{self.reward}$"

    def lose_text(self):
        return "Nothing bites."

    # --- drawing ----------------------------------------------------------------------------------
    def on_draw(self):
        sw, sh = self.screen.get_size()
        if self.hook_y is None:
            self.draw_header("A/D aim, Space drop the line. The hook catches the first thing it touches.",
                             self.frames_left / 60, AIM_SECONDS)
        else:
            self.draw_header("...")
        pond = pygame.Rect(0, 0, int(sw * 0.6), int(sh * 0.7))
        pond.midtop = (sw // 2, int(sh * 0.2))
        pygame.draw.rect(self.screen, (20, 45, 80), pond, 0, 18)                    # the cold water
        ice = pygame.Rect(pond.left, pond.top, pond.width, int(pond.height * 0.07))
        pygame.draw.rect(self.screen, (210, 230, 245), ice, 0, 18)
        pygame.draw.rect(self.screen, (150, 190, 220), pond, 4, 18)
        px = lambda x: pond.left + int(x * pond.width)
        py = lambda y: pond.top + int(y * pond.height)
        hook_x = px(self.aim)
        hook = py(self.hook_y if self.hook_y is not None else 0.04)
        self.screen.set_clip(pond)
        for s in self.swimmers:
            if s is self.caught:
                centre = (hook_x, hook + int(s.width * pond.width * 0.3))          # hanging on the hook
            else:
                centre = (px(s.x), py(self.row_y(s.row)))
            self.draw_swimmer(s, centre, int(s.width * pond.width))
        self.screen.set_clip(None)
        pygame.draw.line(self.screen, (235, 235, 235), (hook_x, ice.top), (hook_x, hook), 2)
        pygame.draw.circle(self.screen, (200, 200, 210), (hook_x, hook), max(4, pond.width // 120), 2)
        # values on the side (the deeper, the better)
        for row, (_, _, value, _, _) in enumerate(ROWS):
            label = self.font_small.render(f"{value}$", True, (240, 240, 255) if row == PEARL_ROW else (200, 220, 235))
            self.screen.blit(label, (pond.right + 12, py(self.row_y(row)) - label.get_height() // 2))

    def draw_swimmer(self, s, centre, width):
        img = _image(s.picture)
        if img:
            flip = s.speed > 0 and s.row != PEARL_ROW               # the pictures look left
            key = (s.picture, width, flip)
            if key not in _scaled:
                height = int(width * img.get_height() / img.get_width())
                _scaled[key] = pygame.transform.flip(pygame.transform.smoothscale(img, (width, height)), flip, False)
            pic = _scaled[key]
            self.screen.blit(pic, pic.get_rect(center=centre))
        elif s.row == PEARL_ROW:
            pygame.draw.circle(self.screen, (240, 240, 255), centre, width // 2)
        else:
            rect = pygame.Rect(0, 0, width, width * 2 // 3)
            rect.center = centre
            pygame.draw.ellipse(self.screen, (150, 190, 210), rect)
