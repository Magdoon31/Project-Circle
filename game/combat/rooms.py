# FIGHT ROOMS (8.11): bigger rooms for bigger fights + rare obstacles (like the rooms in Enter the Gungeon).
#
# - Size: up to 3 enemies the room is the screen. Every enemy above 3 adds ROOM_GROW of the area (max ROOM_MAX);
#   the room gets a random shape (wider or taller), the camera follows the player (Combat).
# - Obstacles (8.11 v2): in many normal fights (OBSTACLE_CHANCE per biome - more in the later biomes), always
#   SYMMETRIC (mirrored left-right, up-down, both, or turned round the middle) - except the loose pillars (19.11,
#   Filip: small and medium ones stand at random spots, each its own size). Mostly small (LAYOUTS weights):
#     center    one pillar in the middle of the room (you start next to it)
#     pair      2-3 loose pillars, or 2 short walls mirrored
#     quad      3-5 loose pillars
#     walls     2 or 4 long walls, mirrored
#     room      a small room in the middle (doors on opposite sides) - you start inside
#     corridor  two parallel walls round the middle line, gaps mirrored - you start in it
#   + (23.11) a room with walls (walls / room / corridor) sometimes gets 1-3 loose pillars too (PILLARS_WITH_WALLS)
#   + (until 11.11) sometimes covers: pairs of crates that break from your shots (COVER_HITS) - off now (COVER_CHANCE 0).
#   Walls and pillars can't be broken; they stop you, the enemies and all bullets (thrown bombs fly over).
#   The look depends on the biome (THEMES): hedges in the village, candy in the grove, ice rocks in the tundra...
# - Bosses: never (they have their own arenas). You start in the middle, or next to it if a pillar is there.
#
# A wall is the same dict as the Frost Golem's ice walls: {"rect", "hits", "max", "life"} + "solid" (can't break,
# doesn't melt) / "cover" (a crate) and "theme" (the biome, for drawing).

import math
import random

import pygame

from game.combat import sprites as FIGHT_SPRITES

ROOM_GROW = 0.15              # + area per enemy above ROOM_FREE
ROOM_FREE = 3                 # this many enemies still fit on the screen
ROOM_MAX = 2.0                # the biggest room = 2x the screen's area
START_CLEAR = 110             # px around your start without obstacles
GAP = 170                     # px of free space kept between obstacles (you always fit through)
COVER_HITS = 6                # shots to break a crate
COVER_CHANCE = 0.0            # an obstacle room also gets (a mirrored pair of) crates - (11.11) none any more (Filip)
FOREVER = 10 ** 9
PAIR_PILLARS = 0.6            # "pair": how often it is loose pillars (else 2 mirrored short walls)
SCATTER = {"pair": (2, 3), "quad": (3, 5)}      # (19.11) how many loose pillars (fewest, most)
LOOSE_PILLAR = (70, 129)      # (19.11) px: a loose pillar's size - small (under 100) or medium (sprites.PILLAR_SIZES)
SCATTER_TRIES = 60            # tries to find a free spot for one loose pillar
SOLID_ALPHA = 128             # (23.11) a sprite pixel this opaque or more is solid (the half-transparent shadow isn't)
OBSTACLE_FRAME_MS = 300       # (23.11) ms per frame of an animated obstacle (sprites.obstacle_frames)
PUSH_STEPS = 8                # (23.11) halvings when finding how far to push a body out of a sprite's pixels

OBSTACLE_CHANCE = {          # (23.11, Filip) more everywhere (+0.15 in all); the garden and the core: nearly always
    "village": 0.40, "lunapark": 0.45, "rainbow_fields": 0.45, "sugarwood_grove": 0.50,
    "toy_factory": 0.55, "silverpine_tundra": 0.55, "underground_garden": 0.85, "the_core": 0.90, "the_void": 0.70,
}
LAYOUTS = {"center": 5, "pair": 5, "quad": 3, "walls": 2, "room": 1, "corridor": 1}      # weights: mostly small
BIOME_LAYOUTS = {            # (23.11) biomes with their own weights (else LAYOUTS): the garden - mostly walls (roots)
    "underground_garden": {"center": 2, "pair": 4, "quad": 2, "walls": 6, "room": 1, "corridor": 2},
}
THIN_WALL = (40, 50)          # px: a wall's thickness - thin (drawn with <biom>_wall_h / _wall_v) ...
THICK_SIZE = (80, 95)         # (23.11) ... or thick (over sprites.THICK_WALL: <biom>_wall_thick_h / _thick_v)
THICK_CHANCE = {"underground_garden": 0.5, "the_void": 0.5}   # (23.11) how often a wall is thick (the Void: a galaxy)
DEFAULT_THICK = 0.15
PILLARS_WITH_WALLS = 0.4      # (23.11, Filip) a room with walls also gets a few loose pillars this often ...
EXTRA_PILLARS = (1, 3)        # ... this many (fewest, most) - each still GAP away from everything
MIRRORS = ["x", "y", "xy"]    # left-right, up-down, turned round the middle (point)

# how the obstacles of a biome look: fill, edge, detail colour, style; crate fill, crate edge
THEMES = {
    "village":            {"fill": (52, 120, 58),  "edge": (30, 80, 36),   "detail": (88, 160, 80),   "style": "hedge",
                           "crate": (165, 120, 70), "crate_edge": (110, 75, 40)},
    "lunapark":           {"fill": (245, 160, 200), "edge": (200, 90, 140), "detail": (255, 255, 255), "style": "stripes",
                           "crate": (110, 180, 240), "crate_edge": (60, 120, 190)},
    "rainbow_fields":     {"fill": (190, 160, 240), "edge": (120, 90, 190), "detail": (255, 255, 255), "style": "crystal",
                           "crate": (240, 200, 120), "crate_edge": (190, 140, 70)},
    "sugarwood_grove":    {"fill": (240, 120, 150), "edge": (180, 60, 90),  "detail": (255, 245, 245), "style": "stripes",
                           "crate": (120, 70, 45),  "crate_edge": (80, 45, 25)},
    "toy_factory":        {"fill": (120, 125, 140), "edge": (70, 72, 85),   "detail": (175, 178, 190), "style": "metal",
                           "crate": (170, 130, 70), "crate_edge": (110, 80, 40)},
    "silverpine_tundra":  {"fill": (175, 205, 230), "edge": (100, 140, 180), "detail": (235, 245, 255), "style": "crystal",
                           "crate": (130, 105, 85), "crate_edge": (85, 65, 50)},
    "underground_garden": {"fill": (70, 82, 78),   "edge": (35, 45, 42),   "detail": (60, 160, 110), "style": "moss",
                           "crate": (95, 70, 120),  "crate_edge": (60, 40, 85)},
    "the_core":           {"fill": (60, 50, 68),   "edge": (25, 18, 30),   "detail": (255, 80, 110), "style": "metal",
                           "crate": (96, 78, 70),   "crate_edge": (55, 42, 38)},
    "the_void":           {"fill": (70, 45, 120),  "edge": (150, 100, 230), "detail": (200, 160, 255), "style": "crystal",
                           "crate": (100, 76, 150), "crate_edge": (175, 140, 235)},
}
DEFAULT_THEME = "village"


def room_size(n_enemies, screen_size, rng=random):
    """(w, h) of the fight room: the screen, or bigger for more than ROOM_FREE enemies."""
    sw, sh = screen_size
    area = min(ROOM_MAX, 1 + ROOM_GROW * max(0, n_enemies - ROOM_FREE))
    if area <= 1:
        return sw, sh
    u = rng.uniform(0.25, 0.75)              # how the extra area is split between the width and the height
    return round(sw * area ** u), round(sh * area ** (1 - u))


def make_obstacles(biome, room, rng=random, chance=None):
    """Obstacles for a normal fight in this biome (often none): (walls, where you start)."""
    w, h = room
    if rng.random() >= (OBSTACLE_CHANCE.get(biome, 0.3) if chance is None else chance):
        return [], (w / 2, h / 2)
    weights = BIOME_LAYOUTS.get(biome, LAYOUTS)
    layout = rng.choices(list(weights), weights=list(weights.values()))[0]
    how = rng.choice(MIRRORS)                                # one symmetry for the whole room
    thick = THICK_CHANCE.get(biome, DEFAULT_THICK)
    rects = LAYOUT_MAKERS[layout](w, h, rng, how, thick)
    if layout in ("walls", "room", "corridor") and rng.random() < PILLARS_WITH_WALLS:
        rects += _scatter(w, h, rng, *EXTRA_PILLARS, placed=rects)       # (23.11) pillars among the walls
    if rects and rng.random() < COVER_CHANCE:
        rects_c = _mirrored(w, h, rng, lambda: _square(w, h, rng, 58, 76), rects, how)
    else:
        rects_c = []
    walls = [_wall(r, biome) for r in rects] + [_wall(r, biome, cover=True) for r in rects_c]
    for wall in walls:
        give_shape(wall)
    return walls, start_spot(w, h, [x["rect"] for x in walls])


def start_spot(w, h, rects):
    """The middle, or the nearest free spot round it (a pillar can stand in the middle)."""
    def free(x, y):
        return all(math.hypot(x - min(max(x, r.left), r.right), y - min(max(y, r.top), r.bottom)) >= START_CLEAR
                   for r in rects)
    if free(w / 2, h / 2):
        return w / 2, h / 2
    for dist in range(120, 700, 40):
        for k in range(16):
            a = math.pi + k * math.tau / 16                  # left of the middle first
            x, y = w / 2 + math.cos(a) * dist, h / 2 + math.sin(a) * dist
            if 100 < x < w - 100 and 100 < y < h - 100 and free(x, y):
                return x, y
    return w / 2, h / 2


def _wall(rect, biome, cover=False):
    theme = biome if biome in THEMES else DEFAULT_THEME
    if cover:
        return {"rect": rect, "hits": COVER_HITS, "max": COVER_HITS, "life": FOREVER, "cover": True, "theme": theme}
    return {"rect": rect, "hits": FOREVER, "max": 0, "life": FOREVER, "solid": True, "theme": theme}


# --- (23.11) collision with the drawn pixels ----------------------------------------------------------------------
# An obstacle with a sprite is solid only where its picture is (pygame mask): bullets stop at its pixels, round bodies
# (you, the enemies) slide round its outline. Its "rect" shrinks to the box round those pixels - the enemies' path
# finding and line of sight still use that box. Without a sprite (or an ice wall) the rect itself is solid, as before.
def give_shape(wall):
    """Gives a room obstacle its sprite's solid pixels: wall["mask"] at wall["mask_at"] (top-left, room px)."""
    if wall.get("cover"):
        return
    frames = FIGHT_SPRITES.obstacle_frames(wall["theme"], wall["rect"], wall.get("variant"))
    if not frames:
        return
    picture, (ox, oy) = frames[0]
    if len(frames) > 1:                                       # (23.11) animated (the Void's galaxies)
        wall["frames"] = [p for p, _ in frames]
    mask = pygame.mask.from_surface(picture, SOLID_ALPHA - 1)
    boxes = mask.get_bounding_rects()
    if not boxes:
        return
    box = boxes[0].unionall(boxes[1:])
    art_x, art_y = wall["rect"].x + ox, wall["rect"].y + oy
    wall["rect"] = pygame.Rect(art_x + box.x, art_y + box.y, box.w, box.h)
    wall.update(mask=mask, mask_at=(art_x, art_y), img=picture, img_hits=wall["hits"],
                img_offset=(art_x - wall["rect"].x, art_y - wall["rect"].y))   # drawn where it was


def solid_at(wall, x, y):
    """Is this room point inside the obstacle (its pixels, or its rect without a sprite)?"""
    if not wall["rect"].collidepoint(x, y):
        return False
    mask = wall.get("mask")
    if mask is None:
        return True
    mx, my = wall["mask_at"]
    return bool(mask.get_at((int(x - mx), int(y - my))))


_circles = {}


def _circle_mask(radius):
    r = max(1, int(radius))
    if r not in _circles:
        surf = pygame.Surface((2 * r + 1, 2 * r + 1), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, 255), (r, r), r)
        _circles[r] = pygame.mask.from_surface(surf)
    return _circles[r]


def touches(wall, x, y, radius):
    """(23.11) Does a round body at (x, y) touch the obstacle (its pixels, or its rect without a sprite)?"""
    r = max(1, int(radius))
    rect = wall["rect"]
    if not rect.colliderect(pygame.Rect(x - r, y - r, 2 * r + 1, 2 * r + 1)):
        return False
    mask = wall.get("mask")
    if mask is None:
        nx, ny = min(max(x, rect.left), rect.right), min(max(y, rect.top), rect.bottom)
        return math.hypot(x - nx, y - ny) < r
    mx, my = wall["mask_at"]
    return mask.overlap(_circle_mask(r), (int(round(x - r - mx)), int(round(y - r - my)))) is not None


def push_out(wall, x, y, radius):
    """Where a round body at (x, y) must move to stop touching the obstacle's pixels; None = it doesn't touch them.
    It goes away from the middle of the touching part, just as far as needed (found by halving)."""
    r = max(1, int(radius))
    if not wall["rect"].colliderect(pygame.Rect(x - r, y - r, 2 * r + 1, 2 * r + 1)):
        return None
    mask, (mx, my), circle = wall["mask"], wall["mask_at"], _circle_mask(r)

    def touches(px, py):
        return mask.overlap(circle, (int(round(px - r - mx)), int(round(py - r - my)))) is not None
    if not touches(x, y):
        return None
    cx, cy = mask.overlap_mask(circle, (int(round(x - r - mx)), int(round(y - r - my)))).centroid()
    dx, dy = x - (mx + cx), y - (my + cy)
    d = math.hypot(dx, dy)
    ux, uy = (dx / d, dy / d) if d > 1e-6 else (0.0, -1.0)
    lo, hi = 0.0, 2.0 * r
    while touches(x + ux * hi, y + uy * hi) and hi < 4 * r + max(mask.get_size()):
        lo, hi = hi, hi * 2
    for _ in range(PUSH_STEPS):
        mid = (lo + hi) / 2
        if touches(x + ux * mid, y + uy * mid):
            lo = mid
        else:
            hi = mid
    return x + ux * hi, y + uy * hi


def _mirror(r, w, h, how):
    x = w - r.right if "x" in how else r.x
    y = h - r.bottom if "y" in how else r.y
    return pygame.Rect(round(x), round(y), r.w, r.h)


def _inside(r, w, h):
    return r.left >= 90 and r.top >= 90 and r.right <= w - 90 and r.bottom <= h - 90


def _apart(rects, placed, gap=GAP):
    return not any(r.inflate(gap * 2, gap * 2).colliderect(o) for r in rects for o in placed) and \
        all(not a.inflate(gap * 2, gap * 2).colliderect(b) for i, a in enumerate(rects) for b in rects[i + 1:])


def _mirrored(w, h, rng, make, placed=(), hows=None):
    """One piece + its mirror copies (2 pieces, or 4 for "quad"), apart from each other and from `placed`."""
    for _try in range(80):
        r = make()
        how = rng.choice(MIRRORS) if hows is None else hows
        group = [r] + ([_mirror(r, w, h, m) for m in ("x", "y", "xy")] if how == "quad" else [_mirror(r, w, h, how)])
        if all(_inside(g, w, h) for g in group) and _apart(group, placed):
            return group
    return []


def _square(w, h, rng, lo, hi):
    s = rng.randint(lo, hi)
    return pygame.Rect(rng.randint(90, w - 90 - s), rng.randint(90, h - 90 - s), s, s)


def _thickness(rng, thick):
    """(23.11) A wall's thickness: thick with the chance `thick`, else thin."""
    return rng.randint(*THICK_SIZE) if rng.random() < thick else rng.randint(*THIN_WALL)


def _center(w, h, rng, how, thick=0):
    s = rng.randint(90, 150)
    if rng.random() < 0.3:                                    # sometimes a short thick wall instead of a square
        ww, hh = (s * 2, s // 2 + 10) if rng.random() < 0.5 else (s // 2 + 10, s * 2)
    else:
        ww = hh = s
    return [pygame.Rect(round(w / 2 - ww / 2), round(h / 2 - hh / 2), ww, hh)]


def _pair(w, h, rng, how, thick=0):
    if rng.random() < PAIR_PILLARS:
        return _scatter(w, h, rng, *SCATTER["pair"])
    t = _thickness(rng, thick)                                # both walls of the pair alike
    def one():
        long = rng.randint(180, 320)
        ww, hh = (long, t) if rng.random() < 0.5 else (t, long)
        return pygame.Rect(rng.randint(90, max(91, w - 90 - ww)), rng.randint(90, max(91, h - 90 - hh)), ww, hh)
    return _mirrored(w, h, rng, one, hows=how)


def _quad(w, h, rng, how, thick=0):
    return _scatter(w, h, rng, *SCATTER["quad"])


def _scatter(w, h, rng, fewest, most, placed=()):
    """(19.11, Filip) Loose pillars: each at a random spot with its own random size (small / medium), not mirrored;
    still GAP apart, so you always fit between them. A pillar with no free spot is left out."""
    others, new = list(placed), []                            # (23.11) placed: obstacles already in the room
    for _pillar in range(rng.randint(fewest, most)):
        for _try in range(SCATTER_TRIES):
            r = _square(w, h, rng, *LOOSE_PILLAR)
            if _apart([r], others + new):
                new.append(r)
                break
    return new


def _walls(w, h, rng, how, thick=0):
    def one():
        long, t = rng.randint(260, 480), _thickness(rng, thick)
        ww, hh = (long, t) if rng.random() < 0.5 else (t, long)
        return pygame.Rect(rng.randint(90, max(91, w - 90 - ww)), rng.randint(90, max(91, h - 90 - hh)), ww, hh)
    return _mirrored(w, h, rng, one, hows=how)


def _inner_room(w, h, rng, how, thick=0):
    """A small room in the middle: 4 walls; doors in the middle of 2 opposite sides (or all 4)."""
    t = THICK_SIZE[0] if rng.random() < thick else 40           # (23.11) sometimes thick walls
    rw, rh = rng.randint(480, 640), rng.randint(380, 460)
    x, y = round(w / 2 - rw / 2), round(h / 2 - rh / 2)
    doors = rng.choice([("left", "right"), ("top", "bottom"), ("top", "bottom", "left", "right")])
    out = []
    door = 170
    for side in ("top", "bottom", "left", "right"):
        horizontal = side in ("top", "bottom")
        if horizontal:
            sx, sy, length = x, (y if side == "top" else y + rh - t), rw
        else:
            sx, sy, length = (x if side == "left" else x + rw - t), y + t, rh - 2 * t
        pieces = [(0, length)]
        if side in doors:
            at = (length - door) // 2
            gap = length - 2 * at                      # the same size on both sides of the door
            pieces = [(0, at), (at + gap, at)]
        for off, size in pieces:
            out.append(pygame.Rect(sx + off, sy, size, t) if horizontal else pygame.Rect(sx, sy + off, t, size))
    return out


def _corridor(w, h, rng, how, thick=0):
    """Two long walls, mirrored round the middle line; their gaps mirrored too. You start in the corridor."""
    t, width = (THICK_SIZE[0] if rng.random() < thick else 42), rng.randint(240, 290)      # (23.11) or thick
    horizontal = rng.random() < 0.5
    L = (w if horizontal else h)
    length = int(L * rng.uniform(0.5, 0.7))
    start = (L - length) // 2
    gap = rng.randint(150, 190)
    at = rng.randint(80, max(81, length // 2 - gap - 40))      # a gap in the first half, mirrored in the second
    pieces = [(0, at), (at + gap, length - 2 * (at + gap)), (length - at, at)]
    out = []
    for k in (-1, 1):
        mid = (h if horizontal else w) / 2
        pos = round(mid - width / 2 - t) if k < 0 else round(mid + width / 2)
        for off, size in pieces:
            if size > 20:
                out.append(pygame.Rect(start + off, pos, size, t) if horizontal else pygame.Rect(pos, start + off, t, size))
    return out


LAYOUT_MAKERS = {"center": _center, "pair": _pair, "quad": _quad, "walls": _walls, "room": _inner_room,
                 "corridor": _corridor}


def draw_obstacle(screen, wall):
    """A wall / pillar / crate in its biome's look (drawn once into a picture, then just blitted)."""
    img = wall.get("img")
    hits = wall["hits"]
    if img is None or wall.get("img_hits") != hits:
        drawn = None if wall.get("cover") else FIGHT_SPRITES.obstacle_picture(wall["theme"], wall["rect"], wall.get("variant"))   # (13.11)
        img, wall["img_offset"] = drawn or (_render(wall), (0, 0))
        wall["img"] = img
        wall["img_hits"] = hits
    frames = wall.get("frames")
    if frames:                                                # (23.11) an animated obstacle: its frames in a loop
        img = frames[pygame.time.get_ticks() // OBSTACLE_FRAME_MS % len(frames)]
    offset = wall.get("img_offset", (0, 0))
    screen.blit(img, (wall["rect"].x + offset[0], wall["rect"].y + offset[1]))


def _render(wall):
    r = wall["rect"]
    th = THEMES[wall["theme"]]
    surf = pygame.Surface(r.size, pygame.SRCALPHA)
    box = surf.get_rect()
    rnd = random.Random(r.x * 7919 + r.y * 104729 + r.w)       # the same details every frame
    if wall.get("cover"):
        pygame.draw.rect(surf, th["crate"], box, 0, 6)
        pygame.draw.rect(surf, th["crate_edge"], box, 4, 6)
        pygame.draw.line(surf, th["crate_edge"], (6, 6), (box.w - 7, box.h - 7), 4)
        pygame.draw.line(surf, th["crate_edge"], (box.w - 7, 6), (6, box.h - 7), 4)
        broken = wall["max"] - wall["hits"]                      # cracks the more you hit it
        for i in range(max(0, broken)):
            x0 = rnd.randint(4, box.w - 4)
            pygame.draw.line(surf, (40, 30, 25), (x0, 4), (x0 + rnd.randint(-14, 14), box.h // 2 + rnd.randint(-8, 8)), 2)
        return surf
    style = th["style"]
    radius = 14 if style in ("hedge", "moss") else 6
    pygame.draw.rect(surf, th["fill"], box, 0, radius)
    if style == "hedge":                      # leafy bumps
        for _ in range(max(3, box.w * box.h // 900)):
            pygame.draw.circle(surf, th["detail"], (rnd.randint(8, box.w - 8), rnd.randint(8, box.h - 8)), rnd.randint(4, 8))
    elif style == "stripes":                  # candy stripes
        for x in range(-box.h, box.w, 28):
            pygame.draw.line(surf, th["detail"], (x, box.h), (x + box.h, 0), 9)
    elif style == "crystal":                  # facets + a shine
        for _ in range(max(2, (box.w + box.h) // 90)):
            x = rnd.randint(0, box.w)
            pygame.draw.line(surf, th["detail"], (x, 0), (x + rnd.randint(-30, 30), box.h), 2)
        pygame.draw.line(surf, (255, 255, 255), (6, 8), (min(box.w - 6, 40), 8), 3)
    elif style == "metal":                    # plates + rivets
        step = 60
        for x in range(step, box.w, step):
            pygame.draw.line(surf, th["edge"], (x, 3), (x, box.h - 3), 2)
        for y in range(step, box.h, step):
            pygame.draw.line(surf, th["edge"], (3, y), (box.w - 3, y), 2)
        for cx, cy in ((8, 8), (box.w - 9, 8), (8, box.h - 9), (box.w - 9, box.h - 9)):
            pygame.draw.circle(surf, th["detail"], (cx, cy), 3)
    elif style == "moss":                     # moss patches
        for _ in range(max(2, box.w * box.h // 1500)):
            pygame.draw.ellipse(surf, th["detail"], (rnd.randint(0, box.w - 16), rnd.randint(0, box.h - 10), rnd.randint(14, 30), rnd.randint(8, 14)))
    pygame.draw.rect(surf, th["edge"], box, 4, radius)
    return surf


# --- TEST ROOM (23.11, test only: key T on the map) --------------------------------------------------------------
# One obstacle of every kind of the biome (3 pillar sizes - each in all its variants, 23.11 -, thin / thick walls
# lying and standing) along the top and the left of a bigger room; the enemies stand on a grid in the rest of it.
TEST_ROOM = 1.6               # the test room = the screen x this (width and height)
TEST_BASE = (3072, 1728)      # the room TEST_OBSTACLES are placed for (1080p x TEST_ROOM); other sizes: moved, not resized
TEST_OBSTACLES = [            # (x, y, w, h) px from the room's top-left corner
    (1150, 220, 380, 45), (1750, 200, 320, 80),                            # thin and thick wall, lying
    (300, 800, 45, 360), (620, 800, 80, 320),                              # thin and thick wall, standing (23.11: lower)
]
TEST_PILLARS = [              # (23.11) (x, y, size, px down to the next variant): every variant of each pillar size,
    (300, 200, 85, 160), (540, 185, 115, 170), (810, 170, 140, 180),       # one under another: small, medium, large
]
TEST_VARIANTS = 3             # (23.11) the most variants of one pillar size shown (more would reach the walls)
TEST_GRID = 220               # px between the enemies' spots (in TEST_BASE; smaller rooms: closer, at least TEST_GRID_MIN)
TEST_GRID_MIN = 140
TEST_KEEP_OFF = 180           # px an enemy's spot keeps from the obstacles and from where you start


def test_room_size(screen_size):
    return round(screen_size[0] * TEST_ROOM), round(screen_size[1] * TEST_ROOM)


def test_obstacles(biome, room):
    """Every obstacle kind of the biome once: (walls, where you start = the middle)."""
    kx, ky = room[0] / TEST_BASE[0], room[1] / TEST_BASE[1]
    walls = [_wall(pygame.Rect(round(x * kx), round(y * ky), w, h), biome) for x, y, w, h in TEST_OBSTACLES]
    for x, y, size, step in TEST_PILLARS:                    # (23.11) every pillar variant
        theme = _wall(pygame.Rect(0, 0, size, size), biome)["theme"]
        found = len(FIGHT_SPRITES.pillar_variants(theme, FIGHT_SPRITES.pillar_size(size, size)))
        for variant in range(max(1, min(found, TEST_VARIANTS))):
            pillar = _wall(pygame.Rect(round(x * kx), round((y + variant * step) * ky), size, size), biome)
            pillar["variant"] = variant
            walls.append(pillar)
    for wall in walls:
        give_shape(wall)
    return walls, (room[0] / 2, room[1] / 2)


def test_spots(n, room, walls, start):
    """n spots for the enemies on a grid, away from the obstacles, from you and from the room's edges."""
    w, h = room
    step = max(TEST_GRID_MIN, round(TEST_GRID * w / TEST_BASE[0]))
    def free(x, y):
        return math.dist((x, y), start) >= TEST_KEEP_OFF and \
            not any(wall["rect"].inflate(TEST_KEEP_OFF, TEST_KEEP_OFF).collidepoint(x, y) for wall in walls)
    spots = [(x, y) for y in range(step, h - step // 2, step)
             for x in range(step, w - step // 2, step) if free(x, y)]
    spots.sort(key=lambda p: math.dist(p, start))          # the nearest first: you see them all soon
    return spots[:n]
