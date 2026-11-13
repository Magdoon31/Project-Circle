# FIGHT SPRITES (13.11): pictures for the player, enemies, bosses, floors and obstacles in the fights.
# Pixel art, drawn at half size and shown x PIXEL_SCALE with hard pixels (SPRITES.md). Seen from above at an angle
# (3/4 view), so a body stands on the bottom of its hit circle and may stick out above it.
# Every function returns False / None when there is no picture - the caller then draws its old shape.

import math

import pygame

from game.lib import sprites as SPR

PIXEL_SCALE = 2
FLOOR_SCALE = 4                # (13.11) floors twice as big again: a 64 x 64 file covers 256 x 256 px
WALK_FRAME_TIME = 8            # frames per step picture (<dir>_1, <dir>_2 ...)
DIRECTIONS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]     # by angle, 45 degrees each (y grows down)
START_DIRECTION = "s"
SPRITE_OF = {"bloom_copy": "night_bloom", "void_copy": "void_boss"}   # copies look like their boss
BOSS_FOLDER = "combat/bosses"
ENEMY_FOLDER = "combat/enemies"
PLAYER_FOLDER = "combat/player"
FLOOR_FOLDER = "combat/floors"
OBSTACLE_FOLDER = "combat/obstacles"
OBJECT_FOLDER = "combat/objects"
PILLAR_SIZES = [(100, "small"), (130, "medium"), (10 ** 9, "large")]   # the obstacle's longer side (px) -> file
THICK_WALL = 70                # a wall thicker than this (px) uses <biom>_wall_thick_h
PILLAR_SHAPE = 1.6             # longer / shorter side under this = a pillar, not a wall


# --- the player -----------------------------------------------------------------------------------------------
def direction(vx, vy, old):
    """One of the 8 directions for a move (vx, vy); standing still keeps the old one."""
    if not vx and not vy:
        return old
    turn = math.atan2(vy, vx) % math.tau
    return DIRECTIONS[round(turn / (math.tau / 8)) % 8]


def draw_player(screen, player):
    """The player's picture for its direction (and step frame while walking). False = no picture."""
    facing = getattr(player, "facing", START_DIRECTION)
    name = f"{PLAYER_FOLDER}/{facing}"
    if getattr(player, "walking", False):
        steps = _steps(name)
        if steps:
            name = steps[(player.walk_timer // WALK_FRAME_TIME) % len(steps)]
    picture = SPR.pixel(name, PIXEL_SCALE)
    if picture is None:
        return False
    screen.blit(picture, picture.get_rect(midbottom=(player.x, player.y + player.width)))
    return True


def _steps(name):
    """<dir>_1, <dir>_2, ... while they exist."""
    found = []
    k = 1
    while SPR.load(f"{name}_{k}") is not None:
        found.append(f"{name}_{k}")
        k += 1
    return found


# --- enemies and bosses ---------------------------------------------------------------------------------------
def enemy_picture(enemy):
    """The enemy's picture (its phase's, if drawn) facing where it goes, or None."""
    base = SPRITE_OF.get(enemy.name, enemy.name)
    if not base:
        return None
    folder = BOSS_FOLDER if SPR.load(f"{BOSS_FOLDER}/{base}") is not None else ENEMY_FOLDER
    phase = getattr(enemy, "phase_no", 1)
    name = SPR.first(f"{folder}/{base}_f{phase}", f"{folder}/{base}") if phase > 1 else f"{folder}/{base}"
    picture = SPR.pixel(name, PIXEL_SCALE) if name else None
    if picture is not None and getattr(enemy, "face_left", False):
        picture = SPR.flipped(picture)
    return picture


def draw_enemy(screen, enemy):
    """False = no picture (draw the old circle / box)."""
    picture = enemy_picture(enemy)
    if picture is None:
        return False
    if getattr(enemy, "shape", "") == "square":                    # machines, crates: centred on their box
        screen.blit(picture, picture.get_rect(center=(enemy.x, enemy.y)))
    else:
        screen.blit(picture, picture.get_rect(midbottom=(enemy.x, enemy.y + enemy.width)))
    return True


# --- floors ---------------------------------------------------------------------------------------------------
_floors = {}


def floor_name(combat):
    """Which floor file this fight uses (None = the Void: it draws its own islands)."""
    if combat.void:
        return None
    if combat.song:
        return "song_floor"
    if getattr(combat, "arena", {}).get("ice"):
        return "arena_ice"
    if combat.core:
        return "arena_core"
    return getattr(combat, "floor_biome", None)


def draw_floor(screen, name):
    """The floor made of its repeated tile (variants picked per tile). False = no picture."""
    if not name:
        return False
    key = (name, screen.get_size())
    if key not in _floors:
        _floors.clear()                                            # one fight at a time - keep only this one
        _floors[key] = _build_floor(name, screen.get_size())
    if _floors[key] is None:
        return False
    screen.blit(_floors[key], (0, 0))
    return True


def _build_floor(name, size):
    names = SPR.variants(f"{FLOOR_FOLDER}/{name}")
    if not names:
        return None
    floor = pygame.Surface(size)
    step_x, step_y = SPR.pixel(names[0], FLOOR_SCALE).get_size()   # (13.11) the file's own size x4 (64 -> 256 px)
    for ty in range(0, size[1], step_y):
        for tx in range(0, size[0], step_x):
            variant = SPR.pick(names, tx // step_x, ty // step_y)          # (a variant of another size: fitted)
            floor.blit(SPR.to_size(variant, (step_x, step_y), smooth=False), (tx, ty))
    return floor


# --- obstacles ------------------------------------------------------------------------------------------------
def obstacle_picture(theme, rect):
    """A room obstacle (pillar or wall) of this biome at this size: (picture, top-left offset) or None."""
    w, h = rect.size
    if max(w, h) / max(1, min(w, h)) < PILLAR_SHAPE:
        return _pillar(theme, w, h)
    if w >= h:
        return _wall(theme, w, h)
    return _wall(theme, h, w, vertical=True)


def _pillar(theme, w, h):
    size = next(label for limit, label in PILLAR_SIZES if max(w, h) < limit)
    names = SPR.variants(f"{OBSTACLE_FOLDER}/{theme}_pillar_{size}")
    if not names:
        return None
    raw = SPR.load(SPR.pick(names, w, h))
    k = w / raw.get_width()                          # as wide as the obstacle; taller = sticks out above it
    picture = pygame.transform.scale(raw, (w, max(h, round(raw.get_height() * k))))
    return picture, (0, h - picture.get_height())


def _wall(theme, length, thick, vertical=False):
    """A long wall from its pieces: the middle repeated, the two ends (the far one mirrored)."""
    if thick > THICK_WALL:
        middle, end = f"{OBSTACLE_FOLDER}/{theme}_wall_thick_h", None
    elif vertical:
        middle, end = f"{OBSTACLE_FOLDER}/{theme}_wall_v", f"{OBSTACLE_FOLDER}/{theme}_wall_v_end"
    else:
        middle, end = f"{OBSTACLE_FOLDER}/{theme}_wall_h", f"{OBSTACLE_FOLDER}/{theme}_wall_h_end"
    raw = SPR.load(middle)
    if raw is None:
        return None
    turn = vertical and thick > THICK_WALL                    # a thick vertical wall: the horizontal one turned
    if turn or not vertical:
        strip = _strip(raw, SPR.load(end) if end else None, length, thick)
        if turn:
            strip = pygame.transform.rotate(strip, 90)
        return strip, (0, 0)
    side = pygame.transform.rotate(raw, 90)                   # build it lying down, then stand it up
    end_raw = SPR.load(end)
    strip = _strip(side, pygame.transform.rotate(end_raw, 90) if end_raw else None, length, thick)
    return pygame.transform.rotate(strip, -90), (0, 0)


def _strip(middle, end, length, thick):
    """A horizontal strip `length` x `thick`: end, middle, middle, ..., mirrored end (pixel art scaled to `thick`)."""
    k = thick / middle.get_height()
    mid = pygame.transform.scale(middle, (max(1, round(middle.get_width() * k)), thick))
    strip = pygame.Surface((length, thick), pygame.SRCALPHA)
    cap = pygame.transform.scale(end, (max(1, round(end.get_width() * k)), thick)) if end else None
    left = cap.get_width() if cap else 0
    right = length - left
    x = left
    while x < right:
        strip.blit(mid, (x, 0), pygame.Rect(0, 0, right - x, thick))
        x += mid.get_width()
    if cap:
        strip.blit(cap, (0, 0))
        strip.blit(pygame.transform.flip(cap, True, False), (length - cap.get_width(), 0))
    return strip


def object_picture(name, size, flip=False):
    """A fight object (combat/objects/<name>) at exactly this size, hard pixels; None if not drawn."""
    return SPR.to_size(f"{OBJECT_FOLDER}/{name}", size, smooth=False, flip_x=flip)


def clear():
    _floors.clear()
