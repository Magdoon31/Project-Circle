import pygame
from game.inventory.items.item_database import ItemDatabase

class Inventory:

    def __init__(self, screen):
        self.ItemD = ItemDatabase(screen.get_height())
        self.active_weapon = self.ItemD.get_item("Simple Blaster")
        self.active_armor = self.ItemD.get_item("Simple Armor")
        self.active_trinket = None
        self.items = [self.ItemD.get_item("Simple Pistol")]
        self.selected_item = None
        self.active_items = {"weapon": self.active_weapon, "armor": self.active_armor, "trinket": self.active_trinket}
        self.all_itmes = self.items 

    def add_item(self, item):
        self.items.append(item)
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
            if self.active_trinket is not None:
                self.add_item(self.active_trinket)
            self.remove_item(item)
            self.active_trinket = item
            self.active_items["trinket"] = self.active_trinket
            self.selected_item = None

    def unequip_item(self, item):
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
        elif item.type == "trinket":
            self.add_item(item)
            self.active_trinket = None
            self.active_items["trinket"] = self.active_trinket
            self.selected_item = None



