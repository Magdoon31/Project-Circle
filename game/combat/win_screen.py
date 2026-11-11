# THE WIN SCREEN (11.11): after a won fight - the fight dimmed behind a panel in the biome's colour (faded; darkened
# in bright biomes): "Victory", the gold counting up, "Flawless!!", a small table of the beaten enemies (a circle in
# its colour - later a small sprite -, how many, the gold from them, the icons of what they dropped) and the new
# items popping out one by one.
#   - one click skips the animations, the next one closes it (Game asks click()).
# Combat collects what happened (Defeated rows) and gives the summary; here only the timing and the drawing.

import pygame

PANEL_W = 0.36                    # share of the screen's width (its height: as much as is in it)
MARGIN = 24                       # px above the title and under the hint
DIM = 150                         # how dark the fight behind gets (alpha)
FADE_GREY = (120, 120, 128)       # the biome's colour is mixed with this (faded) ...
FADE_SHARE = 0.55
BRIGHT = 110                      # ... and darkened when it is still this bright (light biomes: a dark panel,
DARKEN = 0.5                      #     the rarity colours and Flawless stay readable)
COUNT_FRAMES = 60                 # the gold counts up this long
COIN_EVERY = 5                    # frames between two coin ticks while counting
ROW_FRAMES = 8                    # a table row comes in this long after the one before
ITEM_FRAMES = 24                  # an item pops this long after the one before
POP_FRAMES = 14                   # an item's pop (grows, flashes)
MIN_FRAMES = 30                   # it can't be closed earlier (a stray click while fighting)
ICON = 64                         # px: a new item's icon
SMALL_ICON = 30                   # px: a drop's icon in the table
BODY = 13                         # px: an enemy's circle in the table
RARITY_COLOURS = {"common": (225, 225, 230), "medium": (120, 200, 255), "rare": (255, 205, 90)}
FLAWLESS_COLOUR = (255, 230, 120)


class Defeated:
    """One row of the table: one kind of enemy."""

    def __init__(self, name, title, colour):
        self.name, self.title, self.colour = name, title, colour
        self.count = 0
        self.gold = 0
        self.drops = []


class WinScreen:
    def __init__(self, fonts, panel_colour, total_gold, flawless, rows, items, item_icon, rarity, sfx):
        self.fonts = fonts                        # {"title", "big", "text", "small"}
        self.panel_colour = faded(panel_colour)
        self.ink = ink_for(self.panel_colour)
        self.total_gold, self.flawless = total_gold, flawless
        self.rows, self.items = rows, items
        self.item_icon, self.rarity = item_icon, rarity      # name -> Surface / "common" | "medium" | "rare"
        self.sfx = sfx
        self.timer = 0
        self.items_from = COUNT_FRAMES + ROW_FRAMES * len(rows)
        self.end = self.items_from + ITEM_FRAMES * len(items) + POP_FRAMES

    # --- the timing ---------------------------------------------------------------------------------------------
    def update(self):
        self.timer += 1
        if self.timer <= COUNT_FRAMES and self.timer % COIN_EVERY == 0 and self.total_gold:
            self.sfx.play("coin_pickup", 0.35)
        for i in range(len(self.items)):
            if self.timer == self.items_from + ITEM_FRAMES * i:
                self.sfx.play("new_item")

    def click(self):
        """True = close it. The first click only skips the animations."""
        if self.timer < MIN_FRAMES:
            return False
        if self.timer < self.end:
            self.timer = self.end
            return False
        return True

    def gold_now(self):
        return int(self.total_gold * min(1.0, self.timer / COUNT_FRAMES))

    # --- drawing ------------------------------------------------------------------------------------------------
    def draw(self, screen):
        w, h = screen.get_size()
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        veil.fill((0, 0, 0, DIM))
        screen.blit(veil, (0, 0))
        panel = pygame.Rect(0, 0, int(w * PANEL_W), min(h - 40, self.height()))
        panel.center = (w // 2, h // 2)
        pygame.draw.rect(screen, self.panel_colour, panel, 0, 16)
        pygame.draw.rect(screen, mix(self.panel_colour, self.ink, 0.35), panel, 4, 16)
        y = self.draw_header(screen, panel)
        y = self.draw_table(screen, panel, y)
        self.draw_items(screen, panel, y)
        self.draw_hint(screen, panel)

    def height(self):
        """How tall the panel must be for everything in it (the title, the gold, Flawless, the table, the items,
        the hint)."""
        line = {name: line_height(font) for name, font in self.fonts.items()}
        header = line["title"] + 4 + line["big"] + (line["text"] if self.flawless else 0)
        table = len(self.rows) * (max(SMALL_ICON, BODY * 2) + 8) + 30
        items = line["text"] + ICON + 14 + line["small"] if self.items else 0
        return MARGIN + header + table + items + 20 + line["small"] + MARGIN

    def draw_header(self, screen, panel):
        y = panel.top + MARGIN
        y = self.text(screen, "title", "Victory", self.ink, panel.centerx, y)
        y = self.text(screen, "big", f"+{self.gold_now()}$", self.ink, panel.centerx, y + 4)
        if self.flawless and self.timer >= COUNT_FRAMES:
            y = self.text(screen, "text", "Flawless!!", FLAWLESS_COLOUR, panel.centerx, y)
        return y + 16

    def draw_table(self, screen, panel, y):
        """Each kind of beaten enemy: its circle, x how many, the gold from it, the icons of its drops."""
        left, right = panel.left + 40, panel.right - 40
        line = max(SMALL_ICON, BODY * 2) + 8
        for i, row in enumerate(self.rows):
            if self.timer < COUNT_FRAMES + ROW_FRAMES * i:
                break
            cy = y + line // 2
            pygame.draw.circle(screen, row.colour, (left + BODY, cy), BODY)
            label = self.fonts["small"].render(f"{row.title}  x{row.count}", True, self.ink)
            screen.blit(label, label.get_rect(midleft=(left + BODY * 2 + 12, cy)))
            gold = self.fonts["small"].render(f"{row.gold}$" if row.gold else "-", True, self.ink)
            gold_rect = gold.get_rect(midright=(right - (SMALL_ICON + 6) * max(1, len(row.drops)) - 10, cy))
            screen.blit(gold, gold_rect)
            for k, name in enumerate(row.drops):
                icon = pygame.transform.smoothscale(self.item_icon(name), (SMALL_ICON, SMALL_ICON))
                screen.blit(icon, icon.get_rect(midright=(right - (SMALL_ICON + 6) * k, cy)))
            y += line
        return y + 14

    def draw_items(self, screen, panel, y):
        """The new items: they pop out one after another (bigger, a flash), the name in its rarity's colour."""
        shown = [n for i, n in enumerate(self.items) if self.timer >= self.items_from + ITEM_FRAMES * i]
        if not shown:
            return
        y = self.text(screen, "text", "New items", self.ink, panel.centerx, y)
        gap = ICON + 70
        x0 = panel.centerx - gap * (len(self.items) - 1) / 2
        for i, name in enumerate(shown):
            age = self.timer - (self.items_from + ITEM_FRAMES * i)
            k = min(1.0, age / POP_FRAMES)
            size = max(1, int(ICON * (0.4 + 0.6 * k + 0.25 * k * (1 - k) * 4)))
            cx, cy = int(x0 + gap * i), y + ICON // 2 + 6
            colour = RARITY_COLOURS[self.rarity(name)]
            if k < 1:
                pygame.draw.circle(screen, colour, (cx, cy), int(ICON * 0.9 * (1 - k)) + 2, 3)
            icon = pygame.transform.smoothscale(self.item_icon(name), (size, size))
            screen.blit(icon, icon.get_rect(center=(cx, cy)))
            self.text(screen, "small", name, colour, cx, cy + ICON // 2 + 8)

    def draw_hint(self, screen, panel):
        hint = "click" if self.timer >= self.end else "click to skip"
        img = self.fonts["small"].render(hint, True, mix(self.panel_colour, self.ink, 0.6))
        screen.blit(img, img.get_rect(midbottom=(panel.centerx, panel.bottom - MARGIN)))

    def text(self, screen, font, words, colour, cx, top):
        img = self.fonts[font].render(words, True, colour)
        screen.blit(img, img.get_rect(midtop=(cx, top)))
        return top + img.get_height()


def line_height(font):
    """How tall a rendered line really is (a bit more than font.get_height() for some fonts)."""
    return font.render("Ag", True, (0, 0, 0)).get_height()


# --- colours ----------------------------------------------------------------------------------------------------
def mix(a, b, share):
    return tuple(int(a[i] + (b[i] - a[i]) * share) for i in range(3))


def brightness(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def faded(colour):
    """The biome's colour, faded; darkened if it is still bright (so the text can be read)."""
    c = mix(colour, FADE_GREY, FADE_SHARE)
    if brightness(c) > BRIGHT:
        c = tuple(int(v * DARKEN) for v in c)
    return c


def ink_for(colour):
    return (20, 20, 26) if brightness(colour) > 140 else (245, 245, 250)
