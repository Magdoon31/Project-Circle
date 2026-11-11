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
# REROLLS (7.11): as many as you like, after a reroll every shelf has a different item than before. The FIRST one after
# every boss is free, then the price grows with the square: base x 1, 4, 9, 16... (free again after the next boss).
# PRICES (7.11): price = how many fights in the item's biome it is worth x the average gold of one fight there
#   (FIGHT_GOLD: enemies' money + the biome's gold on the map spread over ~15 fights). Common (weight 10) = 4 fights,
#   medium (5) = 8, rare (2) = 16. A reroll = 1 fight of the newest biome. All rounded to 10.
# RARE items (weight 2) of a biome come up only after its boss is beaten - before that only through a REROLL and
#   only once you have won RARE_WINS fights in that biome (Game.counters["biome_wins"]). A restock never brings them.
# Never: items the player already has, story / quest items (loot.NOT_RANDOM, items outside the biome pools).

import random
from game.world import loot

SHELVES = 6
TIERS = {"village": 1, "rainbow_fields": 2, "sugarwood_grove": 3, "toy_factory": 4, "silverpine_tundra": 4,
         "underground_garden": 5, "the_core": 6}
PATHS = {"factory": "toy_factory", "tundra": "silverpine_tundra"}
# average gold of one normal fight in the biome, map gold included (7.11 simulation: 3000 fights, 5 worlds)
FIGHT_GOLD = {"village": 21, "rainbow_fields": 41, "sugarwood_grove": 108, "toy_factory": 190, "silverpine_tundra": 181,
              "underground_garden": 654, "the_core": 857, "the_void": 1702}
FIGHTS_FOR = ((10, 4), (5, 8), (0, 16))     # loot weight >= ... -> worth this many fights (common / medium / rare)
RARE_WEIGHT = 2             # weight <= this = rare
RARE_WINS = 5               # won fights in a biome before its rare items can come up in a reroll (boss not beaten yet)
BOSS_OF = {"village": "village", "rainbow_fields": "rainbow_fields", "sugarwood_grove": "candy", "toy_factory": "factory",
           "silverpine_tundra": "tundra", "underground_garden": "garden", "the_core": "core"}
# extra items on the counter: the Foreman's Meter while his quest is running; (11.11) the Pocket AK from the Core's
# boss on (the Void's own items are not on the shelves: its weapons / armours only drop, one of each in the Void Shrine)
COUNTER_ITEMS = [{"item": "Meter", "quest": "foreman", "price": 400},
                 {"item": "Pocket AK", "flag": "boss:core", "price": 6810}]     # (= 4 fights in the Void, a common item)
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


def round10(value):
    return max(10, int(value / 10 + 0.5) * 10)


def price_of(item, biome):
    """The price of an item on a shelf of this biome (before the Haggler sigil)."""
    w = loot.weight(item)
    fights = next(f for limit, f in FIGHTS_FOR if w >= limit)
    return round10(FIGHT_GOLD.get(biome, 100) * fights)


def reroll_price(flags, used=0, mult=1.0):
    """The first reroll since the last boss is free, then the gold of one fight in the newest open biome x (rerolls
    done since the last boss) squared (x mult - the Lucky Coin sigil)."""
    biomes = open_biomes(flags)
    base = max(FIGHT_GOLD.get(b, 100) for b, t in biomes if t == biomes[0][1])
    return round10(base * used ** 2 * mult) if used else 0


def rare_allowed(biome, flags, wins, reroll):
    """Can a rare item of this biome come up now? (its boss beaten / a reroll after RARE_WINS won fights there)"""
    if f"boss:{BOSS_OF.get(biome)}" in flags:
        return True
    return reroll and (wins or {}).get(biome, 0) >= RARE_WINS


def roll(flags, owned, avoid=(), rnd=random, luck=0, wins=None, reroll=False):
    """New shelves: [{"item", "biome", "sold"}]. avoid = items that must not come back (reroll)."""
    shelves, taken = [], set(owned) | set(avoid)
    for biome in shelf_biomes(flags):
        rare_ok = rare_allowed(biome, flags, wins, reroll)
        can = [n for n in loot.random_pool(biome) if rare_ok or loot.weight(n) > RARE_WEIGHT]
        pool = [n for n in can if n not in taken]
        if not pool:                                   # nothing new left: an older item is better than nothing
            pool = [n for n in can if n not in owned and n not in {s["item"] for s in shelves}]
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
        self.used = data.get("used", 0)                 # rerolls done since the last boss (the price grows)
        self.greeted = data.get("greeted", [])         # stage_key of the last greeting (a boss line after a boss)

    def to_dict(self):
        return {"stage": self.stage, "shelves": self.shelves, "used": self.used, "greeted": self.greeted}

    def refresh(self, flags, owned, luck=0, wins=None):
        """New stock if a boss was beaten since the last roll. True if it was rolled now."""
        key = stage_key(flags)
        if self.stage == key and self.shelves:
            return False
        self.stage, self.used = key, 0
        self.shelves = roll(flags, owned, luck=luck, wins=wins)
        return True

    def reroll(self, flags, owned, luck=0, wins=None):
        self.used += 1
        self.shelves = roll(flags, owned, avoid=[s["item"] for s in self.shelves if s["item"]], luck=luck,
                            wins=wins, reroll=True)
        return True

    def counter_items(self, active_quests, owned, flags=()):
        """The extra items on the counter right now (the Meter during the Foreman's quest, the Pocket AK after the
        Core's boss) - not what you already have."""
        def wanted(c):
            return c["quest"] in active_quests if "quest" in c else c["flag"] in flags
        return [c for c in COUNTER_ITEMS if wanted(c) and c["item"] not in owned]
