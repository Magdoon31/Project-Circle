# SIGILS - permanent upgrades (like the chips in FNaF World). Not items: they have their own page in the inventory
# (Items / Sigils switch at the top). 4 columns x 3 sigils, only ONE active per column (4 at once at most).
# Each one is found through a secret (secrets: to be designed - TEST: key 0 on the map gives all of them).
# All sigils of a column share its picture: assets/img/inventory/sigils/<column picture>.png
#
# Where they work: shop (Haggler, Lucky Coin), fight money (Lucky Coin), luck (Lucky Charm - Game.luck()),
# inventory (Spare Pocket = 2nd trinket slot), Shooter (Steady Hands, Overflow, Vigor, Might, Swift),
# Combat (Headstart, Bullet Time, Close Call).

# HOW THEY ARE FOUND (7.11, see the project's SIGILS.md): "how" = shown on a locked card instead of what it does;
# "secret" = a locked card shows only ??? (the better ones). Given by Game.award_sigil().
#   Overflow - Wren (Separated Village, the first one; the Sigils page shows up only after it)
#   Close Call - win a Tundra fight with <= 10% HP | Lucky Charm - secret hall in the Factory (conveyor through a wall)
#   Vigor / Swift / Might - shrines in the Garden | Haggler - the "?" field on Lucky's wheel (secret) | Lucky Coin - Firefly Queen in a dash
#   Headstart / Spare Pocket - Pale World (not made yet) | Steady Hands - the Core's gold vault (opens once all its gold is picked up)
#   Bullet Time - 30 near misses in one Core fight
SHRINE_HOW = "Find a shrine hidden\nin the Underground Garden."
COLUMN_COLOURS = {"fortune": (236, 178, 104), "craft": (120, 200, 220), "warden": (130, 140, 255), "tribe": (196, 120, 255)}
NAMES = {}          # sigil id -> name (filled below)

COLUMNS = [
    {"id": "fortune", "name": "Fortune", "image": "fortune.png", "sigils": [
        {"id": "haggler", "name": "Haggler", "text": "Shop prices -15%.",
         "secret": True},
        {"id": "lucky_coin", "name": "Lucky Coin", "text": "Shop rerolls -15%.\n+20% gold from fights.",
         "how": "Defeat a Firefly Queen\nduring her dash."},
        {"id": "lucky_charm", "name": "Lucky Charm", "text": "+1 luck.", "secret": True},
    ]},
    {"id": "craft", "name": "Craft", "image": "craft.png", "sigils": [
        {"id": "spare_pocket", "name": "Spare Pocket", "text": "A second trinket slot.", "secret": True},
        {"id": "steady_hands", "name": "Steady Hands", "text": "Your weapon has no recoil\n(shotguns: 90% less).", "secret": True},
        {"id": "overflow", "name": "Overflow", "text": "Shotguns fire +1 pellet.", "how": "Talk to Wren."},
    ]},
    {"id": "warden", "name": "Warden", "image": "warden.png", "sigils": [
        {"id": "headstart", "name": "Headstart", "text": "Enemies don't move or shoot\nfor the first 2 s of a fight.",
         "secret": True},
        {"id": "bullet_time", "name": "Bullet Time", "text": "Enemy bullets fly 15% slower.",
         "how": "In one fight in The Core,\nlet 30 bullets fly right past you."},
        {"id": "close_call", "name": "Close Call", "text": "Dodged enemy bullet reloads your\nweapon but enemies hurt you 50% more.",
         "how": "Win a fight in the Silverpine Tundra\nwith 10% HP or less."},
    ]},
    {"id": "tribe", "name": "Tribe", "image": "tribe.png", "sigils": [
        {"id": "vigor", "name": "Vigor", "text": "+15% max HP in fights.", "how": SHRINE_HOW},
        {"id": "might", "name": "Might", "text": "+10% damage.", "how": SHRINE_HOW},
        {"id": "swift", "name": "Swift", "text": "+10% movement speed in fights.", "how": SHRINE_HOW},
    ]},
]
ALL_SIGILS = [s["id"] for c in COLUMNS for s in c["sigils"]]
NAMES.update({s["id"]: s["name"] for c in COLUMNS for s in c["sigils"]})
IMAGE_OF = {s["id"]: c["image"] for c in COLUMNS for s in c["sigils"]}
COLUMN_OF = {s["id"]: c["id"] for c in COLUMNS for s in c["sigils"]}

# the numbers
STEADY_SHOTGUN = 0.1             # Steady Hands: a shotgun keeps 10% of its spread
HAGGLER_PRICE = 0.85
LUCKY_COIN_REROLL = 0.85         # Lucky Coin: reroll price x this
LUCKY_COIN_GOLD = 1.2
LUCKY_CHARM_LUCK = 1            # see Game.luck()
CLOSE_CALL_HP = 0.10            # Close Call: win a Tundra fight with this share of HP or less
NEAR_MISSES = 30                # Bullet Time: near misses in one Core fight
HEADSTART_FRAMES = 120          # 2 s (10.11, was 1.5 s)
BULLET_TIME_SPEED = 0.85
CLOSE_CALL_DISTANCE = 2.6       # x the player's radius: closer than this (but no hit) = a close call
CLOSE_CALL_COOLDOWN = 60        # (8.11) frames: Close Call reloads at most once a second (Flare Gun + a line of icicles)
CLOSE_CALL_HURT = 1.5           # (8.11) the price: with Close Call on, enemies hurt you x1.5
VIGOR_HP = 1.15
MIGHT_DMG = 1.10
SWIFT_SPEED = 1.10


class Sigils:
    """What the player has found and what is switched on (saved in Game.counters["sigils"])."""

    def __init__(self, data=None):
        self.load(data)

    def load(self, data):
        data = data or {}
        self.owned = [s for s in data.get("owned", []) if s in COLUMN_OF]
        self.active = {c: s for c, s in data.get("active", {}).items() if s in self.owned and COLUMN_OF.get(s) == c}

    def to_dict(self):
        return {"owned": list(self.owned), "active": dict(self.active)}

    def give(self, sigil_id):
        if sigil_id in COLUMN_OF and sigil_id not in self.owned:
            self.owned.append(sigil_id)
            return True
        return False

    def toggle(self, sigil_id):
        """Switch a found sigil on (the other one of its column goes off) or off again."""
        if sigil_id not in self.owned:
            return False
        column = COLUMN_OF[sigil_id]
        if self.active.get(column) == sigil_id:
            del self.active[column]
        else:
            self.active[column] = sigil_id
        return True

    def on(self, sigil_id):
        return sigil_id in self.active.values()

    def active_set(self):
        return set(self.active.values())
