# VOID SPRITES (19.11): pictures for the Void's arena - the abyss, the islands and the bridges. void_arena.py asks
# for them; every function returns False when there is no picture, and the arena draws its old shapes instead.
# Files in assets/img/combat/floors/ (list and sizes: SPRITES.md):
#   void_abyss (+ _2, _3 ...)           the abyss under everything: a 64 x 64 tile shown x4, like the fight floors
#   void_island_middle                  the middle island at its biggest (r 420, F5 and the end)
#   void_island_middle_small            (optional) the middle island in F1-F4 (r 330); without it the big one, smaller
#   void_island_outer                   the 8 outer islands (r 220 in every phase)
#   void_bridge_<short/medium/long>     a bridge lying left-right; the game turns it to where it goes
#   void_belt_<short/medium/long>       F3's wide conveyor bridges; the moving arrows are still drawn over them
#   <any of these>_pale                 (optional) the Pale phase's look; without it that phase keeps its white shapes
# (19.11, Filip) Shown at ART_SCALE like every fight picture - same-sized pixels, nothing stretched. An island file is
# as wide as its island / ART_SCALE; its top is the island's top, and what is under the circle (the rock below, 3/4
# view) hangs down past it. Only while an island grows or shrinks (F5) is the nearest file scaled for a moment.
# A bridge is drawn at its own length, centred between its islands (SPRITES.md: long enough to tuck under them).

import math

import pygame

from game.combat import sprites as FIGHT_SPRITES
from game.lib import sprites as SPR

FOLDER = "combat/floors"
ABYSS = "void_abyss"
PALE = "_pale"
ISLAND_FILES = {                                  # kind -> (the radius the file is drawn for, file); nearest one wins
    "middle": [(420, "void_island_middle"), (330, "void_island_middle_small")],
    "outer": [(220, "void_island_outer")],
}
SIZE_STEP = 4                    # px: sizes rounded to this, so a growing island / bridge isn't scaled anew every frame
FAR_SHADE = (150, 150, 175)      # F5: the outer islands out of reach are darker (multiplied)
CACHE_LIMIT = 400                # pictures kept; more = forget them all and start again
FLIP_BELOW = -1e-6               # a bridge going left is mirrored (not turned upside down)

_cache = {}


def draw_abyss(screen, pale):
    """The abyss tiled over the whole arena. False = no picture."""
    return FIGHT_SPRITES.draw_floor(screen, ABYSS + PALE if pale else ABYSS)


# --- islands --------------------------------------------------------------------------------------------------
def draw_island(screen, kind, island, pale=False, far=False):
    """kind "middle" / "outer"; island (x, y, radius). False = no picture."""
    x, y, r = island
    picture = _remember(("island", kind, _rounded(r), pale, far), lambda: _island_picture(kind, _rounded(r), pale, far))
    if picture is None:
        return False
    half = picture.get_width() / 2                           # the art's circle is as wide as the file
    screen.blit(picture, (round(x - half), round(y - half)))
    return True


def _island_picture(kind, radius, pale, far):
    drawn = _island_file(kind, radius, pale)
    if drawn is None:
        return None
    made_for, name = drawn
    if abs(made_for - radius) <= SIZE_STEP:
        picture = SPR.pixel(name, FIGHT_SPRITES.ART_SCALE)                  # its own size: pixels x4
    else:                                                                   # growing / shrinking: scaled for now
        raw = SPR.load(name)
        width = round(2 * radius * raw.get_width() * FIGHT_SPRITES.ART_SCALE / (2 * made_for))
        picture = SPR.to_size(name, (width, round(raw.get_height() * width / raw.get_width())), smooth=False)
    if far:
        picture = picture.copy()
        picture.fill(FAR_SHADE, special_flags=pygame.BLEND_RGB_MULT)
    return picture


def _island_file(kind, radius, pale):
    """(the radius it is made for, file) of the drawn file nearest to this radius (None = none drawn)."""
    suffix = PALE if pale else ""
    drawn = [(r, f"{FOLDER}/{name}{suffix}") for r, name in ISLAND_FILES[kind]
             if SPR.load(f"{FOLDER}/{name}{suffix}") is not None]
    return min(drawn, key=lambda d: abs(d[0] - radius)) if drawn else None


# --- bridges --------------------------------------------------------------------------------------------------
def draw_bridge(screen, look, a, b, pale=False):
    """look = (size, belt, middle, grown): which picture ("short" / "medium" / "long", a belt or not), where its
    middle goes (px from a towards b) and how far from a the bridge has grown yet (px). a, b = the middles of the two
    islands. Drawn at its own length (ART_SCALE), cut to the part that has grown. False = no picture."""
    size, belt, middle, grown = look
    name = f"{FOLDER}/void_{'belt' if belt else 'bridge'}_{size}{PALE if pale else ''}"
    full = SPR.pixel(name, FIGHT_SPRITES.ART_SCALE)
    if full is None:
        return False
    length = full.get_width()
    start = middle - length / 2
    shown = grown - start
    if shown <= 0:
        return True                                         # it has only just started to grow
    shown = min(length, _rounded(shown, 2 * SIZE_STEP))
    angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    picture = _remember(("bridge", name, shown, round(angle, 1)), lambda: _bridge_picture(full, shown, angle))
    d = math.dist(a, b) or 1
    along = start + shown / 2                               # the middle of the part that stands
    centre = (a[0] + (b[0] - a[0]) / d * along, a[1] + (b[1] - a[1]) / d * along)
    screen.blit(picture, picture.get_rect(center=(round(centre[0]), round(centre[1]))))
    return True


def _bridge_picture(full, shown, angle):
    """The bridge cut to its standing part (from a's side), turned to its angle. Going left it is mirrored and
    turned the other way, so its side face stays at the bottom."""
    part = full.subsurface(pygame.Rect(0, 0, shown, full.get_height())).copy()
    if math.cos(math.radians(angle)) < FLIP_BELOW:
        part = pygame.transform.flip(part, True, False)
        angle -= 180
    return pygame.transform.rotate(part, -angle)            # (pygame turns anticlockwise; y grows down)


# --- the cache ------------------------------------------------------------------------------------------------
def _remember(key, make):
    if key not in _cache:
        if len(_cache) >= CACHE_LIMIT:
            _cache.clear()
        _cache[key] = make()
    return _cache[key]


def _rounded(value, step=SIZE_STEP):
    return max(step, int(round(value / step)) * step)


def clear():
    """Forget the pictures (F5 reloads the files)."""
    _cache.clear()
