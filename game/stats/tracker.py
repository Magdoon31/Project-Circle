# THE SAVE'S STATS (13.11): numbers counted while you play, kept in the save's counters ("stats"). Game calls these
# at the moments that matter; the money is followed frame by frame (every rise = earned, every drop = spent).

class StatsTracker:
    def __init__(self, counters):
        self.counters = counters                     # () -> the save's counters dict
        self.last_money = None

    @property
    def data(self):
        return self.counters().setdefault("stats", {})

    def add(self, name, amount=1):
        self.data[name] = self.data.get(name, 0) + amount

    def get(self, name):
        return self.data.get(name, 0)

    def follow_money(self, money):
        """Once a frame in a game: what the money did since the last frame."""
        if self.last_money is not None and money != self.last_money:
            self.add("gold_earned" if money > self.last_money else "gold_spent", abs(money - self.last_money))
        self.last_money = money

    def forget_money(self):
        """A save was loaded / a new game: its money is not "earned"."""
        self.last_money = None

    def on_fight_end(self, combat):
        player = combat.player
        self.add("hits_taken", player.hits_taken)
        self.add("shots_fired", player.shots_fired)
        if combat.escaped:
            self.add("fights_escaped")
        elif combat.win:
            self.add("fights_won")
            if combat.boss:
                self.add("bosses_beaten")
        else:
            self.add("fights_lost")
