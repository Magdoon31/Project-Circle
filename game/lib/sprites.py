# SPRITES (13.11): the one place that loads pictures from assets/img (list and sizes: SPRITES.md).
# A picture is named by its path under assets/img without ".png", e.g. "combat/enemies/slime_small".
# A missing file is fine: you get None and the game draws its old shape instead - so sprites can come one by one.
# Pictures are loaded once and kept (also the scaled copies); clear() forgets them all (F5 in the game: new files
# show up without a restart).
#   load(name)               the picture as it is (or None)
#   pixel(name, scale)       pixel art: bigger by a whole number, no smoothing (the fights: x2)
#   to_size(name, size, ...) a fixed size; smooth = False keeps the pixels hard
#   variants(name)           [name, name_2, name_3, ...] - those that exist (a missing name_2 ends the list)
#   pick(names, x, y)        always the same one for the same spot (so a floor doesn't flicker)

import os

import pygame

ROOT = os.path.join("assets", "img")
MAX_VARIANTS = 9

_pictures = {}
_scaled = {}


def path_of(name):
    return os.path.join(ROOT, *name.split("/")) + ".png"


def load(name):
    if name not in _pictures:
        _pictures[name] = _read(path_of(name))
    return _pictures[name]


def _read(path):
    if not os.path.exists(path):
        return None
    try:
        picture = pygame.image.load(path)
        return picture.convert_alpha() if pygame.display.get_surface() else picture
    except pygame.error:
        return None


def pixel(name, scale):
    """Pixel art `scale` times bigger with hard pixels (or None)."""
    picture = load(name)
    if picture is None:
        return None
    key = (name, "x", scale)
    if key not in _scaled:
        w, h = picture.get_size()
        _scaled[key] = pygame.transform.scale(picture, (round(w * scale), round(h * scale)))
    return _scaled[key]


def to_size(name, size, smooth=True, flip_x=False):
    """The picture at exactly `size` (w, h) - smooth (drawn art) or hard pixels (pixel art); flip_x = mirrored."""
    picture = load(name)
    if picture is None:
        return None
    size = (max(1, int(size[0])), max(1, int(size[1])))
    key = (name, size, smooth, flip_x)
    if key not in _scaled:
        scaled = (pygame.transform.smoothscale if smooth else pygame.transform.scale)(picture, size)
        _scaled[key] = pygame.transform.flip(scaled, True, False) if flip_x else scaled
    return _scaled[key]


def flipped(picture):
    """A mirrored copy (left <-> right), kept so it is made only once."""
    key = ("flip", id(picture))
    if key not in _scaled:
        _scaled[key] = (picture, pygame.transform.flip(picture, True, False))
    return _scaled[key][1]


def variants(name):
    found = [name] if load(name) is not None else []
    for k in range(2, MAX_VARIANTS + 1):
        if load(f"{name}_{k}") is None:
            break
        found.append(f"{name}_{k}")
    return found


def pick(names, x, y):
    """One of `names` for the spot (x, y) - random-looking, but always the same for the same spot."""
    if not names:
        return None
    return names[(x * 73856093 ^ y * 19349663) % len(names)]


def first(*names):
    """The first of these names that has a picture (or None)."""
    return next((n for n in names if load(n) is not None), None)


def clear():
    """Forget everything loaded (F5): the next draw reads the files again."""
    _pictures.clear()
    _scaled.clear()
