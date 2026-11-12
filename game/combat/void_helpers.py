# THE VOID'S HELPERS (11.11, F3 - the Factory): now and then a Scrap Beetle or a Toy Soldier (the Void's own,
# stronger kinds: EnemyDB "void_beetle" / "void_soldier") comes up on an outer island far from you. Never more than
# a few at once - they add to the fight, they don't drown it. They walk only on the ground (islands, bridges); the
# belts carry the beetles (a soldier stands firm). Here: when, where and keeping them on the ground; Combat fights
# them like any enemy.

import math
import random

KINDS = ["void_beetle", "void_soldier"]
EVERY = 5 * 60                    # frames between two helpers coming
MOST = 3                          # no more than this many at once
HARD_EVERY = round(EVERY / 1.33)  # (12.11) hard mode: they come 1.33x as often ...
HARD_MOST = None                  # ... and there is no limit
BELT_PROOF = {"void_soldier"}     # the belts don't move these
FAR = 700                         # px: they come up at least this far from you
COLOUR = (150, 120, 190)


class VoidHelpers:
    def __init__(self, make_enemy, hard=False):
        self.make_enemy = make_enemy              # name -> a new Enemy
        self.every = HARD_EVERY if hard else EVERY
        self.most = HARD_MOST if hard else MOST
        self.timer = 0
        self.alive = []
        self.places = {}                          # helper -> its last place on the ground

    def update(self, arena, player, enemies):
        """One frame: maybe a new one (added to `enemies`), and every helper kept on the ground."""
        self.timer += 1
        self.alive = [e for e in self.alive if e in enemies and e.hp > 0]
        if self.timer % self.every == 0 and (self.most is None or len(self.alive) < self.most):
            helper = self.come_up(arena, player)
            enemies.append(helper)
            self.alive.append(helper)
        for e in self.alive:
            self.keep_on_ground(e, arena)

    def come_up(self, arena, player):
        far = [p for p in arena.outer if math.dist(p, (player.x, player.y)) >= FAR] or arena.outer
        x, y = random.choice(far)
        helper = self.make_enemy(KINDS[(self.timer // self.every) % len(KINDS)])
        helper.x, helper.y = x, y
        helper.no_drops = True
        helper.color = COLOUR
        return helper

    def keep_on_ground(self, e, arena):
        if e.name not in BELT_PROOF:
            dx, dy = arena.belt_push(e.x, e.y)
            e.x, e.y = e.x + dx, e.y + dy
        if arena.on_ground(e.x, e.y):
            self.places[e] = (e.x, e.y)
        else:
            e.x, e.y = self.places.get(e, arena.nearest_island(e.x, e.y))

    def leave(self):
        """The phase is over: they go (Combat takes away what is marked remove_me)."""
        for e in self.alive:
            e.remove_me = True
        self.alive = []
