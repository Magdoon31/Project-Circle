# FIGHT SPRITES (13.11): pictures for the player, enemies, bosses, floors and obstacles in the fights.
# Pixel art shown x ART_SCALE with hard pixels (SPRITES.md). (19.11, Filip) EVERY picture in a fight (bullets aside)
# has pixels of the same size - one file pixel = ART_SCALE screen px, like the floors: nothing is stretched to fit
# its obstacle any more (a wall is built from whole pieces, a pillar stands on its box). Seen from above at an angle
# (3/4 view), so a body stands on the bottom of its hit circle and may stick out above it.
# Every function returns False / None when there is no picture - the caller then draws its old shape.

import math
import random

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


PLAYER_SCALE = 3               # (23.11, Filip) the player is drawn a bit smaller than the rest (x3, not x4)
AIM_FACE_MS = 350              # (23.11) after a shot the player looks where it shot this long (even walking away)


def draw_player(screen, player):
    """The player's picture for its direction (and step frame while walking). False = no picture."""
    facing = getattr(player, "facing", START_DIRECTION)
    if pygame.time.get_ticks() < getattr(player, "aim_until", 0):
        facing = player.aim_facing                                  # (23.11) it just shot: turned that way
    name = f"{PLAYER_FOLDER}/{facing}"
    if getattr(player, "walking", False):
        steps = _steps(name)
        if steps:
            name = steps[(player.walk_timer // WALK_FRAME_TIME) % len(steps)]
    picture = SPR.pixel(name, PLAYER_SCALE)
    if picture is None:
        return False
    rect = picture.get_rect(midbottom=(player.x, player.y + player.width))
    screen.blit(picture, rect)
    player.sprite_top = rect.top                                    # (23.11) the HP bar goes over it ...
    player.sprite_right = rect.right                                # ... the effects' icons on its right
    return True


# --- (23.11) the player's HP bar: pictures (combat/objects/hp_bar*), shown x2 - smaller pixels than the rest ------
HP_BAR_SCALE = 2
HP_FILL_X = (1, 22)            # file px of hp_bar.png where the fill goes (from, to) - tools/make_hp_bar.py
HP_BAR_GAP = 6                 # px between the bar and the top of the player's picture
HP_MID, HP_LOW = 0.5, 0.25     # under these shares of max HP the fill is yellow / red


def draw_hp_bar(screen, x, top, share, shown):
    """The HP bar centred on x, its bottom HP_BAR_GAP px over `top`; share = HP left (0..1), shown = what the bar
    still shows of it (falls slowly after a hit: the "lost" part). -> the bar's top (px), None = no picture."""
    frame = SPR.pixel(f"{OBJECT_FOLDER}/hp_bar", HP_BAR_SCALE)
    if frame is None:
        return None
    fill = "hp_bar_fill_low" if share < HP_LOW else "hp_bar_fill_mid" if share < HP_MID else "hp_bar_fill"
    left, y = round(x - frame.get_width() / 2), round(top - HP_BAR_GAP - frame.get_height())
    screen.blit(frame, (left, y))
    for name, part in (("hp_bar_lost", shown), (fill, share)):
        picture = SPR.pixel(f"{OBJECT_FOLDER}/{name}", HP_BAR_SCALE)
        if picture is None:
            continue
        pixels = round((HP_FILL_X[1] - HP_FILL_X[0]) * max(0.0, min(1.0, part)))   # whole file pixels
        if pixels:
            width = (HP_FILL_X[0] + pixels) * HP_BAR_SCALE
            screen.blit(picture, (left, y), pygame.Rect(0, 0, width, picture.get_height()))
    return y


# --- (23.11) the effects on the player: icons in a row over its HP bar (combat/objects/effect_<name>.png, x2) -------
EFFECT_GAP = 2                 # px between two icons, and between them and the bar


def draw_effect_icons(screen, left, top, effects):
    """(23.11, Filip: on the player's right) The icons of the effects that have one, one under another from (left,
    top). False = none drawn (no pictures)."""
    icons = [(SPR.pixel(f"{OBJECT_FOLDER}/effect_{name}", HP_BAR_SCALE), value) for name, value in effects.items()]
    icons = [(picture, value) for picture, value in icons if picture is not None]
    if not icons:
        return False
    y = round(top)
    for picture, value in icons:                    # (23.11, Filip) no blinking: always shown, easy to see
        screen.blit(picture, (round(left), y))
        y += picture.get_height() + EFFECT_GAP
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
    jumped = _jump_picture(enemy, name)
    # (23.11) a drawn _jump / _fly picture wins; without one a jumper keeps its other poses (a pixie's flapping)
    name = jumped if jumped != name else _action_picture(enemy, name)
    picture = SPR.pixel(name, PIXEL_SCALE) if name else None
    if picture is not None and getattr(enemy, "face_left", False) and not _stands(enemy):
        picture = SPR.flipped(picture)
    return picture


def _stands(enemy):
    """(23.11, Filip) An enemy that never walks (a factory, a generator, a crate, a machine) doesn't turn round."""
    return getattr(enemy, "og_speed", getattr(enemy, "speed", 1)) == 0


def _jump_picture(enemy, name):
    """(21.11) A jumper shows <name>_jump (crouching, just before and after it takes off), then <name>_fly (in the
    air) - each only if drawn; standing = its normal picture."""
    pose = getattr(enemy, "jump_pose", lambda: None)()
    if name and pose and SPR.load(f"{name}_{pose}") is not None:
        return f"{name}_{pose}"
    return name


# (23.11) Optional enemy poses (each only if drawn; a jumper's _jump / _fly come first):
#   <name>_spin1, _spin2 .. in a loop (ENEMY_SPIN_FRAMES each) while an attack of it lasts (a sprinkler, a burst)
#   <name>_aim              while it aims a telegraphed shot (the line before an Ice Shooter's bolt)
#   <name>_shoot            for ENEMY_SHOOT_FRAMES after it fired
#   <name>_walk1, _walk2 .. while it moves, a step every ENEMY_STEP_PX px walked (as many steps as drawn)
#   <name>_idle1, _idle2 .. otherwise, in a loop all the time (ENEMY_IDLE_FRAMES each; e.g. a burning fuse)
ENEMY_SHOOT_FRAMES = 12
ENEMY_SPIN_FRAMES = 5
ENEMY_IDLE_FRAMES = 6
ENEMY_STEP_PX = 24               # (23.11, Filip: 14 was too quick)
ENEMY_MOVING_PX = 0.3            # px per frame: moving less than this = standing (its normal picture)


def _action_picture(enemy, name):
    if not name:
        return name
    spins = _spin_count(name)
    if spins and any(info.get("is_bursting") for info in getattr(enemy, "attacks", {}).values()
                     if isinstance(info, dict)):
        return f"{name}_spin{int(getattr(enemy, 'attack_timer', 0) // ENEMY_SPIN_FRAMES) % spins + 1}"
    if getattr(enemy, "aiming", None) and SPR.load(f"{name}_aim") is not None:
        return f"{name}_aim"
    if getattr(enemy, "attack_timer", 0) - getattr(enemy, "shot_at", -10 ** 9) < ENEMY_SHOOT_FRAMES \
            and SPR.load(f"{name}_shoot") is not None:
        return f"{name}_shoot"
    moved = _walked(enemy)
    steps = _pose_count(name, "walk") if moved else 0
    if steps:
        return f"{name}_walk{int(enemy.walk_px // ENEMY_STEP_PX) % steps + 1}"
    idles = _pose_count(name, "idle")
    if idles:
        return f"{name}_idle{int(getattr(enemy, 'attack_timer', 0) // ENEMY_IDLE_FRAMES) % idles + 1}"
    return name


def _spin_count(name):
    """How many _spin pictures in a row the enemy has (0 = none)."""
    return _pose_count(name, "spin")


def _pose_count(name, pose):
    """How many <name>_<pose>1, 2 ... pictures in a row there are (0 = none)."""
    k = 0
    while SPR.load(f"{name}_{pose}{k + 1}") is not None:
        k += 1
    return k


def _walked(enemy):
    """Did the enemy move since it was last drawn? (adds the distance to enemy.walk_px for the steps)"""
    last = getattr(enemy, "drawn_at", None)
    enemy.drawn_at = (enemy.x, enemy.y)
    if last is None:
        enemy.walk_px = 0.0
        return False
    d = math.dist(last, enemy.drawn_at)
    enemy.walk_px = getattr(enemy, "walk_px", 0.0) + d
    return d >= ENEMY_MOVING_PX


CENTRED = {"pixie", "rainbow_pixie"}   # (23.11) floaters drawn round their middle (the ball = the hitbox)


def draw_enemy(screen, enemy):
    """False = no picture (draw the old circle / box)."""
    picture = enemy_picture(enemy)
    if picture is None:
        return False
    if getattr(enemy, "shape", "") == "square" or enemy.name in CENTRED:   # machines, crates, floaters: centred
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
def obstacle_picture(theme, rect, variant=None, frame=1, used=None):
    """A room obstacle (pillar or wall) of this biome at this size: (picture, top-left offset) or None.
    variant: which pillar variant (0 = the first file found); None = picked by the obstacle's spot.
    frame: (23.11) which animation frame (a piece with <name>_frame<k> uses it; others stay as they are);
    used: a list that gets the names of the pieces used."""
    used = [] if used is None else used
    w, h = rect.size
    if max(w, h) / max(1, min(w, h)) < PILLAR_SHAPE:
        picture = _pillar(theme, rect, variant, frame, used)
    elif w >= h:
        picture = _strip(theme, "wall_thick_h" if h > THICK_WALL else "wall_h", w, frame, used)
    else:
        picture = _vertical_wall(theme, w, h, frame, used)
    if picture is None:
        return None
    return picture, ((w - picture.get_width()) // 2, h - picture.get_height())


# (23.11) ANIMATED obstacles (the Void's galaxies): a piece may have frames <name>_frame2, <name>_frame3, ... - the
# game shows them in a loop (rooms.OBSTACLE_FRAME_MS each). Draw them with the same solid pixels in every frame: the
# collision mask comes from frame 1.
MAX_FRAMES = 9


def obstacle_frames(theme, rect, variant=None):
    """All animation frames of an obstacle: [(picture, offset), ...] - one item when nothing is animated; None
    when it has no sprite."""
    used = []
    first = obstacle_picture(theme, rect, variant, 1, used)
    if first is None:
        return None
    frames = [first]
    for k in range(2, MAX_FRAMES + 1):
        if not any(SPR.load(f"{name}_frame{k}") is not None for name in used):
            break
        frames.append(obstacle_picture(theme, rect, variant, k))
    return frames


def _piece(name, frame, used):
    """A piece at ART_SCALE in this animation frame (its _frame<k> file if there is one) - or None."""
    used.append(name)
    if frame > 1 and SPR.load(f"{name}_frame{frame}") is not None:
        name = f"{name}_frame{frame}"
    return SPR.pixel(name, ART_SCALE)


def pillar_size(w, h):
    """The pillar file's size label ("small" / "medium" / "large") for an obstacle of this size (px)."""
    return next(label for limit, label in PILLAR_SIZES if max(w, h) < limit)


def pillar_variants(theme, size):
    """The pillar's variant files (names) of this biome and size label."""
    return SPR.variants(f"{OBSTACLE_FOLDER}/{theme}_pillar_{size}")


def _pillar(theme, rect, variant=None, frame=1, used=None):
    # (23.11) The variant was picked by the pillar's SIZE (SPR.pick(names, w, h)): a square pillar (w == h) always
    # gave an even number, so with 2 variants it was always the first. Now: by its spot, well mixed (or given).
    names = pillar_variants(theme, pillar_size(*rect.size))
    if not names:
        return None
    if variant is None:
        variant = random.Random(f"{rect.x},{rect.y},{rect.w},{rect.h}").randrange(len(names))
    return _piece(names[variant % len(names)], frame, [] if used is None else used)


def _vertical_wall(theme, w, h, frame=1, used=None):
    """A thick vertical wall uses its own pieces (_wall_thick_v) if drawn, else the thin ones."""
    kinds = ["wall_thick_v", "wall_v"] if w > THICK_WALL else ["wall_v"]
    used = [] if used is None else used
    return next((p for p in (_column(theme, kind, h, frame, used) for kind in kinds) if p), None)


def _strip(theme, kind, length, frame=1, used=None):
    """A horizontal wall `length` px long: end, middle, middle, ..., mirrored end - whole pieces at ART_SCALE, the
    last middle cut. The middles may have variants (<kind>_2, ...). None = no middle drawn."""
    used = [] if used is None else used
    middles = SPR.variants(f"{OBSTACLE_FOLDER}/{theme}_{kind}")
    if not middles:
        return None
    cap = _piece(f"{OBSTACLE_FOLDER}/{theme}_{kind}_end", frame, used)
    height = max([SPR.pixel(m, ART_SCALE).get_height() for m in middles] + ([cap.get_height()] if cap else []))
    strip = pygame.Surface((length, height), pygame.SRCALPHA)
    left = cap.get_width() if cap else 0
    _repeat(strip, middles, left, length - left, along_x=True, frame=frame, used=used)
    if cap:
        strip.blit(cap, (0, height - cap.get_height()))
        strip.blit(pygame.transform.flip(cap, True, False), (length - cap.get_width(), height - cap.get_height()))
    return strip


def _column(theme, kind, length, frame=1, used=None):
    """(19.11) A vertical wall `length` px tall: its top piece (<kind>_top), the middle repeated, its bottom piece
    (<kind>_end) - whole pieces at ART_SCALE, the last middle cut. Without a top piece the middle goes up to the
    top. None = no middle drawn."""
    used = [] if used is None else used
    middles = SPR.variants(f"{OBSTACLE_FOLDER}/{theme}_{kind}")
    if not middles:
        return None
    top = _piece(f"{OBSTACLE_FOLDER}/{theme}_{kind}_top", frame, used)
    bottom = _piece(f"{OBSTACLE_FOLDER}/{theme}_{kind}_end", frame, used)
    width = max(SPR.pixel(m, ART_SCALE).get_width() for m in middles)
    column = pygame.Surface((width, length), pygame.SRCALPHA)
    first = top.get_height() if top else 0
    _repeat(column, middles, first, length - (bottom.get_height() if bottom else 0), along_x=False, frame=frame,
            used=used)
    if top:
        column.blit(top, ((width - top.get_width()) // 2, 0))
    if bottom:
        column.blit(bottom, ((width - bottom.get_width()) // 2, length - bottom.get_height()))
    return column


def _repeat(surface, names, start, stop, along_x, frame=1, used=None):
    """The middle pieces one after another from `start` to `stop` (px along the wall), the last one cut; a piece
    narrower than the wall is centred across it (a vertical wall) or stands on its bottom (a horizontal one)."""
    at, piece = start, 0
    while at < stop:
        mid = _piece(SPR.pick(names, piece, stop), frame, [] if used is None else used)
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


def object_pixel(name, flip=False):
    """(23.11) A fight object (combat/objects/<name>) at ART_SCALE, hard pixels (flip = mirrored); None if not drawn."""
    picture = SPR.pixel(f"{OBJECT_FOLDER}/{name}", ART_SCALE)
    if picture is None or not flip:
        return picture
    return SPR.flipped(picture)


def object_picture(name, size, flip=False):
    """A fight object (combat/objects/<name>) at exactly this size, hard pixels; None if not drawn."""
    return SPR.to_size(f"{OBJECT_FOLDER}/{name}", size, smooth=False, flip_x=flip)


def clear():
    _floors.clear()
    _objects.clear()
