# THE ACHIEVEMENTS SCREEN (13.11): the achievements as icons, a page of 5 x 3 at a time (the arrows / Left, Right
# turn the pages), in the list's order; reached = in colour, not yet = grey, a hidden one not yet = "???". Under the
# mouse: its name, what to do and - in a game, for the counted ones - how far this save is. Opened from the main menu
# (Achievements) and from the map's menu (ESC).

import pygame

from game.achievements.book import BOOK
from game.achievements.data import ACHIEVEMENTS
from game.achievements.icons import icon
from game.menu import fancy_text as FANCY
from game.menu.sprite_button import SpriteButton, load, scaled

COLUMNS, ROWS = 5, 3
PER_PAGE = COLUMNS * ROWS
ICON = 0.15                       # an icon's size, share of the screen's height
GAP = 0.03
GRID_TOP = 0.22
ARROW_H = 0.07
GRID_HALF = (COLUMNS * ICON + (COLUMNS - 1) * GAP) / 2       # half the grid's width (share of the height)
ARROW_GAP = 0.08                  # the arrows: this far out from the grid's sides (share of the height)
TITLE_Y = 0.09
INFO_Y = 0.89                     # the description under the grid
HOVER_GROW = 1.12
HOVER_FRAMES = 9                  # (13.11) 0.15 s to grow / shrink
TEXT, MUTED, DONE = (236, 228, 214), (170, 150, 200), (150, 226, 160)
HIDDEN_TEXT = "A hidden achievement."
TURN_KEYS = {pygame.K_LEFT: -1, pygame.K_a: -1, pygame.K_RIGHT: 1, pygame.K_d: 1}


class AchievementsScreen:
    def __init__(self, screen, sfx=None, progress=None):
        """progress: counter -> this save's number (None in the main menu: no save is open)."""
        self.screen, self.sfx, self.progress = screen, sfx, progress
        h = screen.get_height()
        self.title = scaled(load("title_achievements"), h * 0.1)
        self.back_button = SpriteButton("back", h * 0.05)
        self.arrows = {-1: scaled(load("settings/icon_arrow_left"), h * ARROW_H),
                       1: scaled(load("settings/icon_arrow_right"), h * ARROW_H)}
        self.arrow_rects = {}
        self.page = 0
        self.growth = {}                  # (13.11) id -> its size now (1 .. HOVER_GROW)
        self.hovered = None

    @property
    def pages(self):
        return (len(ACHIEVEMENTS) + PER_PAGE - 1) // PER_PAGE

    def turn(self, step):
        page = max(0, min(self.pages - 1, self.page + step))
        if page != self.page:
            self.page = page
            if self.sfx and "hover" in self.sfx.sfx:
                self.sfx.play("hover")

    # --- input ------------------------------------------------------------------------------------------------
    def handle(self, events, mouse):
        """"back" when it should close (Back or Esc), else None."""
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "back"
            if e.type == pygame.KEYDOWN and e.key in TURN_KEYS:
                self.turn(TURN_KEYS[e.key])
            if e.type == pygame.MOUSEWHEEL:
                self.turn(-e.y)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for step, rect in self.arrow_rects.items():
                    if rect.collidepoint(mouse):
                        self.turn(step)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.back_button.rect.collidepoint(mouse):
                if self.sfx:
                    self.sfx.play("use") if "use" in self.sfx.sfx else None
                return "back"
        return None

    # --- drawing ----------------------------------------------------------------------------------------------
    def draw(self, mouse=None):
        mouse = mouse or pygame.mouse.get_pos()
        w, h = self.screen.get_size()
        self.screen.blit(self.title, self.title.get_rect(center=(w // 2, int(h * TITLE_Y))))
        count = sum(BOOK.has(a["id"]) for a in ACHIEVEMENTS)
        tally = FANCY.fancy(f"{count} / {len(ACHIEVEMENTS)}", int(h * 0.035))
        self.screen.blit(tally, tally.get_rect(center=(w // 2, int(h * (TITLE_Y + 0.07)))))
        self.hovered = None
        shown = ACHIEVEMENTS[self.page * PER_PAGE:(self.page + 1) * PER_PAGE]
        for i, achievement in enumerate(shown):
            rect = self.cell(i)
            if rect.collidepoint(mouse):
                self.hovered = achievement
            self.draw_icon(achievement, rect, self.grow(achievement["id"], rect.collidepoint(mouse)))
        self.draw_arrows(mouse)
        self.draw_info(self.hovered)
        self.back_button.draw(self.screen, (w - w // 10, h - h // 14))

    def draw_arrows(self, mouse):
        w, h = self.screen.get_size()
        middle_y = int(h * GRID_TOP) + (ROWS * int(h * ICON) + (ROWS - 1) * int(h * GAP)) // 2
        self.arrow_rects = {}
        for step, picture in self.arrows.items():
            if not 0 <= self.page + step < self.pages:
                continue                                  # no page that way
            rect = picture.get_rect(center=(w // 2 + step * int(h * (GRID_HALF + ARROW_GAP)), middle_y))
            self.arrow_rects[step] = rect
            if rect.collidepoint(mouse):
                grown = pygame.transform.smoothscale_by(picture, HOVER_GROW)
                self.screen.blit(grown, grown.get_rect(center=rect.center))
            else:
                self.screen.blit(picture, rect)
        number = FANCY.font(int(h * 0.028)).render(f"{self.page + 1} / {self.pages}", True, MUTED)
        grid_bottom = int(h * GRID_TOP) + ROWS * int(h * ICON) + (ROWS - 1) * int(h * GAP)
        self.screen.blit(number, number.get_rect(midtop=(w // 2, grid_bottom + int(h * 0.015))))

    def cell(self, i):
        w, h = self.screen.get_size()
        size, gap = int(h * ICON), int(h * GAP)
        left = w // 2 - (COLUMNS * size + (COLUMNS - 1) * gap) // 2
        return pygame.Rect(left + (i % COLUMNS) * (size + gap), int(h * GRID_TOP) + (i // COLUMNS) * (size + gap),
                           size, size)

    def grow(self, achievement_id, hovered):
        """(13.11) How big an icon is now: it grows under the mouse (and back) in HOVER_FRAMES."""
        step = (HOVER_GROW - 1) / HOVER_FRAMES
        now = self.growth.get(achievement_id, 1.0)
        now = min(HOVER_GROW, now + step) if hovered else max(1.0, now - step)
        self.growth[achievement_id] = now
        return now

    def draw_icon(self, achievement, rect, scale):
        reached = BOOK.has(achievement["id"])
        size = int(rect.width * scale)
        if reached:
            picture = icon(achievement["id"], size)
        elif achievement.get("hidden"):
            picture = icon("locked", size, dim=True)
        else:
            picture = icon(achievement["id"], size, dim=True)
        self.screen.blit(picture, picture.get_rect(center=rect.center))

    def draw_info(self, achievement):
        if achievement is None:
            return
        w, h = self.screen.get_size()
        reached = BOOK.has(achievement["id"])
        secret = achievement.get("hidden") and not reached
        name = FANCY.fancy("???" if secret else achievement["name"], int(h * 0.04))
        text = HIDDEN_TEXT if secret else achievement["text"]
        line = FANCY.font(int(h * 0.026)).render(text + self.status(achievement, reached), True,
                                                 DONE if reached else TEXT)
        top = int(h * INFO_Y) - name.get_height()
        self.screen.blit(name, name.get_rect(midbottom=(w // 2, top + name.get_height())))
        self.screen.blit(line, line.get_rect(midtop=(w // 2, top + name.get_height() + int(h * 0.008))))

    def status(self, achievement, reached):
        if reached:
            return "   - unlocked"
        goal = achievement.get("goal")
        if goal and self.progress and not achievement.get("hidden"):
            now = min(self.progress(goal[0]), goal[1])
            return f"   ({now:,} / {goal[1]:,})"
        return ""
