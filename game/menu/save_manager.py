import json
import os
import random
import hashlib

MAX_SEED = 10**9


def seed_from_text(text):
    """Seed typed in the menu -> world seed. Empty = random. Digits = that number. Any other text is turned
    into a number the same way every time (so "filip" always gives the same world)."""
    text = text.strip()
    if not text:
        return random.randrange(1, MAX_SEED)
    if text.isdigit():
        return int(text) % MAX_SEED
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % MAX_SEED

def to_bool(value):
    # older saves stored hard_mode as the string "True"
    return value is True or value == "True"

class SaveManager:
    def __init__(self, player, inventory, map):
        self.player = player
        self.inventory = inventory
        self.map = map
        self.pending_seed = None      # (seed, text) chosen in the menu for the next NEW game
        self.started_new = False      # True after load_game made a NEW game (Game plays the intro)
        self.game_quests = None       # Game's QuestLog (set by load_game)
        self.game_counters = None     # Game's counters dict (minigame plays / wins ...)
        self.seed_text = ""           # what the player typed for the current world ("" = random) - for the stats page later
        
    def save_game(self, nr, hard_mode):
        if nr in (1,2,3):
            save_data = {
                        "player": {
                            "x": self.player.x,
                            "y": self.player.y,
                            "money": self.player.money,
                            "playtime" : self.player.play_time
                        },
                        "inventory": {
                            "active_items": [item.id for slot, item in self.inventory.active_items.items()
                                             if item is not None and slot != "trinket2"],
                            "active_trinket2": self.inventory.active_items.get("trinket2").id
                                               if self.inventory.active_items.get("trinket2") else None,
                            "items": [item.id for item in self.inventory.items]
                        },
                        "map": {
                            # the world is rebuilt from the seed; only changes are stored, per level (surface / cellar)
                            "seed": self.map.seed,
                            "seed_text": self.seed_text,                # what was typed in the menu ("" = random)
                            "level": self.map.level,                    # where the player is
                            "levels": self.map.levels_state(),          # collected loot, beaten bosses, seen tiles
                            "flags": sorted(self.map.flags),            # story switches (e.g. void_unlocked)
                        },
                        "quests": self.game_quests.state() if self.game_quests else {},
                        "counters": dict(self.game_counters) if self.game_counters is not None else {},
                        "game": {
                            "hard_mode" : to_bool(hard_mode)
                        }
                    }
            with open(f"game/text/save{nr}.json", "w") as f:
                json.dump(save_data, f, indent=4)

    def has_world(self, nr):
        """True if this save slot already holds a world (loading it = rebuilding the saved terrain, not a new one)."""
        try:
            with open(f"game/text/save{nr}.json", "r") as f:
                return "seed" in json.load(f).get("map", {})
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, TypeError):
            return False

    def load_game(self, nr, game):
        game.inventory.items = []
        # clear equipment from a previously loaded save
        for slot in ("weapon", "armor", "trinket", "trinket2"):
            game.inventory.active_items[slot] = None
        game.inventory.selected_item = None
        self.game_quests = game.quests
        game.counters.clear()
        self.game_counters = game.counters
        self.started_new = False
        if nr in (1,2,3):
            try:
                with open(f"game/text/save{nr}.json", "r") as f:
                    save_data = json.load(f)
                    game.player.x = save_data["player"]["x"]
                    game.player.y = save_data["player"]["y"]
                    game.player.money = save_data["player"]["money"]
                    game.player.play_time = save_data["player"]["playtime"]
                    game.quests.load(save_data.get("quests"))
                    game.counters.update(save_data.get("counters", {}))
                    map_data = save_data["map"]
                    self.seed_text = map_data.get("seed_text", "")
                    if "levels" in map_data:
                        game.map.generate(map_data["seed"], map_data["levels"], map_data.get("level", "surface"), map_data.get("flags"))
                    elif "seed" in map_data:
                        # save from before the cellar existed: everything belongs to the surface
                        game.map.generate(map_data["seed"], {"surface": {"collected": map_data.get("collected", []),
                                                                         "defeated": map_data.get("defeated", []),
                                                                         "explored": map_data.get("explored")}})
                    else:
                        # old save (fixed test map): new world, player goes to the village start
                        game.map.generate(random.randrange(1, 10**9))
                        game.player.x, game.player.y = game.map.start_position()
                    game.hard_mode = to_bool(save_data["game"]["hard_mode"])
                    for item_name in save_data["inventory"]["active_items"]:
                        item = game.inventory.ItemDB.get_item(item_name)
                        if item is not None:
                            game.inventory.active_items[item.type] = item
                    second = save_data["inventory"].get("active_trinket2")     # Spare Pocket (sigil)
                    if second and game.inventory.ItemDB.get_item(second) is not None:
                        game.inventory.active_items["trinket2"] = game.inventory.ItemDB.get_item(second)
                    for item_name in save_data["inventory"]["items"]:
                        item = game.inventory.ItemDB.get_item(item_name)
                        if item is not None:
                            game.inventory.items.append(item)
            except (FileNotFoundError, json.JSONDecodeError):
                game.player.money = 0
                game.player.play_time = 0
                # NEW GAME: the seed chosen in the menu (difficulty page), or a random one
                self.started_new = True
                game.quests.load({})
                seed, self.seed_text = self.pending_seed or (random.randrange(1, MAX_SEED), "")
                self.pending_seed = None
                game.map.generate(seed)
                game.player.x, game.player.y = game.map.start_position()
                game.inventory.active_items["weapon"] = game.inventory.ItemDB.get_item("Simple Blaster")
                game.inventory.items = [game.inventory.ItemDB.get_item("Simple Pistol")]

    def get_save_info(self,nr):
        if nr in (1,2,3):
            try:
                with open(f"game/text/save{nr}.json", "r") as f:
                    save_data = json.load(f)
                    hard_mode = to_bool(save_data["game"]["hard_mode"])
                    time = int(save_data['player']['playtime'])
                    return [f"Save {nr}","Time Played:", f"{time//3600}:{(time//60)%60:02d}",f"Money: {save_data['player']['money']}"], hard_mode
            except (FileNotFoundError, json.JSONDecodeError):
                    return [f"Save {nr}"," ",f"EMPTY"], False
        return None, False
    
    def reset_data(self, nr):
        if os.path.exists(f"game/text/save{nr}.json"):
            os.remove(f"game/text/save{nr}.json")
