from game.inventory.item import Item

class Armor(Item):
    def __init__(self, name, description, type, defense, bonus_hp, effect, effect_description, img):
        super().__init__(name, description, effect, effect_description, type, img)
        self.defense = defense
        self.bonus_hp = bonus_hp
