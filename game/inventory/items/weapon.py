import pygame
from game.inventory.item import Item

class Weapon(Item):
    def __init__(self, name, description, type, damage, rate_of_fire, effect):
        super().__init__(name, description, type)
        self.damage = damage
        self.rate_of_fire = rate_of_fire
        self.effect = effect
