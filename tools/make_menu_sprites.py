# MAKES THE MENUS' SPRITES (11.11) - run it from the project folder: python tools/make_menu_sprites.py
# The words (buttons, titles) in the style of the game's title: cream at the top going lavender at the bottom, a
# sharp bevel (a bright edge on top, a lavender rim and a dark lip at the bottom - hard steps, not smooth), a crisp
# dark purple outline, a little grain and a few cracks; the save cards (dark, an ornamental frame; hard mode = red;
# an empty slot = faint, dashed); the volume slider (track, fill, knob) and its icons in the same style.
# Folders = where a picture is used: assets/img/menu/main (the main menu), saves (the save screen), esc (the menu
# under ESC - on the map and in a fight), settings (the Settings screen - the same one from the main menu and from
# ESC); used in more than one place = straight in assets/img/menu.
# Every word of one letter size is as tall as the others (from its tallest to its lowest letters), so buttons line
# up.
# Add a word to WORDS and run it again to get a new one in the same style.
# Font: Cinzel Bold (assets/font/Cinzel-Bold.ttf, SIL Open Font License 1.1). Needs Pillow and numpy.

import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "assets/font/Cinzel-Bold.ttf"
ROOT = "assets/img/menu"
OUTLINE = (31, 0, 49)
CRACK = (84, 60, 104)
PALETTES = {      # body gradient (top -> bottom), top bevel, bottom rim, the dark lip over the rim
    "cream": {"body": [(252, 255, 232), (246, 250, 222), (226, 222, 204), (196, 176, 196), (176, 150, 196)],
              "top": (255, 255, 250), "rim": (160, 127, 190), "lip": (112, 80, 142)},
    "red": {"body": [(255, 240, 228), (250, 214, 204), (232, 160, 160), (200, 100, 116)],
            "top": (255, 250, 246), "rim": (176, 60, 84), "lip": (118, 30, 52)},
    "green": {"body": [(244, 255, 238), (214, 246, 206), (160, 222, 166), (96, 176, 120)],     # (12.11) easy
              "top": (250, 255, 246), "rim": (58, 140, 88), "lip": (28, 92, 54)},
}

MAIN, SAVES, ESC, SETTINGS, SHARED = "main", "saves", "esc", "settings", ""
WORDS = {         # file name -> (text, letter size, palette, folder)
    # the main menu
    "btn_play": ("Play", 96, "cream", MAIN),
    "btn_achievements": ("Achievements", 96, "cream", MAIN),
    "btn_settings": ("Settings", 96, "cream", MAIN),
    "btn_quit": ("Quit", 96, "cream", MAIN),
    # the menu under ESC (on the map / in a fight)
    "btn_return": ("Return", 84, "cream", ESC),
    "btn_save": ("Save", 84, "cream", ESC),
    "btn_stats": ("Stats", 84, "cream", ESC),
    "btn_main_menu": ("Main Menu", 84, "cream", ESC),
    "btn_quit_game": ("Quit Game", 84, "cream", ESC),
    "btn_settings_esc": ("Settings", 84, "cream", ESC),
    "title_paused": ("Paused", 110, "cream", ESC),
    "title_stats": ("Stats", 110, "cream", ESC),
    # the save screen
    "btn_continue": ("Continue", 84, "cream", SAVES),
    "btn_new_game": ("New Game", 84, "cream", SAVES),
    "btn_yes": ("Yes", 84, "cream", SAVES),
    "btn_no": ("No", 84, "cream", SAVES),
    "btn_normal": ("Normal", 84, "cream", SAVES),
    "btn_hard_mode": ("Hard Mode", 84, "red", SAVES),
    "btn_delete": ("Delete", 56, "red", SAVES),
    "title_saves": ("Saves", 120, "cream", SAVES),
    "title_new_save": ("New Save", 110, "cream", SAVES),
    "title_sure_delete": ("Delete this save?", 84, "cream", SAVES),
    "title_sure_overwrite": ("Start over on this slot?", 72, "cream", SAVES),
    "label_name": ("Name", 52, "cream", SAVES),
    "label_seed": ("Seed", 52, "cream", SAVES),
    # in more than one place
    # the settings screen
    "title_settings": ("Settings", 110, "cream", SETTINGS),
    "tab_audio": ("Audio", 72, "cream", SETTINGS),
    "tab_video": ("Video", 72, "cream", SETTINGS),
    "tab_controls": ("Controls", 72, "cream", SETTINGS),
    "tab_gameplay": ("Gameplay", 72, "cream", SETTINGS),
    "btn_defaults": ("Default", 72, "red", SETTINGS),
    # in more than one place
    "btn_back": ("Back", 72, "cream", SHARED),
    # (12.11) added last: the words before keep their look (each word's seed comes from its place in this list)
    "btn_i_have_a_job": ("I Have a Job", 84, "green", SAVES),
}
SAME_HEIGHT = "HQqgj"            # the tallest and lowest letters: the height every word gets
SLIDER = (640, 44)                # px: the volume slider's track (the game scales it)
KNOB = 64
STAR = 96                         # px: an ending star on a save card (the game scales it)
FILL_PAD = 11                     # px from the track's edge to the lit part - the same on all four sides
ICON = 96
CARD = (480, 620)                 # px (the game scales it)
CARD_PALETTE = {"easy": "green", "normal": "cream", "hard": "red"}   # a save card's frame (= game/difficulty.py)


# --- words ------------------------------------------------------------------------------------------------------
def word(text, size, palette, seed):
    p = PALETTES[palette]
    font = ImageFont.truetype(FONT, size)
    stroke = max(2, size // 26)
    left, _, right, _ = font.getbbox(text, stroke_width=stroke)
    _, top, _, bottom = font.getbbox(SAME_HEIGHT, stroke_width=stroke)   # every word of this size is as tall
    pad = stroke * 2 + size // 20
    w, h = right - left + pad * 2, bottom - top + pad * 2
    origin = (pad - left, pad - top)
    fill = mask_of(text, font, origin, (w, h))
    edge = mask_of(text, font, origin, (w, h), stroke)
    return styled(fill, edge, size, palette, seed, crop="width")


def styled(fill, edge, size, palette, seed, crop="both", cracks=True):
    """Any shape (a mask) in the words' style: the shading, the bevel, grain, cracks (unless cracks=False), the
    outline and a shadow. crop: "both" - to the picture's edges, "width" - only left and right, "none" - as it is."""
    p = PALETTES[palette]
    h, w = fill.shape
    letters = fill > 0
    colours = shade(letters, size, p)
    add_grain(colours, letters, seed)
    if cracks:
        add_cracks(colours, letters, size, seed)
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = OUTLINE
    out[..., 3] = edge
    inside = fill.astype(np.float32)[..., None] / 255
    out[..., :3] = (out[..., :3] * (1 - inside) + colours * inside).astype(np.uint8)
    img = with_shadow(Image.fromarray(out, "RGBA"), edge, size)
    if crop == "none":
        return img
    left, top, right, bottom = img.getbbox()
    return img.crop((left, top, right, bottom) if crop == "both" else (left, 0, right, h))


def mask_of(text, font, origin, size, stroke=0):
    img = Image.new("L", size)
    ImageDraw.Draw(img).text(origin, text, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    return np.array(img)


def shade(letters, size, p):
    """The body gradient over the letters' own height, then the bevel in hard steps."""
    h, w = letters.shape
    top_y, bottom_y = letter_rows(letters)
    rows = np.clip((np.arange(h) - top_y) / max(1, bottom_y - top_y), 0, 1)
    body = gradient_rows(rows, p["body"])
    colours = np.repeat(body[:, None, :], w, axis=1)
    d = max(2, size // 30)
    lit = letters & ~np.roll(letters, d, axis=0)                 # the edges facing up
    rim = letters & ~np.roll(letters, -d, axis=0)                # the edges facing down
    lip = letters & ~np.roll(letters, -(d + max(1, d // 2)), axis=0) & ~rim
    colours[lip] = p["lip"]
    colours[rim] = p["rim"]
    colours[lit] = p["top"]
    return colours.astype(np.float32)


def letter_rows(letters):
    rows = np.where(letters.any(axis=1))[0]
    return rows[0], rows[-1]


def gradient_rows(t, colours):
    stops = np.linspace(0, 1, len(colours))
    return np.stack([np.interp(t, stops, [c[i] for c in colours]) for i in range(3)], axis=1)


def add_grain(colours, letters, seed):
    rnd = np.random.default_rng(seed)
    grain = rnd.normal(1.0, 0.035, letters.shape)[..., None]
    colours[letters] = np.clip(colours * grain, 0, 255)[letters]


def add_cracks(colours, letters, size, seed):
    """A few thin cracks (only on the letters)."""
    rnd = random.Random(seed)
    h, w = letters.shape
    layer = Image.new("L", (w, h))
    d = ImageDraw.Draw(layer)
    for _ in range(max(2, w // (size * 2))):
        x, y = rnd.uniform(0, w), rnd.uniform(h * 0.25, h * 0.75)
        a = rnd.choice([-1, 1]) * rnd.uniform(0.4, 1.2)
        points = [(x, y)]
        for _ in range(3):
            x += math.cos(a) * size * 0.12
            y += math.sin(a) * size * 0.12
            a += rnd.uniform(-0.6, 0.6)
            points.append((x, y))
        d.line(points, fill=255, width=max(1, size // 48))
    crack = (np.array(layer) > 0) & letters
    colours[crack] = CRACK


def with_shadow(img, edge, size):
    """A small, fairly sharp shadow under the word."""
    shadow = Image.new("RGBA", img.size, (8, 0, 16, 0))
    alpha = Image.fromarray(edge).filter(ImageFilter.GaussianBlur(max(1, size / 40)))
    shadow.putalpha(alpha.point(lambda v: v * 120 // 255))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(shadow, (0, max(2, size // 30)))
    out.alpha_composite(img)
    return out


# --- cards ------------------------------------------------------------------------------------------------------
def gradient(size, colours):
    w, h = size
    rows = gradient_rows(np.linspace(0, 1, h), colours)
    data = np.repeat(rows[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(np.dstack([data, np.full((h, w), 255, np.uint8)]), "RGBA")


def card(kind):
    """kind: easy / normal / hard / empty."""
    w, h = CARD
    img = Image.new("RGBA", CARD, (0, 0, 0, 0))
    body = {"normal": [(40, 28, 62), (18, 12, 30)], "hard": [(96, 22, 38), (38, 6, 14)],
            "easy": [(24, 64, 42), (8, 28, 16)], "empty": [(30, 24, 44), (16, 12, 24)]}[kind]
    mask = Image.new("L", CARD)
    ImageDraw.Draw(mask).rounded_rectangle((6, 6, w - 7, h - 7), 28, fill=150 if kind == "empty" else 232)
    img.paste(gradient(CARD, body), (0, 0), mask)
    p = PALETTES[CARD_PALETTE.get(kind, "cream")]
    frame = gradient(CARD, [p["top"], p["body"][2], p["rim"]])
    border = Image.new("L", CARD)
    d = ImageDraw.Draw(border)
    if kind == "empty":
        dashed_round_rect(d, (6, 6, w - 7, h - 7), 28, 150)
    else:
        d.rounded_rectangle((6, 6, w - 7, h - 7), 28, outline=255, width=5)
        d.rounded_rectangle((20, 20, w - 21, h - 21), 18, outline=150, width=2)
        ornaments(d, w)
    img.paste(frame, (0, 0), border)
    return img


def ornaments(d, w):
    """Small diamonds in the corners; a divider with a ringed diamond under the name."""
    h = CARD[1]
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


# --- the volume slider and its icons ------------------------------------------------------------------------------
def slider_parts():
    """The track (a dark groove in a light frame), the fill (what is turned up) and the knob (a gem)."""
    w, h = SLIDER
    groove = Image.new("L", SLIDER)
    ImageDraw.Draw(groove).rounded_rectangle((4, 4, w - 5, h - 5), h // 2 - 4, fill=255)
    frame = Image.new("L", SLIDER)
    ImageDraw.Draw(frame).rounded_rectangle((4, 4, w - 5, h - 5), h // 2 - 4, outline=255, width=4)
    track = Image.new("RGBA", SLIDER, (0, 0, 0, 0))
    track.paste(gradient(SLIDER, [(14, 8, 24), (34, 24, 52)]), (0, 0), groove)
    p = PALETTES["cream"]
    track.paste(gradient(SLIDER, [p["top"], p["body"][2], p["rim"]]), (0, 0), frame)
    inner = Image.new("L", SLIDER)
    ImageDraw.Draw(inner).rounded_rectangle((FILL_PAD, FILL_PAD, w - 1 - FILL_PAD, h - 1 - FILL_PAD),
                                            h // 2 - FILL_PAD, fill=255)
    a = np.array(inner)
    full = styled(a, a, h * 2, "cream", seed=5, crop="none")
    knob_mask = Image.new("L", (KNOB, KNOB))
    r = KNOB // 2 - 8
    c = KNOB // 2
    ImageDraw.Draw(knob_mask).polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=255)
    k = np.array(knob_mask)
    edge = np.array(knob_mask.filter(ImageFilter.MaxFilter(5)))
    knob = styled(k, edge, KNOB * 2, "cream", seed=9, cracks=False)
    return track, full, knob


def icon(kind):
    """The Audio rows' icons (master: a speaker with sound waves, music: a note, sounds: a burst, dialogue: a speech
    bubble) and the arrows of a setting's choices, in the words' style."""
    mask = Image.new("L", (ICON, ICON))
    d = ImageDraw.Draw(mask)
    if kind == "arrow_left":
        d.polygon([(22, 48), (66, 18), (66, 78)], fill=255)
    elif kind == "arrow_right":
        d.polygon([(74, 48), (30, 18), (30, 78)], fill=255)
    elif kind == "sounds":
        points = [(48 + math.cos(a * math.pi / 8) * (40 if a % 2 == 0 else 18),
                   48 + math.sin(a * math.pi / 8) * (40 if a % 2 == 0 else 18)) for a in range(16)]
        d.polygon(points, fill=255)
    elif kind == "dialogue":
        d.rounded_rectangle((8, 14, 88, 66), 18, fill=255)
        d.polygon([(26, 60), (44, 60), (20, 86)], fill=255)
    elif kind == "music":
        d.ellipse((14, 60, 42, 84), fill=255)
        d.ellipse((54, 52, 82, 76), fill=255)
        d.rectangle((36, 18, 42, 72), fill=255)
        d.rectangle((76, 10, 82, 64), fill=255)
        d.polygon([(36, 18), (82, 10), (82, 24), (36, 32)], fill=255)
    else:
        d.rectangle((12, 36, 30, 60), fill=255)
        d.polygon([(30, 36), (54, 16), (54, 80), (30, 60)], fill=255)
        for r in (14, 26):
            d.arc((54 - r, 48 - r, 54 + r + 8, 48 + r), -50, 50, fill=255, width=6)
    m = np.array(mask)
    edge = np.array(mask.filter(ImageFilter.MaxFilter(5)))
    return styled(m, edge, ICON * 2, "cream", seed=11, cracks=False)


def star(palette):
    """(12.11) A five-pointed star in the words' style (no cracks), in a save card's colours (cream / red / green)."""
    mask = Image.new("L", (STAR, STAR))
    c, outer, inner = STAR / 2, STAR / 2 - 8, STAR / 2 * 0.42
    points = [(c + math.cos(math.radians(-90 + i * 36)) * (outer if i % 2 == 0 else inner),
               c + 2 + math.sin(math.radians(-90 + i * 36)) * (outer if i % 2 == 0 else inner)) for i in range(10)]
    ImageDraw.Draw(mask).polygon(points, fill=255)
    m = np.array(mask)
    edge = np.array(mask.filter(ImageFilter.MaxFilter(5)))
    return styled(m, edge, STAR * 2, palette, seed=13, cracks=False)


def main():
    for folder in (MAIN, SAVES, ESC, SETTINGS):
        os.makedirs(f"{ROOT}/{folder}", exist_ok=True)
    for i, (name, (text, size, palette, folder)) in enumerate(WORDS.items()):
        word(text, size, palette, seed=i * 7 + 3).save(path(folder, name))
    for kind in ("easy", "normal", "hard", "empty"):
        card(kind).save(path(SAVES, "card_" + kind))
    for name, img in zip(("slider_track", "slider_fill", "slider_knob"), slider_parts()):
        img.save(path(SETTINGS, name))
    for palette in ("cream", "red", "green"):        # a normal / a hard mode / an easy save card
        star(palette).save(path(SAVES, "star_" + palette))
    for kind in ("master", "music", "sounds", "dialogue", "arrow_left", "arrow_right"):
        icon(kind).save(path(SETTINGS, "icon_" + kind))
    print(len(WORDS), "words, the cards, the slider and its icons written to", ROOT)


def path(folder, name):
    return f"{ROOT}/{folder}/{name}.png" if folder else f"{ROOT}/{name}.png"


if __name__ == "__main__":
    main()
