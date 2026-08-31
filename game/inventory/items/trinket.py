from game.inventory.item import Item

class Trinket(Item):
    def __init__(self, name, description, type, effect):
        super().__init__(name, description, type)
        self.effect = effect
