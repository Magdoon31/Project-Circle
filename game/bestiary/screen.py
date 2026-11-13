# THE BESTIARY SCREEN (13.11) - the map's menu (ESC) -> Bestiary. On the left: every enemy, by place (a list you
# scroll: the wheel, W / S or the arrows); on the right: the chosen one's card - its picture in a medallion of its
# place's colour, the name, the place and its kind, the kills, then (5 kills)
# the description and its numbers, then (15 kills) what it drops (a boss: all of it after one win). Seen but never defeated = a dark "???".

import math

import pygame

from game.bestiary.data import ENTRIES, ENTRY, PLACES, PLACE_COLOUR, stages_for
from game.menu import fancy_text as FANCY
from game.menu.sprite_button import SpriteButton, load, scaled
from game.lib import sprites as SPRITES

PICTURES = "assets/img/bestiary/{}.png"   # (13.11) else its fight sprite (combat/bosses, combat/enemies)
TITLE_Y = 0.075
LIST = (0.05, 0.16, 0.30, 0.74)             # the list panel: x, y, width, height (shares of the screen)
CARD = (0.38, 0.16, 0.57, 0.74)             # the card panel
ROW_H = 0.045                               # a row of the list (share of the height)
HEADER_H = 0.05
PANEL, PANEL_EDGE = (16, 10, 26, 215), (120, 96, 160)
TEXT, MUTED, DIM = (236, 228, 214), (170, 150, 200), (95, 85, 115)
EASE = 0.25                                 # how fast the chosen row's highlight follows
SCROLL_STEP = 3                             # rows per wheel notch
KEYS_UP = (pygame.K_UP, pygame.K_w)
KEYS_DOWN = (pygame.K_DOWN, pygame.K_s)


class BestiaryScreen:
    def __init__(self, screen, enemy_db, progress, item_icon, sfx=None):
        self.screen, self.db, self.progress, self.item_icon, self.sfx = screen, enemy_db, progress, item_icon, sfx
        h = screen.get_height()
        self.title = scaled(load("title_bestiary"), h * 0.09)
        self.back_button = SpriteButton("back", h * 0.05)
        self.rows = self.make_rows()               # [("header", place) / ("entry", id)]
        self.selected = next(i for i, r in enumerate(self.rows) if r[0] == "entry")
        self.scroll = 0.0                          # rows scrolled (smooth) ...
        self.scroll_goal = 0.0                     # ... and where it is going
        self.glow = 0.0                            # the highlight bar's y (rows, smooth)
        self.row_rects = []
        self.pictures = {}
        self.timer = 0

    @staticmethod
    def make_rows():
        rows = []
        for key, _, _ in PLACES:
            rows.append(("header", key))
            rows += [("entry", e[0]) for e in ENTRIES if e[2] == key]
        return rows

    # --- input ------------------------------------------------------------------------------------------------
    def open(self):
        self.glow = self.selected

    def handle(self, events, mouse):
        """"back" when it should close, else None."""
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return "back"
                if e.key in KEYS_UP:
                    self.move(-1)
                elif e.key in KEYS_DOWN:
                    self.move(1)
            elif e.type == pygame.MOUSEWHEEL:
                self.scroll_goal = self.clamp_scroll(self.scroll_goal - e.y * SCROLL_STEP)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.back_button.rect.collidepoint(mouse):
                    return "back"
                for i, rect in self.row_rects:
                    if rect.collidepoint(mouse) and self.rows[i][0] == "entry":
                        self.choose(i)
        return None

    def move(self, step):
        i = self.selected + step
        while 0 <= i < len(self.rows) and self.rows[i][0] != "entry":
            i += step
        if 0 <= i < len(self.rows):
            self.choose(i)
            visible = self.visible_rows()
            if i < self.scroll_goal + 1:
                self.scroll_goal = self.clamp_scroll(i - 1)
            elif i > self.scroll_goal + visible - 2:
                self.scroll_goal = self.clamp_scroll(i - visible + 2)

    def choose(self, i):
        if i != self.selected and self.sfx and "hover" in self.sfx.sfx:
            self.sfx.play("hover")
        self.selected = i

    def visible_rows(self):
        return int(LIST[3] / ROW_H) - 1

    def clamp_scroll(self, value):
        return max(0.0, min(float(len(self.rows) - self.visible_rows()), value))

    # --- drawing ----------------------------------------------------------------------------------------------
    def draw(self, mouse=None):
        mouse = mouse or pygame.mouse.get_pos()
        self.timer += 1
        self.scroll += (self.scroll_goal - self.scroll) * EASE
        self.glow += (self.selected - self.glow) * EASE
        w, h = self.screen.get_size()
        self.screen.blit(self.title, self.title.get_rect(center=(w // 2, int(h * TITLE_Y))))
        found = FANCY.font(int(h * 0.024)).render(
            f"Discovered {self.progress.discovered()} / {len(ENTRIES)}", True, MUTED)
        self.screen.blit(found, found.get_rect(center=(w // 2, int(h * (TITLE_Y + 0.055)))))
        self.draw_list(mouse)
        self.draw_card(self.rows[self.selected][1])
        self.back_button.draw(self.screen, (w - w // 10, h - h // 14))

    def panel(self, spec):
        w, h = self.screen.get_size()
        rect = pygame.Rect(int(w * spec[0]), int(h * spec[1]), int(w * spec[2]), int(h * spec[3]))
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, PANEL, surface.get_rect(), 0, 18)
        self.screen.blit(surface, rect)
        pygame.draw.rect(self.screen, PANEL_EDGE, rect, 2, 18)
        return rect

    # --- the list ---------------------------------------------------------------------------------------------
    def draw_list(self, mouse):
        h = self.screen.get_height()
        area = self.panel(LIST)
        row_h = int(h * ROW_H)
        inner = area.inflate(-int(h * 0.02), -int(h * 0.03))
        self.screen.set_clip(inner)
        self.row_rects = []
        bar_y = inner.top + (self.glow - self.scroll) * row_h
        place = PLACE_COLOUR[ENTRY[self.rows[self.selected][1]][2]]
        bar = pygame.Surface((inner.width, row_h), pygame.SRCALPHA)
        pygame.draw.rect(bar, place + (70,), bar.get_rect(), 0, 10)
        pygame.draw.rect(bar, place + (200,), (0, 0, 5, row_h), 0, 3)
        self.screen.blit(bar, (inner.left, int(bar_y)))
        for i, (kind, key) in enumerate(self.rows):
            y = inner.top + (i - self.scroll) * row_h
            if y < inner.top - row_h or y > inner.bottom:
                continue
            rect = pygame.Rect(inner.left, int(y), inner.width, row_h)
            self.row_rects.append((i, rect))
            if kind == "header":
                self.draw_header(key, rect)
            else:
                self.draw_row(key, rect, rect.collidepoint(mouse) and inner.collidepoint(mouse))
        self.screen.set_clip(None)
        self.draw_scrollbar(inner)

    def draw_header(self, place, rect):
        colour = PLACE_COLOUR[place]
        name = next(label for key, label, _ in PLACES if key == place)
        label = FANCY.font(int(rect.height * 0.5)).render(name.upper(), True, colour)
        self.screen.blit(label, label.get_rect(midleft=(rect.left + 8, rect.centery + 2)))
        line_y = rect.centery + 2
        pygame.draw.line(self.screen, colour, (rect.left + label.get_width() + 20, line_y), (rect.right - 8, line_y), 1)

    def draw_row(self, entry_id, rect, hovered):
        known, seen = self.progress.knows(entry_id, "name"), self.progress.seen(entry_id)
        colour = PLACE_COLOUR[ENTRY[entry_id][2]]
        dot = rect.height // 3
        centre = (rect.left + 18 + dot, rect.centery)
        if known:
            pygame.draw.circle(self.screen, colour, centre, dot)
        else:
            pygame.draw.circle(self.screen, DIM, centre, dot, 2)
        name = ENTRY[entry_id][1] if known else "???"
        text_colour = TEXT if known else (MUTED if seen else DIM)
        size = int(rect.height * (0.52 if hovered else 0.48))
        label = FANCY.font(size).render(name, True, text_colour)
        self.screen.blit(label, label.get_rect(midleft=(centre[0] + dot + 14, rect.centery)))
        kills = self.progress.kills(entry_id)
        if kills:
            count = FANCY.font(int(rect.height * 0.4)).render(f"x{kills}", True, MUTED)
            self.screen.blit(count, count.get_rect(midright=(rect.right - 12, rect.centery)))

    def draw_scrollbar(self, inner):
        total, visible = len(self.rows), self.visible_rows()
        if total <= visible:
            return
        track = pygame.Rect(inner.right + 2, inner.top, 4, inner.height)
        pygame.draw.rect(self.screen, (50, 40, 70), track, 0, 2)
        size = max(20, int(track.height * visible / total))
        top = track.top + int((track.height - size) * self.scroll / max(1, total - visible))
        pygame.draw.rect(self.screen, PANEL_EDGE, (track.left, top, 4, size), 0, 2)

    # --- the card ---------------------------------------------------------------------------------------------
    def draw_card(self, entry_id):
        h = self.screen.get_height()
        area = self.panel(CARD)
        pad = int(h * 0.03)
        place = ENTRY[entry_id][2]
        colour = PLACE_COLOUR[place]
        known = self.progress.knows(entry_id, "name")
        size = int(h * 0.2)
        medal = pygame.Rect(area.left + pad, area.top + pad, size, size)
        self.draw_medallion(entry_id, medal, colour, known)
        left = medal.right + pad
        name = FANCY.fancy(ENTRY[entry_id][1] if known else "???", int(h * 0.055))
        self.screen.blit(name, (left, medal.top + int(h * 0.01)))
        chips_y = medal.top + int(h * 0.01) + name.get_height() + int(h * 0.012)
        x = self.chip(next(label for key, label, _ in PLACES if key == place), colour, left, chips_y)
        if known and entry_id in self.db.enemies:
            self.chip(self.db.enemies[entry_id][9].title(), MUTED, x + int(h * 0.012), chips_y)
        self.draw_progress(entry_id, pygame.Rect(left, medal.bottom - int(h * 0.06), area.right - left - pad, int(h * 0.06)), colour)
        y = medal.bottom + pad
        if not self.progress.knows(entry_id, "lore"):
            self.locked_note(area, y, f"Defeat it {stages_for(entry_id)['lore']} times to learn more." if known
                             else "Defeat it to learn what it is.")
            return
        y = self.draw_text(ENTRY[entry_id][3], area.left + pad, y, area.width - 2 * pad)
        y = self.draw_numbers(entry_id, area.left + pad, y + int(h * 0.02), area.width - 2 * pad)
        self.draw_drops(entry_id, area.left + pad, y + int(h * 0.025), area.width - 2 * pad)

    def draw_medallion(self, entry_id, rect, colour, known):
        """A round frame with a soft glow of the place's colour; inside its picture (or a drawn token / "?")."""
        pulse = 0.5 + 0.5 * math.sin(self.timer / 30)
        glow = pygame.Surface((rect.width * 2, rect.height * 2), pygame.SRCALPHA)
        for r in range(rect.width, rect.width // 2, -4):
            alpha = int(40 * (1 - (r - rect.width / 2) / (rect.width / 2)) * (0.7 + 0.3 * pulse))
            pygame.draw.circle(glow, colour + (alpha,), glow.get_rect().center, r)
        self.screen.blit(glow, glow.get_rect(center=rect.center))
        pygame.draw.circle(self.screen, (28, 20, 40), rect.center, rect.width // 2)
        picture = self.picture(entry_id, rect.width - 24, colour) if known else None
        if picture:
            self.screen.blit(picture, picture.get_rect(center=rect.center))
        else:
            mark = FANCY.fancy("?", int(rect.height * 0.5), "pale")
            self.screen.blit(mark, mark.get_rect(center=rect.center))
        pygame.draw.circle(self.screen, colour if known else DIM, rect.center, rect.width // 2, 4)
        pygame.draw.circle(self.screen, (255, 255, 255), rect.center, rect.width // 2 - 7, 1)

    def picture(self, entry_id, size, colour):
        key = (entry_id, size)
        if key not in self.pictures:
            raw = SPRITES.first(f"bestiary/{entry_id}", f"combat/bosses/{entry_id}", f"combat/enemies/{entry_id}")
            self.pictures[key] = fit_picture(raw, size) if raw else token(ENTRY[entry_id][1], size, colour)
        return self.pictures[key]

    def chip(self, text, colour, x, y):
        h = self.screen.get_height()
        label = FANCY.font(int(h * 0.02)).render(text, True, colour)
        rect = label.get_rect(topleft=(x, y)).inflate(int(h * 0.02), int(h * 0.008))
        rect.topleft = (x, y)
        pygame.draw.rect(self.screen, colour, rect, 1, rect.height // 2)
        self.screen.blit(label, label.get_rect(center=rect.center))
        return rect.right

    def draw_progress(self, entry_id, rect, colour):
        """How many of it you have defeated (13.11: only the number)."""
        h = self.screen.get_height()
        label = FANCY.font(int(h * 0.024)).render(f"Defeated: {self.progress.kills(entry_id)}", True, TEXT)
        self.screen.blit(label, label.get_rect(bottomleft=rect.bottomleft))
        return rect.bottom

    def locked_note(self, area, y, text):
        h = self.screen.get_height()
        label = FANCY.font(int(h * 0.024)).render(text, True, DIM)
        self.screen.blit(label, label.get_rect(midtop=(area.centerx, y + int(h * 0.05))))

    def draw_text(self, text, x, y, width):
        font = FANCY.font(int(self.screen.get_height() * 0.027))
        for line in wrap(text, font, width):
            self.screen.blit(font.render(line, True, TEXT), (x, y))
            y += int(font.get_linesize() * 1.1)
        return y

    def draw_numbers(self, entry_id, x, y, width):
        """Small boxes in a row: HP, defence, touch, shots, kind."""
        h = self.screen.get_height()
        stats = numbers(self.db, entry_id)
        gap, box_h = int(h * 0.012), int(h * 0.075)
        box_w = (width - (len(stats) - 1) * gap) // len(stats)
        for n, (label, value) in enumerate(stats):
            box = pygame.Rect(x + n * (box_w + gap), y, box_w, box_h)
            pygame.draw.rect(self.screen, (34, 26, 50), box, 0, 10)
            pygame.draw.rect(self.screen, (70, 58, 96), box, 1, 10)
            small = FANCY.font(int(h * 0.018)).render(label, True, MUTED)
            big = FANCY.fancy(value, int(h * 0.032))
            if big.get_width() > box_w - 10:                      # a long number: smaller, to fit its box
                big = pygame.transform.smoothscale(big, (box_w - 10, int(big.get_height() * (box_w - 10) / big.get_width())))
            self.screen.blit(small, small.get_rect(midtop=(box.centerx, box.top + int(h * 0.008))))
            self.screen.blit(big, big.get_rect(midbottom=(box.centerx, box.bottom - int(h * 0.006))))
        return y + box_h

    def draw_drops(self, entry_id, x, y, width):
        h = self.screen.get_height()
        drops = self.db.drops.get(entry_id, [])
        title = FANCY.font(int(h * 0.022)).render("DROPS", True, MUTED)
        self.screen.blit(title, (x, y))
        y += title.get_height() + int(h * 0.008)
        if not self.progress.knows(entry_id, "drops"):
            note = f"Defeat it {stages_for(entry_id)['drops']} times to see what it drops."
            self.screen.blit(FANCY.font(int(h * 0.022)).render(note, True, DIM), (x, y))
            return
        if not drops:
            self.screen.blit(FANCY.font(int(h * 0.022)).render("Nothing.", True, DIM), (x, y))
            return
        size = int(h * 0.055)
        for n, (item, chance) in enumerate(drops):
            cell = pygame.Rect(x + (n % 2) * (width // 2), y + (n // 2) * (size + int(h * 0.01)), width // 2, size)
            got = self.progress.got_drop(entry_id, item)
            icon_rect = pygame.Rect(cell.left, cell.top, size, size)
            pygame.draw.rect(self.screen, (34, 26, 50), icon_rect, 0, 8)
            pygame.draw.rect(self.screen, (70, 58, 96), icon_rect, 1, 8)
            icon = self.icon(item) if got else None
            if icon:
                self.screen.blit(icon, icon.get_rect(center=icon_rect.center))
            else:
                mark = FANCY.font(int(size * 0.5)).render("?", True, DIM)
                self.screen.blit(mark, mark.get_rect(center=icon_rect.center))
            label = FANCY.font(int(h * 0.022)).render(item if got else "???", True, TEXT if got else DIM)
            odds = FANCY.font(int(h * 0.018)).render(f"{chance * 100:g}%", True, MUTED)
            self.screen.blit(label, (icon_rect.right + 10, cell.top + 2))
            self.screen.blit(odds, (icon_rect.right + 10, cell.top + 4 + label.get_height()))

    def icon(self, item):
        try:
            picture = self.item_icon(item)
        except AttributeError:
            return None
        size = int(self.screen.get_height() * 0.045)
        return pygame.transform.smoothscale(picture, (size, size)) if picture else None


# --- helpers -----------------------------------------------------------------------------------------------------
def numbers(db, entry_id):
    """[(label, value)] - its HP, defence, touch damage, strongest shot and kind (from EnemyDB)."""
    raw = db.enemies.get(entry_id) or db.bosses.get(entry_id)
    if raw is None:
        return [("HP", "-"), ("Defence", "-"), ("Touch", "-"), ("Shots", "-"), ("Kind", "Song")]
    attacks = [raw[-1]] + [p.get("attacks", {}) for p in db.boss_info.get(entry_id, {}).get("phases", [])]
    shot = max((d for a in attacks for d in damages(a)), default=0)
    return [("HP", f"{round(raw[2]):,}"), ("Defence", defence_text(raw[8])), ("Touch", f"{round(raw[6]):,} DMG"), ("Shots", f"{shot:,} DMG" if shot else "-"),
            ("Kind", raw[9].title())]


def fit_picture(name, size):
    """(13.11) A Bestiary picture inside a size x size square, its shape kept; pixel art (the fight sprites) hard."""
    raw = SPRITES.load(name)
    w, h = raw.get_size()
    k = size / max(w, h)
    pixel_art = not name.startswith("bestiary/")
    return SPRITES.to_size(name, (w * k, h * k), smooth=not pixel_art)


def defence_text(defence):
    """(13.11) Defence as the enemy has it ("-" when none); damage taken = x 100 / (100 + defence)."""
    return f"{round(defence):,}" if defence > 0 else "-"


def damages(spec):
    for value in spec.values():
        if isinstance(value, dict):
            if isinstance(value.get("damage"), (int, float)):
                yield int(value["damage"])
            yield from damages(value)


def wrap(text, font, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if font.size(test)[0] > width and line:
            lines.append(line)
            line = word
        else:
            line = test
    return lines + [line] if line else lines


def token(name, size, colour):
    """A drawn picture while there is no sprite: a soft ball of the place's colour with the name's initials."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    centre = (size // 2, size // 2)
    for r in range(size // 2, 0, -2):
        k = r / (size / 2)
        shade = tuple(int(c * (0.55 + 0.45 * (1 - k))) for c in colour)
        pygame.draw.circle(surface, shade, (centre[0] - int((1 - k) * size * 0.08), centre[1] - int((1 - k) * size * 0.08)), r)
    initials = "".join(part[0] for part in name.replace("-", " ").split()[:2]).upper()
    letters = FANCY.fancy(initials, int(size * 0.32))
    surface.blit(letters, letters.get_rect(center=centre))
    return surface
