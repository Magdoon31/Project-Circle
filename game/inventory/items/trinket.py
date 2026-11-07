from game.inventory.item import Item

class Trinket(Item):
    def __init__(self, name, description, type, effect, effect_description, img):
        super().__init__(name, description, effect, effect_description, type, img)
