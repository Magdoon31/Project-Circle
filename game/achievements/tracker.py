# WHEN AN ACHIEVEMENT IS REACHED (13.11). Game calls the on_... methods at the moments that matter; the progress
# (kills, spins, steps...) is kept in the save's counters ("ach") - so it counts per save, while the unlocked
# achievements themselves are global (book.py).

from game.achievements.book import BOOK

BOSS_WINS = {"slime_king": "royal_flush", "prism": "shattered_expectations", "shroom_mother": "mother_knows_less",
             "frost_golem": "chill_out", "assembly_line": "quality_control", "night_bloom": "lights_out",
             "mascot": "showtime", "milo": "every_beat", "void_boss": "remembered"}
NO_HIT = {"slime_king": "slippery", "prism": "light_footed", "shroom_mother": "allergy_free",
          "frost_golem": "ice_skater", "assembly_line": "zero_defects", "night_bloom": "sixth_sense",
          "mascot": "perfect_pitch", "milo": "heartless", "void_boss": "untouched_by_the_void"}
FLAGS = {"talked:milo_village": "new_in_town", "quest_done:hook": "off_the_hook", "quest_done:hal": "can_you_hear_me_now",
         "quest_done:wren": "things_that_dont_fit", "quest_done:foreman": "overtime",
         "found:factory_hall": "behind_the_wall", "ending:main": "round_and_round",
         "ending:extra": "almost_the_truth", "ending:secret": "a_world_that_lives"}
ENDINGS = ("ending:main", "ending:extra", "ending:secret")
COUNTED = {"kills": [(1000, "pest_control"), (10000, "is_this_your_job_now")], "purchases": [(50, "shopaholic")],
           "escapes": [(100, "tactical_retreat")], "falls": [(10, "fell_for_it")],
           "surface_steps": [(20000, "touch_grass")], "small_fish": [(10, "small_fry")]}
LORE_ITEMS = ("Broken Bulb", "Cassette Tape", "Old Note")
ALL_SIGILS = 13
RICH = 50000
STARTER_WEAPONS = ("Simple Blaster", "Simple Pistol")             # (Old Faithful)
CLOSE_SHAVE = 0.05
SPONGE_HITS = 50
MEMORY_SECONDS_LEFT = 16
PEARL_VALUE, SMALL_FISH_VALUE = 250, 1
SAME_NPC_TALKS = 20
WINDOW_SHOPS = 20
LOSING_SPINS = 10
PAID_REROLLS = 5
REWINDS = 10
BOSS_LOSSES = 10
SPEEDRUN_S, LATE_S = 3600, 3 * 3600
EVERY_PLACE = ("surface", "cellar", "lunapark", "core", "void")   # (Been There, Done That)
LEVEL_DONE = {"surface": "tourist", "void": "mind_the_gap"}       # 100% of one level
FULL_MAP = 0.995                         # "100%" (rounded, as the world map shows it)
MAP_CHECK_EVERY = 300                    # frames between the (slower) explored-map checks
WHEEL_SPINS, SUDOKU_WINS = 50, 15


class AchievementTracker:
    def __init__(self, game):
        self.game = game
        self.timer = 0

    # --- the save's own numbers ----------------------------------------------------------------------------
    @property
    def numbers(self):
        return self.game.counters.setdefault("ach", {})

    def add(self, name, amount=1):
        """Counts on (this save); unlocks what the new number reaches (COUNTED)."""
        value = self.numbers.get(name, 0) + amount
        self.numbers[name] = value
        for goal, achievement in COUNTED.get(name, []):
            if value >= goal:
                BOOK.unlock(achievement)
        return value

    def progress(self, counter):
        """How far this save is towards a "goal" (the screen shows it)."""
        if counter == "sigils":
            return len(self.game.sigils.owned)
        if counter in ("wheel_plays", "sudoku_wins"):
            return self.game.counters.get(counter, 0)
        return self.numbers.get(counter, 0)

    # --- every frame on the map ---------------------------------------------------------------------------
    def on_map_frame(self):
        game = self.game
        flags = game.map.flags
        for flag, achievement in FLAGS.items():
            if flag in flags:
                BOOK.unlock(achievement)
        if any(f in flags for f in ENDINGS):
            self.on_ending_reached()
        if game.player.money >= RICH:
            BOOK.unlock("dragon_hoard")
        if len(game.sigils.owned) >= ALL_SIGILS:
            BOOK.unlock("sticker_album")
        self.timer += 1
        if self.timer % 30 == 0:                       # (items: a set of names - not needed every frame)
            owned = game.owned_item_names()
            if all(name in owned for name in LORE_ITEMS):
                BOOK.unlock("keeper_of_memories")
            if "Peace Gun" in owned:
                BOOK.unlock("peacekeeper")
        if self.timer % MAP_CHECK_EVERY == 0:
            self.check_maps()

    def on_pale_world(self):
        BOOK.unlock("feeling_a_bit_pale")

    def check_maps(self):
        level = self.game.map.level
        if level not in EVERY_PLACE:
            return
        explored = self.numbers.setdefault("explored", {})          # level -> its best explored share (this save)
        explored[level] = max(explored.get(level, 0.0), self.game.map.explored_fraction())
        if explored[level] >= FULL_MAP and level in LEVEL_DONE:
            BOOK.unlock(LEVEL_DONE[level])
        if level == "cellar" and self.game.map.biome_explored("underground_garden") >= FULL_MAP:
            BOOK.unlock("cartographer")
        if all(explored.get(name, 0.0) >= FULL_MAP for name in EVERY_PLACE):
            BOOK.unlock("been_there_done_that")

    def on_step(self, level):
        """The player came onto a new tile."""
        if level == "surface":
            self.add("surface_steps")

    def on_ending_reached(self):
        difficulty = self.game.difficulty
        if difficulty == "easy":
            BOOK.unlock("i_have_a_life_too")
        elif difficulty == "hard":
            BOOK.unlock("unemployed")

    # --- fights ---------------------------------------------------------------------------------------------
    def on_fight_end(self, combat, won):
        player = combat.player
        self.add("kills", sum(row.count for row in combat.defeated.values()))
        if combat.void:
            self.add("falls", combat.void.falls)
        if combat.core and combat.core.rewinds >= REWINDS:
            BOOK.unlock("deja_vu")
        if combat.escaped:
            self.add("escapes")
            return
        if not won:
            if combat.boss:
                self.on_boss_lost(combat.boss)
            return
        hits = combat.song.hits if combat.song else player.hits_taken
        if player.hp <= player.max_hp * CLOSE_SHAVE:
            BOOK.unlock("close_shave")
        if player.hits_taken >= SPONGE_HITS:
            BOOK.unlock("bullet_sponge")
        if player.shots_fired == 0 and not combat.song and not combat.core and not combat.void:
            BOOK.unlock("pacifist")
        if not combat.boss:
            if hits == 0:
                BOOK.unlock("untouchable")
            return
        self.on_boss_won(combat, hits)

    def on_boss_won(self, combat, hits):
        boss, game = combat.boss, self.game
        if boss in BOSS_WINS:
            BOOK.unlock(BOSS_WINS[boss])
        if combat.hard_mode and hits == 0 and boss in NO_HIT:
            BOOK.unlock(NO_HIT[boss])
        if combat.hard_mode and combat.void and combat.void.lives_lost == 0:
            BOOK.unlock("nothing_left_to_lose")
        if boss == "mascot" and combat.song.grade == "A":
            BOOK.unlock("encore")
        if boss == "prism" and getattr(game.inventory.active_weapon, "name", None) in STARTER_WEAPONS:
            BOOK.unlock("old_faithful")
        if boss == "milo" and game.player.play_time < SPEEDRUN_S:
            BOOK.unlock("speedrunner")
        if boss == "slime_king" and game.player.play_time >= LATE_S:
            BOOK.unlock("fashionably_late")

    def on_boss_lost(self, boss):
        losses = self.numbers.setdefault("boss_losses", {})
        losses[boss] = losses.get(boss, 0) + 1
        if losses[boss] >= BOSS_LOSSES:
            BOOK.unlock("skill_issue")

    # --- minigames, the shop, talks -------------------------------------------------------------------------
    def on_minigame_end(self, family, minigame, won):
        counters = self.game.counters
        if family == "memory" and won and minigame.frames_left >= MEMORY_SECONDS_LEFT * 60:
            BOOK.unlock("memory_like_an_elephant")
        elif family == "sudoku":
            if won and minigame.mode["name"] == "Thinking":
                BOOK.unlock("number_cruncher")
            if counters.get("sudoku_wins", 0) >= SUDOKU_WINS:
                BOOK.unlock("sudoku_addict")
        elif family == "fishing" and minigame.caught is not None:
            if minigame.caught.value >= PEARL_VALUE:
                BOOK.unlock("the_big_one")
            elif minigame.caught.value == SMALL_FISH_VALUE:
                self.add("small_fish")
        elif family == "wheel":
            if counters.get("wheel_plays", 0) >= WHEEL_SPINS:
                BOOK.unlock("gamble_addict")
            streak = 0 if won else self.numbers.get("losing_spins", 0) + 1
            self.numbers["losing_spins"] = streak
            if streak >= LOSING_SPINS:
                BOOK.unlock("the_house_always_wins")

    def on_shop_open(self):
        if self.add("shop_visits_empty") >= WINDOW_SHOPS:
            BOOK.unlock("window_shopper")

    def on_buy(self, money_left):
        self.numbers["shop_visits_empty"] = 0
        self.add("purchases")
        if money_left == 0:
            BOOK.unlock("zero_balance")

    def on_reroll(self, rerolls_this_stock):
        if rerolls_this_stock - 1 >= PAID_REROLLS:       # the first one is free
            BOOK.unlock("just_one_more_reroll")

    def on_talk(self, npc_id):
        talks = self.numbers.setdefault("talks", {})
        talks[npc_id] = talks.get(npc_id, 0) + 1
        if talks[npc_id] >= SAME_NPC_TALKS:
            BOOK.unlock("small_talk_champion")
