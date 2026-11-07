# QUESTS - what the player was asked to do. Started / moved on / finished from dialogues ("do": {"quest": ...}).
#
# Active quests are listed in the inventory (Quests panel). Finished quests disappear from the list
# (the game remembers them as flag "quest_done:<id>").

QUESTS = {
    "hook": {
        "title": "The Angler's Hook",
        "steps": {
            "find": "Somebody in the Village has the Angler's Hook. Ask around.",
            "return": "You have the Hook. Bring it back to the Angler.",
        },
    },
    "hal": {
        "title": "Hal's Antennas",
        "steps": {
            "fix0": "Fix the 3 broken antennas around the Tundra for Hal (0/3).",
            "fix1": "Fix the 3 broken antennas around the Tundra for Hal (1/3).",
            "fix2": "Fix the 3 broken antennas around the Tundra for Hal (2/3).",
            "return": "All three antennas work. Go back to Hal.",
        },
    },
    "foreman": {
        "title": "Line Bloodbath",
        "steps": {
            "parts": "Bring the Foreman a Gear (somewhere in the Factory halls), a Meter (from the shop) "
                     "and a Fuse (robo-teslas carry them).",
        },
    },
    "wren": {
        "title": "Things That Don't Fit",
        "steps": {
            "look0": "Examine the 3 places in the Garden that bother Wren: stone rows, a buried playground, an old lab (0/3).",
            "look1": "Examine the 3 places in the Garden that bother Wren: stone rows, a buried playground, an old lab (1/3).",
            "look2": "Examine the 3 places in the Garden that bother Wren: stone rows, a buried playground, an old lab (2/3).",
            "return": "You've seen all three places. Tell Wren what you saw.",
        },
    },
    "gardener": {
        "title": "The Gardener's Sprouts",
        "steps": {
            "sprouts": "Bring the Gardener 3 Glowing Sprouts: two grow in far corners of the Garden, "
                       "one was swallowed by a toxic flower.",
            "water": "Fill the Gardener's watering can at the very end of the old pier.",
            "return": "Bring the water back to the Gardener.",
        },
    },
    "gus": {
        "title": "Something Useful for Gus",
        "steps": {
            "find": "Gus wants a Sugar Crystal. Sugar casters in Sugarwood Grove sometimes drop one.",
        },
    },
}


class QuestLog:
    def __init__(self):
        self.active = {}            # quest id -> current step

    def start(self, quest_id, step=None):
        if quest_id in self.active:
            return False
        self.active[quest_id] = step or next(iter(QUESTS[quest_id]["steps"]))
        return True

    def step(self, quest_id, step):
        if quest_id in self.active:
            self.active[quest_id] = step

    def finish(self, quest_id):
        self.active.pop(quest_id, None)

    def entries(self):
        """[(title, text of the current step)] for the inventory list, in the order they were started."""
        return [(QUESTS[q]["title"], QUESTS[q]["steps"].get(s, "")) for q, s in self.active.items() if q in QUESTS]

    # save file
    def state(self):
        return dict(self.active)

    def load(self, data):
        self.active = {q: s for q, s in (data or {}).items() if q in QUESTS}
