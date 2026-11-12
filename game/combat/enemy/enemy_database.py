from game.combat.enemy.enemy import Enemy
from game.world.loot import LUCK_DROP
from game.combat.bullet_types import BulletTypes
import copy, random, math
from game import difficulty as DIFF

# SPAWNS (7.11): biome : [[lower, upper] number of enemies, {enemy: weight}]
# WEIGHT = how heavy an enemy is (1 weak, e.g. fly ... 5 heavy, lots of bullets). A fight gets
# POINTS = random number of enemies (lower..upper; hard mode: lower + 1) x the biome's average weight;
# then random enemies are added (each takes its weight) until the points are <= 0 (the last one may go below 0).
# At most MAX_ENEMIES, on spawn points in a ring around the player.
SPAWNS = {
    "village": [[1,3], {"slime_small": 1, "slime_big": 2, "shooter": 2}],
    "rainbow_fields": [[1,4], {"rainbow_slime": 2, "flower_spitter": 2, "rainbow_guard": 3}],
    "sugarwood_grove": [[2,4], {"toffee_runner": 1, "gum_goblin": 2, "sugar_caster": 3, "candy_shroom": 4}],
    "toy_factory": [[3,5], {"toy_soldier": 2, "scrap_beetle": 2, "robo-tesla": 3, "robo-bomber": 3, "portable_factory": 5}],
    "silverpine_tundra": [[3,5], {"frost_wolf": 2, "ice_shooter": 3, "frozen_orb": 4, "tundra_watcher": 4}],
    "underground_garden": [[3,6], {"rainbow_pixie": 3, "pixie": 3, "inferno_flower": 3, "frost_flower": 3, "toxic_flower": 3,
                                   "poison_skeleton": 4, "firefly_queen": 4}],
    "the_core": [[3,6], {"skeleton": 1, "fly": 1, "guard": 3, "generator": 4, "liche": 5}],
    "the_void": [[2,6], {"voidling": 3, "blue_crystal": 4, "red_crystal": 5, "purple_crystal": 5}],
}
MAX_ENEMIES = 15                # = spawn points around the player
SPAWN_RING = (0.42, 0.40)       # the ring of spawn points: share of the screen width / height from the centre


def fight_points(biome, difficulty, rnd=random):
    """How many points of enemies this fight gets (hard: +1 enemy at least, 12.11 easy: one fewer, at least 1)."""
    (low, high), weights = SPAWNS[biome]
    avg = sum(weights.values()) / len(weights)
    shift = DIFF.ENEMY_COUNT_SHIFT[difficulty]
    if shift < 0:
        low, high = max(1, low + shift), max(1, high + shift)
    count = rnd.randint(min(high, low + max(0, shift)), high)
    return round(count * avg)


BELTS = [[0.30, 0.40, 1], [0.52, 0.62, -1], [0.74, 0.84, 1]]     # (8.11) Assembly Line's conveyor belts (share of the height)
GLUE_FRAMES = 150                 # (11.11) Assembly Line: how long its rows and bottom vents glue you (was 90)
MACHINES = {"assembly_machine_1", "assembly_machine_2", "assembly_machine_3"}   # stand still - belts don't move them
BELT_RIDERS = {"belt_turret", "bomb_crate"}   # only ride the belts; gone when carried off the far end
SQUARE = MACHINES | BELT_RIDERS                # drawn as boxes
ANCHORED = MACHINES | {"assembly_line", "milo", "milo_core"}    # (Milo is moved by core_fight.py only)
SHADOWED = {"night_bloom"}                     # (8.11) the real one casts a shadow (its copies don't)        # (8.11) never moved by anything (pushes, knockback)
WALL_BOUNCE = {"frozen_orb"}     # (8.11) these enemies' bullets bounce off walls (room obstacles, ice walls)
WALL_PASS = {"generator"}        # (8.11) these enemies' bullets fly through walls (it can't move to see you)


def spawn_points(w, h, rnd=random):
    """MAX_ENEMIES points in a ring around the centre of the screen (where the player starts), in random order."""
    turn = rnd.uniform(0, math.tau)
    pts = []
    for i in range(MAX_ENEMIES):
        a = turn + i * math.tau / MAX_ENEMIES
        pts.append((min(w - 90, max(90, w / 2 + math.cos(a) * w * SPAWN_RING[0])),
                    min(h - 90, max(90, h / 2 + math.sin(a) * h * SPAWN_RING[1]))))
    rnd.shuffle(pts)
    return pts


class EnemyDB:
    def __init__(self, sfx, bullet_type_info=None):
        self.enemies = {
            # BALANCE (6.11, see BALANCE.md): HP so that a NORMAL enemy dies in ~2.5 s to a 1.0x weapon of its biome
            # (small ~1 s, tank ~5.6 s), x3 per biome level. Defence is now a % : damage x 100 / (100 + def)
            # (def 25 = -20%, 50 = -33%, 100 = -50%).
            # DAMAGE (6.11): every attack + touching scaled so the biome's average hit = 10 x 3^(level-1)
            # (village 10, rainbow 30, sugarwood 90, factory/tundra 270, garden 810, core 2430, void 7290); minigun bursts
            # x0.5 per bullet. "telegraph": frames of the aiming line before a fast shot (the shot is then x1.3 faster).
            # PATTERNS (7.11): split / pulse / wall / sprinkler / line / wave, "repeat" series, throw "ring", creeping
            # mines - all described at the top of enemy.py.
             # --- VILLAGE ---

            "slime_small": [0,0,12,18,"enemy",3.4,6.9,4,0,"mystical","to_player_jump",{}],

            "slime_big": [0,0,68,36,"enemy",2.0,14,12,0,"mystical","to_player_jump",{"death_spawn":{"amount":2,"enemy_name":"slime_small"}}],

            "shooter": [0,0,30,22,"enemy",3.2,5.7,10,0,"human","away_player_distance",
                {"basic": {"damage": 14, "cooldown": 2.2, "last_used": 0, "width": 14, "speed": 16, "range": 3200, "effects": {}, "type":["arrow_red"]}}],


            # --- RAINBOW FIELDS ---

            "rainbow_slime": [0,0,72,24,"enemy",3.8,18,12,25,"mystical","to_player_jump",
                {"death_spiral": {"bullets":4,"damage": 40, "width": 13, "speed": 6, "range": 4000, "effects": {}, "type":["normal_yellow","normal_red","normal_green","normal_blue"]}}],

            "flower_spitter": [0,0,90,23,"enemy",1.0,14,10,0,"animal","away_player_normal",
                {"split": {"damage": 50, "cooldown": 2.2, "last_used": 0, "width": 12, "speed": 8, "range": 3600, "effects": {"slow":[45,0.15],"homing":[0.25]}, "type":["flower_pink"],
                           "split": {"after": 60, "bullets": 4, "start": 0, "speed": 7, "damage": 30, "width": 9}}}],

            "rainbow_guard": [0,0,160,30,"enemy",2.1,32,14,25,"human","to_player_normal",
                {"shotgun": {"damage": 27, "cooldown": 2.2, "last_used": 0, "width": 16, "speed": 14, "range": 750, "recoil": 30, "bullets": 3, "repeat": [2, 0.3], "effects": {}, "type":["nail"]}}],


            # --- SUGARWOOD GROVE ---

            "gum_goblin": [0,0,270,26,"enemy",4.8,29,16,0,"animal","to_player_distance",
                {"basic": {"damage": 120, "cooldown": 1.6, "last_used": 0, "width": 13, "speed": 16, "range": 1800, "effects": {"glued":[60,0.25]}, "type":["normal_green"]}}],

            "candy_shroom": [0,0,490,24,"enemy",0.8,59,20,25,"plant","random_normal",
                {"sprinkler": {"damage": 44, "cooldown": 2.0, "last_used": 0, "width": 12, "speed": 7, "range": 3500, "streams": 3, "duration": 2.0, "every": 8, "turn": 9, "effects": {"poison":[185,15]}, "type":["spore"], "stop_move":[20,10]}}],

            "toffee_runner": [0,0,86,18,"enemy",3.8,88,10,25,"animal","to_player_zigzag",{}],

            "sugar_caster": [0,0,220,25,"enemy",2.3,73,22,25,"mystical","away_player_normal",
                {"throw": {"radius": 90, "recoil":150, "damage": 220, "width":15, "exp_type":"nova_", "cooldown": 2.0, "last_used": 0, "fly_time": 1.5, "effects": {"speed":[60,0.25]},"stop_move":[24,8], "type":["flower_white"],
                           "ring": {"bullets": 8, "speed": 6, "damage": 90, "width": 11, "effects": {}}}}],

            # Shroom Mother's guards (boss phase 2): stand in a corner, 2 spinning streams; not in normal fights
            "shroom_guard": [0,0,490,30,"enemy",0,90,0,25,"mystical","random_normal",
                {"sprinkler": {"damage": 70, "cooldown": 3.0, "last_used": -60, "width": 12, "speed": 7, "range": 5000,
                               "streams": 2, "duration": 2.0, "every": 6, "turn": 9, "effects": {}, "type": ["spore"]}}],


            # --- TOY FACTORY ---

            "toy_soldier": [0,0,810,20,"enemy",1.8,140,25,0,"mechanical","to_player_normal",
                {"basic": {"damage": 410, "cooldown": 2.2, "last_used": 0, "width": 16, "speed": 14, "range": 3500, "repeat": [3, 0.15], "effects": {}, "type":["bullet_red"]}}],

            "portable_factory": [0,0,1820,40,"enemy",0,14,50,0,"mechanical","random_normal",
                {"spawn": {"enemy_name":"toy_soldier","amount" : 1,"cooldown": 7.5, "last_used": 0},
                "spiral": {"damage": 220, "cooldown": 3.5, "last_used": 0, "width": 12, "speed": 6, "range": 3800, "bullets": 14, "effects": {}, "type":["normal_red"]}}],

            "robo-tesla": [0,0,320,23,"enemy",1.8,140,30,25,"mechanical","random_normal",
                           {"wave": {"damage": 300, "cooldown": 1.5, "last_used": 0, "width": 8, "speed": 13, "range": 2600, "bullets": 8, "every": 4, "amp": 28, "period": 36, "double": True, "effects": {"weakness":[120,0.2]}, "type":["normal_blue"]},
                            "spiral": {"damage": 300, "cooldown": 1.0, "last_used": 0, "width": 5, "speed": 11, "range": 1800, "bullets": 16, "effects": {"weakness":[120,0.2]}, "type":["normal_blue"]}}],

            "robo-bomber": [0,0,650,23,"enemy",1.8,140,30,25,"mechanical","random_normal",
                            {"throw": {"radius": 180, "recoil":250, "damage": 480, "width":15, "exp_type":"", "cooldown": 3.2, "last_used": 0, "fly_time": 0.8, "effects": {"burn":[60,27]}, "type":["grenade_red"]}}],
                           
            "scrap_beetle": [0,0,260,14,"enemy",5.2,270,20,25,"mechanical","to_player_normal",
                {"mine": {"damage": 610, "radius": 80, "cooldown": 1.5, "last_used": 0, "width": 18, "exp_time": 3.5, "effects": {}, "type": ["mine_red"]}}],

            # ASSEMBLY LINE's machines (8.11, Factory boss): stand at the top, put products on the belts; while one
            # stands the core can't be hurt. _1 = small toys, _2 = + turrets and bomb crates, _3 = everything, faster
            "assembly_machine_1": [0,0,500,42,"enemy",0,60,0,150,"mechanical","random_normal",
                {"spawn": {"enemy_name": ["scrap_beetle", "line_soldier"], "amount": 1, "belt": True, "no_drops": True, "fade": [30, 30, 0.85], "cooldown": 3.0, "last_used": -150}}],

            "assembly_machine_2": [0,0,500,42,"enemy",0,60,0,150,"mechanical","random_normal",
                {"spawn": {"enemy_name": ["line_beetle", "belt_turret", "bomb_crate", "bomb_crate"], "amount": 1, "belt": True, "no_drops": True, "fade": [30, 30, 0.85], "cooldown": 2.6, "last_used": -150}}],

            "assembly_machine_3": [0,0,420,42,"enemy",0,60,0,150,"mechanical","random_normal",
                {"spawn": {"enemy_name": ["belt_turret", "bomb_crate", "bomb_crate", "scrap_beetle"], "hard_only": ["scrap_beetle"], "unfaded": ["scrap_beetle"], "amount": 1, "belt": True, "no_drops": True, "fade": [30, 30, 0.85], "cooldown": 2.4, "last_used": -150}}],

            # ... and what they make (no gold, nothing drops): small toys walk at you, turrets and crates just ride
            "line_soldier": [0,0,260,16,"enemy",2.2,140,0,0,"mechanical","to_player_normal",
                {"basic": {"damage": 270, "cooldown": 2.6, "last_used": -60, "width": 14, "speed": 12, "range": 3000, "effects": {}, "type": ["bullet_red"]}}],
            "line_beetle": [0,0,180,12,"enemy",4.6,200,0,0,"mechanical","to_player_normal", {}],
            "belt_turret": [0,0,600,24,"enemy",0,100,0,0,"mechanical","random_normal",
                {"line": {"damage": 250, "cooldown": 2.4, "last_used": -40, "width": 12, "speed": 13, "range": 4000, "bullets": 3, "every": 5, "effects": {}, "type": ["bullet_red"]}}],
            "bomb_crate": [0,0,300,22,"enemy",0,60,0,0,"mechanical","random_normal",
                {"fuse": {"cooldown": 4.0, "last_used": 0},
                 "death_spiral": {"damage": 250, "cooldown": 0, "last_used": 0, "width": 13, "speed": 7, "range": 3000, "bullets": 12, "effects": {}, "type": ["normal_red"]}}],


            # --- SILVERPINE TUNDRA ---

            "frost_wolf": [0,0,650,26,"enemy",3.4,420,30,25,"animal","to_player_normal",{}],

            "ice_shooter": [0,0,810,26,"enemy",1.1,210,32,0,"human","away_player_normal",
                {"basic": {"telegraph": 30, "damage": 220, "cooldown": 1.4, "last_used": 0, "width": 12, "speed": 30, "range": 4500, "effects": {"slow":[45,0.55]}, "type":["arrow_blue"]}}],

            "frozen_orb": [0,0,1220,28,"enemy",0.8,170,30,50,"mystical","random_normal",
                {"pulse": {"damage": 310, "cooldown": 2.6, "last_used": 0, "width": 14, "speed": 6, "range": 9000, "bullets": 10, "pulse": [45, 15], "effects": {"slow":[60,0.55]}, "type":["normal_blue"]},
                 "death_spiral": {"damage": 310, "cooldown": 0, "last_used": 0, "width": 14, "speed": 8, "range": 4000, "bullets": 16, "effects": {"slow":[60,0.55],"homing":[0.34]}, "type":["normal_blue"]}}],

            "tundra_watcher": [0,0,1820,35,"enemy",1.2,210,45,25,"human","random_normal",
                {"shotgun":{"damage": 220, "cooldown": 3.5, "last_used": 0, "width": 16, "speed": 15, "range": 4000, "recoil": 60, "bullets": 5, "effects": {"slow":[50,0.3]}, "type":["laser_blue"]},
                "line": {"damage": 200, "cooldown": 1.6, "last_used": 0, "width": 16, "speed": 20, "range": 4000, "bullets": 5, "every": 3, "effects": {}, "type":["laser_blue"]}}],


            # --- UNDERGROUND GARDEN ---

            "pixie": [0,0,1940,20,"enemy",2.8,950,70,25,"mystical","random_jump",
                {"minigun": {"damage": 300,"cooldown": 1.5,"last_used": 0,"width": 18,"speed": 10,"burst_count": 0,"burst_max": 10,"burst_delay": 0.05,"last_shot": 0,"is_bursting": False, "spread": 360, "range": 3000, "effects" : {"confusion":[120,0.75],"slow":[180,0.25]},"type":["normal_yellow"]}}],

            "rainbow_pixie": [0,0,970,20,"enemy",1.5,950,200,0,"mystical","random_jump",
                              {"death_spiral": {"damage": 950, "cooldown": 0, "last_used": 0, "width": 18, "speed": 10, "range": 3000, "bullets": 18, "effects": {"confusion":[120,0.75],"slow":[180,0.25]}, "type":["normal_yellow","normal_green","normal_blue","normal_red"]},
                              "death_spawn": {"amount": 2, "enemy_name":"pixie"}}],

            "poison_skeleton": [0,0,5470,28,"enemy",3.1,950,85,0,"undead","away_player_normal",
                                {"basic": {"telegraph": 30, "damage": 950, "cooldown": 1.8, "last_used": 0, "width": 22, "speed": 32, "range": 3800, "effects": {"poison":[240,143]}, "type":["arrow_red"]}}],

            "inferno_flower": [0,0,1940,26,"enemy",0.6,950,85,25,"mystical","random_normal",
                               {"shotgun":{"damage": 600, "cooldown": 3.0, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "recoil": 40, "bullets": 4, "repeat": [2, 0.35], "effects": {"burn":[120,71]}, "type":["flower_orange"]},
                                "basic": {"damage": 720, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.5],"burn":[120,71]}, "type":["flower_orange"]}}],

            "frost_flower": [0,0,1940,26,"enemy",0.6,950,85,25,"mystical","random_normal",
                               {"pulse":{"damage": 600, "cooldown": 2.8, "last_used": 0, "width": 12, "speed": 9, "range": 8000, "bullets": 10, "pulse": [45, 15], "effects": {"slow":[120,0.33],"weakness":[160,0.5]}, "type":["flower_blue"]},
                                "basic": {"damage": 720, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"slow":[120,0.33],"weakness":[160,0.5]}, "type":["flower_blue"]}}],

            "toxic_flower": [0,0,1940,26,"enemy",0.6,950,85,25,"mystical","random_normal",
                               {"split":{"damage": 600, "cooldown": 2.5, "last_used": 0, "width": 18, "speed": 7, "range": 3000, "effects": {"acid":[120,0.33],"poison":[180,191]}, "type":["flower_green"],
                                         "split": {"after": 50, "bullets": 6, "speed": 7, "damage": 360, "width": 10}},
                                "basic": {"damage": 720, "cooldown": 1.9, "last_used": 0, "width": 12, "speed": 12, "range": 2100, "effects": {"homing":[0.8],"acid":[120,0.33],"poison":[180,191]}, "type":["flower_green"]}}],


            # Firefly Queen (7.11): like the sun in ETG - glows, 3 dashes at you, then a full ring of light;
            # when she dies she bursts: pushes everyone away (no damage to enemies), the player takes a hit
            "firefly_queen": [0,0,1940,26,"enemy",2.6,950,85,25,"animal","random_normal",
                {"dash": {"cooldown": 3.0, "last_used": 0, "dashes": 3, "windup": 24, "distance": 350, "dash_frames": 12, "type": ["normal_yellow"],
                          "spiral": {"bullets": 16, "damage": 600, "speed": 8, "width": 13, "range": 3500, "effects": {}}},
                 "death_blast": {"radius": 180, "damage": 810, "push": 140}}],

            # THE HEART OF THE CORE (10.11, Milo's fight): stands in the middle, shielded while Milo stands (blocks
            # your shots); touching it burns. After Milo falls it can be broken (core_fight.py).
            "milo_core": [0,0,16000,80,"enemy",0,1500,0,50,"mechanical","random_normal",{}],

            # NIGHT BLOOM's copies (8.11, Garden boss, phase 3-4): look like it, don't shoot; pop into a small ring when hit
            # (hit the real one first and they just vanish)
            "bloom_copy": [0,0,1,60,"enemy",1.0,0,0,0,"plant","random_normal",
                {"death_spiral": {"damage": 400, "cooldown": 0, "last_used": 0, "width": 12, "speed": 6, "range": 3000, "bullets": 8, "effects": {}, "type": ["spore"]}}],


            # --- THE CORE ---

            "liche": [0,0,10940,26,"enemy",2.5,840,120,50,"undead","random_normal",
                {"basic": {"damage": 4180, "cooldown": 1.0, "last_used": 0, "width": 18, "speed": 12, "range": 3400, "effects": {"poison":[300,501],"confusion":[80,0.5]}, "type":["ghost_bullet"]},
                "sprinkler": {"damage": 2510, "cooldown": 2.4, "last_used": 0, "width": 14, "speed": 8, "range": 2600, "streams": 3, "duration": 1.8, "every": 8, "turn": 9, "effects": {"weakness":[300,0.3],"confusion":[80,0.5]}, "type":["ghost_bullet"]},
                "shotgun":{"damage": 2510, "cooldown": 2.6, "last_used": 0, "width": 14, "speed": 10, "range": 2200, "recoil": 30, "bullets": 5, "effects": {"glued":[300,0.3],"confusion":[80,0.5]}, "type":["ghost_bullet"]}}],

            "skeleton": [0,0,2330,21,"enemy",4.2,2510,30,25,"undead","to_player_normal",
                      {}],

            "mecha-skeleton": [0,0,3000,35,"boss",2.5,100,400,8,"undead","random_normal",
                      {"basic": {"damage": 40, "cooldown": 2.6, "last_used": 0, "width": 28, "speed": 10, "range": 2000, "effects": {"homing":[1],"burn":[120,4]}, "type":["missile_red"]},
                       "mine": {"damage": 50, "radius": 50, "cooldown": 1.7, "last_used": 0, "width": 25, "exp_time": 5.0, "effects": {"binded":[90,0.75]}, "type": ["mine_red"]},
                       "spawn": {"enemy_name":"skeleton","amount" : 2,"cooldown": 4.9, "last_used": 0},
                       "shotgun":{"damage": 25, "cooldown": 0.8, "last_used": 0, "width": 10, "speed": 8, "range": 2000, "recoil": 60, "bullets": 4, "effects": {"burn":[120,4]}, "type":["normal_red"]}}],

            "guard": [0,0,8200,22,"enemy",2.2,3340,90,100,"human","to_player_normal",
                      {}],

            "fly": [0,0,1940,18,"enemy",4.8,2510,30,50,"animal","to_player_normal",
                      {"death_spiral": {"damage": 1670, "cooldown": 0, "last_used": 0, "width": 15, "speed": 12, "range": 1600, "bullets": 8, "effects": {"poison":[180,835]}, "type":["spore"]}}],

            "generator": [0,0,4860,26,"enemy",0,840,120,50,"mechanical","random_normal",
                      {"wall": {"damage": 2920, "cooldown": 1.8, "last_used": 0, "width": 13, "speed": 6, "range": 4500, "bullets": 11, "spacing": 34, "gap": 3, "effects": {"glued":[100,0.33]}, "type":["normal_yellow"]},
                       "death_spiral": {"damage": 2920, "cooldown": 0, "last_used": 0, "width": 13, "speed": 8, "range": 4000, "bullets": 24, "effects": {"glued":[160,0.33]}, "type":["normal_yellow"]}}],


            # --- THE VOID ---

            # (11.11) the Void's F3 helpers (void_helpers.py): the Factory's Toy Soldier and Scrap Beetle, the Void's
            # strength (its bullets ~5-7k like the boss's); no money, no drops
            "void_soldier": [0,0,16000,20,"enemy",1.8,6000,0,25,"mechanical","to_player_normal",
                {"basic": {"damage": 5500, "cooldown": 2.6, "last_used": 0, "width": 16, "speed": 13, "range": 3500, "repeat": [3, 0.15], "effects": {}, "type":["bullet_red"]}}],
            "void_beetle": [0,0,9000,14,"enemy",5.2,6000,0,25,"mechanical","to_player_normal",
                {"mine": {"damage": 7000, "radius": 80, "cooldown": 2.0, "last_used": 0, "width": 18, "exp_time": 3.5, "effects": {}, "type": ["mine_red"]}}],
            "voidling": [0,0,10500,14,"enemy",2.4,7850,80,50,"void","to_player_normal",
                {"spawn": {"enemy_name":"voidling","amount" : 1,"cooldown": 4.5, "last_used": 0},
                 "death_spiral": {"damage": 5610, "cooldown": 0, "last_used": 0, "width": 12, "speed": 12, "range": 3000, "bullets": 3, "effects": {"confusion":[30,0.5]}, "type":["flower_pink"]}}],

            "red_crystal": [0,0,32800,25,"enemy",1.5,5610,200,50,"void","away_player_normal",
                {"shotgun":{"damage": 8970, "cooldown": 3.2, "last_used": 0, "width": 14, "speed": 12, "range": 3500, "recoil": 35, "bullets": 6, "repeat": [2, 0.35], "effects": {"burn":[180,336]}, "type":["flower_orange"]},
                 "basic": {"telegraph": 30, "damage": 12340, "cooldown": 1.8, "last_used": 0, "width": 24, "speed": 18, "range": 3600, "effects": {"burn":[180,336]}, "type":["flower_orange"]}}],

            "purple_crystal": [0,0,32800,25,"enemy",1.8,5610,250,50,"void","random_normal",
                {"death_spawn": {"amount": 1, "enemy_name": "voidling"},
                "pulse": {"damage": 5610, "cooldown": 4.4, "last_used": -178, "width": 10, "speed": 6, "range": 9000, "bullets": 24, "pulse": [45, 15], "effects": {"confusion":[30,1.0]}, "type":["flower_pink"]},
                "sprinkler": {"damage": 5610, "cooldown": 2.8, "last_used": 0, "width": 10, "speed": 8, "range": 4000, "streams": 4, "duration": 1.6, "every": 8, "turn": 8, "effects": {"confusion":[30,1.0]}, "type":["flower_pink"]}}],

            # THE VOID BOSS's copies (11.11, its Pale phase F4): look like it, don't shoot; pop into a ring when hit
            "void_copy": [0,0,1,70,"enemy",1.2,0,0,0,"void","random_normal",
                {"death_spiral": {"damage": 5000, "cooldown": 0, "last_used": 0, "width": 12, "speed": 6, "range": 4000, "bullets": 8, "effects": {}, "type": ["ghost_bullet"]}}],

            "blue_crystal": [0,0,24600,30,"enemy",1.1,10090,300,100,"void","to_player_normal",
                {"death_spiral": {"damage": 5610, "cooldown": 0, "last_used": 0, "width": 16, "speed": 14, "range": 3200, "bullets": 12, "effects": {"slow":[120,0.8]}, "type":["flower_blue"]},
                "wave": {"damage": 5610, "cooldown": 2.5, "last_used": 0, "width": 14, "speed": 10, "range": 3400, "bullets": 4, "every": 6, "amp": 30, "period": 40, "double": True, "effects": {"confusion":[80,0.5]}, "type":["arrow_blue"]},
                "wall": {"damage": 5610, "cooldown": 3.5, "last_used": -90, "width": 14, "speed": 7, "range": 4500, "bullets": 13, "spacing": 34, "gap": 3, "effects": {"slow":[120,0.8]}, "type":["flower_blue"]}}]
        }
            
        # BOSSES (7.11): [x, y, hp, width, "boss", speed, contact dmg, gold, defence, species, movement, attacks (phase 1)]
        # + boss_info below (name over the big HP bar, the later phases). Which boss stands where: BOSS_OF_ZONE.
        # Fight length grows with the stage (village ~45 s at the biome's 1.0x weapon DPS: 12 -> ~500 HP).
        self.bosses = {
            # SLIME KING (village, 3 phases: 100-80%, 80-40%, 40-0%): 1) hops at you (aimed, with a short wind-up,
            # no warning) and leaves a small ring where it lands, 5-bullet shotgun. 2) slower, lobs slime that
            # bursts into a ring, calls 2 small slimes. 3) a triple hop (like the Firefly Queen, no landing ring, 0.35 s
            # between hops) with a ring after the 1st and 2nd hop + the shotgun + 1 small slime.
            "slime_king": [960, 300, 600, 90, "boss", 2.4, 14, 40, 0, "mystical", "to_player",
                {"dash": {"cooldown": 2.6, "last_used": -60, "dashes": 1, "windup": 40, "distance": 380, "dash_frames": 20,
                          "type": ["normal_green"],
                          "spiral": {"bullets": 8, "damage": 8, "speed": 6, "width": 14, "range": 3000, "effects": {}}},
                 "shotgun": {"damage": 10, "cooldown": 3.4, "last_used": 0, "width": 14, "speed": 9, "range": 3000,
                             "bullets": 5, "recoil": 50, "effects": {}, "type": ["normal_green"]}}],
            # PRISM (rainbow fields, 3 phases: 100-80%, 80-40%, 40-0%): a hanging crystal that splits light (rainbow
            # bullets). 1) a ball that bursts into 6 + a quick row at you (line). 2) drifts around, 4 spinning streams
            # (sprinkler). 3) a pulsing rainbow ring + a wall with a gap + the bursting ball again.
            # ~2000 HP = ~55 s at the Rainbow 1.0x weapon (36 DPS).
            "prism": [960, 300, 2000, 52, "boss", 1.2, 30, 80, 0, "mystical", "random_normal",
                {"split": {"damage": 30, "cooldown": 2.4, "last_used": -60, "width": 16, "speed": 8, "range": 3600, "effects": {},
                           "type": ["laser_red", "laser_yellow", "laser_green", "laser_blue", "laser_purple"],
                           "split": {"after": 50, "bullets": 6, "speed": 7, "damage": 20, "width": 11}},
                 "line": {"damage": 25, "cooldown": 3.0, "last_used": 0, "width": 12, "speed": 14, "range": 3600, "bullets": 6,
                          "every": 5, "effects": {}, "type": ["laser_red", "laser_yellow", "laser_green", "laser_blue", "laser_purple"]}}],
            # SHROOM MOTHER (candy / sugarwood, 3 phases: 100-80%, 80-47%, 47-0%): 1) spore bursts (48 spores, random directions and speeds,
            # slowing down - like the mushroom in ETG) + leaps (up off the screen, a shadow, down somewhere else -
            # hurts you under it - and bursts there). 2) two shroom guards in random corners (2 spinning streams, don't
            # move; 1 or 2 at random); while one of them lives she can't be hurt; she walks at you the whole phase
            # (hurts by touch); new ones at most every 19 s, once the old ones are dead. 3) leaps + bursts
            # faster + two DNA lines (at you and straight back) that bounce off the walls. Guards that are still alive stay. Drops the Flavoured
            # Candy (10%). 6000 HP = ~55 s of hitting at the Sugarwood 1.0x weapon (108 DPS) + killing the guards.
            "shroom_mother": [960, 400, 6000, 80, "boss", 1.0, 90, 220, 0, "mystical", "random_normal",
                {"burst": {**{"bullets": 48, "speed": [5, 11], "decay": 0.988, "min_speed": 1.5, "damage": 70, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}, "cooldown": 3.5, "last_used": -120},
                 "leap": {"cooldown": 6.0, "last_used": 0, "up": 30, "air": 70, "land_damage": 120, "burst": {"bullets": 48, "speed": [5, 11], "decay": 0.988, "min_speed": 1.5, "damage": 70, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}}}],
            # FROST GOLEM (tundra, 3 phases, each different): 1) stomps - 3 ice walls rise in random spots (they stop
            # everything; your shots break them in 5 hits, they melt after 8 s) + a ground crack that runs at you and
            # throws icicles out to both sides. 2) the floor turns to ice (you slide) - pulsing ring + a quick row of
            # icicles. 3) a short snowstorm (3 s every 12 s: you only see around you) - everything at once, faster. ~19000 HP = ~75 s at the Tundra 1.0x weapon (324 DPS).
            "frost_golem": [960, 300, 19000, 85, "boss", 1.2, 270, 360, 25, "mystical", "to_player",
                {"ice_walls": {"count": 3, "hits": 5, "life": 8, "long": 200, "thick": 44, "cooldown": 5.0, "last_used": -180},
                 "ground_crack": {"cooldown": 3.0, "last_used": -60, "speed": 16, "length": 1600, "every": 120, "bullets": {"damage": 250, "speed": 6, "width": 13, "range": 5000, "effects": {"slow": [90, 0.3], "weakness": [180, 0.25]}, "type": ["arrow_blue"]}}}],
            # ASSEMBLY LINE (factory, 8.11): a core at the top of a factory hall with conveyor belts across it. It can't
            # be hurt while its machines stand (def 150; they put toys / turrets / bomb crates on the belts - fewer toys once a phase lasts 30 s);
            # phases 33/33/33 %; break them -> the core is open for 16.5% of its HP, then sealed 2 s, then new machines
            # (2 rounds a phase); at most 2 turrets at once;
            # phase 3: vents in the bottom edge shoot up (no hiding down there); the side nozzles: one belt at a time. 1) 2 machines, small toys. 2) + turrets and bomb crates,
            # nozzles in the walls shoot along a belt. 3) 3 machines, faster belts that turn round, nozzles, a spiral.
            "assembly_line": [960, 175, 9000, 70, "boss", 0, 270, 380, 25, "mechanical", "to_player",
                {"spawn": {"enemy_name": "assembly_machine_1", "amount": 2, "guards": True, "replace": True,
                           "at": [[0.2, 0.17], [0.8, 0.17]], "open_damage": 0.165, "rebuild": 2.0, "color": [150, 150, 165], "cooldown": 1.0, "last_used": -60},
                 "line": {"damage": 270, "cooldown": 2.6, "last_used": -30, "width": 13, "speed": 14, "range": 4000, "bullets": 4, "every": 5, "effects": {}, "type": ["bullet_red"]}}],
            # NIGHT BLOOM (garden, 8.11): the arena is DARK - you only see yourself (a small circle of light). Light seeds
            # come up now and then: pick one up -> for a while a big circle round you, round the boss and a few random
            # spots light up. 1) short: spore rings + aimed flowers. 2) bullet hell: rows from the walls with a few
            # safe lanes, spinning petals, thrown lanterns (they light up, then burst). 3) phase 1 + it splits into
            # copies (the real one casts a shadow). 4) everything; no seeds, but your own light is as big as a seed's, and lightning flickers
            # nearly all the time (the storm is there from phase 1, rarely). Rows from the walls are shown 0.75 s before.
            "night_bloom": [960, 300, 75000, 60, "boss", 1.0, 810, 1300, 50, "plant", "random_normal",
                {"spiral": {"damage": 600, "cooldown": 2.6, "last_used": -60, "width": 13, "speed": 5, "range": 5000, "bullets": 16, "effects": {}, "type": ["spore"]},
                 "basic": {"damage": 650, "cooldown": 1.8, "last_used": -30, "width": 14, "speed": 9, "range": 5000, "repeat": [3, 0.2], "effects": {}, "type": ["flower_white"]}}],
            # MILO (the Core, 10.11, the last boss of the normal game): the fight itself is game/combat/core_fight.py -
            # a heart in the middle (milo_core) beats faster and faster, everything happens on its beats. Small (a bit
            # bigger than you). F1 Guard 100-75%, F2 Cracks 75-50%, F3 Overheat 50-25%, F4 Despair 25-0%, then he falls,
            # a fake "Win!", and the heart (F5, can't be lost). ~3 min at the Core's 1.0x weapon (2916 DPS, def 25).
            # (11.11) Milo counts as UNDEAD (he is only kept going by the heart): the Holy Orb is very strong on him.
            "milo": [960, 220, 340000, 32, "boss", 0, 2500, 2500, 25, "undead", "random_normal", {}],
            # THE VOID (11.11, the last boss): the fight itself is game/combat/void_fight.py - islands over the abyss
            # (2 x 2 screens), music "Fire and Thunder" (Cjbeards, CC BY 3.0). Its name is never the same (broken signs).
            # Its phases (F1-F3 ~17% each, then the checkpoint at 50%, F4 and F5 25% each) are what the system cut away: F1 Slime King / Prism, F2 Shroom Mother / Frost Golem,
            # F3 the Factory (belts), F4 Night Bloom in the Pale World (copies), F5 everything; then the interlude and
            # the end (not on the HP bar). ~4 min of F1-F5 at the Void's 1.0x weapon (8748 DPS, def 50).
            "void_boss": [1920, 900, 950000, 70, "boss", 1.4, 7290, 6000, 50, "void", "random_normal",
                {"throw": {"radius": 80, "recoil": 120, "damage": 6500, "width": 18, "exp_type": "", "cooldown": 3.0,
                           "last_used": -90, "fly_time": 1.1, "effects": {}, "type": ["ghost_bullet"],
                           "ring": {"bullets": 10, "speed": 6, "damage": 5000, "width": 12}},
                 "split": {"damage": 6000, "cooldown": 2.6, "last_used": -60, "width": 16, "speed": 8, "range": 4000, "effects": {},
                           "type": ["laser_purple", "laser_blue"], "split": {"after": 50, "bullets": 6, "speed": 7, "damage": 4500, "width": 11}},
                 "dash": {"cooldown": 4.0, "last_used": -60, "dashes": 2, "windup": 24, "spiral_on": [1],
                          "distance": 320, "dash_frames": 16, "type": ["ghost_bullet"],
                          "spiral": {"bullets": 10, "damage": 5000, "speed": 6, "width": 13, "range": 4000, "effects": {}}}}],
            "boss1": [900, 900,10,40,"boss",4.2,5,200,0,"undead","to_player",{"basic" : {"damage": 3, "cooldown": 2.0, "last_used": 0, "width": 30, "speed": 9, "range": 2000, "effects" : {"homing":[2],"slow":[180,0.1]}, "type":["missile_blue"]}, 
                                                "spiral1" : {"damage": 2, "cooldown": 3.2, "last_used": 0, "width": 24, "speed": 6, "range": 2000, "bullets": 12, "effects" : {"poison" : [600,2]}, "type":["normal_green"]},
                                                "spiral2" : {"damage": 1, "cooldown": 2.8, "last_used": 0, "width": 8, "speed": 7, "range": 2000, "bullets": 36, "effects" : {"glued" : [60,0.5]}, "type":["normal_yellow"]},
                                                "minigun": {"damage": 1,"cooldown": 2.5,"last_used": 0,"width": 8,"speed": 10,"burst_count": 0,"burst_max": 30,"burst_delay": 0.03,"last_shot": 2500,"is_bursting": False, "range": 2000, "effects" : {"confusion" : [180,0.5]},"type":["bullet_blue"]}}]
        }
        self.boss_info = {
            "void_boss": {"name": "", "phases": [
                {"at": 0.84, "speed": 1.2, "color": [150, 220, 170],                       # F2: the forest and the ice
                 "hard_tweaks": {"burst": {"return_after": 300}, "leap": {"burst": {"return_after": 300}}}, "attacks": {
                    "burst": {**{"bullets": 30, "speed": [5, 11], "decay": 0.98, "min_speed": 2.0, "damage": 4500, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}, "cooldown": 3.2, "last_used": -90},
                    "leap": {"cooldown": 5.5, "last_used": 0, "up": 26, "air": 60, "land_damage": 8000, "burst": {"bullets": 30, "speed": [5, 11], "decay": 0.98, "min_speed": 2.0, "damage": 4500, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}},
                    "line": {"damage": 5000, "cooldown": 2.6, "last_used": -30, "width": 12, "speed": 15, "range": 4000, "bullets": 7, "every": 4, "effects": {"slow": [40, 0.2]}, "type": ["arrow_blue", "laser_blue"]}}},   # (11.11: Frost Golem's row of icicles, not its crack - too hard on the bridges)
                {"at": 0.67, "speed": 1.0, "color": [255, 170, 90], "attacks": {   # F3: the Factory (the bridges are belts: void_arena.py;
                    #   (11.11) instead of its pulsing ring: Scrap Beetles and Toy Soldiers on the outer islands - void_helpers.py)
                    "line": {"damage": 6000, "cooldown": 2.6, "last_used": -30, "width": 13, "speed": 14, "range": 4000, "bullets": 4, "every": 5, "effects": {}, "type": ["bullet_red"]},
                    "throw": {"radius": 90, "recoil": 150, "damage": 6000, "width": 18, "exp_type": "", "cooldown": 3.6,   # bomb crates
                              "last_used": -90, "fly_time": 1.0, "effects": {}, "type": ["grenade_red"],
                              "ring": {"bullets": 12, "speed": 6, "damage": 4500, "width": 12,   # (11.11) the small grenades go off on you
                                       "effects": {"explosion": [55, 1.0], "contact_only": [1]}}}}},
                {"at": 0.5, "speed": 0, "color": [236, 236, 240], "attacks": {}},        # F4: Night Bloom in the Pale World - the
                #   copies and their shots are void_fight.py's (like the Brain of Cthulhu's); the checkpoint (50%)
                {"at": 0.25, "speed": 0, "color": [190, 120, 255], "attacks": {         # F5: everything (void_fight.py flies it round the middle island)
                    "split": {"damage": 6000, "cooldown": 3.0, "last_used": -60, "width": 16, "speed": 8, "range": 4000, "effects": {},
                              "type": ["laser_purple", "laser_blue"], "split": {"after": 50, "bullets": 6, "speed": 7, "damage": 4500, "width": 11}},
                    "pulse": {"damage": 5000, "cooldown": 3.6, "last_used": -60, "width": 14, "speed": 7, "range": 8000, "bullets": 16, "pulse": [45, 15], "effects": {}, "type": ["flower_blue"]},
                    "spiral": {"damage": 5500, "cooldown": 3.2, "last_used": -60, "width": 13, "speed": 5, "range": 6000, "bullets": 14, "effects": {}, "type": ["ghost_bullet"]},
                    "line": {"damage": 6000, "cooldown": 3.0, "last_used": -30, "width": 13, "speed": 14, "range": 4000, "bullets": 4, "every": 5, "effects": {}, "type": ["bullet_red"]}}}]},
            "milo": {"name": "Milo", "phases": [{"at": 0.75, "color": [255, 168, 80]}, {"at": 0.5, "color": [255, 138, 70]},
                                                {"at": 0.25, "color": [255, 105, 60]}]},   # (11.11) 25% each
            "night_bloom": {"name": "Night Bloom",
                            "hard": {"throw": {"radius": 100, "recoil": 260, "damage": 500, "width": 18, "exp_type": "", "cooldown": 4.2, "last_used": -120, "fly_time": 1.0, "light": 230, "effects": {}, "type": ["flower_orange"]}},
                            "arena": {"darkness": {"light": 130, "fog": 0.75, "seed": {"every": 300, "life": 600, "time": 420, "player": 360, "boss": 220, "spots": 4, "spot_r": 180}, "storm": {"every": 300, "flicker": [4, 3, 6], "fade": 24}}}, "phases": [
                {"at": 0.9, "color": [200, 150, 230], "hard_tweaks": {"edge_rain": {"gaps": 1}}, "arena": {"darkness": {"light": 130, "fog": 0.8, "seed": {"every": 300, "life": 600, "time": 420, "player": 360, "boss": 220, "spots": 4, "spot_r": 180}, "storm": {"every": 300, "flicker": [4, 3, 6], "fade": 24}}}, "attacks": {
                    "edge_rain": {"warn": 45, "cooldown": 5.5, "last_used": -120, "sides": ["left", "right"], "spacing": 64, "gaps": 2, "gap": 190, "speed": 4, "damage": 500, "width": 13, "range": 6000, "effects": {}, "type": ["flower_white"]},
                    "sprinkler": {"damage": 450, "cooldown": 5.5, "last_used": -200, "width": 13, "speed": 7, "range": 5000, "streams": 4, "duration": 1.67, "every": 6, "turn": 12, "effects": {}, "type": ["flower_pink"]},
                    "throw": {"radius": 100, "recoil": 260, "damage": 500, "width": 18, "exp_type": "", "cooldown": 3.8, "last_used": -90, "fly_time": 1.0, "light": 230, "effects": {}, "type": ["flower_orange"]}}},
                {"at": 0.62, "color": [170, 210, 240], "hard_set": {"shadow_alpha": 110}, "arena": {"darkness": {"light": 130, "fog": 0.85, "seed": {"every": 300, "life": 600, "time": 420, "player": 360, "boss": 220, "spots": 4, "spot_r": 180}, "storm": {"every": 300, "flicker": [4, 3, 6], "fade": 24}}}, "attacks": {
                    "spiral": {"damage": 600, "cooldown": 2.6, "last_used": -60, "width": 13, "speed": 5, "range": 5000, "bullets": 16, "effects": {}, "type": ["spore"]},
                    "basic": {"damage": 650, "cooldown": 1.8, "last_used": -30, "width": 14, "speed": 9, "range": 5000, "repeat": [3, 0.2], "effects": {}, "type": ["flower_white"]},
                    "decoys": {"copies": 3, "copy": "bloom_copy", "keep_away": 360, "cooldown": 8.0, "last_used": -30}}},
                {"at": 0.34, "color": [240, 120, 170], "hard_arena": {"darkness": {"storm": {"every": 220}}}, "arena": {"darkness": {"light": 300, "storm": {"every": 110, "flicker": [6, 1, 4, 2, 30], "fade": 24}}}, "attacks": {
                    "edge_rain": {"warn": 45, "cooldown": 6.8, "last_used": -120, "sides": ["left", "right", "top", "bottom"], "spacing": 64, "gaps": 2, "side_gaps": {"top": 4, "bottom": 4}, "gap": 190, "speed": 4, "damage": 540, "width": 12, "range": 7000, "effects": {}, "type": ["flower_white"]},
                    "sprinkler": {"damage": 480, "cooldown": 9.0, "last_used": -200, "width": 11, "speed": 6, "range": 5000, "streams": 4, "duration": 1.33, "every": 6, "turn": 13.5, "effects": {}, "type": ["flower_pink"]},
                    "throw": {"radius": 70, "recoil": 260, "damage": 500, "width": 18, "exp_type": "", "cooldown": 4.4, "last_used": -90, "fly_time": 1.0, "light": 230, "effects": {}, "type": ["flower_orange"]},
                    "spiral": {"damage": 600, "cooldown": 3.0, "last_used": -60, "width": 13, "speed": 5, "range": 5000, "bullets": 16, "effects": {}, "type": ["spore"]},
                    "decoys": {"copies": 3, "copy": "bloom_copy", "keep_away": 360, "cooldown": 9.0, "last_used": -30}}}]},
            "assembly_line": {"name": "Assembly Line", "arena": {"belts": {"lanes": BELTS, "speed": 2}}, "phases": [   # (11.11) phases 2-3: its rows and the bottom vents glue (GLUE_FRAMES; the Fire Ring, Factory, protects)
                {"at": 0.67, "color": [255, 170, 90], "arena": {"belts": {"lanes": BELTS, "speed": 2.6}}, "hard_tweaks": {"nozzles": {"lanes": 2}}, "attacks": {
                    "spawn": {"enemy_name": "assembly_machine_2", "amount": 2, "guards": True, "replace": True,
                              "at": [[0.2, 0.17], [0.8, 0.17]], "open_damage": 0.165, "rebuild": 2.0, "color": [170, 150, 120], "cooldown": 1.0, "last_used": -60},
                    "line": {"damage": 270, "cooldown": 3.0, "last_used": -30, "width": 13, "speed": 14, "range": 4000, "bullets": 4, "every": 5, "effects": {"glued": [GLUE_FRAMES, 0.35]}, "type": ["bullet_red"]},
                    "nozzles": {"cooldown": 4.5, "last_used": -120, "lanes": 1, "warn": 45, "rows": 2, "bullets": 10, "every": 5,
                                "speed": 14, "damage": 250, "width": 13, "range": 3000, "type": ["bullet_red"]}}},
                {"at": 0.33, "color": [255, 110, 70], "arena": {"belts": {"lanes": BELTS, "speed": 3, "reverse": [480, 75]}}, "attacks": {
                    "spawn": {"enemy_name": "assembly_machine_3", "amount": 2, "guards": True, "replace": True,
                              "at": [[0.2, 0.17], [0.8, 0.17], [0.5, 0.93]], "open_damage": 0.165, "rebuild": 2.0, "color": [190, 130, 110], "cooldown": 1.0, "last_used": -60},
                    "line": {"damage": 270, "cooldown": 3.0, "last_used": -30, "width": 13, "speed": 15, "range": 4000, "bullets": 4, "every": 5, "effects": {"glued": [GLUE_FRAMES, 0.35]}, "type": ["bullet_red"]},
                    "nozzles": {"cooldown": 3.5, "last_used": -60, "lanes": 1, "warn": 45, "rows": 2, "bullets": 10, "every": 5,
                                "speed": 14, "damage": 250, "width": 13, "range": 3000, "type": ["bullet_red"]},
                    "vents": {"cooldown": 3.0, "last_used": -90, "count": 1, "warn": 40, "pattern": "ring", "bullets": 9, "speed": 6, "damage": 230, "width": 13, "range": 3000, "effects": {"glued": [GLUE_FRAMES, 0.35]}, "type": ["normal_red"]},
                    "vents_line": {"kind": "vents", "cooldown": 3.6, "last_used": -200, "count": 1, "warn": 40, "pattern": "line", "bullets": 4, "every": 5, "speed": 12, "damage": 230, "width": 12, "range": 3000, "effects": {"glued": [GLUE_FRAMES, 0.35]}, "type": ["bullet_red"]}}}]},
            "frost_golem": {"name": "Frost Golem", "hard_tweaks": {"ground_crack": {"branches": 2}}, "phases": [   # (11.11) slow + weakness often: the Frozen Ring (Tundra) is worth wearing here
                {"at": 0.8, "speed": 1.6, "color": [200, 230, 255], "arena": {"ice": True},
                 "hard": {"throw": {"anywhere": True, "radius": 110, "recoil": 0, "damage": 250, "width": 18, "exp_type": "frost_",   # winter blasts
                                    "cooldown": 2.6, "last_used": -90, "fly_time": 1.0, "repeat": [3, 0.3],
                                    "effects": {"slow": [90, 0.3]}, "type": ["normal_blue"]}}, "attacks": {
                    "pulse": {"damage": 250, "cooldown": 3.2, "last_used": -60, "width": 14, "speed": 7, "range": 8000, "bullets": 16, "pulse": [45, 15], "effects": {"weakness": [180, 0.25]}, "type": ["flower_blue"]},
                    "line": {"damage": 250, "cooldown": 2.4, "last_used": -30, "width": 12, "speed": 15, "range": 4000, "bullets": 7, "every": 4, "effects": {"slow": [90, 0.3], "weakness": [180, 0.25]}, "type": ["arrow_blue", "laser_blue"]}}},
                {"at": 0.4, "speed": 1.6, "color": [235, 245, 255], "arena": {"blizzard": [180, 720]}, "hard_arena": {"ice": True}, "attacks": {
                    "ice_walls": {"count": 3, "hits": 5, "life": 8, "long": 200, "thick": 44, "cooldown": 4.0, "last_used": -60},
                    "ground_crack": {"cooldown": 2.8, "last_used": 0, "speed": 16, "length": 1600, "every": 120, "bullets": {"damage": 250, "speed": 6, "width": 13, "range": 5000, "effects": {"slow": [90, 0.3], "weakness": [180, 0.25]}, "type": ["arrow_blue"]}},
                    "pulse": {"damage": 250, "cooldown": 2.6, "last_used": -60, "width": 14, "speed": 7, "range": 8000, "bullets": 16, "pulse": [45, 15], "effects": {"weakness": [180, 0.25]}, "type": ["flower_blue"]},
                    "line": {"damage": 250, "cooldown": 2.0, "last_used": -30, "width": 12, "speed": 15, "range": 4000, "bullets": 7, "every": 4, "effects": {"slow": [90, 0.3], "weakness": [180, 0.25]}, "type": ["arrow_blue", "laser_blue"]}}}]},
            "shroom_mother": {"name": "Shroom Mother", "hard_tweaks": {"leap": {"burst": {"effects": {"poison": [180, 20]}}}}, "phases": [
                {"at": 0.8, "speed": 2.2, "movement": "to_player", "color": [255, 170, 210],
                 "hard": {"sprinkler": {"damage": 70, "cooldown": 6.0, "last_used": -120, "width": 13, "speed": 6, "range": 6000,
                                        "streams": 3, "duration": 2.0, "every": 7, "turn": 9, "effects": {}, "type": ["spore"]}}, "attacks": {
                    "spawn": {"enemy_name": "shroom_guard", "amount": [1, 2], "corners": True, "guards": True, "color": [230, 120, 170],
                              "cooldown": 19.0, "last_used": -1140}}},
                {"at": 0.47, "speed": 1.4, "color": [255, 120, 190], "hard_tweaks": {"burst": {"bullets": 20, "repeat": [3, 0.35]}}, "attacks": {
                    "burst": {**{"bullets": 32, "speed": [6, 13], "decay": 0.975, "min_speed": 2.0, "damage": 70, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}, "cooldown": 2.6, "last_used": -60},
                    "leap": {"cooldown": 4.5, "last_used": 0, "up": 24, "air": 55, "land_damage": 120, "burst": {"bullets": 32, "speed": [6, 13], "decay": 0.8, "min_speed": 2.0, "damage": 70, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}},
                    "wave": {"damage": 70, "cooldown": 3.0, "last_used": -90, "width": 13, "speed": 12, "range": 6000,
                             "bullets": 10, "every": 4, "amp": 30, "period": 36, "double": True, "bounce": 2, "opposite": True,
                             "effects": {}, "type": ["normal_red"]}}}]},
            "prism": {"name": "Prism", "hard_tweaks": {"line": {"opposite": True}}, "phases": [
                {"at": 0.8, "speed": 2.0, "color": [230, 200, 255], "attacks": {
                    "sprinkler": {"damage": 22, "cooldown": 3.2, "last_used": -90, "width": 12, "speed": 8, "range": 4000,
                                  "streams": 4, "duration": 2.0, "every": 7, "turn": 7, "effects": {}, "type": ["laser_red", "laser_yellow", "laser_green", "laser_blue", "laser_purple"]}},
                    "hard": {"spiral": {"damage": 22, "cooldown": 2.6, "last_used": -30, "width": 13, "speed": 7, "range": 3600,
                                        "bullets": 6, "effects": {}, "type": ["laser_red", "laser_yellow", "laser_green", "laser_blue", "laser_purple"]}}},
                {"at": 0.4, "speed": 1.6, "color": [255, 220, 240], "attacks": {
                    "pulse": {"damage": 25, "cooldown": 3.0, "last_used": -60, "width": 13, "speed": 7, "range": 8000,
                              "bullets": 14, "pulse": [45, 15], "effects": {}, "type": ["laser_red", "laser_yellow", "laser_green", "laser_blue", "laser_purple"]},
                    "wall": {"damage": 30, "cooldown": 4.0, "last_used": -120, "width": 14, "speed": 7, "range": 4500,
                             "bullets": 15, "spacing": 34, "gap": 3, "effects": {}, "type": ["laser_red", "laser_yellow", "laser_green", "laser_blue", "laser_purple"]},
                    "split": {"damage": 30, "cooldown": 3.0, "last_used": 0, "width": 16, "speed": 8, "range": 3600, "effects": {},
                              "type": ["laser_red", "laser_yellow", "laser_green", "laser_blue", "laser_purple"], "split": {"after": 50, "bullets": 6, "speed": 7, "damage": 20, "width": 11}}}}]},
            # (12.11) "hard..." = hard mode only (Enemy.apply_hard): what each boss does more there
            "slime_king": {"name": "Slime King", "hard_tweaks": {"dash": {"spiral": {"bullets": 12, "speed": 7.5}}}, "phases": [
                {"at": 0.8, "speed": 1.6, "color": [150, 230, 150], "hard_tweaks": {"spawn": {"amount": 3}}, "attacks": {
                    "throw": {"radius": 70, "recoil": 120, "damage": 12, "width": 16, "exp_type": "", "cooldown": 2.8,
                              "last_used": -90, "fly_time": 1.1, "effects": {}, "type": ["normal_green"],
                              "ring": {"bullets": 8, "speed": 6, "damage": 8, "width": 12}},
                    "spawn": {"enemy_name": "slime_small", "amount": 2, "cooldown": 6.0, "last_used": -120}}},
                {"at": 0.4, "speed": 2.4, "color": [90, 200, 110],
                 "hard_tweaks": {"dash": {"windup": 15, "distance": 330, "cooldown": 2.8}}, "attacks": {
                    "dash": {"cooldown": 3.2, "last_used": -60, "dashes": 3, "windup": 21, "spiral_on": [1, 2],
                             "distance": 300, "dash_frames": 16, "type": ["normal_green"],
                             "spiral": {"bullets": 8, "damage": 8, "speed": 6, "width": 14, "range": 3000, "effects": {}}},
                    "shotgun": {"damage": 10, "cooldown": 3.4, "last_used": 0, "width": 14, "speed": 9, "range": 3000,
                                "bullets": 5, "recoil": 50, "effects": {}, "type": ["normal_green"]},
                    "spawn": {"enemy_name": "slime_small", "amount": 1, "cooldown": 6.0, "last_used": -120}}}]},
        }
        # shared with the rest of the game when passed in (projectile images loaded once)
        self.bullet_type_info = bullet_type_info if bullet_type_info is not None else BulletTypes()

        # ITEM DROPS: enemy name -> [(item name, chance 0-1), ...]
        # rolled once per killed enemy; items are given only if the fight is won
        # (6.11 distribution, see BALANCE.md) - some of the best items come ONLY from here (loot weight 0).
        # An item you already have isn't dropped again. Luck: +25% chance per point (loot.LUCK_DROP).
        self.drops = {
            "shroom_mother": [("Flavoured Candy", 0.10)],
            "night_bloom": [("Firefly Jar", 0.10)],             # boss (8.11): farmed for its trinket        # boss (7.11): farmed for its trinket
            "slime_small": [("Toy Rifle", 0.04)],
            "slime_big": [("Toy Rifle", 0.04)],
            "rainbow_guard": [("Rifle A2", 0.02)],
            "rainbow_slime": [("Normal Blaster", 0.02)],
            "flower_spitter": [("Rose", 0.10)],
            "candy_shroom": [("Bubble Gun", 0.02)],
            "gum_goblin": [("Tape", 0.04)],
            "toy_soldier": [("Blaster 2.0", 0.04)],
            "robo-bomber": [("G-Launcher", 0.05)],
            "portable_factory": [("Rifle A4", 0.06)],
            "frozen_orb": [("Liquidator Hose", 0.04), ("Frost Armor", 0.04)],
            "ice_shooter": [("Frozen Ring", 0.07), ("Ice Mix", 0.05), ("Golden Chestplate", 0.04)],
            "inferno_flower": [("RPG", 0.05)],
            "frost_flower": [("Ultra Blaster", 0.04)],
            "poison_skeleton": [("Laser Cannon 2.0", 0.04), ("Plate Armor", 0.04)],
            "pixie": [("Magic Dust", 0.04)],
            "toxic_flower": [("Tribe Armor", 0.04)],
            "skeleton": [("Samurai God", 0.04)],
            "generator": [("Laser Arrow", 0.04), ("Mecha Armor", 0.04)],
            "liche": [("Ghost USP", 0.03)],
            "voidling": [("Ghost Rifle", 0.05), ("Ghost Armor", 0.04)],
            "purple_crystal": [("Ghost Shotgun", 0.06)],
            "red_crystal": [("Missile-3000", 0.04), ("Fallen knight armor", 0.04)],
            "blue_crystal": [("Laser SMG v2", 0.05), ("Mecha-King Armor", 0.04)],
        }
        self.luck = 0                   # set by Game before each fight (Game.luck())
        # QUEST DROPS: enemy name -> [(item name, chance, quest id[, max owned]), ...]
        # only while that quest is active and the player has fewer than "max owned" (default 1) - at most one per fight
        self.quest_drops = {
            "sugar_caster": [("Sugar Crystal", 0.08, "gus")],
            "robo-tesla": [("Fuse", 0.25, "foreman")],
            "toxic_flower": [("Glowing Sprout", 0.25, "gardener", 3)],      # (.., max you may own: 3 sprouts)
        }
        self.active_quests = set()      # set by Game before each fight
        self.skip_items = set()         # items the player already has (set by Game before each fight)
        self.dropped_now = set()        # quest items already dropped in this fight (one per fight)
        self.owned_counts = {}          # how many of each item the player has (set by Game before each fight)
        self.sfx = sfx

    def get_enemy(self, name):
        e = self.enemies[name]
        enemy = Enemy(*e[:-1],copy.deepcopy(e[-1]),self.sfx, self.bullet_type_info)
        enemy.name = name   # needed for drops
        if name in SQUARE:                                     # (8.11) Assembly Line's machines and products
            enemy.shape = "square"
        enemy.machine = name in MACHINES
        enemy.anchored = name in ANCHORED
        enemy.ride_off = name in BELT_RIDERS
        if name in BELT_RIDERS:
            enemy.color = (110, 110, 125) if name == "belt_turret" else (200, 150, 80)
        if name in ("line_soldier", "line_beetle"):
            enemy.color = (205, 95, 85) if name == "line_soldier" else (150, 120, 90)
        return enemy
    def get_boss(self, name):
        b = self.bosses[name]
        enemy = Enemy(*b[:-1],copy.deepcopy(b[-1]),self.sfx, self.bullet_type_info)
        enemy.name = name
        enemy.anchored = name in ANCHORED
        enemy.casts_shadow = name in SHADOWED
        if name in self.boss_info:
            enemy.set_phases(self.boss_info[name])
        return enemy

    def roll_drops(self, enemy):
        dropped = []
        for item_name, chance in self.drops.get(enemy.name, []):
            if item_name in self.skip_items or item_name in self.dropped_now:
                continue                # you have it already / it dropped in this fight
            if random.random() < chance * (1 + LUCK_DROP * self.luck):
                dropped.append(item_name)
                self.dropped_now.add(item_name)
        for item_name, chance, quest, *limit in self.quest_drops.get(enemy.name, []):
            enough = self.owned_counts.get(item_name, 1 if item_name in self.skip_items else 0) >= (limit[0] if limit else 1)
            if quest in self.active_quests and not enough and item_name not in self.dropped_now and random.random() < chance:
                dropped.append(item_name)
                self.dropped_now.add(item_name)
        return dropped

    def provoke_enemies(self, biome, difficulty, screen):
        """A normal fight: random enemies of the biome until the fight's points run out (see SPAWNS)."""
        money = 0
        weights = SPAWNS[biome][1]
        points = fight_points(biome, difficulty)
        spawnpoints = spawn_points(screen.get_width(), screen.get_height())
        provoked_enemies = []
        while points > 0 and spawnpoints:
            name = random.choice(list(weights))
            points -= weights[name]
            enemy = self.get_enemy(name)
            enemy.x, enemy.y = spawnpoints.pop()
            enemy.color = (random.randint(100,200),random.randint(100,200),random.randint(100,200))
            provoked_enemies.append(enemy)
            money += enemy.money

        return provoked_enemies, money
