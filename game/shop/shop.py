# THE SHOP - its own screen, opened from anywhere on the map (key B or the "Shop" button; not before talking to Milo).
#   left: the shopkeeper (no name) says a line - when you come in, when you buy, when you can't pay.
#         Text only (no talk sound); a voice file assets/sfx/shop/<line id>.mp3/.wav/.ogg is played if it exists.
#         Lines: game/shop/lines.json. His mood follows the story (for good): happy -> calm -> neutral.
#         In the Void he isn't there - only a sign "BRB, or not." (the shelves still work).
#   right: 6 shelves (game/shop/stock.py), a 7th item on the counter sometimes (the Foreman's Meter).
#   mouse: click a shelf = buy, point at it = what it is. Reroll button. Esc / B / Leave = back to the map.
# SELL page (7.11, after the Rainbow Fields boss - tabs Buy / Sell at the top): another person, the BUYER, sits
#   (8.11: Filip's buyer in a green apron - assets/img/shopkeeper/buyer_<normal / happy / bored>.png;
#   happy for 3 s after a sale until you have seen the Separated Village, bored in the Void, else normal)
#   there instead; the right side shows your inventory (not what you wear). Click an item = sell it for
#   SELL_SHARE of its shop price. Story / quest items can't be sold. ctx: can_sell, inventory(), sell_price(name), sell(item)
# Music: Game crossfades to the shop music and back (the biome music goes on where it stopped).
#
# The shopkeeper: assets/img/shopkeeper/shopkeeper_<normal / happy>.png (per line: "pose"), a small bounce
# after every purchase. PLACEHOLDER pictures - drawn by code until these files exist (assets/img/shop/):
#   background.png (whole screen; 8.11 drawn), background_sell.png (the Sell page; 8.11 drawn),
#   brb_sign.png (the Void; 8.11 drawn - stands on the counter), shelf.png (one shelf board, under each item), counter.png (the counter, bottom left)

import json, math, os, random
import pygame
from game.shop import stock as S

LINES_FILE = "game/shop/lines.json"
IMG_DIR = "assets/img/shop"
KEEPER_DIR = "assets/img/shopkeeper"     # the shopkeeper's pictures (7.11): shopkeeper_<name>.png
# his picture follows the LINE he is saying: "pose" in lines.json = normal / happy -> shopkeeper_<pose>.png
# (a missing file -> shopkeeper_normal.png; nothing said yet -> normal)
KEEPER_HEIGHT = 0.5           # share of the screen height (his lower part is hidden behind the counter)
KEEPER_TOP = 0.32             # where his head starts (share of the screen height) - the counter starts at 0.8
BOUNCE_FRAMES = 70            # after a purchase he bobs down and up a little, softer and softer, then stops
BOUNCE_SIZE = 0.022           # share of the screen height (the first dip)
VOICE_DIR = "assets/sfx/shop"
RARE_CHANCE = 0.08            # a rare (Pale World) line instead of a greeting
TYPE_SPEED = 1.5              # letters per frame
NOTE_FRAMES = 120             # how long a small note ("Inventory full") stays
BUY_COOLDOWN = 180            # frames (3 s) after buying before the next thing can be bought
BUYER_HAPPY_FRAMES = 180      # (8.11) the buyer smiles this long after you sell him something
BRB_TEXT = "BRB, or not."
SELL_COOLDOWN = 20            # frames between two sales (no double clicks)
BUYER_COAT, BUYER_EYES = (52, 78, 66), (150, 230, 160)   # PLACEHOLDER buyer: the keeper's shape, other colours


def mood_of(flags):
    """happy (start) -> calm (been to the Separated Village / the lunapark) -> neutral (the Garden / the Core).
    The boss flags count too (older saves have no "visited:" flags)."""
    if flags & {"visited:garden", "visited:core", "boss:garden"}:
        return "neutral"
    if flags & {"visited:separated", "visited:lunapark", "boss:factory", "boss:tundra"}:
        return "calm"
    return "happy"


def _load_image(name):
    path = os.path.join(IMG_DIR, name)
    try:
        return pygame.image.load(path).convert_alpha() if os.path.exists(path) else None
    except pygame.error:
        return None


def _load_voice(line_id):
    for ext in (".mp3", ".wav", ".ogg"):
        path = os.path.join(VOICE_DIR, line_id + ext)
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except pygame.error:
                return None
    return None


class Shop:
    def __init__(self, screen, item_db, volume=1.0):
        self.screen = screen
        self.item_db = item_db
        self.volume = volume
        self.is_open = False
        with open(LINES_FILE, encoding="utf-8") as f:
            self.lines = json.load(f)["lines"]
        sh = screen.get_height()
        self.font = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(18, sh // 34))
        self.font_big = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(24, sh // 22))
        self.font_small = pygame.font.Font("assets/font/Nexa-ExtraLight.ttf", max(14, sh // 48))
        self.font_small_bold = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(14, sh // 48))
        self.images = {name: _load_image(name) for name in
                       ("background.png", "background_sell.png", "keeper.png", "keeper_happy.png", "keeper_calm.png", "keeper_neutral.png",
                        "brb_sign.png", "shelf.png", "counter.png")}
        self._scaled = {}
        self.voice = None
        self.stock = None
        self.ctx = None
        self.line = None                 # the line being said: {"id", "text", ...}
        self.shown = 0.0                 # letters typed so far
        self.note, self.note_timer = "", 0
        self.buy_cooldown = 0
        self.bounce = 0                  # frames of the after-purchase bounce left
        self.buyer_happy = 0             # (8.11) frames the buyer still smiles after a sale
        self.keeper_pics = {}            # file -> picture cut to its visible part (None = no file)
        self.hover = None                # ("shelf", i) / ("counter", i) / ("inv", i) / "reroll" / "leave" / ("tab", page)
        self.page = "buy"                # "buy" / "sell"
        self.rects = {}

    # --- opening / closing --------------------------------------------------------------------------
    def open(self, stock, ctx):
        """ctx: dict with flags, owned (set), active_quests (set), level, get_money(), pay(n), give(name) -> bool,
        inventory_full() -> bool, play_sfx(name)"""
        self.is_open = True
        self.stock, self.ctx = stock, ctx
        stock.refresh(ctx["flags"], ctx["owned"], ctx.get("luck", 0), ctx.get("wins"))
        self.note_timer = self.buy_cooldown = 0
        self.page = "buy"
        self.say(self.greeting())

    def reroll_price(self):
        """Grows with every reroll since the last boss (stock.py); the Lucky Coin sigil makes it cheaper."""
        return S.reroll_price(self.ctx["flags"], self.stock.used, self.ctx.get("reroll_mult", 1.0))

    def close(self):
        self.is_open = False
        if self.voice:
            self.voice.stop()
        self.line = None

    @property
    def keeper_here(self):
        return self.ctx["level"] != "void"

    @property
    def mood(self):
        return mood_of(self.ctx["flags"])

    # --- what he says -------------------------------------------------------------------------------
    def pick(self, kind):
        flags = self.ctx["flags"]
        options = [l for l in self.lines if l["kind"] == kind
                   and ("moods" not in l or self.mood in l["moods"])
                   and ("flag" not in l or l["flag"] in flags)]
        return random.choice(options) if options else None

    def greeting(self):
        key = S.stage_key(self.ctx["flags"])
        first_after_boss = key and key != self.stock.greeted
        self.stock.greeted = key
        if first_after_boss:
            line = self.pick("boss")
            if line:
                return line
        if random.random() < RARE_CHANCE:
            line = self.pick("rare")
            if line:
                return line
        return self.pick("greet")

    def say(self, line):
        if not line or (not self.keeper_here and self.page == "buy"):
            return
        self.line, self.shown = line, 0.0
        if self.voice:
            self.voice.stop()
        self.voice = _load_voice(line["id"])
        if self.voice:
            channel = self.voice.play()
            if channel:
                channel.set_volume(self.volume)

    def show_note(self, text):
        self.note, self.note_timer = text, NOTE_FRAMES

    # --- buying -------------------------------------------------------------------------------------
    def price(self, value):
        """Price after the Haggler sigil (still a multiple of 10)."""
        mult = self.ctx.get("price_mult", 1.0)
        return value if mult == 1.0 else S.round10(value * mult)

    def buy(self, item_name, price, mark_sold=None):
        ctx = self.ctx
        if self.buy_cooldown > 0:
            return False                 # just bought something - wait a moment
        if ctx["get_money"]() < price:
            self.say(self.pick("poor"))
            if not self.keeper_here:
                self.show_note("Not enough money")
            return False
        if ctx["inventory_full"]():
            self.show_note("Inventory full")
            return False
        ctx["pay"](price)
        ctx["give"](item_name)
        ctx["owned"].add(item_name)
        if mark_sold:
            mark_sold()
        ctx["play_sfx"]("buy")
        self.buy_cooldown = BUY_COOLDOWN
        self.bounce = BOUNCE_FRAMES
        self.say(self.pick("buy"))
        return True

    def rarity(self, name):
        from game.world import loot
        w = loot.weight(name)
        return "common" if w >= 10 else "medium" if w >= 5 else "rare"

    def sell(self, item):
        if self.buy_cooldown > 0:
            return
        price = self.ctx["sell_price"](item.name)
        if price is None:
            self.show_note("He won't take that")
            return
        self.ctx["sell"](item, price)
        self.ctx["play_sfx"]("buy")
        self.buy_cooldown = SELL_COOLDOWN
        self.say(self.pick("sell_" + self.rarity(item.name)))
        self.buyer_happy = BUYER_HAPPY_FRAMES
        if self.buyer_pose() == "happy":
            self.bounce = BOUNCE_FRAMES                  # (8.11) a happy little bob, like the shopkeeper

    def click(self, target):
        ctx = self.ctx
        if target == "leave":
            return "leave"
        if isinstance(target, tuple) and target[0] == "tab":
            if target[1] != self.page:
                self.page = target[1]
                self.line = None                          # the other person hasn't said anything yet
                ctx["play_sfx"]("use")
            return None
        if isinstance(target, tuple) and target[0] == "inv":
            items = ctx["inventory"]()
            if target[1] < len(items):
                self.sell(items[target[1]])
            return None
        if target == "reroll":
            price = self.reroll_price()
            if ctx["get_money"]() < price:
                self.say(self.pick("poor"))
                if not self.keeper_here:
                    self.show_note("Not enough money")
            else:
                ctx["pay"](price)
                self.stock.reroll(ctx["flags"], ctx["owned"], ctx.get("luck", 0), ctx.get("wins"))
                ctx["play_sfx"]("use")
            return None
        if isinstance(target, tuple) and target[0] == "shelf":
            shelf = self.stock.shelves[target[1]]
            if shelf["item"] and not shelf["sold"]:
                if self.buy(shelf["item"], self.price(S.price_of(shelf["item"], shelf["biome"])), lambda: shelf.__setitem__("sold", True)) \
                        and ctx.get("bought"):
                    ctx["bought"](shelf["item"], shelf["biome"])        # (Game: e.g. the Haggler sigil counts Garden items)
        elif isinstance(target, tuple) and target[0] == "counter":
            items = self.stock.counter_items(ctx["active_quests"], ctx["owned"])
            if target[1] < len(items):
                self.buy(items[target[1]]["item"], self.price(items[target[1]]["price"]))
        return None

    def handle_events(self, events, mouse_pos):
        """Returns "leave" when the shop should close."""
        self.hover = next((name for name, rect in self.rects.items() if rect.collidepoint(mouse_pos)), None)
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_b):
                return "leave"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.hover is not None:
                if self.click(self.hover) == "leave":
                    return "leave"
        return None

    def update(self):
        if self.line and self.shown < len(self.line["text"]):
            self.shown += TYPE_SPEED
        if self.note_timer > 0:
            self.note_timer -= 1
        if self.buy_cooldown > 0:
            self.buy_cooldown -= 1
        if self.bounce > 0:
            self.bounce -= 1
        if self.buyer_happy > 0:
            self.buyer_happy -= 1

    # --- drawing ------------------------------------------------------------------------------------
    def image(self, name, size):
        img = self.images.get(name)
        if not img:
            return None
        key = (name, size)
        if key not in self._scaled:
            self._scaled[key] = pygame.transform.smoothscale(img, size)
        return self._scaled[key]

    def item_picture(self, name, size):
        item = self.item_db.find_item(name)
        key = ("item:" + name, size)
        if key not in self._scaled:
            self._scaled[key] = pygame.transform.smoothscale(item.img, size) if item and item.img else None
        return self._scaled[key]

    def draw(self):
        screen = self.screen
        sw, sh = screen.get_size()
        self.rects = {}
        bg = (self.page == "sell" and self.image("background_sell.png", (sw, sh))) or self.image("background.png", (sw, sh))
        if bg:
            screen.blit(bg, (0, 0))
        else:                                                   # PLACEHOLDER: a dim wooden shop
            screen.fill((46, 34, 32))
            for y in range(0, sh, sh // 12):
                pygame.draw.line(screen, (38, 27, 26), (0, y), (sw, y), 3)
        if self.page == "sell":
            self.draw_buyer(sw, sh)
            self.draw_counter(sw, sh, items=False)
            self.draw_inventory(sw, sh)
        else:
            self.draw_keeper(sw, sh)
            self.draw_counter(sw, sh)
            self.draw_shelves(sw, sh)
        self.draw_buttons(sw, sh)
        money = self.font_big.render(f"{self.ctx['get_money']()}$", True, (255, 225, 120))
        screen.blit(money, (sw - money.get_width() - sw // 40, sh // 40))
        title = self.font_big.render("Shop", True, (240, 230, 220))
        screen.blit(title, (sw // 40, sh // 40))
        self.draw_tabs(sw, sh, title.get_width())
        self.draw_tooltip(sw, sh)
        if self.note_timer > 0:
            note = self.font.render(self.note, True, (240, 90, 80))
            note.set_alpha(min(255, self.note_timer * 6))
            screen.blit(note, (sw * 0.7 - note.get_width() // 2, sh * 0.86))

    def draw_keeper(self, sw, sh):
        screen = self.screen
        centre = (int(sw * 0.2), int(sh * 0.56))
        size = (int(sh * 0.42), int(sh * 0.5))
        if not self.keeper_here:                                # the Void: only a sign, standing on the counter
            sign = self.image("brb_sign.png", (int(sh * 0.3), int(sh * 0.22)))
            rect = pygame.Rect(0, 0, int(sh * 0.3), int(sh * 0.16))
            rect.midbottom = (centre[0], int(sh * 0.8) - int(sh * 0.12))
            if sign:
                screen.blit(sign, sign.get_rect(midbottom=(centre[0], int(sh * 0.8) + 2)))   # its legs touch the counter
            else:
                pygame.draw.line(screen, (90, 60, 40), rect.midbottom, (rect.centerx, rect.bottom + sh * 0.12), 8)
                pygame.draw.rect(screen, (170, 130, 90), rect, 0, 6)
                pygame.draw.rect(screen, (90, 60, 40), rect, 5, 6)
                text = self.font.render(BRB_TEXT, True, (40, 25, 20))
                screen.blit(text, text.get_rect(center=rect.center))
            return
        pic = self.keeper_picture(sh)
        if pic:
            # standing behind the counter; after a purchase a small bounce that dies down
            t = BOUNCE_FRAMES - self.bounce
            dip = sh * BOUNCE_SIZE * math.exp(-t / 22) * math.sin(t / BOUNCE_FRAMES * math.pi * 5) if self.bounce else 0
            rect = pic.get_rect(midtop=(centre[0], int(sh * KEEPER_TOP + dip)))
            screen.blit(pic, rect)
        else:                                                   # PLACEHOLDER: a hooded figure, eyes show the mood
            body = pygame.Rect(0, 0, size[0] * 0.7, size[1] * 0.62)
            body.midbottom = (centre[0], centre[1] + size[1] // 2)
            pygame.draw.rect(screen, (70, 55, 85), body, 0, 40)
            head = (centre[0], body.top - size[1] * 0.08)
            pygame.draw.circle(screen, (70, 55, 85), head, size[0] * 0.24)
            pygame.draw.circle(screen, (25, 18, 30), head, size[0] * 0.18)
            eye = {"happy": (255, 220, 120), "calm": (200, 200, 170), "neutral": (170, 170, 175)}[self.mood]
            for side in (-1, 1):
                pos = (head[0] + side * size[0] * 0.07, head[1])
                if self.mood == "happy":                        # smiling eyes
                    pygame.draw.arc(screen, eye, pygame.Rect(pos[0] - 9, pos[1] - 4, 18, 14), 0.3, 2.8, 4)
                else:
                    pygame.draw.circle(screen, eye, pos, 6 if self.mood == "calm" else 4)
        if self.line:                                           # speech bubble above him
            self.draw_bubble(sw, sh, self.line["text"][:int(self.shown)])

    def draw_tabs(self, sw, sh, title_w):
        if not self.ctx.get("can_sell"):
            return
        x = sw // 40 + title_w + sw // 30
        for page, label in (("buy", "Buy"), ("sell", "Sell")):
            img = self.font.render(label, True, (25, 20, 20) if page == self.page else (200, 190, 180))
            rect = pygame.Rect(x, sh // 40 + 4, img.get_width() + 36, img.get_height() + 14)
            self.rects[("tab", page)] = rect
            colour = (240, 225, 200) if page == self.page else (80, 60, 55)
            if self.hover == ("tab", page) and page != self.page:
                colour = (120, 95, 80)
            pygame.draw.rect(self.screen, colour, rect, 0, 8)
            self.screen.blit(img, img.get_rect(center=rect.center))
            x = rect.right + 12

    def buyer_pose(self):
        """(8.11) The buyer: bored in the Void; happy while thanking you for a sale - only until you have seen the
        Separated Village (then it's nothing special any more: normal); otherwise normal."""
        if not self.keeper_here:
            return "bored"
        if self.buyer_happy > 0 and self.mood == "happy":
            return "happy"
        return "normal"

    def draw_buyer(self, sw, sh):
        """The buyer (8.11): assets/img/shopkeeper/buyer_<normal / happy / bored>.png, placed like the shopkeeper."""
        screen = self.screen
        centre = (int(sw * 0.2), int(sh * 0.56))
        size = (int(sh * 0.42), int(sh * 0.5))
        pic = self.keeper_picture(sh, f"buyer_{self.buyer_pose()}.png", "buyer_normal.png")
        if pic:
            t = BOUNCE_FRAMES - self.bounce
            dip = sh * BOUNCE_SIZE * math.exp(-t / 22) * math.sin(t / BOUNCE_FRAMES * math.pi * 5) if self.bounce else 0
            screen.blit(pic, pic.get_rect(midtop=(centre[0], int(sh * KEEPER_TOP + dip))))
        else:                                                   # PLACEHOLDER: the keeper's shape in other colours
            body = pygame.Rect(0, 0, size[0] * 0.7, size[1] * 0.62)
            body.midbottom = (centre[0], centre[1] + size[1] // 2)
            pygame.draw.rect(screen, BUYER_COAT, body, 0, 40)
            head = (centre[0], body.top - size[1] * 0.08)
            pygame.draw.circle(screen, BUYER_COAT, head, size[0] * 0.24)
            pygame.draw.circle(screen, (20, 26, 22), head, size[0] * 0.18)
            for side in (-1, 1):
                pygame.draw.circle(screen, BUYER_EYES, (head[0] + side * size[0] * 0.07, head[1]), 5)
        if self.line:
            self.draw_bubble(sw, sh, self.line["text"][:int(self.shown)])

    def draw_inventory(self, sw, sh):
        """Sell page: your inventory (4 x 4) on the right, the price under each item."""
        area = pygame.Rect(int(sw * 0.46), int(sh * 0.13), int(sw * 0.5), int(sh * 0.7))
        cols = rows = 4
        w, h = area.width // cols, area.height // rows
        items = self.ctx["inventory"]()
        size = int(min(w, h) * 0.55)
        for i in range(cols * rows):
            cell = pygame.Rect(area.left + (i % cols) * w, area.top + (i // cols) * h, w, h).inflate(-14, -14)
            if i >= len(items):
                continue
            item = items[i]
            self.rects[("inv", i)] = cell
            if self.hover == ("inv", i):
                pygame.draw.rect(self.screen, (255, 240, 200), cell, 3, 10)
            spot = pygame.Rect(0, 0, size, size)
            spot.center = (cell.centerx, cell.centery - h // 10)
            pic = self.item_picture(item.name, (size, size))
            price = self.ctx["sell_price"](item.name)
            if pic:
                if price is None:
                    pic = pic.copy()
                    pic.set_alpha(90)
                self.screen.blit(pic, spot)
            label = f"{price}$" if price is not None else "-"
            tag = self.font_small_bold.render(label, True, (150, 240, 160) if price is not None else (150, 130, 125))
            self.screen.blit(tag, tag.get_rect(midtop=(cell.centerx, spot.bottom + 6)))

    def keeper_picture(self, sh, name=None, fallback="shopkeeper_normal.png"):
        """The shopkeeper for his line (or another picture from KEEPER_DIR, e.g. the buyer), cut to its visible
        part and scaled to KEEPER_HEIGHT (kept in memory)."""
        if name is None:
            name = f"shopkeeper_{(self.line or {}).get('pose', 'normal')}.png"
        if not os.path.exists(os.path.join(KEEPER_DIR, name)):
            name = fallback
        key = (name, sh)
        if key not in self.keeper_pics:
            path = os.path.join(KEEPER_DIR, name)
            pic = None
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = img.subsurface(img.get_bounding_rect()).copy()
                    h = int(sh * KEEPER_HEIGHT)
                    pic = pygame.transform.smoothscale(img, (round(img.get_width() * h / img.get_height()), h))
            except pygame.error:
                pic = None
            self.keeper_pics[key] = pic
        return self.keeper_pics[key]

    def draw_bubble(self, sw, sh, text):
        box = pygame.Rect(int(sw * 0.03), int(sh * 0.1), int(sw * 0.36), int(sh * 0.2))
        pygame.draw.rect(self.screen, (245, 240, 230), box, 0, 18)
        pygame.draw.rect(self.screen, (60, 45, 50), box, 4, 18)
        tail = [(box.centerx - 20, box.bottom - 2), (box.centerx + 20, box.bottom - 2), (box.centerx, box.bottom + 26)]
        pygame.draw.polygon(self.screen, (245, 240, 230), tail)
        pygame.draw.lines(self.screen, (60, 45, 50), False, [tail[0], tail[2], tail[1]], 4)
        y = box.top + 16
        for row in self.wrap(text, self.font, box.width - 36):
            img = self.font.render(row, True, (40, 30, 35))
            self.screen.blit(img, (box.left + 18, y))
            y += img.get_height() + 4

    @staticmethod
    def wrap(text, font, width):
        rows = [""]
        for word in text.split(" "):
            test = (rows[-1] + " " + word).strip()
            if font.size(test)[0] <= width or not rows[-1]:
                rows[-1] = test
            else:
                rows.append(word)
        return rows

    def draw_counter(self, sw, sh, items=True):
        counter = pygame.Rect(0, int(sh * 0.8), int(sw * 0.42), int(sh * 0.2))
        pic = self.image("counter.png", counter.size)
        if pic:
            self.screen.blit(pic, counter)
        else:
            pygame.draw.rect(self.screen, (110, 72, 48), counter)
            pygame.draw.rect(self.screen, (75, 48, 32), counter, 6)
        if not items:
            return
        items = self.stock.counter_items(self.ctx["active_quests"], self.ctx["owned"])
        size = int(sh * 0.1)
        for i, entry in enumerate(items):
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (int(sw * (0.33 - i * 0.08)), int(sh * 0.86))
            self.rects[("counter", i)] = rect.inflate(20, 50)
            pic = self.item_picture(entry["item"], (size, size))
            if pic:
                self.screen.blit(pic, rect)
            self.draw_price(rect, f"{self.price(entry['price'])}$")

    def shelf_rects(self, sw, sh):
        area = pygame.Rect(int(sw * 0.46), int(sh * 0.13), int(sw * 0.5), int(sh * 0.62))
        cols, rows = 2, 3
        w, h = area.width // cols, area.height // rows
        return [pygame.Rect(area.left + (i % cols) * w, area.top + (i // cols) * h, w, h) for i in range(S.SHELVES)]

    def draw_shelves(self, sw, sh):
        for i, cell in enumerate(self.shelf_rects(sw, sh)):
            shelf = self.stock.shelves[i] if i < len(self.stock.shelves) else {"item": None, "sold": True}
            board = pygame.Rect(cell.left + 14, cell.bottom - cell.height // 5, cell.width - 28, cell.height // 9)
            pic = self.image("shelf.png", board.size)
            if pic:
                self.screen.blit(pic, board)
            else:
                pygame.draw.rect(self.screen, (125, 85, 55), board, 0, 4)
                pygame.draw.rect(self.screen, (80, 52, 35), board, 3, 4)
            size = int(cell.height * 0.52)
            spot = pygame.Rect(0, 0, size, size)
            spot.midbottom = (cell.centerx, board.top)
            if shelf["item"] and not shelf["sold"]:
                self.rects[("shelf", i)] = pygame.Rect(cell.left + 14, cell.top, cell.width - 28, cell.height)
                if self.hover == ("shelf", i):
                    pygame.draw.rect(self.screen, (255, 240, 200), self.rects[("shelf", i)], 3, 10)
                item_pic = self.item_picture(shelf["item"], (size, size))
                if item_pic:
                    self.screen.blit(item_pic, spot)
                self.draw_price(board, f"{self.price(S.price_of(shelf['item'], shelf['biome']))}$")
            elif i < len(self.stock.shelves):                    # bought (an empty shelf beyond the stock: nothing)
                sold = self.font.render("SOLD", True, (200, 80, 70))
                self.screen.blit(sold, sold.get_rect(center=spot.center))

    def draw_price(self, rect, text):
        can_pay = self.ctx["get_money"]() >= int(text.rstrip("$"))
        tag = self.font_small_bold.render(text, True, (255, 230, 140) if can_pay else (230, 120, 110))
        pos = tag.get_rect(midtop=(rect.centerx, rect.bottom + 6))
        pygame.draw.rect(self.screen, (40, 28, 26), pos.inflate(14, 6), 0, 6)
        self.screen.blit(tag, pos)

    def draw_buttons(self, sw, sh):
        price = self.reroll_price()
        buttons = [("reroll", f"Reroll {price}$" if price else "Reroll FREE", True),
                   ("leave", "Leave", True)]
        if self.page == "sell":
            buttons = buttons[1:]
        x = int(sw * 0.46)
        for key, label, active in buttons:
            img = self.font.render(label, True, (20, 20, 20) if active else (110, 110, 110))
            rect = pygame.Rect(x, int(sh * 0.9), img.get_width() + 40, int(sh * 0.06))
            self.rects[key] = rect
            colour = (240, 235, 225) if active else (150, 145, 140)
            if self.hover == key and active:
                colour = (255, 225, 150)
            pygame.draw.rect(self.screen, colour, rect, 0, 8)
            self.screen.blit(img, img.get_rect(center=rect.center))
            x = rect.right + sw // 50

    def draw_tooltip(self, sw, sh):
        """What the item you point at is (like the inventory tooltip)."""
        name = None
        if isinstance(self.hover, tuple) and self.hover[0] == "shelf":
            name = self.stock.shelves[self.hover[1]]["item"]
        elif isinstance(self.hover, tuple) and self.hover[0] == "inv":
            items = self.ctx["inventory"]()
            name = items[self.hover[1]].name if self.hover[1] < len(items) else None
        elif isinstance(self.hover, tuple) and self.hover[0] == "counter":
            items = self.stock.counter_items(self.ctx["active_quests"], self.ctx["owned"])
            name = items[self.hover[1]]["item"] if self.hover[1] < len(items) else None
        item = self.item_db.find_item(name) if name else None
        if not item:
            return
        rows = [(item.name, self.font_small_bold, (255, 255, 255)), (f"Type: {item.type}", self.font_small, (190, 190, 190))]
        if item.type == "weapon":
            shots = f" x {item.effect['shotgun'][1]}" if "shotgun" in item.effect else ""
            rows += [(f"DMG: {item.damage}{shots}", self.font_small, (255, 120, 120)),
                     (f"Fire Rate: {item.rate_of_fire}   Range: {item.range // 10}", self.font_small, (130, 230, 130))]
        elif item.type == "armor":
            rows += [(f"Bonus HP: {item.bonus_hp}   DEF: {item.defense}", self.font_small, (140, 170, 255))]
        width = int(sw * 0.3)
        for part in item.description.split("\n"):
            rows += [(r, self.font_small, (225, 225, 225)) for r in self.wrap(part, self.font_small, width - 30)]
        for k, part in enumerate(str(item.effect_description).split("\n")):     # "Effect:" only once, on the 1st line
            text = ("Effect: " + part) if k == 0 else part
            rows += [(r, self.font_small, (235, 150, 225)) for r in self.wrap(text, self.font_small, width - 30) if r]
        imgs = [(font.render(text, True, colour)) for text, font, colour in rows]
        line = lambda img, font: max(img.get_height(), font.get_linesize()) + 4
        height = sum(line(img, font) for img, (_, font, _) in zip(imgs, rows)) + 36     # 12 top + 24 bottom
        mx, my = pygame.mouse.get_pos()
        box = pygame.Rect(mx + 20, my + 20, width, height)
        box.right, box.bottom = min(box.right, sw - 10), min(box.bottom, sh - 10)
        pygame.draw.rect(self.screen, (25, 22, 28), box, 0, 10)
        pygame.draw.rect(self.screen, (200, 190, 180), box, 2, 10)
        y = box.top + 12
        for img, (_, font, _) in zip(imgs, rows):
            self.screen.blit(img, (box.left + 15, y))
            y += line(img, font)
