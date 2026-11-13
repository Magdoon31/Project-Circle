# ACHIEVEMENT ICONS (12.11, redone 13.11): a badge for every achievement - a dark rounded square, a raised frame in
# its group's colour and a raised symbol in the middle. Everything is drawn 4x bigger and scaled down (smooth
# edges); the relief comes from a soft height map lit from the top left (smooth shading, a small shine, a soft
# shadow). Written to assets/img/menu/achievements/<id>.png; "locked" = the ??? badge of a hidden one.
# Run from the game's folder:  python tools/make_achievement_icons.py [folder]      Needs Pillow and numpy.

import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = "assets/img/menu/achievements"
FONT = "assets/font/Cinzel-Bold.ttf"
SIZE = 192                        # px of the finished icon (the game scales it)
SS = 4                            # drawn this many times bigger, then scaled down
BIG = SIZE * SS
LIGHT = np.array([-0.45, -0.75, 0.65])          # from the top left, a little in front
LIGHT = LIGHT / np.linalg.norm(LIGHT)
OUTLINE = (24, 10, 36)

# group -> (the metal: top -> bottom of the symbol, the badge's dark body: top -> bottom)
GROUPS = {
    "story": ([(255, 250, 230), (232, 214, 240), (168, 132, 206)], [(48, 34, 72), (20, 13, 32)]),
    "world": ([(240, 255, 232), (170, 226, 170), (70, 150, 96)], [(26, 62, 42), (9, 26, 17)]),
    "minigames": ([(240, 248, 255), (164, 198, 246), (72, 112, 200)], [(28, 46, 82), (10, 16, 36)]),
    "combat": ([(255, 238, 228), (238, 150, 150), (172, 52, 74)], [(92, 26, 40), (36, 9, 15)]),
    "nohit": ([(255, 250, 222), (246, 214, 120), (196, 136, 34)], [(86, 60, 20), (30, 19, 5)]),
    "weird": ([(252, 252, 255), (206, 206, 218), (120, 120, 140)], [(54, 54, 62), (20, 20, 26)]),
}


# --- small image tools (float arrays, 0..1) -------------------------------------------------------------------
def blur(a, radius):
    """A gaussian blur (two passes along the axes)."""
    if radius <= 0:
        return a
    x = np.arange(-int(radius * 3), int(radius * 3) + 1)
    k = np.exp(-x * x / (2 * radius * radius))
    k /= k.sum()
    pad = len(x) // 2
    out = np.pad(a, pad, mode="edge")
    out = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 0, out)
    out = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, out)
    return out[pad:-pad, pad:-pad]


def mask_of(draw):
    img = Image.new("L", (BIG, BIG))
    draw(ImageDraw.Draw(img), BIG / 192)
    return np.asarray(img, np.float32) / 255


def grow(mask, px):
    """The mask made px wider all round (soft)."""
    return np.clip(blur(mask, px / 2) * 3, 0, 1)


def vertical(colours, top, bottom):
    """A gradient down the picture from row `top` to `bottom` (BIG x BIG x 3)."""
    t = np.clip((np.arange(BIG) - top) / max(1, bottom - top), 0, 1)
    stops = np.linspace(0, 1, len(colours))
    rows = np.stack([np.interp(t, stops, [c[i] for c in colours]) for i in range(3)], axis=1)
    return np.repeat(rows[:, None, :], BIG, axis=1)


def relief(mask, metal, softness):
    """A raised shape: its colour lit by its own height map (rounded edges, a shine on top)."""
    height = blur(mask, softness) * softness * 1.6
    gy, gx = np.gradient(height)
    normal = np.dstack([-gx, -gy, np.ones_like(gx)])
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    diffuse = np.clip(normal @ LIGHT, 0, 1)
    shine = np.clip(normal @ (LIGHT + np.array([0, 0, 1])) / np.linalg.norm(LIGHT + np.array([0, 0, 1])), 0, 1) ** 40
    rows = np.where(mask.max(axis=1) > 0.5)[0]
    base = vertical(metal, rows[0], rows[-1]) if len(rows) else vertical(metal, 0, BIG)
    colour = base * (0.35 + 0.75 * diffuse[..., None]) + 255 * 0.55 * shine[..., None]
    return np.clip(colour, 0, 255)


# --- putting a picture together (RGBA float, BIG x BIG) -------------------------------------------------------
def over(dst, rgb, alpha):
    a = alpha[..., None]
    dst[..., :3] = rgb * a + dst[..., :3] * (1 - a)
    dst[..., 3] = alpha + dst[..., 3] * (1 - alpha)


def raised(dst, mask, metal, softness, outline=True):
    """A shape with a soft shadow under it, a dark outline round it and its relief."""
    shadow = np.roll(blur(mask, 2.5 * SS), (int(4 * SS), int(2 * SS)), axis=(0, 1)) * 0.6
    over(dst, np.zeros((BIG, BIG, 3)), shadow)
    if outline:
        over(dst, np.full((BIG, BIG, 3), OUTLINE, np.float32), grow(mask, 2.5 * SS))
    over(dst, relief(mask, metal, softness), mask)


def badge(group, draw_symbol):
    metal, body = GROUPS[group]
    pic = np.zeros((BIG, BIG, 4), np.float32)
    plate = mask_of(lambda d, k: d.rounded_rectangle((8 * k, 8 * k, 184 * k, 184 * k), 34 * k, fill=255))
    shading = vertical(body, 0, BIG) * (1 - 0.35 * glow_from_edge(plate))[..., None]
    over(pic, shading, plate)
    ring = mask_of(lambda d, k: d.rounded_rectangle((8 * k, 8 * k, 184 * k, 184 * k), 34 * k,
                                                    outline=255, width=int(9 * k)))
    raised(pic, ring, metal, 3 * SS, outline=False)
    symbol = mask_of(draw_symbol)
    raised(pic, symbol, metal, 5 * SS)
    out = Image.fromarray(np.dstack([pic[..., :3], pic[..., 3] * 255]).astype(np.uint8), "RGBA")
    return out.resize((SIZE, SIZE), Image.LANCZOS)


def glow_from_edge(plate):
    """1 near the plate's edge, 0 in the middle (a soft vignette)."""
    return np.clip(1 - blur(plate, 14 * SS), 0, 1) * plate * 2


# --- the symbols (drawn on a 192 x 192 grid, k = the scale) ----------------------------------------------------
C = 96


def crown(d, k):
    pts = [(46, 140), (38, 70), (70, 100), (96, 56), (122, 100), (154, 70), (146, 140)]
    d.polygon([(x * k, y * k) for x, y in pts], fill=255)
    for x, y in ((38, 64), (96, 50), (154, 64)):
        d.ellipse(((x - 9) * k, (y - 9) * k, (x + 9) * k, (y + 9) * k), fill=255)
    d.rounded_rectangle((44 * k, 132 * k, 148 * k, 152 * k), 5 * k, fill=255)
    for x in (70, 96, 122):
        d.ellipse(((x - 6) * k, 136 * k, (x + 6) * k, 148 * k), fill=0)


def snowflake(d, k):
    for n in range(6):
        a = n * math.pi / 3 - math.pi / 2
        ex, ey = C + math.cos(a) * 62, C + math.sin(a) * 62
        d.line((C * k, C * k, ex * k, ey * k), fill=255, width=int(10 * k))
        d.ellipse(((ex - 6) * k, (ey - 6) * k, (ex + 6) * k, (ey + 6) * k), fill=255)
        for t, length in ((0.5, 22), (0.75, 15)):
            bx, by = C + math.cos(a) * 62 * t, C + math.sin(a) * 62 * t
            for side in (-1, 1):
                b = a + side * math.pi / 3.2
                d.line((bx * k, by * k, (bx + math.cos(b) * length) * k, (by + math.sin(b) * length) * k),
                       fill=255, width=int(8 * k))
    d.regular_polygon((C * k, C * k, 16 * k), 6, rotation=30, fill=255)


def pearl(d, k):
    """A scallop shell (a fan with ribs and a round edge) and a pearl in front of its base."""
    base = (C, 150)
    ribs = 7
    spread = math.radians(130)
    for n in range(ribs):                                     # each rib: a narrow wedge with a round end
        a = -math.pi / 2 - spread / 2 + spread * (n + 0.5) / ribs
        half = spread / ribs / 2 * 0.86
        tip = 74 if n in (0, ribs - 1) else 84
        wedge = [base] + [(base[0] + math.cos(a + t) * tip, base[1] + math.sin(a + t) * tip)
                          for t in np.linspace(-half, half, 12)]
        d.polygon([(x * k, y * k) for x, y in wedge], fill=255)
        ex, ey = base[0] + math.cos(a) * tip, base[1] + math.sin(a) * tip
        r = math.sin(half) * tip
        d.ellipse(((ex - r) * k, (ey - r) * k, (ex + r) * k, (ey + r) * k), fill=255)
    d.ellipse(((C - 27) * k, 121 * k, (C + 27) * k, 175 * k), fill=0)          # a gap round the pearl
    d.ellipse(((C - 22) * k, 126 * k, (C + 22) * k, 170 * k), fill=255)        # the pearl


def wheel(d, k):
    """Lucky's wheel: a rim with pegs, 12 fields (every other one filled), a hub and the pointer on top."""
    cy, rim = 106, 62
    d.ellipse(((C - rim) * k, (cy - rim) * k, (C + rim) * k, (cy + rim) * k), fill=255)
    d.ellipse(((C - rim + 9) * k, (cy - rim + 9) * k, (C + rim - 9) * k, (cy + rim - 9) * k), fill=0)
    inner = rim - 14
    for n in range(0, 12, 2):
        d.pieslice(((C - inner) * k, (cy - inner) * k, (C + inner) * k, (cy + inner) * k),
                   n * 30 - 90, n * 30 - 60, fill=255)
    d.ellipse(((C - 16) * k, (cy - 16) * k, (C + 16) * k, (cy + 16) * k), fill=0)
    d.ellipse(((C - 11) * k, (cy - 11) * k, (C + 11) * k, (cy + 11) * k), fill=255)
    for n in range(12):                                       # pegs on the rim, between the fields
        a = math.radians(n * 30 - 90)
        x, y = C + math.cos(a) * (rim - 4.5), cy + math.sin(a) * (rim - 4.5)
        d.ellipse(((x - 2.5) * k, (y - 2.5) * k, (x + 2.5) * k, (y + 2.5) * k), fill=0)
    d.polygon([((C - 12) * k, 28 * k), ((C + 12) * k, 28 * k), (C * k, 52 * k)], fill=255)     # the pointer


def broken_heart(d, k):
    """A heart (its curve), split down the middle by a zigzag crack; the two halves move a little apart."""
    heart = heart_mask(k)
    for side in (-1, 1):
        region = Image.new("L", (BIG, BIG))
        edge = [(x * k, y * k) for x, y in CRACK]
        far = (C + side * 120) * k
        ImageDraw.Draw(region).polygon([(far, 0), (CRACK[0][0] * k, 0)] + edge + [(CRACK[-1][0] * k, BIG), (far, BIG)],
                                       fill=255)
        piece = np.minimum(heart, np.asarray(region, np.float32) / 255)
        piece = np.roll(piece, int(side * 5 * k), axis=1)
        d.bitmap((0, 0), Image.fromarray((piece * 255).astype(np.uint8)), fill=255)


CRACK = [(96, 20), (96, 82), (86, 100), (104, 120), (90, 140), (100, 158), (96, 196)]


def heart_mask(k):
    img = Image.new("L", (BIG, BIG))
    pts = []
    for n in range(400):
        a = n / 400 * math.tau
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append(((C + x * 4.0) * k, (102 - y * 4.0) * k))
    ImageDraw.Draw(img).polygon(pts, fill=255)
    return np.asarray(img, np.float32) / 255


def abyss(d, k):
    """A spiral going down into the dark (drawn as a row of round dots - no seams)."""
    for i in range(1200):
        t = i / 1200 * 3.0 * math.tau
        r = 66 * (1 - i / 1290)
        x, y = C + math.cos(t) * r, C + math.sin(t) * r * 0.78
        w = 4.6
        d.ellipse(((x - w) * k, (y - w) * k, (x + w) * k, (y + w) * k), fill=255)


def question(d, k):
    font = ImageFont.truetype(FONT, int(132 * k))
    d.text((C * k, (C + 4) * k), "?", font=font, fill=255, anchor="mm")


# --- more symbols (13.11) ------------------------------------------------------------------------------------
def poly(d, k, pts, fill=255):
    d.polygon([(x * k, y * k) for x, y in pts], fill=fill)


def circle(d, k, cx, cy, r, fill=255):
    d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), fill=fill)


def ring(d, k, cx, cy, r, width, fill=255):
    d.ellipse(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), outline=fill, width=int(width * k))


def box(d, k, x0, y0, x1, y1, radius=0, fill=255):
    d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), radius * k, fill=fill)


def line(d, k, pts, width, fill=255):
    d.line([(x * k, y * k) for x, y in pts], fill=fill, width=int(width * k), joint="curve")
    for x, y in (pts[0], pts[-1]):
        circle(d, k, x, y, width / 2, fill)


def stroke(d, k, pts, width):
    """A smooth, seamless line through the points: round dots stamped close together all along it."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        steps = max(1, int(math.dist((x0, y0), (x1, y1)) * 2))
        for n in range(steps + 1):
            t = n / steps
            circle(d, k, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, width / 2)


def glyph(d, k, text, size, y=C, fill=255, x=C):
    """Letters / numbers (Cinzel), made bolder so they rise like the other symbols."""
    font = ImageFont.truetype(FONT, int(size * k))
    d.text((x * k, y * k), text, font=font, fill=fill, anchor="mm", stroke_width=int(size * k / 18), stroke_fill=fill)


def arrow_arc(d, k, cx, cy, r, start, end, width, head=16):
    """An arc (degrees, clockwise from 3 o'clock) with an arrow head at its end."""
    d.arc(((cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k), start, end, fill=255, width=int(width * k))
    a = math.radians(end)
    tip = (cx + math.cos(a) * r, cy + math.sin(a) * r)
    along = (-math.sin(a), math.cos(a))                     # the way the arc goes on
    out = (math.cos(a), math.sin(a))
    poly(d, k, [(tip[0] + along[0] * head, tip[1] + along[1] * head),
                (tip[0] + out[0] * head * 0.9, tip[1] + out[1] * head * 0.9),
                (tip[0] - out[0] * head * 0.9, tip[1] - out[1] * head * 0.9)])


def heart_shape(d, k, cx, cy, scale, fill=255):
    pts = []
    for n in range(240):
        a = n / 240 * math.tau
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * scale, cy - y * scale))
    poly(d, k, pts, fill)


def house(d, k):
    poly(d, k, [(C, 34), (162, 96), (146, 96), (146, 160), (46, 160), (46, 96), (30, 96)])
    box(d, k, 82, 112, 110, 160, 4, fill=0)
    box(d, k, 120, 108, 136, 124, 2, fill=0)


def prism(d, k):
    poly(d, k, [(C, 32), (166, 154), (26, 154)])
    line(d, k, [(C, 32), (104, 82), (88, 112), (100, 154)], 5, fill=0)
    line(d, k, [(104, 82), (132, 100)], 4, fill=0)


def mushroom(d, k):
    d.pieslice((28 * k, 36 * k, 164 * k, 164 * k), 180, 360, fill=255)
    box(d, k, 76, 96, 116, 160, 14)
    for x, y, r in ((68, 66, 10), (110, 56, 12), (138, 80, 8), (92, 84, 7)):
        circle(d, k, x, y, r, fill=0)


def gear(d, k):
    teeth = 10
    pts = []
    for n in range(teeth * 4):
        a = n / (teeth * 4) * math.tau
        r = 70 if n % 4 in (0, 1) else 54
        pts.append((C + math.cos(a + 0.06) * r, C + math.sin(a + 0.06) * r))
    poly(d, k, pts)
    circle(d, k, C, C, 22, fill=0)


def flower(d, k):
    for n in range(6):
        a = n * math.pi / 3
        x, y = C + math.cos(a) * 40, C + math.sin(a) * 40
        circle(d, k, x, y, 27)
    circle(d, k, C, C, 25, fill=0)
    circle(d, k, C, C, 19)


def note(d, k):
    d.ellipse((44 * k, 120 * k, 88 * k, 156 * k), fill=255)
    d.ellipse((108 * k, 108 * k, 152 * k, 144 * k), fill=255)
    box(d, k, 78, 44, 88, 140)
    box(d, k, 142, 32, 152, 128)
    poly(d, k, [(78, 44), (152, 32), (152, 56), (78, 68)])


def heart(d, k):
    heart_shape(d, k, C, 100, 4.0)


def heart_outline(d, k):
    """An empty heart with only a little left at the bottom (Close Shave)."""
    heart_shape(d, k, C, 100, 4.0)
    heart_shape(d, k, C, 100, 3.0, fill=0)
    low = Image.new("L", (BIG, BIG))
    heart_shape(ImageDraw.Draw(low), k, C, 100, 3.0)
    box(ImageDraw.Draw(low), k, 0, 0, 192, 116, fill=0)          # only the bottom of it stays
    d.bitmap((0, 0), low, fill=255)


def eclipse(d, k):
    circle(d, k, C, C, 62)
    circle(d, k, C + 18, C - 12, 54, fill=0)
    ring(d, k, C, C, 72, 4)


def loop_arrow(d, k):
    arrow_arc(d, k, C, C, 54, -60, 240, 14, head=20)


def key(d, k):
    ring(d, k, 62, 70, 30, 14)
    line(d, k, [(84, 92), (152, 160)], 14)
    line(d, k, [(126, 134), (110, 150)], 12)
    line(d, k, [(142, 150), (130, 162)], 12)


def sun(d, k):
    circle(d, k, C, C, 36)
    for n in range(12):
        a = n * math.pi / 6
        r0, r1 = 48, 70 if n % 2 == 0 else 60
        line(d, k, [(C + math.cos(a) * r0, C + math.sin(a) * r0), (C + math.cos(a) * r1, C + math.sin(a) * r1)], 9)


def hook(d, k):
    """A fish hook drawn as one unbroken line: the shank, the bend, the point with its barb, and the eye."""
    path = [(118, 40), (118, 118)]
    path += [(92 + math.cos(t) * 26, 118 + math.sin(t) * 26) for t in np.linspace(0, math.pi, 40)]
    path += [(66, 96)]
    stroke(d, k, path, 12)
    poly(d, k, [(66, 80), (56, 104), (76, 100)])                 # the point
    poly(d, k, [(66, 104), (80, 98), (72, 116)])                 # the barb
    ring(d, k, 118, 30, 11, 7)


def antenna(d, k):
    poly(d, k, [(C, 70), (128, 166), (114, 166), (C, 104), (78, 166), (64, 166)])
    circle(d, k, C, 70, 11)
    for r in (30, 50):
        d.arc(((C - r) * k, (70 - r) * k, (C + r) * k, (70 + r) * k), 200, 250, fill=255, width=int(8 * k))
        d.arc(((C - r) * k, (70 - r) * k, (C + r) * k, (70 + r) * k), 290, 340, fill=255, width=int(8 * k))


def magnifier(d, k):
    ring(d, k, 80, 80, 42, 14)
    line(d, k, [(112, 112), (156, 156)], 18)


def clock(d, k):
    ring(d, k, C, C, 64, 12)
    line(d, k, [(C, C), (C, 56)], 10)
    line(d, k, [(C, C), (128, 112)], 10)
    for n in range(12):
        a = n * math.pi / 6
        circle(d, k, C + math.cos(a) * 46, C + math.sin(a) * 46, 3.5)


def orb(d, k):
    circle(d, k, C, C, 52)
    ring(d, k, C, C, 68, 5)
    circle(d, k, C - 18, C - 20, 12, fill=0)
    circle(d, k, C - 18, C - 20, 7)


def peace(d, k):
    ring(d, k, C, C, 62, 13)
    line(d, k, [(C, 36), (C, 156)], 12)
    line(d, k, [(C, C + 4), (54, 140)], 12)
    line(d, k, [(C, C + 4), (138, 140)], 12)


def bricks(d, k):
    for row in range(5):
        y = 42 + row * 24
        offset = 0 if row % 2 == 0 else 22
        for col in range(-1, 4):
            x = 30 + offset + col * 44
            x0, x1 = max(30, x), min(162, x + 40)
            if x1 - x0 > 8:
                box(d, k, x0, y, x1, y + 20, 3)


def bulb(d, k):
    circle(d, k, C, 82, 46)
    poly(d, k, [(70, 104), (122, 104), (114, 138), (78, 138)])
    for n, y in enumerate((142, 154)):
        box(d, k, 78 + n * 3, y, 114 - n * 3, y + 8, 4)
    line(d, k, [(84, 88), (C, 104), (108, 88)], 5, fill=0)


def sigils(d, k):
    for x, y in ((66, 66), (126, 66), (66, 126), (126, 126)):
        poly(d, k, [(x, y - 30), (x + 30, y), (x, y + 30), (x - 30, y)])
        circle(d, k, x, y, 8, fill=0)


def folded_map(d, k):
    poly(d, k, [(28, 54), (72, 40), (120, 54), (164, 40), (164, 146), (120, 160), (72, 146), (28, 160)])
    line(d, k, [(72, 44), (72, 144)], 4, fill=0)
    line(d, k, [(120, 56), (120, 156)], 4, fill=0)
    line(d, k, [(46, 120), (66, 100), (88, 112), (110, 84)], 5, fill=0)
    circle(d, k, 136, 82, 7, fill=0)


def islands(d, k):
    for cx, cy in ((60, 110), (134, 84)):
        d.chord(((cx - 34) * k, (cy - 18) * k, (cx + 34) * k, (cy + 18) * k), 180, 360, fill=255)
        poly(d, k, [(cx - 34, cy), (cx + 34, cy), (cx, cy + 46)])
    line(d, k, [(94, 104), (100, 98)], 4)


def cards(d, k):
    """Two cards: the left one shows a "?", the right one lies face down."""
    box(d, k, 90, 40, 160, 136, 10)
    box(d, k, 28, 52, 102, 150, 10, fill=0)
    box(d, k, 34, 58, 96, 144, 8)
    glyph(d, k, "?", 52, y=101, fill=0, x=65)


def grid(d, k):
    for r in range(3):
        for c in range(3):
            box(d, k, 38 + c * 40, 38 + r * 40, 74 + c * 40, 74 + r * 40, 6)
    glyph(d, k, "9", 30, y=96, fill=0)


def number_plate(text):
    def draw(d, k):
        glyph(d, k, text, 84 if len(text) <= 2 else 64, y=C + 4)
    return draw


def shield(d, k):
    poly(d, k, [(C, 30), (156, 52), (150, 112), (C, 166), (42, 112), (36, 52)])
    poly(d, k, [(C, 48), (138, 64), (134, 108), (C, 146)], fill=0)


def skull(d, k):
    circle(d, k, C, 82, 50)
    box(d, k, 66, 108, 126, 150, 12)
    circle(d, k, 76, 86, 14, fill=0)
    circle(d, k, 116, 86, 14, fill=0)
    poly(d, k, [(C, 104), (104, 120), (88, 120)], fill=0)
    for x in (80, 96, 112):
        box(d, k, x - 3, 132, x + 3, 150, fill=0)


def coins(d, k):
    for n in range(4):
        y = 138 - n * 22
        d.ellipse((46 * k, (y - 18) * k, 146 * k, (y + 18) * k), fill=255)
        d.arc((46 * k, (y - 18) * k, 146 * k, (y + 18) * k), 0, 180, fill=0, width=int(4 * k))
    d.ellipse((60 * k, 64 * k, 132 * k, 84 * k), outline=0, width=int(4 * k))


def bag(d, k):
    box(d, k, 40, 70, 152, 162, 12)
    d.arc((68 * k, 34 * k, 124 * k, 100 * k), 180, 360, fill=255, width=int(10 * k))
    circle(d, k, 72, 86, 6, fill=0)
    circle(d, k, 120, 86, 6, fill=0)


def pistol(d, k):
    poly(d, k, [(30, 64), (160, 64), (160, 92), (96, 92), (88, 104), (72, 150), (40, 150), (54, 92), (30, 92)])
    circle(d, k, 98, 104, 13, fill=0)
    box(d, k, 148, 54, 158, 64)


def no_gun(d, k):
    ring(d, k, C, C, 66, 12)
    poly(d, k, [(54, 82), (138, 82), (138, 100), (96, 100), (90, 108), (80, 138), (60, 138), (68, 100), (54, 100)])
    line(d, k, [(48, 48), (144, 144)], 12)


def three_hearts(d, k):
    for x, y in ((62, 88), (130, 88), (C, 130)):
        heart_shape(d, k, x, y, 2.0)


def briefcase(d, k):
    box(d, k, 32, 66, 160, 152, 12)
    d.rounded_rectangle((72 * k, 40 * k, 120 * k, 74 * k), 8 * k, outline=255, width=int(10 * k))
    box(d, k, 32, 98, 160, 106, fill=0)
    box(d, k, 86, 92, 106, 112, 3)


def broken_briefcase(d, k):
    briefcase(d, k)
    line(d, k, [(96, 66), (84, 96), (104, 118), (92, 152)], 6, fill=0)


def window(d, k):
    box(d, k, 38, 34, 154, 160, 10)
    box(d, k, 50, 46, 92, 92, 3, fill=0)
    box(d, k, 100, 46, 142, 92, 3, fill=0)
    box(d, k, 50, 100, 92, 148, 3, fill=0)
    box(d, k, 100, 100, 142, 148, 3, fill=0)


def bubble(d, k):
    box(d, k, 28, 40, 164, 128, 24)
    poly(d, k, [(56, 120), (90, 120), (48, 164)])
    for x in (66, 96, 126):
        circle(d, k, x, 84, 9, fill=0)


def hourglass(d, k):
    box(d, k, 46, 30, 146, 44, 5)
    box(d, k, 46, 148, 146, 162, 5)
    poly(d, k, [(56, 44), (136, 44), (102, 96), (136, 148), (56, 148), (90, 96)])
    poly(d, k, [(70, 56), (122, 56), (C, 88)], fill=0)
    poly(d, k, [(C, 112), (118, 136), (74, 136)], fill=0)


def dice(d, k):
    box(d, k, 40, 40, 152, 152, 20)
    for x, y in ((68, 68), (124, 68), (C, C), (68, 124), (124, 124)):
        circle(d, k, x, y, 10, fill=0)


def flag(d, k):
    line(d, k, [(52, 32), (52, 166)], 10)
    poly(d, k, [(56, 38), (150, 50), (126, 78), (150, 106), (56, 98)])


def target(d, k):
    for r, fill in ((68, 255), (54, 0), (42, 255), (28, 0), (16, 255)):
        circle(d, k, C, C, r, fill=fill)


def zero_coin(d, k):
    circle(d, k, C, C, 64)
    ring(d, k, C, C, 52, 5, fill=0)
    glyph(d, k, "0", 76, y=C + 2, fill=0)


def reroll(d, k):
    arrow_arc(d, k, C, C, 52, 200, 340, 13, head=18)
    arrow_arc(d, k, C, C, 52, 20, 160, 13, head=18)


def grass(d, k):
    """Blades of grass bending a little, on a strip of ground."""
    for x, h, lean in ((46, 70, -14), (70, 104, -8), (94, 86, 4), (118, 112, 10), (142, 78, 16)):
        top = (x + lean, 150 - h)
        poly(d, k, [(x - 10, 150), (x + 10, 150), ((x + top[0]) / 2 + 6, 150 - h / 2), top, ((x + top[0]) / 2 - 2, 150 - h / 2)])
    box(d, k, 30, 146, 162, 162, 7)


def fish(d, k):
    d.ellipse((46 * k, 72 * k, 136 * k, 124 * k), fill=255)
    poly(d, k, [(128, 98), (164, 70), (156, 98), (164, 126)])
    circle(d, k, 72, 92, 6, fill=0)


def rewind(d, k):
    poly(d, k, [(96, 56), (96, 136), (36, 96)])
    poly(d, k, [(158, 56), (158, 136), (98, 96)])


def tombstone(d, k):
    d.pieslice((52 * k, 34 * k, 140 * k, 122 * k), 180, 360, fill=255)
    box(d, k, 52, 78, 140, 156)
    box(d, k, 36, 152, 156, 166, 4)
    glyph(d, k, "RIP", 26, y=104, fill=0)


def top_hat(d, k):
    box(d, k, 62, 40, 130, 136, 8)
    d.ellipse((26 * k, 126 * k, 166 * k, 156 * k), fill=255)
    box(d, k, 62, 112, 130, 124, fill=0)


def star(d, k, cx, cy, r, fill=255):
    pts = []
    for n in range(10):
        a = -math.pi / 2 + n * math.pi / 5
        rr = r if n % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    poly(d, k, pts, fill)


def starred(draw, cx=148, cy=46, r=26):
    """A symbol with a star in its corner (cut out of it a little, so they don't melt together)."""
    def drawn(d, k):
        draw(d, k)
        star(d, k, cx, cy, r + 7, fill=0)
        star(d, k, cx, cy, r)
    return drawn


def small_grid(d, k):
    for r in range(3):
        for c in range(3):
            box(d, k, 30 + c * 38, 52 + r * 38, 64 + c * 38, 86 + r * 38, 6)


def banknote(d, k):
    box(d, k, 22, 52, 170, 140, 12)
    box(d, k, 32, 62, 160, 130, 8, fill=0)
    box(d, k, 38, 68, 154, 124, 6)
    ring(d, k, C, 96, 24, 5, fill=0)
    glyph(d, k, "$", 34, y=97, fill=0)
    for x in (52, 140):
        circle(d, k, x, 96, 6, fill=0)


def compass(d, k):
    ring(d, k, C, C, 64, 10)
    poly(d, k, [(C, 40), (118, C), (C, 152), (74, C)])
    poly(d, k, [(C, 56), (108, C), (84, C)], fill=0)                    # the north half: hollow
    circle(d, k, C, C, 8, fill=0)
    for a in range(0, 360, 90):
        r = math.radians(a)
        circle(d, k, C + math.cos(r) * 52, C + math.sin(r) * 52, 4)


def globe(d, k):
    circle(d, k, C, C, 64)
    d.ellipse(((C - 26) * k, 34 * k, (C + 26) * k, 158 * k), outline=0, width=int(5 * k))
    box(d, k, C - 2.5, 32, C + 2.5, 160, fill=0)
    for y, half in ((C, 64), (66, 50), (126, 50)):
        box(d, k, C - half, y - 2.5, C + half, y + 2.5, fill=0)


SYMBOLS = {
    "new_in_town": house, "royal_flush": crown, "shattered_expectations": prism, "mother_knows_less": mushroom,
    "chill_out": snowflake, "quality_control": gear, "lights_out": flower, "showtime": note, "every_beat": heart,
    "remembered": eclipse, "round_and_round": loop_arrow, "almost_the_truth": key, "a_world_that_lives": sun,
    "off_the_hook": hook, "can_you_hear_me_now": antenna, "things_that_dont_fit": magnifier, "overtime": clock,
    "feeling_a_bit_pale": orb, "peacekeeper": peace, "behind_the_wall": bricks, "keeper_of_memories": bulb,
    "sticker_album": sigils, "cartographer": folded_map, "mind_the_gap": islands,
    "tourist": compass, "been_there_done_that": globe,
    "memory_like_an_elephant": cards, "number_cruncher": grid, "the_big_one": pearl, "gamble_addict": wheel,
    "sudoku_addict": starred(small_grid), "encore": starred(note, cx=150, cy=150, r=24),
    "untouchable": shield, "close_shave": heart_outline, "pest_control": skull,
    "is_this_your_job_now": number_plate("10K"), "dragon_hoard": banknote, "shopaholic": bag, "pacifist": no_gun,
    "old_faithful": pistol,
    "slippery": crown, "light_footed": prism, "allergy_free": mushroom, "ice_skater": snowflake,
    "zero_defects": gear, "sixth_sense": flower, "perfect_pitch": note, "heartless": broken_heart,
    "nothing_left_to_lose": three_hearts, "untouched_by_the_void": eclipse,
    "i_have_a_life_too": briefcase, "unemployed": broken_briefcase,
    "window_shopper": window, "small_talk_champion": bubble, "fell_for_it": abyss, "speedrunner": hourglass,
    "the_house_always_wins": dice, "tactical_retreat": flag, "bullet_sponge": target, "zero_balance": zero_coin,
    "just_one_more_reroll": reroll, "touch_grass": grass, "small_fry": fish, "deja_vu": rewind,
    "skill_issue": tombstone, "fashionably_late": top_hat,
}


def all_icons():
    """id -> (group, symbol): every achievement (data.py) + "locked"."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from game.achievements.data import ACHIEVEMENTS
    icons = {a["id"]: (a["group"], SYMBOLS[a["id"]]) for a in ACHIEVEMENTS}
    icons["locked"] = ("weird", question)
    return icons


def main(out=OUT):
    os.makedirs(out, exist_ok=True)
    icons = all_icons()
    for name, (group, symbol) in icons.items():
        badge(group, symbol).save(os.path.join(out, name + ".png"))
    print(len(icons), "icons written to", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else OUT)
