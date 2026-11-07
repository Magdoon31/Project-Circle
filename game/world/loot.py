# What can lie on the ground in each biome.
# TEMPORARY pools: items grouped by the biome section they are listed under in item_database.py.
# They will be replaced when we decide the real item distribution (shop / drops / quests / secrets...).

# never rolled as "random" ground loot - these have special sources (start, lore, secrets, Milo fight)
NOT_RANDOM = {"Simple Pistol", "Hook", "Broken Bulb", "Cassette Tape", "Old Note", "Pale Orb", "Eyeballs", "Peace Gun"}

ITEMS_BY_BIOME = {
    "village": ["Simple Pistol", "Simple Blaster", "Flintlock", "Toy Rifle", "Old Pistol", "Leather Chestplate", "Vest",
                "Hook", "Shrooms", "Shoe"],
    "rainbow_fields": ["Water Hose", "Rifle A2", "Normal Blaster", "Finger Gun", "Gladiator's Chestplate",
                       "Medieval Armor I", "Apprentice Armor", "Martini", "Rose"],
    "sugarwood_grove": ["Glue Gun", "Shotgun S4", "Laser SMG", "Bubble Gun", "Hand Cannon", "Reinforced Vest",
                        "Living Plate", "Samurai Jacket", "Book", "Bra", "Cotton Candy", "Tape"],
    # Factory = OFFENCE (more and stronger weapons), Tundra = DEFENCE (more armours) - 6.11
    "toy_factory": ["Laser Cannon", "Poison Gun", "Rifle A4", "Taser", "Hunter's Sniper", "Nail Gun", "G-Launcher",
                    "Minigun", "Blaster 2.0", "Samurai Plating", "Cyber Suit", "Scrap Armor",
                    "Broken Bulb", "Dices", "Fire Ring", "Holy Orb", "D20"],     # D20: moved from Rainbow (6.11)
    "silverpine_tundra": ["Living Pistol", "Liquidator Hose", "Shotgun R6", "Living Hose", "Flare Gun",
                          "Knight Armor", "Medieval Armor II",
                          "Old-World Vest", "Golden Chestplate", "Living Armor", "Frost Armor",
                          "Cassette Tape", "Frozen Ring", "Ice Mix", "Eyeballs"],
    "underground_garden": ["RPG", "Living Rifle", "Flower Gun", "Laser Cannon 2.0", "Shotgun S8", "Shotgun R15",
                           "Ultra Blaster", "Medieval Armor III", "Plate Armor", "Saper Armor", "Tribe Armor",
                           "Samurai Armor", "Cyber Armor", "Atom", "Pale Orb", "Toxic Ring", "Magic Ring", "Magic Dust"],
    "the_core": ["AK-47", "Laser Arrow", "Acid Gun", "Peace Gun", "Combat Sniper", "Ghost USP", "Mecha Armor",
                 "Viking Armor", "Heroic Armor", "Electro Armor", "Samurai God", "Hourglass", "Old Note", "Power Bank"],
    "the_void": ["Ghost Rifle", "Pocket AK", "Ghost Shotgun", "Missile-3000", "Laser SMG v2", "Mecha-King Armor",
                 "Fallen knight armor", "Ghost Armor", "Crown"],
}

ALL_ITEMS = {name for items in ITEMS_BY_BIOME.values() for name in items}

# gold lying on the ground: (min, max) per "$", roughly 2-4 fights' worth of that biome
GOLD_RANGES = {
    "village": (8, 20), "rainbow_fields": (20, 45), "sugarwood_grove": (35, 70), "toy_factory": (60, 120),
    "silverpine_tundra": (60, 120), "underground_garden": (120, 240), "the_core": (200, 400), "the_void": (400, 800),
    "lunapark": (35, 70),
}


# HOW OFTEN an item comes up when something random is picked from its biome (ground loot, shop shelves).
# Higher = more common: 10 common, 5 medium, 2 rare. 0 = NEVER random (start item, quest reward, enemy drop only).
# Not listed = DEFAULT_WEIGHT.
# Enemy drops (the only source for some of the best weapons): EnemyDB.drops in enemy_database.py.
DEFAULT_WEIGHT = 5
LOOT_WEIGHTS = {
    # village
    "Simple Blaster": 0, "Simple Pistol": 0,            # start items
    "Old Pistol": 10, "Flintlock": 2, "Toy Rifle": 0,   # Toy Rifle: slimes drop it
    "Shoe": 10, "Shrooms": 0,                           # Shrooms: the Angler's reward
    # rainbow fields
    "Water Hose": 10, "Finger Gun": 5, "Rifle A2": 2, "Normal Blaster": 2,
    "Martini": 5, "Rose": 0,                            # Rose: flower_spitter drops it
    # sugarwood grove
    "Shotgun S4": 10, "Hand Cannon": 5, "Laser SMG": 5, "Bubble Gun": 2, "Glue Gun": 0,   # Glue Gun: Gus
    "Book": 5, "Bra": 5, "Cotton Candy": 10, "Tape": 0,                                   # Tape: gum_goblin
    # toy factory
    "Poison Gun": 10, "Taser": 10, "Minigun": 5, "Laser Cannon": 5, "Hunter's Sniper": 5,
    "Nail Gun": 0, "Rifle A4": 0, "G-Launcher": 0, "Blaster 2.0": 0,   # Nail Gun: Foreman; the rest: drops
    "Dices": 5, "D20": 2, "Fire Ring": 5, "Holy Orb": 2,
    # silverpine tundra
    "Shotgun R6": 10, "Living Pistol": 10, "Living Hose": 5,
    "Flare Gun": 0, "Liquidator Hose": 0,               # Flare Gun: Hal (instead of the tape); Liquidator: drop
    "Frozen Ring": 0, "Ice Mix": 0,                     # ice_shooter drops them
    # underground garden
    "Shotgun R15": 10, "Living Rifle": 10, "Flower Gun": 5, "Shotgun S8": 5,
    "RPG": 0, "Ultra Blaster": 0, "Laser Cannon 2.0": 0,                  # drops
    "Atom": 5, "Toxic Ring": 5, "Magic Ring": 5, "Magic Dust": 0,        # Magic Dust: pixie
    # the core
    "Combat Sniper": 10, "Acid Gun": 5, "AK-47": 5, "Laser Arrow": 0, "Ghost USP": 0, "Peace Gun": 0,
    "Power Bank": 5, "Hourglass": 5,
    # the void
    "Pocket AK": 10, "Ghost Shotgun": 2, "Ghost Rifle": 2, "Missile-3000": 2, "Laser SMG v2": 2,
    "Crown": 5,
    # ARMOURS (6.11)
    "Leather Chestplate": 10, "Vest": 10,
    "Medieval Armor I": 10, "Gladiator's Chestplate": 5, "Apprentice Armor": 2,
    "Reinforced Vest": 10, "Samurai Jacket": 5, "Living Plate": 2,
    "Samurai Plating": 5, "Cyber Suit": 5, "Scrap Armor": 5,
    "Old-World Vest": 10, "Living Armor": 10, "Knight Armor": 5, "Medieval Armor II": 5,
    "Golden Chestplate": 2, "Frost Armor": 2,                        # + drops (ice_shooter / frozen_orb)
    "Saper Armor": 10, "Cyber Armor": 10, "Medieval Armor III": 5, "Samurai Armor": 5,
    "Plate Armor": 0, "Tribe Armor": 0,                              # drops (poison_skeleton / toxic_flower)
    "Viking Armor": 10, "Heroic Armor": 5, "Electro Armor": 5,
    "Mecha Armor": 0, "Samurai God": 0,                              # drops (generator / skeleton)
    "Mecha-King Armor": 2, "Fallen knight armor": 2, "Ghost Armor": 2,   # + drops (crystals / voidling)
}
# LUCK (Dices trinket, Lucky Charm sigil - Game.luck()): per point, rare things come up more often
# (shop shelves and enemy drops; ground loot is made with the world, so luck can't change it)
LUCK_RARE = 1.5                 # weight <= 2: x1.5 per luck point
LUCK_MEDIUM = 1.25              # weight <= 5: x1.25
LUCK_DROP = 0.25                # enemy drop chance +25% per luck point


def weight(name, luck=0):
    w = LOOT_WEIGHTS.get(name, DEFAULT_WEIGHT)
    if w and luck:
        w *= (LUCK_RARE if w <= 2 else LUCK_MEDIUM if w <= 5 else 1.0) ** luck
    return w


def random_pool(biome):
    """Items that can come up at random in this biome (weight > 0)."""
    return [name for name in ITEMS_BY_BIOME.get(biome, []) if name not in NOT_RANDOM and weight(name) > 0]


def pick(pool, rnd, luck=0):
    """One item from the pool, by weight."""
    if not pool:
        return None
    return rnd.choices(pool, weights=[weight(n, luck) for n in pool])[0]


def roll_item(biome, rnd, already_placed=()):
    # random item from the biome pool (by weight), preferring ones not placed yet on this map
    pool = random_pool(biome)
    fresh = [name for name in pool if name not in already_placed]
    return pick(fresh or pool, rnd)


def roll_gold(biome, rnd, override=None):
    low, high = override or GOLD_RANGES.get(biome, (10, 20))
    return rnd.randint(low, high)
