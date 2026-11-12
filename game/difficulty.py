# DIFFICULTY (12.11): chosen for a new save (the save screen), kept in the save ("difficulty"; older saves: only
# "hard_mode" true / false).
#   easy   - "I Have a Job": enemies hit 25% softer, attack more slowly (bosses even more slowly), fewer bullets in
#            every attack (also Milo's and the Void's own: core_fight.py, void_copies.py, void_turrets.py), one enemy
#            fewer in a normal fight. A green save card.
#   normal - as designed. A cream card.
#   hard   - "Hard Mode": see HARD_* in game.py / combat.py and the bosses' "hard..." data. A red card.

EASY, NORMAL, HARD = "easy", "normal", "hard"
LEVELS = (EASY, NORMAL, HARD)
NAMES = {EASY: "I Have a Job", NORMAL: "Normal", HARD: "Hard Mode"}
CARD_STYLE = {EASY: "green", NORMAL: "cream", HARD: "red"}   # the save card, its words and stars

COOLDOWN = {EASY: 1.1, NORMAL: 1.0, HARD: 0.9}               # enemies' attack cooldowns x this ...
BOSS_COOLDOWN = {EASY: 1.25, NORMAL: 1.0, HARD: 0.9}         # ... a boss's
ENEMY_COUNT_SHIFT = {EASY: -1, NORMAL: 0, HARD: 1}           # enemies in a normal fight (see fight_points)
EASY_ENEMY_DAMAGE = 0.75                                      # every hit on you x this
EASY_BULLETS = 0.75                                           # an attack's bullets x this (at least 1)


def from_save(game_data):
    """The difficulty stored in a save's "game" part (old saves: "hard_mode")."""
    level = game_data.get("difficulty")
    if level in LEVELS:
        return level
    return HARD if str(game_data.get("hard_mode")).lower() == "true" else NORMAL


def fewer(count, easy=True):
    """A count of bullets in "I Have a Job" (x EASY_BULLETS, at least 1); unchanged when not easy."""
    return max(1, round(count * EASY_BULLETS)) if easy else count


def cooldown_mult(level, is_boss):
    return (BOSS_COOLDOWN if is_boss else COOLDOWN)[level]
