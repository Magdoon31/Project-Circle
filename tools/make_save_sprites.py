# MAKES THE SAVE SCREEN'S SPRITES (11.11) - run it once from the project folder: python tools/make_save_sprites.py
# Writes assets/img/menu/saves/*.png: the words (buttons, titles) in the style of the menu's title and buttons
# (cream fading into lavender, a dark purple outline, thin cracks, a soft shadow) and the save cards (dark, an
# ornamental frame; hard mode = red; an empty slot = faint, dashed).
# Font: Cinzel Bold (assets/font/Cinzel-Bold.ttf, SIL Open Font License 1.1). Needs Pillow.

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "assets/font/Cinzel-Bold.ttf"
OUT = "assets/img/menu/saves"
CREAM, LAVENDER, VIOLET = (250, 246, 222), (184, 150, 220), (118, 78, 170)
OUTLINE = (36, 16, 56)
CRACK = (70, 44, 96)
RED_CREAM, RED_LIGHT, RED_DEEP = (255, 232, 222), (236, 130, 140), (170, 50, 70)

WORDS = {                         # file name -> (text, size, colours)
    "title_saves": ("Saves", 120, None),
    "title_new_save": ("New Save", 110, None),
    "title_sure_delete": ("Delete this save?", 84, None),
    "title_sure_overwrite": ("Start over on this slot?", 72, None),
    "btn_continue": ("Continue", 84, None),
    "btn_new_game": ("New Game", 84, None),
    "btn_back": ("Back", 72, None),
    "btn_yes": ("Yes", 84, None),
    "btn_no": ("No", 84, None),
    "btn_normal": ("Normal", 84, None),
    "btn_hard_mode": ("Hard Mode", 84, "red"),
    "btn_delete": ("Delete", 56, "red"),
    "label_name": ("Name", 52, None),
    "label_seed": ("Seed", 52, None),
}
CARD = (480, 620)                 # px (the game scales it)


# --- words ------------------------------------------------------------------------------------------------------
def gradient(size, colours):
    """A vertical gradient through the colours (top -> bottom)."""
    w, h = size
    img = Image.new("RGBA", size)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1) * (len(colours) - 1)
        i = min(int(t), len(colours) - 2)
        k = t - i
        c = tuple(int(colours[i][j] + (colours[i + 1][j] - colours[i][j]) * k) for j in range(3))
        for x in range(w):
            px[x, y] = c + (255,)
    return img


def word(text, size, style, seed):
    font = ImageFont.truetype(FONT, size)
    stroke = max(3, size // 16)
    left, top, right, bottom = font.getbbox(text, stroke_width=stroke)
    pad = stroke * 4
    w, h = right - left + pad * 2, bottom - top + pad * 2
    origin = (pad - left, pad - top)
    fill_mask = Image.new("L", (w, h))
    ImageDraw.Draw(fill_mask).text(origin, text, font=font, fill=255)
    outline_mask = Image.new("L", (w, h))
    ImageDraw.Draw(outline_mask).text(origin, text, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    colours = [RED_CREAM, RED_LIGHT, RED_DEEP] if style == "red" else [CREAM, CREAM, LAVENDER, VIOLET]
    fill = gradient((w, h), colours)
    cracks(fill, fill_mask, size, seed)
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow.paste((10, 4, 18, 150), (0, max(2, size // 24)), outline_mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(size / 18))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(shadow)
    out.paste(OUTLINE + (255,), (0, 0), outline_mask)
    out.paste(fill, (0, 0), fill_mask)
    return out.crop(out.getbbox())


def cracks(fill, mask, size, seed):
    """A few thin cracks in the letters (only where the letters are)."""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", fill.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = fill.size
    for _ in range(max(2, w // (size * 2))):
        x, y = rnd.uniform(0, w), rnd.uniform(h * 0.2, h * 0.8)
        a = rnd.uniform(-1.2, -0.3) if rnd.random() < 0.5 else rnd.uniform(0.3, 1.2)
        points = [(x, y)]
        for _ in range(3):
            x += math.cos(a) * size * 0.12
            y += math.sin(a) * size * 0.12
            a += rnd.uniform(-0.5, 0.5)
            points.append((x, y))
        d.line(points, fill=CRACK + (200,), width=max(1, size // 40))
    clipped = Image.new("RGBA", fill.size, (0, 0, 0, 0))
    clipped.paste(layer, (0, 0), Image.composite(layer.getchannel("A"), Image.new("L", fill.size), mask))
    fill.alpha_composite(clipped)


# --- cards ------------------------------------------------------------------------------------------------------
def card(kind):
    """kind: normal / hard / empty."""
    w, h = CARD
    img = Image.new("RGBA", CARD, (0, 0, 0, 0))
    body = {"normal": [(40, 28, 62), (18, 12, 30)], "hard": [(96, 22, 38), (38, 6, 14)],
            "empty": [(30, 24, 44), (16, 12, 24)]}[kind]
    alpha = 150 if kind == "empty" else 232
    mask = Image.new("L", CARD)
    ImageDraw.Draw(mask).rounded_rectangle((6, 6, w - 7, h - 7), 28, fill=alpha)
    img.paste(gradient(CARD, body), (0, 0), mask)
    frame_colours = [RED_CREAM, RED_LIGHT, RED_DEEP] if kind == "hard" else [CREAM, LAVENDER, VIOLET]
    frame = gradient(CARD, frame_colours)
    border = Image.new("L", CARD)
    d = ImageDraw.Draw(border)
    if kind == "empty":
        dashed_round_rect(d, (6, 6, w - 7, h - 7), 28, 150)
    else:
        d.rounded_rectangle((6, 6, w - 7, h - 7), 28, outline=255, width=5)
        d.rounded_rectangle((20, 20, w - 21, h - 21), 18, outline=150, width=2)
        ornaments(d, w, h)
    img.paste(frame, (0, 0), border)
    return img


def ornaments(d, w, h):
    """Small diamonds in the corners; a divider with a ringed diamond under the name."""
    for cx, cy in ((34, 34), (w - 35, 34), (34, h - 35), (w - 35, h - 35)):
        diamond(d, cx, cy, 9)
    y = 150
    d.line((60, y, w // 2 - 26, y), fill=220, width=3)
    d.line((w // 2 + 26, y, w - 61, y), fill=220, width=3)
    d.ellipse((w // 2 - 18, y - 18, w // 2 + 18, y + 18), outline=255, width=3)
    diamond(d, w // 2, y, 8)
    for x in (60, w - 61):
        diamond(d, x, y, 5)


def diamond(d, cx, cy, r):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=255)


def dashed_round_rect(d, box, radius, value):
    x0, y0, x1, y1 = box
    dash, gap = 22, 14
    for a, b, horizontal in (((x0 + radius, y0), (x1 - radius, y0), True), ((x0 + radius, y1), (x1 - radius, y1), True),
                             ((x0, y0 + radius), (x0, y1 - radius), False), ((x1, y0 + radius), (x1, y1 - radius), False)):
        length = (b[0] - a[0]) if horizontal else (b[1] - a[1])
        t = 0
        while t < length:
            e = min(length, t + dash)
            p = (a[0] + t, a[1]) if horizontal else (a[0], a[1] + t)
            q = (a[0] + e, a[1]) if horizontal else (a[0], a[1] + e)
            d.line((p, q), fill=value, width=4)
            t += dash + gap
    for (cx, cy), start in (((x0 + radius, y0 + radius), 180), ((x1 - radius, y0 + radius), 270),
                            ((x1 - radius, y1 - radius), 0), ((x0 + radius, y1 - radius), 90)):
        d.arc((cx - radius, cy - radius, cx + radius, cy + radius), start, start + 90, fill=value, width=4)


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, (name, (text, size, style)) in enumerate(WORDS.items()):
        word(text, size, style, seed=i * 7 + 3).save(f"{OUT}/{name}.png")
    for kind in ("normal", "hard", "empty"):
        card(kind).save(f"{OUT}/card_{kind}.png")
    print("written:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
