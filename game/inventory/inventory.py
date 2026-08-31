import pygame

class Inventory:

    def __init__(self):
        self.avtive_weapon = None
        self.active_armor = None
        self.active_trinket = None
        self.items = []
        self.selected_item = None

    def add_item(self, item):
        self.items.append(item)
    def remove_item(self, item):
        self.items.remove(item)
    def select_item(self, item):
        self.selected_item = item

    def equip_item(self, item):
        if item.type == "weapon":
            self.items.append(self.active_weapon)
            self.items.remove(item)
            self.active_weapon = item
            self.selected_item = None
        elif item.type == "armor":
            self.items.append(self.active_armor)
            self.items.remove(item)
            self.active_armor = item
            self.selected_item = None
        elif item.type == "trinket":
            self.items.append(self.active_trinket)
            self.items.remove(item)
            self.active_trinket = item
            self.selected_item = None

    def unequip_item(self, item):
        if item.type == "weapon":
            self.items.append(item)
            self.active_weapon = None
            self.selected_item = None
        elif item.type == "armor":
            self.items.append(item)
            self.active_armor = None
            self.selected_item = None
        elif item.type == "trinket":
            self.items.append(item)
            self.active_trinket = None
            self.selected_item = None



