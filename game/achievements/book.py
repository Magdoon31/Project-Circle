# THE ACHIEVEMENT BOOK (13.11): which achievements are unlocked - for the whole game, not per save
# (game/text/achievements.json) - and the queue of "Achievement unlocked" notes waiting to be shown
# (popup.py shows them on the map or in the main menu, never in a fight).

import json
import os
import time

from game.achievements.data import BY_ID

FILE = os.path.join("game", "text", "achievements.json")


class AchievementBook:
    def __init__(self, path=FILE):
        self.path = path
        self.unlocked = self.load()            # id -> when (unix time)
        self.waiting = []                      # ids not shown yet

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return {}
        return {k: v for k, v in data.get("unlocked", {}).items() if k in BY_ID}

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"unlocked": self.unlocked}, f, indent=2)
        except OSError:
            pass

    def has(self, achievement_id):
        return achievement_id in self.unlocked

    def unlock(self, achievement_id):
        """True if it is new (then it is saved at once and waits to be shown)."""
        if achievement_id not in BY_ID or achievement_id in self.unlocked:
            return False
        self.unlocked[achievement_id] = int(time.time())
        self.waiting.append(achievement_id)
        self.save()
        return True

    def next_note(self):
        return self.waiting.pop(0) if self.waiting else None


BOOK = AchievementBook()                       # the one book, shared by the game and the menus
