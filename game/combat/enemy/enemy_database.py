from game.combat.enemy.enemy import Enemy
from game.world.loot import LUCK_DROP
from game.combat.bullet_types import BulletTypes
import copy, random, math

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
    "the_void": [[4,6], {"voidling": 3, "blue_crystal": 4, "red_crystal": 5, "purple_crystal": 5}],
}
MAX_ENEMIES = 15                # = spawn points around the player
SPAWN_RING = (0.42, 0.40)       # the ring of spawn points: share of the screen width / height from the centre


def fight_points(biome, hard_mode, rnd=random):
    """How many points of enemies this fight gets."""
    (low, high), weights = SPAWNS[biome]
    avg = sum(weights.values()) / len(weights)
    count = rnd.randint(min(high, low + (1 if hard_mode else 0)), high)
    return round(count * avg)


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

            # Shroom Mother's guards (boss phase 2): stand in a corner, 2 spinning streams; not in normal fights
            "shroom_guard": [0,0,490,30,"enemy",0,90,0,25,"mystical","random_normal",
                {"sprinkler": {"damage": 70, "cooldown": 3.0, "last_used": -60, "width": 12, "speed": 7, "range": 5000,
                               "streams": 2, "duration": 2.0, "every": 6, "turn": 9, "effects": {}, "type": ["spore"]}}],

            "toffee_runner": [0,0,86,18,"enemy",3.8,88,10,25,"animal","to_player_zigzag",{}],

            "sugar_caster": [0,0,220,25,"enemy",2.3,73,22,25,"mystical","away_player_normal",
                {"throw": {"radius": 90, "recoil":150, "damage": 220, "width":15, "exp_type":"nova_", "cooldown": 2.0, "last_used": 0, "fly_time": 1.5, "effects": {"speed":[60,0.25]},"stop_move":[24,8], "type":["flower_white"],
                           "ring": {"bullets": 8, "speed": 6, "damage": 90, "width": 11, "effects": {}}}}],


            # --- TOY FACTORY ---

            "toy_soldier": [0,0,810,20,"enemy",1.8,140,25,0,"mechanical","to_player_normal",
                {"basic": {"damage": 410, "cooldown": 2.2, "last_used": 0, "width": 16, "speed": 14, "range": 3500, "repeat": [3, 0.15], "effects": {}, "type":["bullet_red"]}}],

            "portable_factory": [0,0,1820,40,"enemy",0,14,50,0,"mechanical","random_normal",
                {"spawn": {"enemy_name":"toy_soldier","amount" : 1,"cooldown": 7.5, "last_used": 0},
                "spiral": {"damage": 220, "cooldown": 3.5, "last_used": 0, "width": 12, "speed": 6, "range": 3800, "bullets": 14, "effects": {}, "type":["normal_red"]}}],

            "robo-tesla": [0,0,650,23,"enemy",1.8,140,30,25,"mechanical","random_normal",
                           {"wave": {"damage": 300, "cooldown": 1.5, "last_used": 0, "width": 8, "speed": 13, "range": 2600, "bullets": 8, "every": 4, "amp": 28, "period": 36, "double": True, "effects": {"weakness":[120,0.2]}, "type":["normal_blue"]},
                            "spiral": {"damage": 300, "cooldown": 1.0, "last_used": 0, "width": 5, "speed": 11, "range": 1800, "bullets": 16, "effects": {"weakness":[120,0.2]}, "type":["normal_blue"]}}],

            "robo-bomber": [0,0,650,23,"enemy",1.8,140,30,25,"mechanical","random_normal",
                            {"throw": {"radius": 180, "recoil":250, "damage": 480, "width":15, "exp_type":"", "cooldown": 3.2, "last_used": 0, "fly_time": 0.8, "effects": {"burn":[60,27]}, "type":["grenade_red"]}}],
                           
            "scrap_beetle": [0,0,260,14,"enemy",5.2,270,20,25,"mechanical","to_player_normal",
                {"mine": {"damage": 610, "radius": 80, "cooldown": 1.5, "last_used": 0, "width": 18, "exp_time": 3.5, "effects": {}, "type": ["mine_red"]}}],


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

            "voidling": [0,0,10940,14,"enemy",2.4,7850,80,100,"void","to_player_normal",
                {"spawn": {"enemy_name":"voidling","amount" : 1,"cooldown": 3.0, "last_used": 0},
                 "death_spiral": {"damage": 5610, "cooldown": 0, "last_used": 0, "width": 12, "speed": 12, "range": 3000, "bullets": 3, "effects": {"confusion":[30,0.5]}, "type":["flower_pink"]}}],

            "red_crystal": [0,0,32800,25,"enemy",1.5,5610,200,50,"void","away_player_normal",
                {"shotgun":{"damage": 8970, "cooldown": 2.6, "last_used": 0, "width": 16, "speed": 12, "range": 3500, "recoil": 40, "bullets": 8, "repeat": [2, 0.35], "effects": {"burn":[180,336]}, "type":["flower_orange"]},
                 "basic": {"telegraph": 30, "damage": 12340, "cooldown": 1.7, "last_used": 0, "width": 24, "speed": 18, "range": 3600, "effects": {"burn":[180,336]}, "type":["flower_orange"]}}],

            "purple_crystal": [0,0,32800,25,"enemy",1.8,5610,250,50,"void","random_normal",
                {"death_spawn": {"amount": 1, "enemy_name": "voidling"},
                "pulse": {"damage": 5610, "cooldown": 4.4, "last_used": -178, "width": 10, "speed": 6, "range": 9000, "bullets": 24, "pulse": [45, 15], "effects": {"confusion":[30,1.0]}, "type":["flower_pink"]},
                "sprinkler": {"damage": 5610, "cooldown": 2.8, "last_used": 0, "width": 10, "speed": 8, "range": 4000, "streams": 4, "duration": 1.6, "every": 8, "turn": 8, "effects": {"confusion":[30,1.0]}, "type":["flower_pink"]}}],

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
            "boss1": [900, 900,10,40,"boss",4.2,5,200,0,"undead","to_player",{"basic" : {"damage": 3, "cooldown": 2.0, "last_used": 0, "width": 30, "speed": 9, "range": 2000, "effects" : {"homing":[2],"slow":[180,0.1]}, "type":["missile_blue"]}, 
                                                "spiral1" : {"damage": 2, "cooldown": 3.2, "last_used": 0, "width": 24, "speed": 6, "range": 2000, "bullets": 12, "effects" : {"poison" : [600,2]}, "type":["normal_green"]},
                                                "spiral2" : {"damage": 1, "cooldown": 2.8, "last_used": 0, "width": 8, "speed": 7, "range": 2000, "bullets": 36, "effects" : {"glued" : [60,0.5]}, "type":["normal_yellow"]},
                                                "minigun": {"damage": 1,"cooldown": 2.5,"last_used": 0,"width": 8,"speed": 10,"burst_count": 0,"burst_max": 30,"burst_delay": 0.03,"last_shot": 2500,"is_bursting": False, "range": 2000, "effects" : {"confusion" : [180,0.5]},"type":["bullet_blue"]}}]
        }
        self.boss_info = {
            "shroom_mother": {"name": "Shroom Mother", "phases": [
                {"at": 0.8, "speed": 2.2, "movement": "to_player", "color": [255, 170, 210], "attacks": {
                    "spawn": {"enemy_name": "shroom_guard", "amount": [1, 2], "corners": True, "guards": True, "color": [230, 120, 170],
                              "cooldown": 19.0, "last_used": -1140}}},
                {"at": 0.47, "speed": 1.4, "color": [255, 120, 190], "attacks": {
                    "burst": {**{"bullets": 32, "speed": [6, 13], "decay": 0.975, "min_speed": 2.0, "damage": 70, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}, "cooldown": 2.6, "last_used": -60},
                    "leap": {"cooldown": 4.5, "last_used": 0, "up": 24, "air": 55, "land_damage": 120, "burst": {"bullets": 32, "speed": [6, 13], "decay": 0.8, "min_speed": 2.0, "damage": 70, "width": 13, "range": 6000, "effects": {}, "type": ["spore"]}},
                    "wave": {"damage": 70, "cooldown": 3.0, "last_used": -90, "width": 13, "speed": 12, "range": 6000,
                             "bullets": 10, "every": 4, "amp": 30, "period": 36, "double": True, "bounce": 2, "opposite": True,
                             "effects": {}, "type": ["normal_red"]}}}]},
            "prism": {"name": "Prism", "phases": [
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
            "slime_king": {"name": "Slime King", "phases": [
                {"at": 0.8, "speed": 1.6, "color": [150, 230, 150], "attacks": {
                    "throw": {"radius": 70, "recoil": 120, "damage": 12, "width": 16, "exp_type": "", "cooldown": 2.8,
                              "last_used": -90, "fly_time": 1.1, "effects": {}, "type": ["normal_green"],
                              "ring": {"bullets": 8, "speed": 6, "damage": 8, "width": 12}},
                    "spawn": {"enemy_name": "slime_small", "amount": 2, "cooldown": 6.0, "last_used": -120}}},
                {"at": 0.4, "speed": 2.4, "color": [90, 200, 110], "attacks": {
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
            "shroom_mother": [("Flavoured Candy", 0.10)],        # boss (7.11): farmed for its trinket
            "slime_small": [("Toy Rifle", 0.04)],
            "slime_big": [("Toy Rifle", 0.04)],
            "rainbow_guard": [("Rifle A2", 0.02)],
            "rainbow_slime": [("Normal Blaster", 0.02)],
            "flower_spitter": [("Rose", 0.10)],
            "candy_shroom": [("Bubble Gun", 0.02)],
            "gum_goblin": [("Tape", 0.04)],
            "toy_soldier": [("Rifle A4", 0.04)],
            "robo-bomber": [("G-Launcher", 0.04)],
            "portable_factory": [("Blaster 2.0", 0.04)],
            "frozen_orb": [("Liquidator Hose", 0.04), ("Frost Armor", 0.04)],
            "ice_shooter": [("Frozen Ring", 0.05), ("Ice Mix", 0.05), ("Golden Chestplate", 0.04)],
            "inferno_flower": [("RPG", 0.04)],
            "frost_flower": [("Ultra Blaster", 0.04)],
            "poison_skeleton": [("Laser Cannon 2.0", 0.04), ("Plate Armor", 0.04)],
            "pixie": [("Magic Dust", 0.04)],
            "toxic_flower": [("Tribe Armor", 0.04)],
            "skeleton": [("Samurai God", 0.04)],
            "generator": [("Laser Arrow", 0.04), ("Mecha Armor", 0.04)],
            "liche": [("Ghost USP", 0.04)],
            "voidling": [("Ghost Rifle", 0.02), ("Ghost Armor", 0.02)],
            "purple_crystal": [("Ghost Shotgun", 0.02)],
            "red_crystal": [("Missile-3000", 0.02), ("Fallen knight armor", 0.02)],
            "blue_crystal": [("Laser SMG v2", 0.02), ("Mecha-King Armor", 0.02)],
        }
        self.luck = 0                   # set by Game before each fight (Game.luck())
        # QUEST DROPS: enemy name -> [(item name, chance, quest id[, max owned]), ...]
        # only while that quest is active and the player has fewer than "max owned" (default 1) - at most one per fight
        self.quest_drops = {
            "sugar_caster": [("Sugar Crystal", 0.05, "gus")],
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
        return enemy
    def get_boss(self, name):
        b = self.bosses[name]
        enemy = Enemy(*b[:-1],copy.deepcopy(b[-1]),self.sfx, self.bullet_type_info)
        enemy.name = name
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

    def provoke_enemies(self, biome, hard_mode, screen):
        """A normal fight: random enemies of the biome until the fight's points run out (see SPAWNS)."""
        money = 0
        weights = SPAWNS[biome][1]
        points = fight_points(biome, hard_mode)
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
