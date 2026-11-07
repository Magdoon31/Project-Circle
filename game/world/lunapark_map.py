# LUNAPARK map: a small closed amusement park, its OWN level (like the cellar, but tiny and always the same layout).
#
#   surface: portal in Sugarwood Grove (sealed until the Candy boss is beaten)  <->  portal at the lunapark gate
#   Lucky (wheel of fortune) by the avenue, the carousel + ferris wheel, a bit of gold - and the Mascot in the big
#   tent in the middle (an optional boss). The gate is 3 tiles wide.
#   No random fights here (game.py NO_FIGHT_LEVELS). The world map (M) shows the Surface here (world_map.py).
#
# The layout is fixed: game/world/prefabs/lunapark.txt (markers: P portal, N Lucky, B Mascot, $ gold, I items).
# Same interface as the other maps (tiles, zones, gates, portals, pickups, npcs, arrivals, player_start, biome_at).

import random
from game.world import loot
from game.world.prefab import load_prefab
from game.world.tiles import TILES, EMPTY

ZONES = {"lunapark": "lunapark"}
MARGIN = 3                       # solid rock around the park
LOOT_BIOME = "sugarwood_grove"   # gold and items like in Sugarwood (the park belongs to it)


class LunaparkMap:
    def __init__(self, seed):
        self.seed = seed
        self.used_seed = seed
        self.rnd = random.Random(f"lunapark-{seed}")
        prefab = load_prefab("lunapark")
        self.width, self.height = prefab.width + 2 * MARGIN, prefab.height + 2 * MARGIN
        self.tiles = [["M"] * self.width for _ in range(self.height)]
        self.zones = [[None] * self.width for _ in range(self.height)]
        self.gates, self.portals, self.pickups, self.npcs, self.structures = [], [], [], [], []
        self.arrivals = {}
        ox = oy = MARGIN
        for y in range(prefab.height):
            for x in range(prefab.width):
                tile = prefab.tile_at(x, y)
                if tile != EMPTY:
                    self.tiles[oy + y][ox + x] = tile
                    self.zones[oy + y][ox + x] = "lunapark"
        (px, py), = prefab.markers_in_order("portal")
        portal = (ox + px, oy + py)
        self.portals.append({"zone": "lunapark", "pos": portal, "leads_to": "surface:candy"})
        self.arrivals["surface:candy"] = (portal[0], portal[1] - 2)          # coming in from Sugarwood
        self.player_start = self.arrivals["surface:candy"]
        (bx, by), = prefab.markers_in_order("boss")
        boss = (ox + bx, oy + by)
        # the Mascot: no gate behind it - an optional fight for a prize (game.py after_boss)
        self.gates.append({"from": "lunapark", "to": "lunapark", "pos": boss, "cells": [], "boss": boss,
                           "entry": (boss[0], boss[1] + 4), "name": "Mascot"})
        for (x, y) in prefab.markers_in_order("gold"):
            self.pickups.append({"pos": (ox + x, oy + y), "type": "gold", "amount": loot.roll_gold(LOOT_BIOME, self.rnd)})
        placed = set()
        for (x, y), entry in zip(prefab.markers_in_order("item"), prefab.list_setting("items")):
            item = loot.roll_item(LOOT_BIOME, self.rnd, placed) if entry == "random" else entry
            placed.add(item)
            self.pickups.append({"pos": (ox + x, oy + y), "type": "item", "item": item})
        for (x, y), npc_id in zip(prefab.markers_in_order("npc"), prefab.list_setting("npcs")):
            self.npcs.append({"pos": (ox + x, oy + y), "id": npc_id, "zone": "lunapark"})
        self.paths_cut = 0

    def biome_at(self, x, y):
        zone = self.zones[y][x]
        return ZONES[zone] if zone else None

    def walkable(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and not TILES[self.tiles[y][x]]["solid"]
