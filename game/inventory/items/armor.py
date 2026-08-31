from game.inventory.item import Item

class Armor(Item):
    def __init__(self, name, description, type, defense, bonus_hp, effect):
        super().__init__(name, description, type)
        self.defense = defense
        self.bonus_hp = bonus_hp
        self.effect = effect
