# FIGHT SPRITES (13.11): pictures for the player, enemies, bosses, floors and obstacles in the fights.
# Pixel art shown x ART_SCALE with hard pixels (SPRITES.md). (19.11, Filip) EVERY picture in a fight (bullets aside)
# has pixels of the same size - one file pixel = ART_SCALE screen px, like the floors: nothing is stretched to fit
# its obstacle any more (a wall is built from whole pieces, a pillar stands on its box). Seen from above at an angle
# (3/4 view), so a body stands on the bottom of its hit circle and may stick out above it.
# Every function returns False / None when there is no picture - the caller then draws its old shape.

import math

import pygame

from game.lib import sprites as SPR

ART_SCALE = 4                  # (19.11) one file pixel = 4 screen px for everything (a 64 x 64 floor = 256 x 256 px)
PIXEL_SCALE = ART_SCALE        # the player, enemies, bosses
FLOOR_SCALE = ART_SCALE
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
THICK_WALL = 70                # a wall thicker than this (px) uses <biom>_wall_thick_h (vertical: _wall_thick_v)
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
    name = _jump_picture(enemy, name)
    picture = SPR.pixel(name, PIXEL_SCALE) if name else None
    if picture is not None and getattr(enemy, "face_left", False):
        picture = SPR.flipped(picture)
    return picture


def _jump_picture(enemy, name):
    """(21.11) A jumper shows <name>_jump (crouching, just before and after it takes off), then <name>_fly (in the
    air) - each only if drawn; standing = its normal picture."""
    pose = getattr(enemy, "jump_pose", lambda: None)()
    if name and pose and SPR.load(f"{name}_{pose}") is not None:
        return f"{name}_{pose}"
    return name


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
_objects = {}                  # (19.11) tiled objects (the ice walls) by name and size


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
# (19.11) Drawn at ART_SCALE, never stretched: the picture stands on the bottom of its box, centred across it (a 3/4
# view - it may stick out above the box or a bit to the sides).
def obstacle_picture(theme, rect):
    """A room obstacle (pillar or wall) of this biome at this size: (picture, top-left offset) or None."""
    w, h = rect.size
    if max(w, h) / max(1, min(w, h)) < PILLAR_SHAPE:
        picture = _pillar(theme, w, h)
    elif w >= h:
        picture = _strip(theme, "wall_thick_h" if h > THICK_WALL else "wall_h", w)
    else:
        picture = _vertical_wall(theme, w, h)
    if picture is None:
        return None
    return picture, ((w - picture.get_width()) // 2, h - picture.get_height())


def _pillar(theme, w, h):
    size = next(label for limit, label in PILLAR_SIZES if max(w, h) < limit)
    names = SPR.variants(f"{OBSTACLE_FOLDER}/{theme}_pillar_{size}")
    return SPR.pixel(SPR.pick(names, w, h), ART_SCALE) if names else None


def _vertical_wall(theme, w, h):
    """A thick vertical wall uses its own pieces (_wall_thick_v) if drawn, else the thin ones."""
    kinds = ["wall_thick_v", "wall_v"] if w > THICK_WALL else ["wall_v"]
    return next((p for p in (_column(theme, kind, h) for kind in kinds) if p), None)


def _strip(theme, kind, length):
    """A horizontal wall `length` px long: end, middle, middle, ..., mirrored end - whole pieces at ART_SCALE, the
    last middle cut. The middles may have variants (<kind>_2, ...). None = no middle drawn."""
    middles = SPR.variants(f"{OBSTACLE_FOLDER}/{theme}_{kind}")
    if not middles:
        return None
    cap = SPR.pixel(f"{OBSTACLE_FOLDER}/{theme}_{kind}_end", ART_SCALE)
    height = max([SPR.pixel(m, ART_SCALE).get_height() for m in middles] + ([cap.get_height()] if cap else []))
    strip = pygame.Surface((length, height), pygame.SRCALPHA)
    left = cap.get_width() if cap else 0
    _repeat(strip, middles, left, length - left, along_x=True)
    if cap:
        strip.blit(cap, (0, height - cap.get_height()))
        strip.blit(pygame.transform.flip(cap, True, False), (length - cap.get_width(), height - cap.get_height()))
    return strip


def _column(theme, kind, length):
    """(19.11) A vertical wall `length` px tall: its top piece (<kind>_top), the middle repeated, its bottom piece
    (<kind>_end) - whole pieces at ART_SCALE, the last middle cut. Without a top piece the middle goes up to the
    top. None = no middle drawn."""
    middles = SPR.variants(f"{OBSTACLE_FOLDER}/{theme}_{kind}")
    if not middles:
        return None
    top = SPR.pixel(f"{OBSTACLE_FOLDER}/{theme}_{kind}_top", ART_SCALE)
    bottom = SPR.pixel(f"{OBSTACLE_FOLDER}/{theme}_{kind}_end", ART_SCALE)
    width = max(SPR.pixel(m, ART_SCALE).get_width() for m in middles)
    column = pygame.Surface((width, length), pygame.SRCALPHA)
    first = top.get_height() if top else 0
    _repeat(column, middles, first, length - (bottom.get_height() if bottom else 0), along_x=False)
    if top:
        column.blit(top, ((width - top.get_width()) // 2, 0))
    if bottom:
        column.blit(bottom, ((width - bottom.get_width()) // 2, length - bottom.get_height()))
    return column


def _repeat(surface, names, start, stop, along_x):
    """The middle pieces one after another from `start` to `stop` (px along the wall), the last one cut; a piece
    narrower than the wall is centred across it (a vertical wall) or stands on its bottom (a horizontal one)."""
    at, piece = start, 0
    while at < stop:
        mid = SPR.pixel(SPR.pick(names, piece, stop), ART_SCALE)
        if along_x:
            surface.blit(mid, (at, surface.get_height() - mid.get_height()), pygame.Rect(0, 0, stop - at, mid.get_height()))
            at += mid.get_width()
        else:
            surface.blit(mid, ((surface.get_width() - mid.get_width()) // 2, at), pygame.Rect(0, 0, mid.get_width(), stop - at))
            at += mid.get_height()
        piece += 1


def object_tiled(name, size, flip=False):
    """(19.11) A fight object (combat/objects/<name>, e.g. the ice wall) filling `size` with its tile repeated at
    ART_SCALE (cut at the far edges) - its pixels as big as everything else's. None if not drawn."""
    key = (name, int(size[0]), int(size[1]), flip)
    if key not in _objects:
        _objects[key] = _tiled(name, size, flip)
    return _objects[key]


def _tiled(name, size, flip):
    tile = SPR.pixel(f"{OBJECT_FOLDER}/{name}", ART_SCALE)
    if tile is None:
        return None
    w, h = max(1, int(size[0])), max(1, int(size[1]))
    picture = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, tile.get_height()):
        for x in range(0, w, tile.get_width()):
            picture.blit(tile, (x, y))
    return pygame.transform.flip(picture, True, False) if flip else picture


def object_picture(name, size, flip=False):
    """A fight object (combat/objects/<name>) at exactly this size, hard pixels; None if not drawn."""
    return SPR.to_size(f"{OBJECT_FOLDER}/{name}", size, smooth=False, flip_x=flip)


def clear():
    _floors.clear()
    _objects.clear()
