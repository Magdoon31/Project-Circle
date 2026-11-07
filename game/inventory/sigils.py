# SIGILS - permanent upgrades (like the chips in FNaF World). Not items: they have their own page in the inventory
# (Items / Sigils switch at the top). 4 columns x 3 sigils, only ONE active per column (4 at once at most).
# Each one is found through a secret (secrets: to be designed - TEST: key 0 on the map gives all of them).
# All sigils of a column share its picture: assets/img/inventory/sigils/<column picture>.png
#
# Where they work: shop (Haggler, Lucky Coin), fight money (Lucky Coin), luck (Lucky Charm - Game.luck()),
# inventory (Spare Pocket = 2nd trinket slot), Shooter (Steady Hands, Overflow, Vigor, Might, Swift),
# Combat (Headstart, Bullet Time, Close Call).

COLUMNS = [
    {"id": "fortune", "name": "Fortune", "image": "fortune.png", "sigils": [
        {"id": "haggler", "name": "Haggler", "text": "Shop prices -15%."},
        {"id": "lucky_coin", "name": "Lucky Coin", "text": "+1 shop reroll after every boss.\n+20% gold from fights."},
        {"id": "lucky_charm", "name": "Lucky Charm", "text": "+1 luck."},
    ]},
    {"id": "craft", "name": "Craft", "image": "craft.png", "sigils": [
        {"id": "spare_pocket", "name": "Spare Pocket", "text": "A second trinket slot."},
        {"id": "steady_hands", "name": "Steady Hands", "text": "Your weapon has no recoil."},
        {"id": "overflow", "name": "Overflow", "text": "Shotguns fire +1 pellet."},
    ]},
    {"id": "warden", "name": "Warden", "image": "warden.png", "sigils": [
        {"id": "headstart", "name": "Headstart", "text": "Enemies don't move or shoot\nfor the first 1.5 s of a fight."},
        {"id": "bullet_time", "name": "Bullet Time", "text": "Enemy bullets fly 15% slower."},
        {"id": "close_call", "name": "Close Call", "text": "An enemy bullet flying right past you\nreloads your weapon instantly."},
    ]},
    {"id": "tribe", "name": "Tribe", "image": "tribe.png", "sigils": [
        {"id": "vigor", "name": "Vigor", "text": "+15% max HP in fights."},
        {"id": "might", "name": "Might", "text": "+10% damage."},
        {"id": "swift", "name": "Swift", "text": "+10% movement speed in fights."},
    ]},
]
ALL_SIGILS = [s["id"] for c in COLUMNS for s in c["sigils"]]
COLUMN_OF = {s["id"]: c["id"] for c in COLUMNS for s in c["sigils"]}

# the numbers
HAGGLER_PRICE = 0.85
LUCKY_COIN_REROLLS = 1
LUCKY_COIN_GOLD = 1.2
LUCKY_CHARM_LUCK = 1            # (luck isn't used by anything yet - see Game.luck())
HEADSTART_FRAMES = 90           # 1.5 s
BULLET_TIME_SPEED = 0.85
CLOSE_CALL_DISTANCE = 2.6       # x the player's radius: closer than this (but no hit) = a close call
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
