# WHAT THIS SAVE KNOWS (13.11): per enemy - seen, how many defeated, which of its drops you got. Kept in the save's
# counters ("bestiary": {"seen": [...], "kills": {id: n}, "drops": {id: [items]}}); Game updates it after a fight.

from game.bestiary.data import ENTRY, stages_for


class BestiaryProgress:
    def __init__(self, counters):
        self.counters = counters               # the save's counters dict (Game's - it changes with the save)

    @property
    def data(self):
        book = self.counters().setdefault("bestiary", {})
        book.setdefault("seen", [])
        book.setdefault("kills", {})
        book.setdefault("drops", {})
        return book

    def kills(self, entry_id):
        return self.data["kills"].get(entry_id, 0)

    def seen(self, entry_id):
        return entry_id in self.data["seen"] or self.kills(entry_id) > 0

    def knows(self, entry_id, stage):
        """Is this much of the entry open yet (STAGES: name / lore / drops)?"""
        return self.kills(entry_id) >= stages_for(entry_id)[stage]

    def got_drop(self, entry_id, item):
        return item in self.data["drops"].get(entry_id, [])

    def complete(self):
        """(13.11) Everything about everything (the Know Thy Enemy achievement)."""
        return all(self.knows(entry_id, "drops") for entry_id in ENTRY)

    def discovered(self):
        return sum(1 for entry_id in ENTRY if self.knows(entry_id, "name"))

    # --- after a fight ----------------------------------------------------------------------------------------
    def on_fight_end(self, combat):
        book = self.data
        for name in self.names_in(combat):
            if name in ENTRY and name not in book["seen"]:
                book["seen"].append(name)
        for name, row in combat.defeated.items():
            if name in ENTRY:
                book["kills"][name] = book["kills"].get(name, 0) + row.count
                got = book["drops"].setdefault(name, [])
                got += [item for item in row.drops if item not in got]
        boss = getattr(combat, "boss", None)
        if combat.win and boss in ENTRY and boss not in combat.defeated:     # (song / scripted ends: Mascot, Milo, Void)
            book["kills"][boss] = book["kills"].get(boss, 0) + 1

    @staticmethod
    def names_in(combat):
        names = set(combat.defeated) | {getattr(e, "name", None) for e in combat.enemies}
        if getattr(combat, "boss", None):
            names.add(combat.boss)
        return names
