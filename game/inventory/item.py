import pygame

class Item:
    def __init__(self, name, description, effect, effect_description, type, img):
        self.name = name
        self.description = description
        self.type = type
        self.img = img
        self.effect = effect
        self.effect_description = effect_description
