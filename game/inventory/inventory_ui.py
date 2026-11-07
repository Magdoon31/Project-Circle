import os
import pygame
from game.inventory import sigils as SG

SIGIL_DIR = "assets/img/inventory/sigils"

class Inventory_ui:
    def __init__(self, screen, inventory, sfx):
        self.screen = screen
        self.inventory = inventory
        self.selected_slot = None
        self.slot_size = self.screen.get_height()//9
        self.columns = 4
        self.padding = 20
        self.slots = []
        self.buttons = []
        self.grid_start_x = self.screen.get_width()//1.4 - self.slot_size*2
        self.grid_start_y = self.screen.get_height()//2.5 - self.slot_size*2
        self.tooltip_start = (self.screen.get_width()//1.84, self.screen.get_height()//1.5)
        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                           "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),
                           "large" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",64)}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                           "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                           "large" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",64)}

        self.confirm_remove = False   # "Remove item?" popup is open
        self.confirm_buttons = []     # [yes_rect, no_rect]
        self.message = ""             # short info text, e.g. "Inventory full"
        self.message_timer = 0
        self.sfx = sfx
        self.sfx.load_sfx("use", "assets/sfx/UI/use.wav")
        self.sfx.load_sfx("click", "assets/sfx/UI/click1.wav")
        self.page = "items"           # "items" / "sigils" (switch at the top)
        self.tab_rects = {}
        self.sigils = None            # Game's Sigils
        self.sigil_rects = {}         # sigil id -> its tile
        self.sigil_images = {}

    def draw(self):
        self.slots = []
        self.buttons = []
        if self.page == "sigils":
            self.draw_sigils()
            return
        self.draw_sigil_background(*self.screen.get_size(), "Inventory")
    #rendering slot grid
        for i in range(self.columns):
            for j in range(self.columns):
                slot = pygame.Rect(
                    (self.screen.get_width()//1.4)+self.slot_size*(j-2)+self.padding*(j-2),
                    (self.screen.get_height()//2.5)+self.slot_size*(i-2)+self.padding*(i-2),
                    self.slot_size
                    ,self.slot_size
                    )
                self.slots.append(slot)
                self.slot_box(slot, self.selected_slot == (i,j))

    # rendering items
        for i, item in enumerate(self.inventory.items):
            row = i // self.columns
            column = i % self.columns

            x = self.grid_start_x + column * self.slot_size + self.padding*(column-2)+self.screen.get_height()//160
            y = self.grid_start_y + row * self.slot_size + self.padding*(row-2)+self.screen.get_height()//160
            self.screen.blit(item.img,(x,y))


        self.draw_back_button()

        
        weapon_slot = pygame.Rect(
                            self.screen.get_width()//4,
                            self.screen.get_height()//6,
                            self.slot_size
                            ,self.slot_size
                            )
        self.slots.append(weapon_slot)
        self.slot_box(weapon_slot, self.selected_slot == (4,0), equipped=True)
        if self.inventory.active_weapon:
            self.screen.blit(self.inventory.active_weapon.img,(weapon_slot.left+self.screen.get_height()//160,weapon_slot.top+self.screen.get_height()//160))
        weapon_slot_text = self.font_heavy["large"].render("Weapon:",True,self.TEXT)
        self.screen.blit(weapon_slot_text,(weapon_slot.left-weapon_slot_text.get_width()*1.1,weapon_slot.top+self.screen.get_height()//100))
        

        armor_slot = pygame.Rect(
                            self.screen.get_width()//4,
                            (self.screen.get_height()//6)*2.5,
                            self.slot_size
                            ,self.slot_size
                            )
        self.slots.append(armor_slot)
        self.slot_box(armor_slot, self.selected_slot == (4,1), equipped=True)
        if self.inventory.active_armor:
            self.screen.blit(self.inventory.active_armor.img,(armor_slot.left+self.screen.get_height()//160,armor_slot.top+self.screen.get_height()//160))
        armor_slot_text = self.font_heavy["large"].render("Armor:",True,self.TEXT)
        self.screen.blit(armor_slot_text,(armor_slot.left-armor_slot_text.get_width()*1.1,armor_slot.top+self.screen.get_height()//100))


        trinket_slot = pygame.Rect(
                            self.screen.get_width()//4,
                            (self.screen.get_height()//6)*4,
                            self.slot_size
                            ,self.slot_size
                            )
        self.slots.append(trinket_slot)
        self.slot_box(trinket_slot, self.selected_slot == (4,2), equipped=True)
        if self.inventory.active_trinket:
            self.screen.blit(self.inventory.active_trinket.img,(trinket_slot.left+self.screen.get_height()//160,trinket_slot.top+self.screen.get_height()//160))
        trinket_slot_text = self.font_heavy["large"].render("Trinket:",True,self.TEXT)
        self.screen.blit(trinket_slot_text,(trinket_slot.left-trinket_slot_text.get_width()*1.1,trinket_slot.top+self.screen.get_height()//100))
        if self.inventory.pocket:                # Spare Pocket sigil: a 2nd trinket slot next to the first one
            pocket_slot = trinket_slot.move(int(self.slot_size * 1.25), 0)
            self.slots.append(pocket_slot)
            self.slot_box(pocket_slot, self.selected_slot == (4,3), equipped=True)
            if self.inventory.active_trinket2:
                self.screen.blit(self.inventory.active_trinket2.img,(pocket_slot.left+self.screen.get_height()//160,pocket_slot.top+self.screen.get_height()//160))
        self.draw_tabs()


        tooltip_rect = pygame.Rect(
                            self.tooltip_start[0],
                            self.tooltip_start[1],
                            self.screen.get_width()//3,
                            self.screen.get_height()//4.8)
        pygame.draw.rect(self.screen,(22,14,38),tooltip_rect,0,10)
        pygame.draw.rect(self.screen,self.FRAME,tooltip_rect,2,10)       # dark box, purple frame (like the sigils page)
        if self.inventory.selected_item:
            # the name goes in the left column; a name too long for it is written in several rows
            column = tooltip_rect.width//(4.2 if self.inventory.selected_item.type == "trinket" else 3.6) - tooltip_rect.width//40 - 8
            words, name_rows = self.inventory.selected_item.name.split(" "), [""]
            for word in words:
                test = (name_rows[-1] + " " + word).strip()
                if self.font_heavy["small"].size(test)[0] <= column or not name_rows[-1]:
                    name_rows[-1] = test
                else:
                    name_rows.append(word)
            name_imgs = [self.font_heavy["small"].render(row,True,(255,255,255)) for row in name_rows]
            extra = sum(img.get_height() for img in name_imgs[1:])     # how much lower the rest goes
            self.tooltip_text = {"Name" : name_imgs[0],
                                "Type" : self.font_light["small"].render(f"Type: {self.inventory.selected_item.type}",True,(190,190,190)),
                                "desc" : self.font_light["small"].render(f"{self.inventory.selected_item.description}",True,(225,225,225))
                                }
            y_name = tooltip_rect.top+self.screen.get_height()//60
            for img in name_imgs:
                self.screen.blit(img,(tooltip_rect.left+tooltip_rect.width//40,y_name))
                y_name += img.get_height()
            self.screen.blit(self.tooltip_text["Type"],(tooltip_rect.left+tooltip_rect.width//40,y_name))
            # description: one row per line
            y = tooltip_rect.top+self.screen.get_height()//60
            for part in str(self.inventory.selected_item.description).split("\n"):
                img = self.font_light["small"].render(part, True, (225,225,225))
                self.screen.blit(img, (tooltip_rect.left+tooltip_rect.width//(4.2 if self.inventory.selected_item.type == "trinket" else 3.6), y))
                y += img.get_height() + 2
            self.desc_bottom = y + 4

        
            if self.inventory.selected_item.type == "weapon":

                self.tooltip_text["Damage"] = self.font_light["small"].render(f"DMG: {self.inventory.selected_item.damage}"+(f" x {self.inventory.selected_item.effect['shotgun'][1]}"if "shotgun" in self.inventory.selected_item.effect else ""),True,(255,120,120))
                self.tooltip_text["Fire Rate"] = self.font_light["small"].render(f"Fire Rate: {self.inventory.selected_item.rate_of_fire}",True,(130,230,130))
                self.tooltip_text["Range"] = self.font_light["small"].render(f"Range: {self.inventory.selected_item.range//10}",True,(130,230,130))

                self.screen.blit(self.tooltip_text["Damage"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*2+extra))
                self.screen.blit(self.tooltip_text["Fire Rate"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*3+extra))
                self.screen.blit(self.tooltip_text["Range"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*4+extra))
                
            elif self.inventory.selected_item.type == "armor":

                self.tooltip_text["Health"] = self.font_light["small"].render(f"Bonus HP: {self.inventory.selected_item.bonus_hp}",True,(255,120,120))
                self.tooltip_text["Defense"] = self.font_light["small"].render(f"DEF: {self.inventory.selected_item.defense}",True,(140,170,255))

                self.screen.blit(self.tooltip_text["Health"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*2+extra))
                self.screen.blit(self.tooltip_text["Defense"],(tooltip_rect.left+tooltip_rect.width//40,tooltip_rect.top+self.screen.get_height()//60+28*3+extra))

            # effect (several lines possible; "Effect:" only once) under the description
            text_x = tooltip_rect.left+tooltip_rect.width//(4.2 if self.inventory.selected_item.type == "trinket" else 3.6)
            y = self.desc_bottom
            for k, part in enumerate(str(self.inventory.selected_item.effect_description).split("\n")):
                img = self.font_light["small"].render(("Effect: " if k == 0 else "") + part, True, (235,150,225))
                self.screen.blit(img, (text_x, y))
                y += img.get_height() + 2

        equip_btn_rect = pygame.Rect(self.screen.get_width()//1.8,
                        self.screen.get_height()//1.12,
                        self.screen.get_width()//7,
                        self.screen.get_height()//20)
        remove_btn_rect = pygame.Rect(self.screen.get_width()//1.8+equip_btn_rect.width*1.1,
                        self.screen.get_height()//1.12,
                        self.screen.get_width()//7,
                        self.screen.get_height()//20)
        if self.inventory.selected_item is not None:
            equip_btn_text = self.font_heavy["mid"].render("Unequip" if self.inventory.selected_item in self.inventory.active_items.values() else "Equip",True,self.TEXT)
            self.buttons.append(equip_btn_rect)
            self.theme_button(equip_btn_rect, self.ORANGE if self.inventory.selected_item not in self.inventory.active_items.values() else self.FRAME)
            self.screen.blit(equip_btn_text,(equip_btn_rect.left+equip_btn_rect.width//2-equip_btn_text.get_width()//2,
                                                     equip_btn_rect.top+equip_btn_rect.height//2-equip_btn_text.get_height()//2))
            remove_btn_text = self.font_heavy["mid"].render("Remove",True,self.TEXT)
            self.buttons.append(remove_btn_rect)
            self.theme_button(remove_btn_rect, (230, 110, 110))
            self.screen.blit(remove_btn_text,(remove_btn_rect.left+remove_btn_rect.width//2-remove_btn_text.get_width()//2,
                                                     remove_btn_rect.top+remove_btn_rect.height//2-remove_btn_text.get_height()//2))

        # item counter above the grid
        count_text = self.font_heavy["mid"].render(f"{len(self.inventory.items)}/16", True, self.TEXT if not self.inventory.is_full() else (255,110,110))
        grid_right = max(slot.right for slot in self.slots[:16])
        self.screen.blit(count_text, (grid_right + self.padding, self.slots[0].top))      # next to the grid

        if self.message_timer > 0:
            self.message_timer -= 1
            message_text = self.font_heavy["mid"].render(self.message, True, (230,70,60))
            self.screen.blit(message_text, (equip_btn_rect.left - message_text.get_width() - self.padding*2,
                                            equip_btn_rect.centery - message_text.get_height()//2))

        if self.confirm_remove:
            self.draw_confirm_remove()

    # --- the Items / Sigils switch and the Sigils page ------------------------------------------------
    def draw_back_button(self):
        back_btn_rect = pygame.Rect(self.screen.get_width() - self.screen.get_width()//6, self.screen.get_height()//30,
                                    self.screen.get_width()//7, self.screen.get_height()//20)
        self.buttons.append(back_btn_rect)
        dark = True
        hover = back_btn_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, ((70, 45, 105) if hover else (45, 28, 72)) if dark else (255, 255, 255), back_btn_rect, 0, 6)
        if dark:
            pygame.draw.rect(self.screen, (170, 130, 230), back_btn_rect, 2, 6)
        back_btn_text = self.font_heavy["mid"].render("Back", True, (230, 215, 255) if dark else (0, 0, 0))
        self.screen.blit(back_btn_text, back_btn_text.get_rect(center=back_btn_rect.center))

    def draw_tabs(self):
        sw, sh = self.screen.get_size()
        dark = True
        self.tab_rects = {}
        x = sw // 40
        for page, label in (("items", "Items"), ("sigils", "Sigils")):
            current = page == self.page
            colour = ((230, 215, 255) if current else (150, 130, 180)) if dark else (0, 0, 0)
            text = self.font_heavy["mid"].render(label, True, colour)
            rect = pygame.Rect(x, sh // 30, text.get_width() + 50, sh // 20)
            self.tab_rects[page] = rect
            if dark:
                pygame.draw.rect(self.screen, (60, 38, 95) if current else (32, 20, 52), rect, 0, 8)
                pygame.draw.rect(self.screen, (170, 130, 230) if current else (90, 70, 120), rect, 2, 8)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255) if current else (170, 170, 110), rect, 0, 8)
                if current:
                    pygame.draw.rect(self.screen, (60, 60, 40), rect, 3, 8)
            self.screen.blit(text, text.get_rect(center=rect.center))
            x = rect.right + sw // 80

    def sigil_image(self, name, size, colour=None):
        """The column's sigil picture, scaled; colour = painted in that colour (the pictures are black)."""
        key = (name, size, colour)
        if key not in self.sigil_images:
            path = os.path.join(SIGIL_DIR, name)
            try:
                img = pygame.image.load(path).convert_alpha() if os.path.exists(path) else None
            except pygame.error:
                img = None
            if img:
                img = pygame.transform.smoothscale(img, (size, size))
                if colour:
                    img.fill((*colour, 0), special_flags=pygame.BLEND_RGBA_MAX)
            self.sigil_images[key] = img
        return self.sigil_images[key]

    # colour of each column's cards (frame, sigil, glow)
    SIGIL_COLOURS = {"fortune": (236, 178, 104), "craft": (120, 200, 220), "warden": (130, 140, 255), "tribe": (196, 120, 255)}

    # the look of both pages: dark purple, light lavender text, purple frames, orange for what's yours / chosen
    TEXT = (235, 222, 255)
    FRAME = (150, 110, 210)
    ORANGE = (236, 160, 90)

    def slot_box(self, rect, selected, equipped=False):
        """An inventory slot: dark glass, purple frame (orange = equipment), bright orange when selected."""
        hover = rect.collidepoint(pygame.mouse.get_pos())
        glass = pygame.Surface(rect.size, pygame.SRCALPHA)
        glass.fill((*(self.ORANGE if selected else (120, 80, 180)), 70 if selected else 45 if hover else 28))
        self.screen.blit(glass, rect)
        colour = self.ORANGE if selected or equipped else self.FRAME
        if equipped and not selected:
            colour = tuple(int(c * 0.75) for c in colour)
        pygame.draw.rect(self.screen, colour, rect, 3 if selected else 2, 6)

    def theme_button(self, rect, colour):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        glass = pygame.Surface(rect.size, pygame.SRCALPHA)
        glass.fill((*colour, 90 if hover else 55))
        self.screen.blit(glass, rect)
        pygame.draw.rect(self.screen, colour, rect, 2, 6)

    def draw_sigil_background(self, sw, sh, title_text="Sigils"):
        for y in range(0, sh, 4):                                    # dark purple, a bit lighter in the middle
            t = 1 - abs(y / sh - 0.45) * 1.6
            pygame.draw.rect(self.screen, (int(16 + 14 * t), int(10 + 6 * t), int(30 + 26 * t)), (0, y, sw, 4))
        frame = pygame.Rect(sw // 60, sh // 9, sw - sw // 30, sh - sh // 9 - sh // 40)
        pygame.draw.rect(self.screen, (95, 60, 140), frame, 2, 24)
        title = self.font_heavy["large"].render(title_text, True, (222, 200, 255))
        tr = title.get_rect(center=(sw // 2, int(sh * 0.075)))
        self.soft_glow(tr.center, tr.width // 2 + 50, (150, 90, 230), 10, oval=0.45)
        self.screen.blit(title, tr)
        for side in (-1, 1):                                        # thin lines with a diamond on both sides
            x0 = tr.centerx + side * (tr.width // 2 + 30)
            x1 = tr.centerx + side * int(sw * 0.3)
            pygame.draw.line(self.screen, (160, 120, 220), (x0, tr.centery), (x1, tr.centery), 2)
            self.diamond((x0 + side * 14, tr.centery), 7, (200, 170, 255))
            self.diamond((x1, tr.centery), 5, (160, 120, 220))

    def soft_glow(self, centre, radius, colour, alpha, oval=1.0):
        """A soft round light: a few circles fading out."""
        glow = pygame.Surface((radius * 2, int(radius * 2 * oval)), pygame.SRCALPHA)
        for i in range(6, 0, -1):
            k = i / 6
            rect = pygame.Rect(0, 0, int(radius * 2 * k), int(radius * 2 * oval * k))
            rect.center = glow.get_rect().center
            pygame.draw.ellipse(glow, (*colour, alpha), rect)
        self.screen.blit(glow, glow.get_rect(center=centre))

    def diamond(self, centre, r, colour):
        x, y = centre
        pygame.draw.polygon(self.screen, colour, [(x, y - r), (x + r * 0.6, y), (x, y + r), (x - r * 0.6, y)])

    def draw_card_frame(self, rect, colour, width):
        pygame.draw.rect(self.screen, colour, rect, width, 6)
        inner = rect.inflate(-14, -14)
        k = max(10, rect.height // 9)                                # little corner ornaments
        for cx, cy, dx, dy in ((inner.left, inner.top, 1, 1), (inner.right, inner.top, -1, 1),
                               (inner.left, inner.bottom, 1, -1), (inner.right, inner.bottom, -1, -1)):
            pygame.draw.line(self.screen, colour, (cx, cy), (cx + dx * k, cy), 2)
            pygame.draw.line(self.screen, colour, (cx, cy), (cx, cy + dy * k), 2)
            self.diamond((cx + dx * 4, cy + dy * 4), 3, colour)

    def draw_sigils(self):
        """4 columns = 4 sigil families (the same picture in a column), 3 sigils in each.
        A card: the sigil big in the middle as a background, its name and what it does under it."""
        sw, sh = self.screen.get_size()
        self.draw_sigil_background(sw, sh)
        self.draw_tabs()
        self.draw_back_button()
        self.sigil_rects = {}
        left, top = int(sw * 0.035), int(sh * 0.145)
        bottom = sh - sh // 40 - int(sh * 0.025)                     # the cards fill the whole frame
        gap_x, gap_y = int(sw * 0.018), int(sh * 0.022)
        card_w = (sw - 2 * left - 3 * gap_x) // 4
        card_h = (bottom - top - 2 * gap_y) // 3
        mouse = pygame.mouse.get_pos()
        for c, column in enumerate(SG.COLUMNS):
            base = self.SIGIL_COLOURS.get(column["id"], (200, 170, 255))
            for k, sigil in enumerate(column["sigils"]):
                rect = pygame.Rect(left + c * (card_w + gap_x), top + k * (card_h + gap_y), card_w, card_h)
                self.sigil_rects[sigil["id"]] = rect
                owned = bool(self.sigils) and sigil["id"] in self.sigils.owned
                active = bool(self.sigils) and self.sigils.on(sigil["id"])
                hover = owned and rect.collidepoint(mouse)
                dim = 1.0 if active else 0.75 if owned else 0.3
                colour = tuple(int(v * dim) for v in base)
                card = pygame.Surface(rect.size, pygame.SRCALPHA)       # tinted glass
                card.fill((*base, 70 if active else 45 if hover else 28 if owned else 14))
                self.screen.blit(card, rect)
                if active:                                              # glow around a switched-on sigil
                    glow = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
                    for w, a in ((8, 25), (4, 45)):
                        pygame.draw.rect(glow, (*base, a), glow.get_rect().inflate(-(8 - w), -(8 - w)), w, 12)
                    self.screen.blit(glow, glow.get_rect(center=rect.center))
                self.draw_card_frame(rect, colour, 3 if active else 2)
                size = int(card_h * 0.44)
                icon = self.sigil_image(column["image"], size, colour)
                centre = (rect.centerx, rect.top + int(card_h * 0.3))
                self.soft_glow(centre, int(size * 0.85), base, 9 if active else 6 if owned else 2)
                if icon:
                    pic = icon if owned else icon.copy()
                    if not owned:
                        pic.set_alpha(90)
                    self.screen.blit(pic, pic.get_rect(center=centre))
                name = self.font_heavy["mid"].render(sigil["name"] if owned else "???", True,
                                                     (245, 235, 255) if owned else (120, 105, 145))
                name_y = rect.top + int(card_h * 0.6)
                self.screen.blit(name, name.get_rect(center=(rect.centerx, name_y)))
                y = name_y + name.get_height() // 2 + 4
                for row in (sigil["text"].split("\n") if owned else ["Not found yet."]):
                    img = self.font_light["small"].render(row, True, (225, 215, 240) if owned else (110, 95, 135))
                    self.screen.blit(img, img.get_rect(midtop=(rect.centerx, y)))
                    y += img.get_height() + 2
                if active:
                    on = self.font_heavy["small"].render("ACTIVE", True, base)
                    self.screen.blit(on, (rect.right - on.get_width() - 22, rect.top + 18))
        if self.message_timer > 0:
            self.message_timer -= 1
            message_text = self.font_heavy["mid"].render(self.message, True, (255, 110, 110))
            self.screen.blit(message_text, message_text.get_rect(midbottom=(sw // 2, sh - sh // 60 - 30)))

    def handle_sigil_click(self, pos, events):
        for event in events:
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            if self.buttons and self.buttons[0].collidepoint(pos):
                self.sfx.play("use")
                return "map"
            for sigil_id, rect in self.sigil_rects.items():
                if rect.collidepoint(pos) and self.sigils and sigil_id in self.sigils.owned:
                    before = self.sigils.on("spare_pocket")
                    self.sigils.toggle(sigil_id)
                    after = self.sigils.on("spare_pocket")
                    if before and not after and not self.inventory.set_pocket(False):
                        self.sigils.toggle(sigil_id if sigil_id == "spare_pocket" else "spare_pocket")   # undo
                        self.show_message("Inventory full - take the 2nd trinket off first")
                    elif after and not before:
                        self.inventory.set_pocket(True)
                    self.sfx.play("use")
        return None

    def show_message(self, text, frames=120):
        self.message = text
        self.message_timer = frames

    def draw_confirm_remove(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        w, h = self.screen.get_width()//3.5, self.screen.get_height()//4.5
        box = pygame.Rect(self.screen.get_width()//2 - w//2, self.screen.get_height()//2 - h//2, w, h)
        pygame.draw.rect(self.screen, (28, 18, 46), box, 0, 10)
        pygame.draw.rect(self.screen, self.FRAME, box, 2, 10)

        item = self.inventory.selected_item
        title = self.font_heavy["mid"].render(f"Remove {item.name if item else ''}?", True, self.TEXT)
        info = self.font_light["small"].render("The item will be lost forever.", True, (180,165,205))
        self.screen.blit(title, (box.centerx - title.get_width()//2, box.top + h//8))
        self.screen.blit(info, (box.centerx - info.get_width()//2, box.top + h//8 + title.get_height()*1.3))

        btn_w, btn_h = w//2.8, h//4.5
        yes_rect = pygame.Rect(box.centerx - btn_w - w//20, box.bottom - btn_h - h//8, btn_w, btn_h)
        no_rect = pygame.Rect(box.centerx + w//20, box.bottom - btn_h - h//8, btn_w, btn_h)
        self.confirm_buttons = [yes_rect, no_rect]
        mouse = pygame.mouse.get_pos()
        for rect, text, color in ((yes_rect, "Remove", (230,140,100)), (no_rect, "Cancel", (170,170,170))):
            self.theme_button(rect, color)
            label = self.font_heavy["mid"].render(text, True, self.TEXT)
            self.screen.blit(label, label.get_rect(center=rect.center))

    def remove_selected_item(self):
        if self.inventory.selected_item in self.inventory.active_items.values():
            if self.inventory.selected_item.type == "weapon":
                self.inventory.active_weapon = None
                self.inventory.active_items["weapon"] = None
            elif self.inventory.selected_item.type == "armor":
                self.inventory.active_armor = None
                self.inventory.active_items["armor"] = None
            elif self.inventory.selected_item is self.inventory.active_trinket2:
                self.inventory.active_trinket2 = None
                self.inventory.active_items["trinket2"] = None
            elif self.inventory.selected_item.type == "trinket":
                self.inventory.active_trinket = None
                self.inventory.active_items["trinket"] = None
        elif self.inventory.selected_item:
            self.inventory.remove_item(self.inventory.selected_item)
        self.inventory.selected_item = None
        self.selected_slot = None

    def handle_confirm_click(self, pos, events):
        # while the popup is open, only it reacts to input
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and len(self.confirm_buttons) == 2:
                if self.confirm_buttons[0].collidepoint(pos):
                    self.sfx.play("use")
                    self.remove_selected_item()
                    self.confirm_remove = False
                elif self.confirm_buttons[1].collidepoint(pos):
                    self.sfx.play("click")
                    self.confirm_remove = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.confirm_remove = False
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.sfx.play("use")
                    self.remove_selected_item()
                    self.confirm_remove = False
            
           
        
        

    def handle_click(self, pos, events):
        if self.confirm_remove:
            self.handle_confirm_click(pos, events)
            return None
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for page, rect in self.tab_rects.items():
                    if rect.collidepoint(pos) and page != self.page:
                        self.page = page
                        self.selected_slot = None
                        self.inventory.selected_item = None
                        self.sfx.play("click")
                        return None
        if self.page == "sigils":
            return self.handle_sigil_click(pos, events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, slot in enumerate(self.slots):
                    if slot.collidepoint(pos):

                        row = i // self.columns
                        column = i % self.columns

                        if self.selected_slot == (row,column):
                            self.selected_slot = None
                            self.inventory.selected_item = None
                            self.sfx.play("click")
                        else:
                            self.selected_slot = (row,column)

                            if self.selected_slot == (4,0):
                                self.inventory.selected_item = self.inventory.active_weapon
                            elif self.selected_slot == (4,1):
                                self.inventory.selected_item = self.inventory.active_armor
                            elif self.selected_slot == (4,2):
                                self.inventory.selected_item = self.inventory.active_trinket
                            elif self.selected_slot == (4,3):
                                self.inventory.selected_item = self.inventory.active_trinket2
                            elif len(self.inventory.items) >= i + 1:
                                self.inventory.selected_item = self.inventory.items[i]
                            else:
                                self.inventory.selected_item = None
                            self.sfx.play("click")
   

                for i, btn in enumerate(self.buttons):
                    if btn.collidepoint(pos):
                        self.sfx.play("use")
                        if i == 0:
                            return "map"
                        elif i == 1:
                            if self.inventory.selected_item in self.inventory.active_items.values():
                                if self.inventory.unequip_item(self.inventory.selected_item):
                                    self.selected_slot = None
                                else:
                                    self.show_message("Inventory full")
                            elif self.inventory.selected_item:
                                self.inventory.equip_item(self.inventory.selected_item)
                                self.selected_slot = None
                        elif i == 2:
                            if self.inventory.selected_item:
                                self.confirm_remove = True   # popup asks before removing
                            break

