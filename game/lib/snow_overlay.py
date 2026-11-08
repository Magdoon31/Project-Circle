# SNOW OVERLAY (8.11): Filip's animated snow (assets/img/map/snow_overlay/frame1..N.png), stretched to the screen.
# Used on the map in the Tundra (Map.draw_overlay) and in the Frost Golem's snowstorm (Combat.draw_blizzard).

import os
import pygame

FOLDER = "assets/img/map/snow_overlay"
FPS = 16                       # animation frames per second
_cache = {}


def frames(size):
    """The frames scaled to `size` (loaded once per size); [] if the files aren't there."""
    if size not in _cache:
        out, i = [], 1
        while os.path.exists(f"{FOLDER}/frame{i}.png"):
            out.append(pygame.transform.smoothscale(pygame.image.load(f"{FOLDER}/frame{i}.png").convert_alpha(), size))
            i += 1
        _cache[size] = out
    return _cache[size]


def draw(screen, alpha=255):
    """Draws the current frame (by the clock) with this transparency."""
    imgs = frames(screen.get_size())
    if not imgs or alpha <= 0:
        return
    img = imgs[(pygame.time.get_ticks() * FPS // 1000) % len(imgs)]
    img.set_alpha(int(alpha))
    screen.blit(img, (0, 0))
