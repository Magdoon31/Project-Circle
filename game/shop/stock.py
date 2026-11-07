# SHOP STOCK: what lies on the 6 shelves (no drawing here - see shop.py).
#
# Biomes in world order (their number = "tier"): village 1, rainbow 2, sugarwood 3, factory / tundra 4, garden 5, core 6.
# A biome is "open" for the shop once the boss before it is beaten:
#   start: village | boss:village -> rainbow | boss:rainbow_fields -> sugarwood | boss:candy -> the chosen path
#   (factory or tundra - the shop changes only once the path IS chosen) | the OTHER path's boss beaten -> that path too
#   | boss:factory or boss:tundra -> garden | boss:garden -> core
# Shelves: the NEWEST biome gets 2, every older one 1, at most 6 - the oldest falls off:
#   VV -> RRV -> SSRV -> FFSRV -> GGFSRV -> (tundra boss) GGFTSR -> ...
# New stock after every boss (rolled the first time the shop is opened after it). A bought shelf stays SOLD.
# 2 rerolls per boss (fixed price), after a reroll every shelf has a different item than before.
# Never: items the player already has, story / quest items (loot.NOT_RANDOM, items outside the biome pools).

import random
from game.world import loot

SHELVES = 6
TIERS = {"village": 1, "rainbow_fields": 2, "sugarwood_grove": 3, "toy_factory": 4, "silverpine_tundra": 4,
         "underground_garden": 5, "the_core": 6}
PATHS = {"factory": "toy_factory", "tundra": "silverpine_tundra"}
PRICE_PER_TIER = 100        # TEMPORARY: price = 100$ x the tier of the item's biome (balance later)
REROLLS_PER_STAGE = 2
REROLL_PRICE_PER_TIER = 50  # reroll = 50$ x the newest tier
# the Foreman's Meter: an extra (7th) item on the counter while his quest is running
COUNTER_ITEMS = [{"item": "Meter", "quest": "foreman", "price": 400}]
STAGE_BOSSES = ("village", "rainbow_fields", "candy", "factory", "tundra", "garden", "core", "void")


def path_chosen(flags):
    return any(f"path:{p}" in flags for p in PATHS)


def stage_key(flags):
    """Which bosses are beaten (the lunapark Mascot doesn't count) - a new key = new stock.
    The Candy boss counts only once the path is chosen (the shop waits to know: Factory or Tundra)."""
    return sorted(f for f in flags if f.startswith("boss:") and f[5:] in STAGE_BOSSES
                  and (f != "boss:candy" or path_chosen(flags)))


def open_biomes(flags):
    """[(biome, tier)] the shop sells from, newest first."""
    beaten = lambda b: f"boss:{b}" in flags
    biomes = [("village", 1)]
    if beaten("village"):
        biomes.append(("rainbow_fields", 2))
    if beaten("rainbow_fields"):
        biomes.append(("sugarwood_grove", 3))
    chosen = next((p for p in PATHS if f"path:{p}" in flags), None)
    if beaten("candy") and chosen:                                     # (before the path is chosen: nothing new yet)
        for path in sorted(PATHS, key=lambda p: p != chosen):          # the chosen path first
            if path == chosen or beaten(path):
                biomes.append((PATHS[path], 4))
    if beaten("factory") or beaten("tundra"):
        biomes.append(("underground_garden", 5))
    if beaten("garden"):
        biomes.append(("the_core", 6))
    order = {b: i for i, (b, _) in enumerate(biomes)}
    return sorted(biomes, key=lambda bt: (-bt[1], order[bt[0]]))


def shelf_biomes(flags):
    """The biome of each shelf, e.g. [garden, garden, factory, tundra, sugarwood, rainbow]."""
    biomes = open_biomes(flags)
    top_tier = biomes[0][1]
    newest = [b for b, t in biomes if t == top_tier]
    slots = []
    for b, t in biomes:
        slots += [b] * (2 if t == top_tier and len(newest) == 1 else 1)
    return slots[:SHELVES]


def newest_tier(flags):
    return open_biomes(flags)[0][1]


def price_of(biome):
    return PRICE_PER_TIER * TIERS.get(biome, 1)


def reroll_price(flags):
    return REROLL_PRICE_PER_TIER * newest_tier(flags)


def roll(flags, owned, avoid=(), rnd=random, luck=0):
    """New shelves: [{"item", "biome", "sold"}]. avoid = items that must not come back (reroll)."""
    shelves, taken = [], set(owned) | set(avoid)
    for biome in shelf_biomes(flags):
        pool = [n for n in loot.random_pool(biome) if n not in taken]
        if not pool:                                   # nothing new left: an older item is better than nothing
            pool = [n for n in loot.random_pool(biome) if n not in owned and n not in {s["item"] for s in shelves}]
        item = loot.pick(pool, rnd, luck)        # by weight (rare items less often, luck helps)
        if item:
            taken.add(item)
        shelves.append({"item": item, "biome": biome, "sold": item is None})
    return shelves


class ShopStock:
    """The saved part of the shop (Game keeps it in counters["shop"])."""

    def __init__(self, data=None):
        data = data or {}
        self.stage = data.get("stage")                  # stage_key the shelves were rolled for (None = never)
        self.shelves = data.get("shelves", [])
        self.rerolls = data.get("rerolls", REROLLS_PER_STAGE)
        self.greeted = data.get("greeted", [])         # stage_key of the last greeting (a boss line after a boss)

    def to_dict(self):
        return {"stage": self.stage, "shelves": self.shelves, "rerolls": self.rerolls, "greeted": self.greeted}

    def refresh(self, flags, owned, luck=0):
        """New stock if a boss was beaten since the last roll. True if it was rolled now."""
        key = stage_key(flags)
        if self.stage == key and self.shelves:
            return False
        self.stage, self.rerolls = key, REROLLS_PER_STAGE
        self.shelves = roll(flags, owned, luck=luck)
        return True

    def reroll(self, flags, owned, luck=0):
        if self.rerolls <= 0:
            return False
        self.rerolls -= 1
        self.shelves = roll(flags, owned, avoid=[s["item"] for s in self.shelves if s["item"]], luck=luck)
        return True

    def counter_items(self, active_quests, owned):
        """The extra items on the counter right now (e.g. the Meter during the Foreman's quest)."""
        return [c for c in COUNTER_ITEMS if c["quest"] in active_quests and c["item"] not in owned]
