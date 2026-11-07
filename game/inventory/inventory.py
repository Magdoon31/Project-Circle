import pygame
from game.inventory.items.item_database import ItemDatabase

MAX_ITEMS = 16   # size of the inventory grid (4x4); equipped items don't count


class Inventory:

    def __init__(self, screen):
        self.ItemDB = ItemDatabase(screen.get_height())
        self.active_weapon = None
        self.active_armor = None
        self.active_trinket = None
        self.active_trinket2 = None    # 2nd trinket slot: only with the Spare Pocket sigil (Game sets .pocket)
        self.pocket = False
        self.items = []
        self.selected_item = None
        self.active_items = {"weapon": self.active_weapon, "armor": self.active_armor, "trinket": self.active_trinket,
                             "trinket2": self.active_trinket2}

    def add_item(self, item):
        self.items.append(item)

    def is_full(self):
        return len(self.items) >= MAX_ITEMS

    def give_item(self, item):
        """Use this for every NEW item (drops, shop, secrets).
        Returns money gained: 0 if the item was added, its value if the inventory was full."""
        if self.is_full():
            return self.item_value(item)
        self.add_item(item)
        return 0

    def item_value(self, item):
        # TEMPORARY money value of an item (used when the inventory is full).
        # To be replaced by real prices when the shop is made.
        if item.type == "weapon":
            pellets = item.effect["shotgun"][1] if "shotgun" in item.effect else 1
            dps = item.damage * pellets / item.rate_of_fire
            return int(dps * 2)
        elif item.type == "armor":
            return int((item.defense * 10 + item.bonus_hp) * 2)
        return 100
    def remove_item(self, item):
        self.items.remove(item)
    def select_item(self, item):
        self.selected_item = item

    def equip_item(self, item):
        if item.type == "weapon":
            if self.active_weapon is not None:
                self.add_item(self.active_weapon)
            self.remove_item(item)
            self.active_weapon = item
            self.active_items["weapon"] = self.active_weapon
            self.selected_item = None
        elif item.type == "armor":
            if self.active_armor is not None:
                self.add_item(self.active_armor)
            self.remove_item(item)
            self.active_armor = item
            self.active_items["armor"] = self.active_armor
            self.selected_item = None
        elif item.type == "trinket":
            if self.pocket and self.active_trinket is not None and self.active_trinket2 is None:
                self.remove_item(item)                  # the first slot is taken: into the Spare Pocket
                self.active_trinket2 = item
                self.active_items["trinket2"] = item
                self.selected_item = None
                return
            if self.active_trinket is not None:
                self.add_item(self.active_trinket)
            self.remove_item(item)
            self.active_trinket = item
            self.active_items["trinket"] = self.active_trinket
            self.selected_item = None

    def unequip_item(self, item):
        # unequipping puts the item into the grid - not possible when the grid is full
        if self.is_full():
            return False
        if item.type == "weapon":
            self.add_item(item)
            self.active_weapon = None
            self.active_items["weapon"] = self.active_weapon
            self.selected_item = None
        elif item.type == "armor":
            self.add_item(item)
            self.active_armor = None
            self.active_items["armor"] = self.active_armor
            self.selected_item = None
        elif item.type == "trinket" and item is self.active_trinket2:
            self.add_item(item)
            self.active_trinket2 = None
            self.active_items["trinket2"] = None
            self.selected_item = None
        elif item.type == "trinket":
            self.add_item(item)
            self.active_trinket = None
            self.active_items["trinket"] = self.active_trinket
            self.selected_item = None
        return True

    def equipped(self):
        return [i for i in (self.active_weapon, self.active_armor, self.active_trinket, self.active_trinket2) if i]

    def set_pocket(self, on):
        """Spare Pocket switched on/off. Off with a trinket in it: back to the grid (False if the grid is full)."""
        if not on and self.active_trinket2 is not None:
            if self.is_full():
                return False
            self.add_item(self.active_trinket2)
            self.active_trinket2 = None
            self.active_items["trinket2"] = None
        self.pocket = on
        return True
