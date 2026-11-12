# The world map in the game: generated from a seed (game/world/surface_map.py), drawn around the player.
#
# Coordinates: the player position (player.x, player.y) is in WORLD PIXELS; tile = pixel // tile_size.
# State that changes while playing (saved in the save file):
#   collected - positions of picked up gold / items
#   defeated  - positions of beaten bosses (their gate opens - for good)
#   away      - beaten bosses that are gone for now; they come back when the next normal fight starts
#               (the gate they opened stays open)
#   flags     - story switches for the whole world, e.g. "void_unlocked"
#   explored  - tiles the player has seen (for the world map, key M)

import math, zlib, base64
from collections import deque
import pygame
from game.world.surface_map import SurfaceMap
from game.world.cellar_map import CellarMap
from game.world.core_map import CoreMap
from game.world.void_map import VoidMap
from game.world.lunapark_map import LunaparkMap
from game.world.tiles import TILES, tile_color, pale_color
from game.world import pale_world as PALE
from game.lib import snow_overlay as SNOW
from game.menu import options as OPT
from game.world import surface_layout as L

TILES_ON_SCREEN_Y = 13          # start screen shows the fenced square + ~2 tiles (author's decision)
BOSS_NAME = "boss1"             # TEMPORARY: boss spots without a real boss yet use boss1
BOSS_OF_ZONE = {"village": "slime_king", "rainbow_fields": "prism", "candy": "shroom_mother", "tundra": "frost_golem",
                "factory": "assembly_line", "garden": "night_bloom", "core": "milo"}    # the real bosses (7.11, one by one): gate "from" -> EnemyDB.bosses
FOG_COLOR = (18, 18, 22)        # unexplored part of the world map
CONVEYOR_ANIM_SPEED = 60        # pixels per second the chevrons on conveyor belts move (just looks)
QUEST_SPOTS = {                  # (11.11) NPC / place -> (quest, flag once it's done): a "!" while it is still to do
    "clue_stones": ("wren", "clue:stones"),
    "clue_playground": ("wren", "clue:playground"),
    "clue_lab": ("wren", "clue:lab"),
}
QUEST_MARK_COLOUR = (255, 214, 60)
CRACK_RANGE = 2.6               # (11.11) tiles: a secret way in shows its crack only this close
CRACK_SHAPE = [(-0.3, -0.42), (-0.05, -0.12), (-0.2, 0.1), (0.12, 0.3), (0.05, 0.45)]   # parts of a tile

# LEVELS: separate maps of the world, all generated from the same seed.
# The cellar is generated only when the player goes there for the first time.
LEVELS = {"surface": SurfaceMap, "cellar": CellarMap, "core": CoreMap, "void": VoidMap, "lunapark": LunaparkMap}
# PALE WORLD (7.11, game/world/pale_world.py): "pale_<level>" = the pale copy of that level (glitch stones lead there)
for _base in PALE.PALE_ZONES:
    LEVELS[PALE.PALE_PREFIX + _base] = (lambda b: lambda seed: PALE.PaleWorld(b, PALE.with_glitches(b, LEVELS[b](seed))))(_base)

# below the pale Garden (the maze to ###): built from the cellar's maze stones
LEVELS[PALE.NOWHERE] = lambda seed: PALE.NowhereMap(seed, PALE.NOWHERE, PALE.deep_targets(seed, LEVELS["cellar"]).get(PALE.NOWHERE))
LEVELS[PALE.NOWHERE2] = lambda seed: PALE.NowhereMap(seed, PALE.NOWHERE2, PALE.deep_targets(seed, LEVELS["cellar"]).get(PALE.NOWHERE2))
LEVELS[PALE.HASH] = PALE.HashMap
LEVEL_TITLES = {"surface": "Surface", "cellar": "Cellar", "core": "The Core", "void": "The Void", "lunapark": "Lunapark",
                "pale_surface": "Surf4ce", "pale_cellar": "C3llar", "pale_core": "The C0re",
                PALE.NOWHERE: "N0wh3r3", PALE.NOWHERE2: "N0wh3r3", PALE.HASH: "###"}   # pale: a little broken
# small side levels without their own world map (M): it shows this level instead (the lunapark -> the Surface)
MAP_SHOWS = {"lunapark": "surface"}
# levels where the world map (M) FORGETS: a seen place fades back into the fog after this many ms.
# ("% explored" still counts everything you have ever seen.) Not saved: after loading the memory is empty.
MAP_MEMORY_MS = {"void": 60_000}
# screen overlay per level (drawn over the world and the player, under the UI, stretched to the screen)
LEVEL_OVERLAYS = {"cellar": "assets/img/map/cellar_overlay.png", "void": "assets/img/map/cellar_overlay.png",
                  "pale_cellar": "assets/img/map/cellar_overlay.png"}
# how many times the overlay is layered in a biome (2 = darker). Changes smoothly when crossing biomes.
BIOME_OVERLAY_STRENGTH = {"underground_garden": 2.0, "the_void": 3.0}
OVERLAY_FADE = 0.03             # per frame
SNOW_BIOMES = {"silverpine_tundra"}     # (8.11) Filip's animated snow overlay over these biomes (fades in/out)


class LevelView:
    """What the world map needs to draw one level (the current one or another visited one)."""
    def __init__(self, game_map, name, lvl):
        self.level = name
        self.is_current = name == game_map.level
        self.world = lvl["world"]
        self.overview = lvl["overview"]
        self.away = lvl["away"]
        self.memory_ms = MAP_MEMORY_MS.get(name)
        self._lvl = lvl

    def is_explored(self, tile):
        i = tile[1] * self.world.width + tile[0]
        return i in self._lvl["seen_until"] if self.memory_ms else bool(self._lvl["explored"][i])

    def explored_fraction(self):
        return self._lvl["explored_count"] / max(1, self._lvl["land_tiles"])


class Map:
    def __init__(self, screen):
        self.screen = screen
        self.tile_size = screen.get_height() // TILES_ON_SCREEN_Y
        self.player = None
        self.item_db = None       # set by Game (for item icons on the ground)
        self.world = None
        self.seed = None
        self.collected = set()
        self.active_quests = set()      # set by Game: pickups with "quest" exist only while that quest is active
        self.quest_steps = {}           # set by Game: quest -> its current step
        self.defeated = set()
        self.away = set()
        self.flags = set()
        self.extra_npcs = []           # NPCs placed by the game (Milo moving after bosses) - set by Game
        self.hidden_npcs = set()       # ids of map NPCs that are gone for now (e.g. Milo left the Village)
        self.locked_gates = set()      # gate positions closed by the story (the way back after choosing a path)
        self.locked_portals = set()    # portal positions closed the same way
        self.lock_hit = False          # the player just bumped into such a closed way
        self.secret_hit = None         # the player just bumped into a closed secret way (its id)
        self.glitch_hit = None         # the glitch stone the player is pushing into right now (tile)
        self.orb_on = False            # the Pale Orb is equipped (glitch stones flicker) - set by Game
        self.pale_return = None        # (level, (x, y) px) where the player came into the Pale World (for saving)
        self.confine = None            # (x, y, w, h) tiles the player may not leave (start fence before Milo) - set by Game
        self.confine_hit = False       # the player just bumped into that invisible border
        self.memory_bonus_ms = 0       # set by Game from the trinket (Eyeballs "map_memory") - longer memory in the Void
        self._icon_cache = {}
        self._overlay_cache = {}
        self.overlay_strength = 1.0
        self.snow_strength = 0.0           # Tundra snow overlay (0..1, fades with the biome)
        self.font = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(12, self.tile_size // 4))

    # --- generating / loading ---------------------------------------------------------
    def generate(self, seed, levels=None, current="surface", flags=None):
        """levels: saved state per level {name: {"collected", "defeated", "away", "explored"}} (from the save file)."""
        self.seed = seed
        self.flags = set(flags or [])
        self.saved_levels = levels or {}
        self.levels = {}
        self.level = None
        self.switch_level(current)

    def is_built(self, name):
        return name in self.levels

    def switch_level(self, name):
        if name not in self.levels:
            self._build_level(name)
        lvl = self.levels[name]
        self.level = name
        # the attributes below always point to the CURRENT level's state (shared objects, not copies)
        self.world = lvl["world"]
        self.collected = lvl["collected"]
        self.defeated = lvl["defeated"]
        self.away = lvl["away"]
        self.explored = lvl["explored"]
        self.gate_of_cell = lvl["gate_of_cell"]
        self.overview = lvl["overview"]
        self.land_tiles = lvl["land_tiles"]
        self.reach = lvl["reach"]
        self.extra_npcs = []               # the game places its own NPCs for the new level (Game.update_story)
        self.refresh_npcs()
        self.last_reveal_tile = None
        self.last_refresh = 0
        self.memory_ms = MAP_MEMORY_MS.get(name)
        self.seen_until = lvl["seen_until"]

    def _build_level(self, name):
        saved = self.saved_levels.get(name, {})
        world = LEVELS[name](self.seed)
        if not PALE.is_pale(name):
            PALE.add_glitches(name, world)            # glitch stones to the Pale World (own random, the rest stays)
        gate_of_cell = {}                  # which gate each "|" tile belongs to
        for gate in world.gates:
            for cell in gate["cells"]:
                gate_of_cell[cell] = gate
        self.world = world
        self.gate_of_cell = gate_of_cell
        self.defeated = {tuple(p) for p in saved.get("defeated", [])}
        self.explored = self.decode_explored(saved.get("explored"))
        self.memory_ms = MAP_MEMORY_MS.get(name)
        self.seen_until = {}               # forgetful levels: tile index -> remembered until (ms, pygame ticks)
        self._build_overview()             # needs world, gate_of_cell, defeated, explored
        # "% explored" counts only tiles the player can actually walk on and reach
        reach = self._reachable_mask(world)
        explored_count = sum(1 for i, r in enumerate(reach) if r and self.explored[i])
        self.levels[name] = {"world": world, "collected": {tuple(p) for p in saved.get("collected", [])},
                             "defeated": self.defeated, "away": {tuple(p) for p in saved.get("away", [])},
                             "explored": self.explored, "gate_of_cell": gate_of_cell,
                             "overview": self.overview, "land_tiles": sum(reach), "reach": reach,
                             "explored_count": explored_count, "seen_until": self.seen_until,
                             "forget_queues": {}}       # how long a place is remembered (ms) -> deque of (until, tiles)

    def _reachable_mask(self, world):
        # walkable tiles reachable from the level's start / arrival points (all passages open)
        starts = [world.player_start] + list(getattr(world, "arrivals", {}).values())
        mask = bytearray(world.width * world.height)
        queue = deque()
        for s in starts:
            mask[s[1] * world.width + s[0]] = 1
            queue.append(s)
        while queue:
            x, y = queue.popleft()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < world.width and 0 <= ny < world.height:
                    i = ny * world.width + nx
                    if not mask[i] and not TILES[world.tiles[ny][nx]]["solid"]:
                        mask[i] = 1
                        queue.append((nx, ny))
        return mask

    def explored_fraction(self):
        lvl = self.levels[self.level]
        return lvl["explored_count"] / max(1, lvl["land_tiles"])

    def levels_state(self):
        """State of every level for the save file (levels never visited keep what was loaded)."""
        state = dict(self.saved_levels)
        for name, lvl in self.levels.items():
            state[name] = {"collected": sorted(list(p) for p in lvl["collected"]),
                           "defeated": sorted(list(p) for p in lvl["defeated"]),
                           "away": sorted(list(p) for p in lvl["away"]),
                           "explored": base64.b64encode(zlib.compress(bytes(lvl["explored"]), 9)).decode("ascii")}
        return state

    def arrival_position(self, leads_to_key):
        """Pixel position where the player appears when arriving through a portal.
        leads_to_key: e.g. "surface:separated" = coming from the surface portal in the separated village."""
        world = self.world
        if hasattr(world, "arrivals") and leads_to_key in world.arrivals:
            return self.tile_centre(world.arrivals[leads_to_key])
        # surface: next to the portal of that zone
        zone = leads_to_key.split(":")[1]
        portal = next(p for p in world.portals if p["zone"] == zone)
        px, py = portal["pos"]
        for dx, dy in ((0, 2), (2, 0), (-2, 0), (0, -2), (2, 2), (-2, 2), (0, 3)):
            tx, ty = px + dx, py + dy
            if not self.blocked(tx, ty):
                return self.tile_centre((tx, ty))
        return self.tile_centre((px, py + 1))

    def start_position(self):
        return self.tile_centre(self.world.player_start)

    def tile_centre(self, tile):
        return (tile[0] + 0.5) * self.tile_size, (tile[1] + 0.5) * self.tile_size

    def tile_at(self, x, y):
        return int(x // self.tile_size), int(y // self.tile_size)

    # --- rules ------------------------------------------------------------------------
    def npcs(self):
        """NPCs on the current level right now: the map's own (minus hidden ones) + those placed by the game."""
        return [n for n in self.world.npcs if n["id"] not in self.hidden_npcs] + self.extra_npcs

    def quest_marked(self, npc):
        """(11.11) Is this NPC / place still to do for an active quest (QUEST_SPOTS) -> drawn with a "!"."""
        spot = QUEST_SPOTS.get(npc["id"])
        return bool(spot) and spot[0] in self.active_quests and spot[1] not in self.flags

    def refresh_npcs(self):
        self.npc_cells = {tuple(n["pos"]) for n in self.npcs()}    # NPCs are solid - you bump into them

    def gate_open(self, gate):
        if tuple(gate["pos"]) in self.locked_gates:
            return False
        return gate["boss"] is None or tuple(gate["boss"]) in self.defeated

    def blocked(self, tx, ty):
        if not (0 <= tx < self.world.width and 0 <= ty < self.world.height):
            return True
        if self.confine:
            cx, cy, cw, ch = self.confine
            if not (cx <= tx < cx + cw and cy <= ty < cy + ch):
                self.confine_hit = True
                return True
        char = self.world.tiles[ty][tx]
        if char == "Q":
            self.glitch_hit = (tx, ty)                 # pushing into a glitch stone (Game counts how long)
        if char == "|":
            gate = self.gate_of_cell[(tx, ty)]
            if tuple(gate["pos"]) in self.locked_gates:
                self.lock_hit = True
            return not self.gate_open(gate)
        for sid, cells in getattr(self.world, "locked", {}).items():
            if (tx, ty) in cells and f"open:{sid}" not in self.flags:
                self.secret_hit = sid                  # e.g. the Core's gold vault: "The gold is still lying..."
                return True
        return TILES[char]["solid"] or (tx, ty) in self.npc_cells

    def can_stand(self, x, y, radius):
        # circle vs tiles: check the centre and 8 points on the edge
        points = [(x, y)] + [(x + math.cos(a) * radius, y + math.sin(a) * radius) for a in [i * math.pi / 4 for i in range(8)]]
        return not any(self.blocked(*self.tile_at(px, py)) for px, py in points)

    def floor_color(self, biome):
        """(8.11) Colour of the biome's ground (its most common walkable tile on this level) - the fight floor."""
        cache = self.__dict__.setdefault("_floor_cache", {})
        key = (self.level, biome, getattr(self.world, "pale", False))
        if key not in cache:
            counts = {}
            for ty in range(self.world.height):
                row = self.world.tiles[ty]
                for tx in range(self.world.width):
                    char = row[tx]
                    if not TILES[char]["solid"] and self.world.biome_at(tx, ty) == biome:
                        counts[char] = counts.get(char, 0) + 1
            char = max(counts, key=counts.get) if counts else "."
            color = tile_color(char, biome)
            cache[key] = pale_color(color) if key[2] else color
        return cache[key]

    def biome_at(self, x, y):
        tx, ty = self.tile_at(x, y)
        if 0 <= tx < self.world.width and 0 <= ty < self.world.height:
            return self.world.biome_at(tx, ty)
        return None

    def conveyor_push(self, x, y):
        """Direction (dx, dy) of the conveyor belt under this point, or None."""
        tx, ty = self.tile_at(x, y)
        if 0 <= tx < self.world.width and 0 <= ty < self.world.height:
            return TILES[self.world.tiles[ty][tx]].get("push")
        return None

    def encounter_allowed(self, x, y):
        if getattr(self.world, "pale", False):
            return False                       # no fights in the Pale World (yet - its own enemies later)
        tx, ty = self.tile_at(x, y)
        return TILES[self.world.tiles[ty][tx]]["encounter"]

    def boss_at(self, x, y, radius):
        # the gate whose boss (present right now) the player touches
        for gate in self.world.gates:
            if gate["boss"] and tuple(gate["boss"]) not in self.away:
                bx, by = self.tile_centre(gate["boss"])
                if math.hypot(x - bx, y - by) < radius + self.tile_size * 0.45:
                    return gate
        return None

    def pickup_shown(self, pickup):
        # "quest": only while that quest is active | "flag": only once that story flag is set (e.g. the Pale Orb)
        return (not pickup.get("quest") or pickup["quest"] in self.active_quests) and \
               (not pickup.get("flag") or pickup["flag"] in self.flags)

    def pickups_at(self, x, y, radius):
        found = []
        for pickup in self.world.pickups:
            if pickup["pos"] in self.collected or not self.pickup_shown(pickup):
                continue
            px, py = self.tile_centre(pickup["pos"])
            if math.hypot(x - px, y - py) < radius + self.tile_size * 0.3:
                found.append(pickup)
        return found

    def portal_open(self, portal):
        # some portals are sealed until a story flag is set (e.g. the Void portal: "void_unlocked")
        if tuple(portal["pos"]) in self.locked_portals:
            return False
        return not portal.get("sealed") or portal["sealed"] in self.flags

    def beat_boss(self, gate):
        boss = tuple(gate["boss"])
        self.defeated.add(boss)        # its gate opens for good
        self.away.add(boss)            # gone until the next normal fight

    def respawn_bosses(self):
        # a normal fight started: every beaten boss is back at its spot (in every level), gates stay open
        for lvl in self.levels.values():
            lvl["away"].clear()
        for state in self.saved_levels.values():
            state["away"] = []

    def npc_near(self, x, y, radius):
        """The NPC the player is close enough to talk to (about one tile between them), or None."""
        for npc in self.npcs():
            nx, ny = self.tile_centre(npc["pos"])
            if math.hypot(x - nx, y - ny) < radius + self.tile_size * 1.1:
                return npc
        return None

    def draw_talk_prompt(self, npc):
        # "E" bubble above an NPC you can talk to
        ts = self.tile_size
        sw, sh = self.screen.get_size()
        cx = (npc["pos"][0] + 0.5) * ts - (self.player.x - sw / 2)
        cy = (npc["pos"][1] - 0.35) * ts - (self.player.y - sh / 2)
        bob = math.sin(pygame.time.get_ticks() / 180) * ts * 0.05
        rect = pygame.Rect(0, 0, ts * 0.5, ts * 0.5)
        rect.center = (cx, cy + bob)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 0, 8)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 3, 8)
        label = self.font.render("E", True, (0, 0, 0))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def portal_at(self, x, y, radius):
        for portal in self.world.portals:
            px, py = self.tile_centre(portal["pos"])
            if math.hypot(x - px, y - py) < radius + self.tile_size * 0.4:
                return portal
        return None

    def zone_spawn(self, zone):
        # TEST helper (number keys): a walkable tile near the middle of a zone, reachable from the start
        cells = [(x, y) for y in range(self.world.height) for x in range(self.world.width) if self.world.zones[y][x] == zone]
        if not cells:
            return None
        cx = sum(c[0] for c in cells) / len(cells)
        cy = sum(c[1] for c in cells) / len(cells)
        start = self.world.player_start
        seen, queue = {start}, deque([start])
        best, best_d = start, 1e9
        while queue:
            x, y = queue.popleft()
            if self.world.zones[y][x] == zone:
                d = math.hypot(x - cx, y - cy)
                if d < best_d:
                    best, best_d = (x, y), d
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n not in seen and 0 <= n[0] < self.world.width and 0 <= n[1] < self.world.height \
                        and not TILES[self.world.tiles[n[1]][n[0]]]["solid"]:
                    seen.add(n)
                    queue.append(n)
        return self.tile_centre(best)

    # --- explored area (world map) -----------------------------------------------------
    def _build_overview(self):
        # 1 pixel per tile picture of the world; unexplored tiles stay dark (fog)
        w = self.world
        self.overview = pygame.Surface((w.width, w.height))
        self.overview.fill(FOG_COLOR)
        for ty in range(w.height):
            row = ty * w.width
            for tx in range(w.width):
                if (row + tx in self.seen_until) if self.memory_ms else self.explored[row + tx]:
                    self.overview.set_at((tx, ty), self.overview_color(tx, ty))

    # --- secret places (7.11): drawn as wall until the player steps in (world.hidden: id -> cells) ---------
    def hidden_cells(self):
        """Cells of the current level's secrets that are not found yet."""
        out = set()
        for sid, cells in getattr(self.world, "hidden", {}).items():
            if f"found:{sid}" not in self.flags:
                out |= cells
        return out

    def discover_secrets(self):
        """The player stepped into a secret place: it shows up (map + world map). Returns its id or None."""
        tile = self.tile_at(self.player.x, self.player.y)
        for sid, cells in getattr(self.world, "hidden", {}).items():
            if tile in cells and f"found:{sid}" not in self.flags:
                self.flags.add(f"found:{sid}")
                for tx, ty in cells:
                    if self.explored[ty * self.world.width + tx]:
                        self.overview.set_at((tx, ty), self.overview_color(tx, ty))
                return sid
        return None

    def overview_color(self, tx, ty):
        if self.world.zones[ty][tx] is None:
            return FOG_COLOR                 # outside every biome (mountains / solid rock) blends into the background
        char = self.world.tiles[ty][tx]
        if char != "#" and (tx, ty) in self.hidden_cells():
            char = "#"
        if getattr(self.world, "pale", False):
            return pale_color(tile_color(char, self.world.biome_at(tx, ty)))
        if char == "|":
            char = "," if self.gate_open(self.gate_of_cell[(tx, ty)]) else "|"
        return tile_color(char, self.world.biome_at(tx, ty))

    def reveal_around_player(self):
        # everything on the screen counts as seen
        if self.memory_ms:
            self.forget_old(self.levels[self.level])
            if pygame.time.get_ticks() - self.last_refresh > 5000:
                self.last_reveal_tile = None          # standing still: what's on the screen stays remembered
        tile = self.tile_at(self.player.x, self.player.y)
        if tile == self.last_reveal_tile:
            return
        self.last_reveal_tile = tile
        half_w = int(self.screen.get_width() / self.tile_size / 2) + 1
        half_h = int(self.screen.get_height() / self.tile_size / 2) + 1
        w = self.world
        now = pygame.time.get_ticks()
        self.last_refresh = now
        seen_now = []
        remember = max(self.memory_ms or 0, self.memory_bonus_ms)     # e.g. Eyeballs: 15 min instead of 1
        until = now + remember
        for ty in range(max(0, tile[1] - half_h), min(w.height, tile[1] + half_h + 1)):
            for tx in range(max(0, tile[0] - half_w), min(w.width, tile[0] + half_w + 1)):
                i = ty * w.width + tx
                if self.memory_ms:
                    if i not in self.seen_until:
                        self.overview.set_at((tx, ty), self.overview_color(tx, ty))
                    if self.seen_until.get(i, 0) < until:      # never shortens a longer memory (Eyeballs)
                        self.seen_until[i] = until
                        seen_now.append(i)
                if not self.explored[i]:
                    self.explored[i] = 1
                    self.overview.set_at((tx, ty), self.overview_color(tx, ty))
                    if self.reach[i]:
                        self.levels[self.level]["explored_count"] += 1
        if seen_now and self.memory_ms:
            self.levels[self.level]["forget_queues"].setdefault(remember, deque()).append((until, seen_now))

    def forget_old(self, lvl):
        # forgetful level: places whose memory ran out go back into the fog on the world map
        # (one queue per memory length, so every queue is sorted by time)
        now = pygame.time.get_ticks()
        w = lvl["world"].width
        seen_until, overview = lvl["seen_until"], lvl["overview"]
        for queue in lvl["forget_queues"].values():
            while queue and queue[0][0] <= now:
                until, tiles = queue.popleft()
                for i in tiles:
                    if seen_until.get(i) == until:      # not seen again since then
                        del seen_until[i]
                        overview.set_at((i % w, i // w), FOG_COLOR)

    def refresh_overview_gates(self):
        # after a boss is beaten its gate is drawn as road on the world map
        for cell in self.gate_of_cell:
            if self.explored[cell[1] * self.world.width + cell[0]]:
                self.overview.set_at(cell, self.overview_color(*cell))

    def reveal_all(self):
        """TEST cheat (world map + ' key): marks the whole current level as explored."""
        for i in range(len(self.explored)):
            self.explored[i] = 1
        if self.memory_ms:
            now = pygame.time.get_ticks()
            until = now + max(self.memory_ms, self.memory_bonus_ms)
            self.seen_until.update((i, until) for i in range(len(self.explored)))
            self.levels[self.level]["forget_queues"].setdefault(until - now, deque()).append((until, list(range(len(self.explored)))))
        self._build_overview()
        self.levels[self.level]["overview"] = self.overview
        self.levels[self.level]["explored_count"] = self.land_tiles

    def is_explored(self, tile):
        i = tile[1] * self.world.width + tile[0]
        return i in self.seen_until if self.memory_ms else bool(self.explored[i])

    def reveal_zone(self, level, zone):
        """Quest reward: uncover one zone of a level on the world map (e.g. "surface", "rainbow_fields")."""
        if level not in LEVELS or MAP_MEMORY_MS.get(level):
            return
        self.view(level)                                    # builds it if needed
        lvl = self.levels[level]
        world, explored, overview = lvl["world"], lvl["explored"], lvl["overview"]
        current = self.level
        if current != level:
            self.switch_level(level)                        # overview_color() works on the current level
        for ty in range(world.height):
            for tx in range(world.width):
                if world.zones[ty][tx] == zone:
                    i = ty * world.width + tx
                    if not explored[i]:
                        explored[i] = 1
                        overview.set_at((tx, ty), self.overview_color(tx, ty))
                        if lvl["reach"][i]:
                            lvl["explored_count"] += 1
        if current != level:
            self.switch_level(current)

    # --- looking at other levels on the world map --------------------------------------------
    def viewable_levels(self):
        """Levels the player has been to (built now, or visited in an earlier session), in world order."""
        return [name for name in LEVELS if (name in self.levels or name in self.saved_levels) and name not in MAP_SHOWS
                and not PALE.is_pale(name)]

    def view(self, name):
        """A read-only look at any visited level for the world map (builds it first if needed, ~1 s)."""
        if name not in self.levels:
            current = self.level
            self._build_level(name)            # sets self.world etc. to the new level ...
            self.switch_level(current)         # ... so point everything back to the current one
        lvl = self.levels[name]
        if MAP_MEMORY_MS.get(name):
            self.forget_old(lvl)
        return LevelView(self, name, lvl)

    def encode_explored(self):
        # 0/1 per tile, compressed -> short text in the save file
        return base64.b64encode(zlib.compress(bytes(self.explored), 9)).decode("ascii")

    def decode_explored(self, text):
        size = self.world.width * self.world.height
        if text:
            try:
                data = bytearray(zlib.decompress(base64.b64decode(text)))
                if len(data) == size:
                    return data
            except (ValueError, zlib.error):
                pass
        return bytearray(size)

    # --- drawing ----------------------------------------------------------------------
    def sigil_icon(self, sigil_id):
        """The picture of the sigil's column, painted in its colour (shrines on the map)."""
        key = ("sigil", sigil_id)
        if key not in self._icon_cache:
            from game.inventory import sigils as SG
            img = None
            column = next((c for c in SG.COLUMNS if any(x["id"] == sigil_id for x in c["sigils"])), None)
            if column:
                try:
                    size = int(self.tile_size * 0.6)
                    img = pygame.transform.smoothscale(pygame.image.load(f"assets/img/inventory/sigils/{column['image']}").convert_alpha(), (size, size))
                    img.fill(SG.COLUMN_COLOURS.get(column["id"], (230, 210, 255)) + (0,), special_flags=pygame.BLEND_RGBA_MAX)
                except (pygame.error, FileNotFoundError):
                    img = None
            self._icon_cache[key] = img
        return self._icon_cache[key]

    def item_icon(self, name):
        if name not in self._icon_cache:
            item = self.item_db.find_item(name) if self.item_db else None
            size = int(self.tile_size * 0.75)
            self._icon_cache[name] = pygame.transform.smoothscale(item.img, (size, size)) if item else None
        return self._icon_cache[name]

    def draw_overlay(self):
        """Darkening overlay of the current level (e.g. the cellar). Call after the player, before the UI."""
        target = 1.0 if self.player.biome in SNOW_BIOMES and not getattr(self.world, "pale", False) else 0.0
        self.snow_strength += max(-OVERLAY_FADE, min(OVERLAY_FADE, target - self.snow_strength))
        if self.snow_strength > 0.01 and OPT.get("weather"):       # (11.11) Settings: weather
            SNOW.draw(self.screen, 255 * self.snow_strength)          # snowfall over the Tundra
        path = LEVEL_OVERLAYS.get(self.level)
        if not path:
            return
        if path not in self._overlay_cache:
            image = pygame.image.load(path).convert_alpha()
            scaled = pygame.transform.smoothscale(image, self.screen.get_size())   # scaled once
            self._overlay_cache[path] = (scaled, scaled.copy())                     # 2nd copy for extra layers
        base, extra = self._overlay_cache[path]
        # strength follows the biome under the player, smoothly
        target = BIOME_OVERLAY_STRENGTH.get(self.player.biome, 1.0)
        target = max(min(target, 0.5), target - getattr(self, "light_bonus", 0))   # (8.11) Firefly Jar: less dark
        if abs(target - self.overlay_strength) <= OVERLAY_FADE:
            self.overlay_strength = target
        else:
            self.overlay_strength += OVERLAY_FADE if target > self.overlay_strength else -OVERLAY_FADE
        strength = self.overlay_strength
        while strength >= 1.0:
            self.screen.blit(base, (0, 0))
            strength -= 1.0
        if strength > 0.01:
            extra.set_alpha(int(255 * strength))
            self.screen.blit(extra, (0, 0))
        self.draw_shrine_lights()

    # --- sigil shrines (7.11): a ring of stones with a pedestal; they shine through the cave's darkness ---------
    def draw_shrine(self, cx, cy, sigil_id):
        ts = self.tile_size
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 300)
        for k in range(8):                                     # the stone ring (about 2 x 2 tiles)
            a = k * math.tau / 8
            sx, sy = cx + math.cos(a) * ts * 0.95, cy + math.sin(a) * ts * 0.95
            pygame.draw.circle(self.screen, (125, 120, 130), (sx, sy), ts * 0.17)
            pygame.draw.circle(self.screen, (75, 72, 82), (sx, sy), ts * 0.17, 2)
        pygame.draw.circle(self.screen, (60, 45, 90), (cx, cy), ts * (0.55 + 0.05 * pulse), max(2, ts // 14))
        pygame.draw.rect(self.screen, (130, 125, 135), (cx - ts * 0.4, cy + ts * 0.12, ts * 0.8, ts * 0.3), 0, 5)
        pygame.draw.rect(self.screen, (80, 76, 86), (cx - ts * 0.4, cy + ts * 0.12, ts * 0.8, ts * 0.3), 2, 5)
        icon = self.sigil_icon(sigil_id)
        if icon:
            self.screen.blit(icon, icon.get_rect(center=(cx, cy - ts * 0.15)))

    def draw_shrine_lights(self):
        """Shrines on the screen glow through the darkness overlay (call after it)."""
        from game.inventory import sigils as SG
        ts = self.tile_size
        sw, sh = self.screen.get_size()
        cam_x, cam_y = self.player.x - sw / 2, self.player.y - sh / 2
        hidden = self.hidden_cells()
        for pickup in self.world.pickups:
            if pickup["type"] != "sigil" or pickup["pos"] in self.collected or tuple(pickup["pos"]) in hidden:
                continue
            cx, cy = (pickup["pos"][0] + 0.5) * ts - cam_x, (pickup["pos"][1] + 0.5) * ts - cam_y
            if not (-ts * 4 < cx < sw + ts * 4 and -ts * 4 < cy < sh + ts * 4):
                continue
            colour = SG.COLUMN_COLOURS.get(SG.COLUMN_OF.get(pickup["sigil"]), (230, 210, 255))
            pulse = 0.85 + 0.15 * math.sin(pygame.time.get_ticks() / 400)
            radius = int(ts * 2.6 * pulse)
            glow = pygame.Surface((radius * 2, radius * 2))
            for k in range(8, 0, -1):                          # soft light: dim at the edge, brighter in the middle
                f = 0.045 * (9 - k)
                pygame.draw.circle(glow, [int(c * f) for c in colour], (radius, radius), radius * k // 8)
            self.screen.blit(glow, glow.get_rect(center=(cx, cy)), special_flags=pygame.BLEND_RGB_ADD)
            self.draw_shrine(cx, cy, pickup["sigil"])

    def draw_secret_cracks(self, hidden, visible, centre):
        """(11.11) A secret way in (prefab marker "h") looks like wall - a thin crack shows on it, but only when the
        player is close (CRACK_RANGE tiles), and fades in as they come nearer."""
        ts = self.tile_size
        player = (self.player.x / ts - 0.5, self.player.y / ts - 0.5)
        for cells in getattr(self.world, "secret_ways", {}).values():
            for cell in cells:
                distance = math.dist(cell, player)
                if cell not in hidden or distance > CRACK_RANGE or not visible(cell):
                    continue
                strength = min(1.0, (CRACK_RANGE - distance) / (CRACK_RANGE - 1))
                colour = [int(c * (1 - 0.55 * strength)) for c in tile_color("#", self.world.biome_at(*cell))]
                cx, cy = centre(cell)
                points = [(cx + ts * dx, cy + ts * dy) for dx, dy in CRACK_SHAPE]
                pygame.draw.lines(self.screen, colour, False, points, max(2, ts // 16))

    def _draw_conveyor(self, sx, sy, push):
        # moving chevrons show the direction of the belt
        ts = self.tile_size
        dx, dy = push
        shift = (pygame.time.get_ticks() * CONVEYOR_ANIM_SPEED / 1000) % (ts / 2)
        color = (120, 120, 132)
        for k in range(2):
            o = k * ts / 2 + shift - ts / 4             # position along the belt
            cx, cy = sx + ts / 2 + dx * o, sy + ts / 2 + dy * o
            px, py = -dy, dx                            # across the belt
            tip = (cx + dx * ts * 0.12, cy + dy * ts * 0.12)
            a = (cx - dx * ts * 0.1 + px * ts * 0.25, cy - dy * ts * 0.1 + py * ts * 0.25)
            b = (cx - dx * ts * 0.1 - px * ts * 0.25, cy - dy * ts * 0.1 - py * ts * 0.25)
            if sx <= tip[0] <= sx + ts and sy <= tip[1] <= sy + ts:
                pygame.draw.lines(self.screen, color, False, [a, tip, b], max(2, ts // 18))

    def draw(self):
        ts = self.tile_size
        sw, sh = self.screen.get_size()
        cam_x = self.player.x - sw / 2
        cam_y = self.player.y - sh / 2
        self.screen.fill((20, 20, 24))
        first_x, first_y = int(cam_x // ts), int(cam_y // ts)
        last_x, last_y = int((cam_x + sw) // ts) + 1, int((cam_y + sh) // ts) + 1
        world = self.world
        hidden = self.hidden_cells()
        pale = getattr(world, "pale", False)

        for ty in range(max(0, first_y), min(world.height, last_y + 1)):
            for tx in range(max(0, first_x), min(world.width, last_x + 1)):
                char = world.tiles[ty][tx] if (tx, ty) not in hidden else "#"
                sx, sy = tx * ts - cam_x, ty * ts - cam_y
                biome = world.biome_at(tx, ty)
                if char == "|":
                    if self.gate_open(self.gate_of_cell[(tx, ty)]):
                        color = tile_color(",", biome)
                    else:
                        color = (235, 235, 235)
                    pygame.draw.rect(self.screen, color, (sx, sy, ts + 1, ts + 1))
                    if not self.gate_open(self.gate_of_cell[(tx, ty)]):
                        pygame.draw.rect(self.screen, (70, 70, 80), (sx + ts * 0.2, sy, ts * 0.15, ts + 1))
                        pygame.draw.rect(self.screen, (70, 70, 80), (sx + ts * 0.65, sy, ts * 0.15, ts + 1))
                else:
                    colour = tile_color(char, biome)
                    if pale:
                        colour = pale_color(colour)
                    pygame.draw.rect(self.screen, colour, (sx, sy, ts + 1, ts + 1))
                    if char == "Q" and self.orb_on:                # a glitch stone flickers while the Pale Orb is on
                        if (pygame.time.get_ticks() // 90 + tx * 7 + ty * 3) % 9 < 2:
                            pygame.draw.rect(self.screen, (235, 235, 245), (sx + ts * 0.15, sy + ts * 0.4, ts * 0.7, ts * 0.12))
                    push = TILES[char].get("push")
                    if push:
                        self._draw_conveyor(sx, sy, push)

        def visible(pos):
            return first_x - 1 <= pos[0] <= last_x + 1 and first_y - 1 <= pos[1] <= last_y + 1

        def centre(pos):
            return (pos[0] + 0.5) * ts - cam_x, (pos[1] + 0.5) * ts - cam_y

        self.draw_secret_cracks(hidden, visible, centre)
        for pos, text in getattr(world, "floor_text", []):          # e.g. "Not yet." in ### (pale_world.py)
            if visible(pos):
                if not hasattr(self, "floor_font"):
                    self.floor_font = pygame.font.Font(None, int(ts * 0.9))
                label = self.floor_font.render(text, True, (150, 150, 155))
                self.screen.blit(label, label.get_rect(center=centre(pos)))
        for portal in world.portals:
            if visible(portal["pos"]):
                sealed = not self.portal_open(portal)
                pygame.draw.circle(self.screen, (90, 90, 100) if sealed else (140, 60, 255), centre(portal["pos"]), ts * 0.45, max(3, ts // 10))
                pygame.draw.circle(self.screen, (25, 25, 30) if sealed else (40, 0, 70), centre(portal["pos"]), ts * 0.3)
        for pickup in world.pickups:
            if pickup["pos"] in self.collected or not visible(pickup["pos"]) or not self.pickup_shown(pickup) \
                    or tuple(pickup["pos"]) in hidden:
                continue
            cx, cy = centre(pickup["pos"])
            if pickup["type"] == "sigil":                  # a shrine (drawn again over the darkness: draw_shrine_lights)
                self.draw_shrine(cx, cy, pickup["sigil"])
            elif pickup["type"] == "gold":
                pygame.draw.circle(self.screen, (255, 210, 40), (cx, cy), ts * 0.2)
                pygame.draw.circle(self.screen, (170, 120, 0), (cx, cy), ts * 0.2, 2)
            else:
                icon = self.item_icon(pickup["item"])
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), ts * 0.42)
                if icon:
                    self.screen.blit(icon, icon.get_rect(center=(cx, cy)))
        for npc in self.npcs():
            if visible(npc["pos"]):
                cx, cy = centre(npc["pos"])
                marked = self.quest_marked(npc)
                pygame.draw.circle(self.screen, QUEST_MARK_COLOUR if marked else (230, 90, 230), (cx, cy), ts * 0.3)
                label = self.font.render("!" if marked else "?", True, (40, 30, 10) if marked else (255, 255, 255))
                self.screen.blit(label, label.get_rect(center=(cx, cy)))
        for gate in world.gates:
            boss = gate["boss"]
            if boss and tuple(boss) not in self.away and visible(boss):
                cx, cy = centre(boss)
                pygame.draw.circle(self.screen, (150, 20, 30), (cx, cy), ts * 0.45)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), ts * 0.45, 3)
                label = self.font.render("BOSS", True, (255, 255, 255))
                self.screen.blit(label, label.get_rect(center=(cx, cy)))
