# THE SAVE SCREEN (11.11): Play -> the 3 save slots as cards (the pictures: tools/make_menu_sprites.py).
#   slots    - each card: its name, where you are, time played, gold, the world's seed; hard mode = a red card,
#              (12.11) "I Have a Job" (easy) = a green one;
#              an empty slot = a faint card. Under a used card: Delete. A card lifts up under the mouse.
#   slot     - a used slot: Continue / New Game (asks first: it starts over) / Back.
#   confirm  - "Delete this save?" / "Start over on this slot?": Yes / No.
#   new_save - a name and a seed (both typed; Tab or a click changes the field), then I Have a Job / Normal / Hard
#              Mode starts it (game/difficulty.py).
# handle() -> ("start_game", slot, difficulty) / ("back",) / None. ESC = Back.

import pygame

from game.menu import fancy_text as FANCY
from game.menu.sprite_button import SpriteButton, load, scaled
from game.menu.save_manager import seed_from_text
from game import difficulty as DIFF

SLOTS = 3
CARD_W = 0.22                     # share of the screen's width
CARD_RATIO = 620 / 480            # the card picture's height / width
CARD_GAP = 0.035
CARD_TOP = 0.25                   # share of the screen's height
LIFT = 14                         # px a card goes up under the mouse
EASE = 0.2
BUTTON_H = 0.06                  # a button's height (share of the screen's height; the whole font height)
SMALL_BUTTON_H = 0.042
TITLE_H = 0.11
STAR_SIZE, STAR_GAP, STAR_Y = 46, 10, 506     # (12.11) the ending stars, in the 480 x 620 card picture's px
NAME_MAX, SEED_MAX = 20, 24
DIFFICULTY_BUTTONS = {"btn_i_have_a_job": DIFF.EASY, "btn_normal": DIFF.NORMAL, "btn_hard_mode": DIFF.HARD}   # (12.11)
FIELD_COLOUR, FIELD_EDGE, FIELD_FOCUS = (24, 16, 38), (120, 96, 160), (250, 246, 222)
INFO_COLOUR, LABEL_COLOUR = (236, 228, 214), (170, 150, 200)


class SaveScreen:
    def __init__(self, screen, sfx, save_manager):
        self.screen, self.sfx, self.saves = screen, sfx, save_manager
        w, h = screen.get_size()
        self.card_size = (int(w * CARD_W), int(w * CARD_W * CARD_RATIO))
        self.cards = {kind: pygame.transform.smoothscale(load("saves/card_" + kind), self.card_size)
                      for kind in DIFF.LEVELS + ("empty",)}
        self.titles = {name: scaled(load("saves/" + name), h * TITLE_H * (0.75 if name.startswith("title_sure") else 1))
                       for name in ("title_saves", "title_new_save", "title_sure_delete", "title_sure_overwrite")}
        self.labels = {name: scaled(load("saves/" + name), h * 0.05) for name in ("label_name", "label_seed")}
        self.buttons = {"btn_" + name: SpriteButton(name, h * BUTTON_H, "saves")
                        for name in ("continue", "new_game", "yes", "no", "i_have_a_job", "normal", "hard_mode")}
        self.buttons["btn_back"] = SpriteButton("back", h * SMALL_BUTTON_H * 1.2)
        self.deletes = [SpriteButton("delete", h * SMALL_BUTTON_H, "saves") for _ in range(SLOTS)]
        self.stars = {}                            # (12.11) the ending stars ("cream" / "red" / "green"), scaled to the cards
        self.lift = [0.0] * SLOTS
        self.hovered = None                       # what is under the mouse (for the hover sound)
        self.open()

    # --- the pages --------------------------------------------------------------------------------------------
    def open(self):
        self.page = "slots"
        self.slot = None
        self.asking = None                        # "delete" / "overwrite" on the confirm page
        self.infos = [self.saves.slot_info(nr) for nr in range(1, SLOTS + 1)]

    def go_to_new_save(self):
        self.page = "new_save"
        self.name_text, self.seed_text, self.focus = "", "", "name"
        pygame.key.start_text_input()

    def leave_new_save(self):
        pygame.key.stop_text_input()

    # --- input ------------------------------------------------------------------------------------------------
    def handle(self, events, pos):
        """-> ("start_game", slot, difficulty) / ("back",) / None"""
        self.hover_sound(pos)
        for event in events:
            if self.page == "new_save":
                self.type(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return self.back()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self.click(pos)
                if result:
                    return result
        return None

    def click(self, pos):
        if self.buttons["btn_back"].rect.collidepoint(pos):
            return self.back()
        return {"slots": self.click_slots, "slot": self.click_slot, "confirm": self.click_confirm,
                "new_save": self.click_new_save}[self.page](pos)

    def back(self):
        if self.page == "slots":
            return ("back",)
        if self.page == "new_save":
            self.leave_new_save()
        self.open()
        return None

    def click_slots(self, pos):
        for i in range(SLOTS):
            if self.infos[i] and self.deletes[i].rect.collidepoint(pos):
                self.slot, self.asking, self.page = i + 1, "delete", "confirm"
                return None
            if self.card_rect(i).collidepoint(pos):
                self.slot = i + 1
                if self.infos[i]:
                    self.page = "slot"
                else:
                    self.go_to_new_save()
                return None
        return None

    def click_slot(self, pos):
        if self.buttons["btn_continue"].rect.collidepoint(pos):
            return ("start_game", self.slot, self.infos[self.slot - 1]["difficulty"])
        if self.buttons["btn_new_game"].rect.collidepoint(pos):
            self.asking, self.page = "overwrite", "confirm"
        return None

    def click_confirm(self, pos):
        if self.buttons["btn_no"].rect.collidepoint(pos):
            self.open()
        elif self.buttons["btn_yes"].rect.collidepoint(pos):
            if self.asking == "delete":
                self.saves.reset_data(self.slot)
                self.open()
            else:
                self.go_to_new_save()
        return None

    def click_new_save(self, pos):
        for field, rect in self.field_rects().items():
            if rect.collidepoint(pos):
                self.focus = field
        for name, difficulty in DIFFICULTY_BUTTONS.items():
            if self.buttons[name].rect.collidepoint(pos):
                return self.start_new(difficulty)
        return None

    def start_new(self, difficulty):
        self.saves.reset_data(self.slot)
        seed = self.seed_text.strip()
        self.saves.pending_seed = (seed_from_text(seed), seed)
        self.saves.pending_name = self.name_text.strip() or f"Save {self.slot}"
        self.leave_new_save()
        return ("start_game", self.slot, difficulty)

    def type(self, event):
        """Typing into the name / the seed field."""
        limit = NAME_MAX if self.focus == "name" else SEED_MAX
        text = self.name_text if self.focus == "name" else self.seed_text
        if event.type == pygame.TEXTINPUT:
            text = (text + "".join(c for c in event.text if c.isprintable()))[:limit]
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            text = text[:-1]
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.focus = "seed" if self.focus == "name" else "name"
            return
        if self.focus == "name":
            self.name_text = text
        else:
            self.seed_text = text

    def hover_sound(self, pos):
        under = None
        for key, rect in self.clickable():
            if rect.collidepoint(pos):
                under = key
        if under is not None and under != self.hovered:
            self.sfx.play("hover")
        self.hovered = under

    def clickable(self):
        items = [("back", self.buttons["btn_back"].rect)]
        if self.page == "slots":
            items += [(("card", i), self.card_rect(i)) for i in range(SLOTS)]
            items += [(("delete", i), self.deletes[i].rect) for i in range(SLOTS) if self.infos[i]]
        else:
            items += [(name, self.buttons[name].rect) for name in self.page_buttons()]
        return items

    def page_buttons(self):
        return {"slot": ["btn_continue", "btn_new_game"], "confirm": ["btn_yes", "btn_no"],
                "new_save": list(DIFFICULTY_BUTTONS)}.get(self.page, [])

    # --- where things are ---------------------------------------------------------------------------------------
    def card_rect(self, i, lift=0.0):
        w, h = self.screen.get_size()
        cw, ch = self.card_size
        gap = w * CARD_GAP
        x = w / 2 - (cw * SLOTS + gap * (SLOTS - 1)) / 2 + i * (cw + gap)
        return pygame.Rect(int(x), int(h * CARD_TOP - lift), cw, ch)

    def field_rects(self):
        w, h = self.screen.get_size()
        fw, fh = int(w * 0.32), int(h * 0.07)
        return {"name": pygame.Rect(w // 2 - fw // 2, int(h * 0.33), fw, fh),
                "seed": pygame.Rect(w // 2 - fw // 2, int(h * 0.50), fw, fh)}

    # --- drawing ------------------------------------------------------------------------------------------------
    def draw(self):
        mouse = pygame.mouse.get_pos()
        {"slots": self.draw_slots, "slot": self.draw_slot, "confirm": self.draw_confirm,
         "new_save": self.draw_new_save}[self.page](mouse)
        w, h = self.screen.get_size()
        back = self.buttons["btn_back"]
        back.draw(self.screen, (w - w // 10, h - h // 14), back.rect.collidepoint(mouse))

    def draw_title(self, name, y_share=0.12):
        w, h = self.screen.get_size()
        img = self.titles[name]
        self.screen.blit(img, img.get_rect(center=(w // 2, int(h * y_share))))

    def draw_slots(self, mouse):
        self.draw_title("title_saves")
        for i in range(SLOTS):
            hovered = self.card_rect(i, self.lift[i]).collidepoint(mouse)
            self.lift[i] += ((LIFT if hovered else 0) - self.lift[i]) * EASE
            rect = self.card_rect(i, self.lift[i])
            self.draw_card(rect, self.infos[i])
            if self.infos[i]:
                delete = self.deletes[i]
                below = self.card_rect(i)
                delete.draw(self.screen, (below.centerx, below.bottom + int(self.screen.get_height() * 0.05)),
                            delete.rect.collidepoint(mouse))

    def draw_card(self, rect, info):
        kind = "empty" if info is None else info["difficulty"]
        self.screen.blit(self.cards[kind], rect)
        k = rect.width / 480                                    # the card picture is 480 px wide
        if info is None:
            self.blit_center(FANCY.fancy("Empty", int(44 * k), "pale"), rect.centerx, rect.y + int(260 * k))
            self.blit_center(FANCY.fancy("New Save", int(28 * k), "pale"), rect.centerx, rect.y + int(330 * k))
            return
        style = DIFF.CARD_STYLE[info["difficulty"]]
        self.blit_center(FANCY.fancy(info["name"], int(fit_size(info["name"], 52) * k), style), rect.centerx,
                         rect.y + int(92 * k))
        self.blit_center(FANCY.fancy(info["place"], int(36 * k), style), rect.centerx, rect.y + int(212 * k))
        hours, minutes = info["time"] // 3600, (info["time"] // 60) % 60
        rows = [("Time played", f"{hours}:{minutes:02d}"), ("Gold", f"{info['money']}$")]
        for n, (label, value) in enumerate(rows):
            y = rect.y + int((292 + n * 104) * k)
            self.blit_center(FANCY.font(int(25 * k)).render(label, True, LABEL_COLOUR), rect.centerx, y)
            self.blit_center(FANCY.fancy(value, int(44 * k), style), rect.centerx, y + int(44 * k))
        self.draw_stars(rect, k, info["stars"], style)
        if info["seed"]:
            seed = FANCY.font(int(21 * k)).render(f"Seed: {info['seed']}", True, LABEL_COLOUR)
            self.blit_center(seed, rect.centerx, rect.bottom - int(52 * k))

    def draw_stars(self, rect, k, reached, style):
        """(12.11) A star at the bottom middle for every ending reached on this save (Main, Extra, Secret), in the
        card's colours; none reached = nothing there at all."""
        count = sum(reached)
        if not count:
            return
        size, gap = int(STAR_SIZE * k), int(STAR_GAP * k)
        star = self.star(style, size)
        left = rect.centerx - (size * count + gap * (count - 1)) // 2
        for n in range(count):
            self.screen.blit(star, (left + n * (size + gap), rect.y + int(STAR_Y * k) - size // 2))

    def star(self, style, size):
        if style not in self.stars or self.stars[style].get_height() != size:
            self.stars[style] = scaled(load("saves/star_" + style), size)
        return self.stars[style]

    def draw_slot(self, mouse):
        w, h = self.screen.get_size()
        info = self.infos[self.slot - 1]
        self.blit_center(FANCY.fancy(info["name"], int(h * 0.075), DIFF.CARD_STYLE[info["difficulty"]]),
                         w // 2, int(h * 0.2))
        self.draw_buttons(mouse, 0.45)

    def draw_confirm(self, mouse):
        w, h = self.screen.get_size()
        self.draw_title("title_sure_delete" if self.asking == "delete" else "title_sure_overwrite", 0.25)
        self.blit_center(FANCY.fancy(self.infos[self.slot - 1]["name"], int(h * 0.05), "pale"), w // 2, int(h * 0.36))
        self.draw_buttons(mouse, 0.52)

    def draw_new_save(self, mouse):
        self.draw_title("title_new_save")
        fields = self.field_rects()
        for field, text, placeholder in (("name", self.name_text, f"Save {self.slot}"),
                                         ("seed", self.seed_text, "random")):
            self.draw_field(fields[field], self.labels["label_" + field], text, placeholder, field == self.focus)
        self.draw_buttons(mouse, 0.72, side_by_side=True)

    def draw_field(self, rect, label, text, placeholder, focused):
        self.screen.blit(label, label.get_rect(midbottom=(rect.centerx, rect.top - 6)))
        pygame.draw.rect(self.screen, FIELD_COLOUR, rect, 0, 12)
        pygame.draw.rect(self.screen, FIELD_FOCUS if focused else FIELD_EDGE, rect, 3, 12)
        size = int(rect.height * 0.5)
        img = FANCY.fancy(text, size) if text else FANCY.font(size).render(placeholder, True, (110, 100, 130))
        self.screen.blit(img, img.get_rect(center=rect.center))
        if focused and pygame.time.get_ticks() // 500 % 2 == 0:       # a blinking cursor
            x = rect.centerx + img.get_width() // 2 + 4 if text else rect.centerx - img.get_width() // 2 - 6
            pygame.draw.line(self.screen, FIELD_FOCUS, (x, rect.y + rect.height * 0.25), (x, rect.y + rect.height * 0.75), 2)

    def draw_buttons(self, mouse, y_share, side_by_side=False):
        w, h = self.screen.get_size()
        names = self.page_buttons()
        for n, name in enumerate(names):
            if side_by_side:
                center = (int(w / 2 + (n - (len(names) - 1) / 2) * w * 0.28), int(h * y_share))
            else:
                center = (w // 2, int(h * (y_share + n * BUTTON_H * 1.5)))
            button = self.buttons[name]
            button.draw(self.screen, center, button.rect.collidepoint(mouse))

    def blit_center(self, img, cx, cy):
        self.screen.blit(img, img.get_rect(center=(cx, cy)))


def fit_size(name, size):
    """A long name gets a smaller font, so it fits on the card."""
    return size if len(name) <= 10 else max(24, int(size * 10 / len(name)))
