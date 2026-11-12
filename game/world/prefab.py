# PREFAB = a hand-made piece of map stored in a .txt file (game/world/prefabs/).
#
# File format:
#   @name village_start          <- lines starting with @ are settings
#   @biome village
#   Structures also use:
#   @biomes rainbow_fields, sugarwood_grove   <- where the generator may place it
#   @items random, Hook          <- one entry per I marker, in reading order ("random" = from the biome pool)
#   @npcs angler                 <- one id per N marker, in reading order
#   @gold 30-60                  <- optional, gold per $ marker (default: biome range)
#   h (11.11) = a secret way in: it and everything behind it (walled off from the rest) looks like wall until
#               the player walks into it (Prefab.secret(); the generator puts it in world.hidden)
#   ; lines starting with ; (before the map) are comments
#   <empty line>
#   then the map itself, one row per line, chars from game/world/tiles.py
#
# The generator places a prefab as a whole; " " (space) tiles are left to the generator.

import os
from game.world.tiles import TILES, MARKERS, EMPTY

PREFAB_DIR = os.path.join("game", "world", "prefabs")
MODS_DIR = "mods"     # players' own content: mods/structures/*.txt, mods/bosses/<biome>.txt (see MODDING.md)


class Prefab:
    def __init__(self, name, settings, rows):
        self.name = name
        self.settings = settings
        self.width = max(len(r) for r in rows)
        self.height = len(rows)
        self.rows = [r.ljust(self.width) for r in rows]   # pad short rows with "empty"
        self.markers = {}   # marker name -> list of (x, y)
        for y, row in enumerate(self.rows):
            for x, char in enumerate(row):
                if char in MARKERS:
                    self.markers.setdefault(MARKERS[char]["name"], []).append((x, y))
                elif char not in TILES and char != EMPTY:
                    raise ValueError(f"Prefab {name}: unknown tile '{char}' at ({x},{y})")

    def tile_at(self, x, y):
        # real terrain char (markers converted), or EMPTY
        char = self.rows[y][x]
        if char in MARKERS:
            becomes = MARKERS[char]["becomes"]
            if becomes is None:   # same as a walkable neighbour (left, right, up, down), grass if none
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= ny < self.height and 0 <= nx < self.width:
                        n = self.rows[ny][nx]
                        if n in TILES and not TILES[n]["solid"]:
                            return n
                return "."
            return becomes
        return char

    def secret(self):
        """(11.11) (the "h" ways in, the whole secret part incl. them) in prefab coordinates - the cells that can't be
        reached from the prefab's open edge without going through an "h". (set(), set()) if it has no secret."""
        ways = set(self.markers.get("secret_way", []))
        if not ways:
            return set(), set()
        open_part = self._reachable_from_edge(blocked=ways)
        part = {(x, y) for y in range(self.height) for x in range(self.width)
                if self.rows[y][x] not in (EMPTY, "#") and (x, y) not in open_part}
        return ways, part | ways

    def _reachable_from_edge(self, blocked):
        """Cells (not wall, not empty, not blocked) reachable from the walkable cells on the prefab's edge."""
        inside = lambda x, y: 0 <= x < self.width and 0 <= y < self.height \
            and self.rows[y][x] not in (EMPTY, "#") and (x, y) not in blocked
        todo = [(x, y) for y in range(self.height) for x in range(self.width)
                if (x in (0, self.width - 1) or y in (0, self.height - 1)) and inside(x, y)
                and not TILES[self.tile_at(x, y)]["solid"]]
        seen = set(todo)
        while todo:
            x, y = todo.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in seen and inside(*n):
                    seen.add(n)
                    todo.append(n)
        return seen

    def markers_in_order(self, marker):
        # positions of one marker type in reading order (left->right, top->bottom)
        return sorted(self.markers.get(marker, []), key=lambda p: (p[1], p[0]))

    def list_setting(self, key):
        # "@items random, Hook" -> ["random", "Hook"]
        value = self.settings.get(key, "")
        return [v.strip() for v in value.split(",") if v.strip()]


def load_prefab(name):
    return load_prefab_file(os.path.join(PREFAB_DIR, f"{name}.txt"), name)


def load_prefab_file(path, name=None):
    name = name or os.path.splitext(os.path.basename(path))[0]
    settings = {}
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f.read().splitlines():
            if not rows and line.startswith("@"):
                key, _, value = line[1:].partition(" ")
                settings[key] = value.strip()
            elif not rows and (line.startswith(";") or line.strip() == ""):
                continue
            else:
                rows.append(line)
    while rows and rows[-1].strip() == "":
        rows.pop()
    return Prefab(settings.get("name", name), settings, rows)


ORDERED_LISTS = (("item", "items"), ("npc", "npcs"))     # markers whose @list follows their reading order


def rotate(prefab, turns):
    """The same prefab turned 90 degrees clockwise `turns` times (0-3). Markers move with it - also the @items /
    @npcs that belong to them (11.11: the reading order changes when turned, the list is put in the new order)."""
    rows = prefab.rows
    for _ in range(turns % 4):
        h, w = len(rows), len(rows[0])
        rows = ["".join(rows[h - 1 - x][y] for x in range(h)) for y in range(w)]
    settings = dict(prefab.settings)
    for marker, key in ORDERED_LISTS:
        if key in settings:
            settings[key] = ", ".join(_reordered(prefab, marker, key, turns))
    return Prefab(prefab.name, settings, rows)


def _reordered(prefab, marker, key, turns):
    """The @list of a marker in the reading order of the turned prefab (entries without a marker stay at the end)."""
    values = prefab.list_setting(key)
    spots = prefab.markers_in_order(marker)
    turned = [(_turn(pos, prefab.height, prefab.width, turns), value) for pos, value in zip(spots, values)]
    turned.sort(key=lambda item: (item[0][1], item[0][0]))
    return [value for _, value in turned] + values[len(spots):]


def _turn(pos, height, width, turns):
    """Where a cell goes when the prefab is turned 90 degrees clockwise `turns` times."""
    x, y = pos
    for _ in range(turns % 4):
        x, y, height, width = height - 1 - y, x, width, height
    return x, y


_structure_cache = None


def all_structures():
    """Every structure prefab: the game's own (game/world/prefabs/structures) + mods (mods/structures).
    A mod file with the same name as a game file replaces it. Broken files are skipped with a warning."""
    global _structure_cache
    if _structure_cache is None:
        found = {}
        for folder in (os.path.join(PREFAB_DIR, "structures"), os.path.join(MODS_DIR, "structures")):
            if not os.path.isdir(folder):
                continue
            for file in sorted(os.listdir(folder)):
                if not file.endswith(".txt"):
                    continue
                try:
                    prefab = load_prefab_file(os.path.join(folder, file))
                    check_structure(prefab)
                    found[prefab.name] = prefab
                except Exception as error:   # a broken mod must not crash the game
                    print(f"[structures] skipped {os.path.join(folder, file)}: {error}")
        _structure_cache = list(found.values())
    return _structure_cache


def check_structure(prefab):
    if not prefab.list_setting("biomes"):
        raise ValueError("missing @biomes")
    if len(prefab.markers.get("item", [])) != len(prefab.list_setting("items")):
        raise ValueError("number of I markers and @items entries differ")
    if len(prefab.markers.get("npc", [])) != len(prefab.list_setting("npcs")):
        raise ValueError("number of N markers and @npcs entries differ")


def boss_building(biome):
    """Building around a boss: mods/bosses/<biome>.txt if a mod has one, else game/world/prefabs/bosses/<biome>.txt.
    Convention: back door in the TOP row (towards the passage), front door in the BOTTOM row, B = where the boss stands."""
    for folder in (os.path.join(MODS_DIR, "bosses"), os.path.join(PREFAB_DIR, "bosses")):
        path = os.path.join(folder, f"{biome}.txt")
        if os.path.exists(path):
            try:
                prefab = load_prefab_file(path)
                if not prefab.markers.get("boss"):
                    raise ValueError("missing B marker")
                return prefab
            except Exception as error:
                print(f"[bosses] skipped {path}: {error}")
    return None
