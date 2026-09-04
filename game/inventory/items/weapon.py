import pygame
from game.inventory.item import Item

class Weapon(Item):
    def __init__(self, name, description, type, damage, rate_of_fire, effect, effect_description, range, bullet_size, bullet_speed, img ):
        super().__init__(name, description, effect, effect_description, type, img)
        self.damage = damage
        self.rate_of_fire = rate_of_fire
        self.range = range
        self.bullet_size = bullet_size
        self.bullet_speed = bullet_speed