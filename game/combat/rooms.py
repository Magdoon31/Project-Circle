# FIGHT ROOMS (8.11): bigger rooms for bigger fights + rare obstacles (like the rooms in Enter the Gungeon).
#
# - Size: up to 3 enemies the room is the screen. Every enemy above 3 adds ROOM_GROW of the area (max ROOM_MAX);
#   the room gets a random shape (wider or taller), the camera follows the player (Combat).
# - Obstacles (8.11 v2): in many normal fights (OBSTACLE_CHANCE per biome - more in the later biomes), always
#   SYMMETRIC (mirrored left-right, up-down, both, or turned round the middle). Mostly small (LAYOUTS weights):
#     center    one pillar in the middle of the room (you start next to it)
#     pair      2 pillars / short walls, mirrored
#     quad      4 pillars, one in each quarter
#     walls     2 or 4 long walls, mirrored
#     room      a small room in the middle (doors on opposite sides) - you start inside
#     corridor  two parallel walls round the middle line, gaps mirrored - you start in it
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

ROOM_GROW = 0.15              # + area per enemy above ROOM_FREE
ROOM_FREE = 3                 # this many enemies still fit on the screen
ROOM_MAX = 2.0                # the biggest room = 2x the screen's area
START_CLEAR = 110             # px around your start without obstacles
GAP = 170                     # px of free space kept between obstacles (you always fit through)
COVER_HITS = 6                # shots to break a crate
COVER_CHANCE = 0.0            # an obstacle room also gets (a mirrored pair of) crates - (11.11) none any more (Filip)
FOREVER = 10 ** 9

OBSTACLE_CHANCE = {
    "village": 0.25, "lunapark": 0.30, "rainbow_fields": 0.30, "sugarwood_grove": 0.35,
    "toy_factory": 0.40, "silverpine_tundra": 0.40, "underground_garden": 0.45, "the_core": 0.50, "the_void": 0.55,
}
LAYOUTS = {"center": 5, "pair": 5, "quad": 3, "walls": 2, "room": 1, "corridor": 1}      # weights: mostly small
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
    layout = rng.choices(list(LAYOUTS), weights=list(LAYOUTS.values()))[0]
    how = rng.choice(MIRRORS)                                # one symmetry for the whole room
    rects = LAYOUT_MAKERS[layout](w, h, rng, how)
    if rects and rng.random() < COVER_CHANCE:
        rects_c = _mirrored(w, h, rng, lambda: _square(w, h, rng, 58, 76), rects, how)
    else:
        rects_c = []
    walls = [_wall(r, biome) for r in rects] + [_wall(r, biome, cover=True) for r in rects_c]
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


def _center(w, h, rng, how):
    s = rng.randint(90, 150)
    if rng.random() < 0.3:                                    # sometimes a short thick wall instead of a square
        ww, hh = (s * 2, s // 2 + 10) if rng.random() < 0.5 else (s // 2 + 10, s * 2)
    else:
        ww = hh = s
    return [pygame.Rect(round(w / 2 - ww / 2), round(h / 2 - hh / 2), ww, hh)]


def _pair(w, h, rng, how):
    def one():
        if rng.random() < 0.6:
            return _square(w, h, rng, 70, 130)
        long, thick = rng.randint(180, 320), rng.randint(40, 50)
        ww, hh = (long, thick) if rng.random() < 0.5 else (thick, long)
        return pygame.Rect(rng.randint(90, max(91, w - 90 - ww)), rng.randint(90, max(91, h - 90 - hh)), ww, hh)
    return _mirrored(w, h, rng, one, hows=how)


def _quad(w, h, rng, how):
    return _mirrored(w, h, rng, lambda: _square(w, h, rng, 70, 120), hows="quad")


def _walls(w, h, rng, how):
    def one():
        long, thick = rng.randint(260, 480), rng.randint(40, 50)
        ww, hh = (long, thick) if rng.random() < 0.5 else (thick, long)
        return pygame.Rect(rng.randint(90, max(91, w - 90 - ww)), rng.randint(90, max(91, h - 90 - hh)), ww, hh)
    return _mirrored(w, h, rng, one, hows=how)


def _inner_room(w, h, rng, how):
    """A small room in the middle: 4 walls; doors in the middle of 2 opposite sides (or all 4)."""
    t = 40
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


def _corridor(w, h, rng, how):
    """Two long walls, mirrored round the middle line; their gaps mirrored too. You start in the corridor."""
    t, width = 42, rng.randint(240, 290)
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
        img = wall["img"] = _render(wall)
        wall["img_hits"] = hits
    screen.blit(img, wall["rect"].topleft)


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
