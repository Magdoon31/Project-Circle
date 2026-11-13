import copy
import math
import random

import pygame
from game.combat.decoy import Decoy
from game.combat.projectile import projectile as prjt
from game.inventory import sigils as SG
from game.combat import win_screen as WIN
from game.combat.damage_numbers import DamageNumbers
from game.lib.motion_blur import MotionBlur
from game.menu import options as OPT
from game import controls as KEYS
from game.lib import snow_overlay as SNOW
from game.combat import rooms as ROOMS
from game.combat import sprites as FIGHT_SPRITES
from game.combat import wall_tactics as TACTICS
from game.combat.darkness import Darkness
from game.combat.song import fight as SONG
from game.combat.enemy.enemy_database import WALL_BOUNCE, WALL_PASS
from game.combat.player import shooter as SH
from game import difficulty as DIFF

# RUNNING AWAY: hold R in a normal fight. Every frame there is a chance to escape (no win, no death).
# While holding R the player can't shoot.
RUN_KEY = pygame.K_r
RUN_CHANCE = 0.006            # per frame of holding R (~1.4 s on average)
RUN_CHANCE_HARD_MODE = 0.004  # ~2 s on average
HARD_ENEMY_DAMAGE = 1.15      # (12.11) hard mode: enemies (and bosses) hit 15% harder ...
HARD_GOLD = 0.88              # ... and every fight gives 12% less gold
FROST_RING_WIDTH = 3           # (13.11) the Frost armour's ring (px)
HELPERS_STAY = {"slime_king"}   # (13.11) the small slimes it called stay after it dies - you finish them off
NO_GOLD_BOSSES = {"milo", "void_boss"}   # (12.11) the last two bosses give no gold (nothing to buy after them)
HARD_BOSS_REACH = 10000       # (12.11) hard mode: a boss's bullets live this long (ms) - they go off the map
SHORT_REACH = 2000            # ... not the ones meant to vanish soon (shorter range) ...
SLOW_BULLET = 4               # ... nor the slow ones (px a frame) ...
OWN_REACH_MOTIONS = {"slowdown", "creep", "pulse", "land_ring"}   # ... nor spores, mines, pulsing rings, bombs
CAN_RUN_FROM_BOSS = False
DEATH_ATTACK_DELAY = 18      # frames (0.3 s) between a death and its death attack (warning ring)
OUT_OF_ROOM = 300           # (11.11) px outside the room after which an enemy bullet flying away is gone
CLUSTER_DELAY = 8           # Atom: frames between its small explosions (0.13 s)
SPREAD_MIN_FRAMES = 180     # Fire / Toxic Ring: a passed-on burn / poison lasts at least 3 s
# Flavoured Candy: what it can do at the start of a fight (good / bad, 50:50)
FLAVOURS_GOOD = ["strength", "speed", "regen", "invulnerable"]
FLAVOURS_BAD = ["burn", "slow", "weakness", "confusion"]
FLAVOUR_STRENGTH = {"strength": 0.3, "speed": 0.25, "slow": 0.3, "weakness": 0.3}
INVULN_FLAVOUR = 180            # frames
CRACK_FADE = 50                # frames a finished ground crack stays and fades
CRACK_HURTS_AFTER = 20         # (10.11) Milo's cracks (no bullets) still hurt this many frames after they stop
CRACK_WIDTH = 12               # px from the crack's line that it hurts
BLIZZARD_SIGHT = 230           # px you can see around you in a snowstorm (boss arena)
CAMERA_EASE = 0.12            # (8.11) big rooms: how fast the camera follows you (share per frame)
ARROW_COLOR = (200, 40, 40)   # (8.11) big rooms: arrows at the screen edge pointing at enemies you can't see
RAIN_WARNING = (255, 120, 90)  # (8.11) the marks where a row of bullets will come in from a wall
RAIN_MARK = 40                 # px long
FIREFLY_SPEED = 9              # (8.11) Firefly Jar: how fast its fireflies fly
ZAP_REACH = 300               # (8.11) px a zap can jump from one enemy to the next
ZAP_FALLOFF = 0.7             # (8.11) every next jump of a zap hits this much weaker
PRODUCT_LIMITS = {"belt_turret": 2}   # (8.11) Assembly Line: at most this many of a product in the fight at once
BELT_BULLETS = 1.0             # (8.11) enemy bullets on a conveyor belt move this share of the belt's speed
BELT_COLOR, BELT_EDGE, BELT_ARROW = (74, 72, 80), (42, 40, 46), (112, 110, 120)
NOZZLE_COLOR, NOZZLE_HOT = (90, 88, 96), (255, 120, 60)
PHASE_FLASH = 18              # frames of the white flash when a boss changes phase
SONG_SFX_VOLUME = {"laser": 0.35, "circle": 0.8, "square": 1.0}   # (10.11) the Mascot's sounds, only on the beat
FLAWLESS_GOLD = 1.2           # no damage taken in a normal fight: x1.2 gold (not in hard mode)     # bosses are only fought on purpose (you walk into them)


def reach_far(bullets):
    """(12.11) Hard mode: a boss's bullets (and what they burst into) fly on till they leave the map."""
    for p in bullets:
        children = (p.motion or {}).get("children")
        if children and children.get("range", 0) >= SHORT_REACH:
            children["range"] = max(children["range"], HARD_BOSS_REACH)
        if keeps_own_reach(p):
            continue
        p.range = max(p.range, HARD_BOSS_REACH)


def explosion_look(effect):
    """The look of a bullet's coloured explosion ("nova_", "frost_"), or None."""
    return next((key[:-len("explosion")] for key in effect if key.endswith("_explosion")), None)


def keeps_own_reach(p):
    """Bullets whose short life is the point: thrown bombs, spores, mines, slow or short-range ones."""
    kind = (p.motion or {}).get("kind")
    return "throw" in p.effects or kind in OWN_REACH_MOTIONS or p.range < SHORT_REACH or p.speed < SLOW_BULLET


class Combat:

    def __init__(self, screen, player, enemies, enemy_db, difficulty, sfx=None, boss=None, assets=None):
        # (8.11) `screen` = the room everything is drawn in (the display, or a bigger picture in a big room);
        # `view` = the display. In a big room the camera shows the part around the player (setup_room).
        self.screen = screen
        self.view = screen
        self.cam = [0.0, 0.0]
        self.player = player
        self.boss = boss
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.enemy_db = enemy_db

        self.enemies = enemies
        self.win = False
        self.finished = False
        self.escaped = False          # True = the player ran away (R)
        self.trying_to_run = False

        self.sfx = sfx
        # sounds / images / fonts are loaded once in CombatAssets (game start), not on every fight
        if assets is None:
            from game.combat.combat_assets import CombatAssets
            assets = CombatAssets(sfx)
        self.assets = assets
        self.font_light = assets.font_light
        self.font_heavy = assets.font_heavy

        self.money = 0
        self.loot = []   # names of items dropped by killed enemies - given to the player only on a win
        self.defeated = {}              # (11.11) enemy name -> Defeated (the win screen's table)
        self.phase_changed = False      # (11.11) a boss changed phase this frame (Settings: pause on it)
        self.win_screen = None          # (11.11) win_screen.py, made when the fight is won
        self.gold_mult = 1.0            # (11.11) Game: Lucky Coin etc. (the win screen shows the gold you really get)
        self.item_icon = lambda name: pygame.Surface((1, 1), pygame.SRCALPHA)   # Game: name -> its picture
        self.rarity = lambda name: "common"                                       # Game: name -> its rarity
        self.font_win = assets.font_win
        self.motion_blur = MotionBlur()
        self.damage_numbers = DamageNumbers(assets.font_heavy["mid"])   # (11.11) Settings -> damage numbers
        self.money_mult = random.randint(10,40)*0.05
        self.money_mult_og = self.money_mult

        self.difficulty = difficulty                     # (12.11) game/difficulty.py
        self.hard_mode = difficulty == DIFF.HARD
        self.easy_mode = difficulty == DIFF.EASY
        if self.hard_mode:
            player.hurt_mult = HARD_ENEMY_DAMAGE
            player.ice_grip = SH.HARD_ICE_GRIP
        elif self.easy_mode:
            player.hurt_mult = DIFF.EASY_ENEMY_DAMAGE
        self.timer = 0

        self.segments = assets.zap_segments
        self.poison_segments = assets.poison_zap_segments
        self.zapped_enemies = []
        self.explosion_img = assets.explosion_img
        self.nova_explosion_img = assets.nova_explosion_img
        self.explosion_looks = {"nova_": assets.nova_explosion_img, "frost_": assets.frost_explosion_img}
        self.explosions = []
        self.pending_explosions = []
        self.near_misses = 0          # enemy bullets that flew right past the player (Bullet Time sigil)
        self.feats = set()            # sigil feats done in this fight, e.g. "firefly_dash" (Game.after_fight_sigils)
        self.pending_bullets = []     # death attacks waiting to go off ([frames left, bullets, pos, size])  # Atom: small explosions waiting to go off ([frames left, pos, effect, type, effects])
        self.decoy = None             # Mascot Plush: dropped on the first frame (the enemies are known by then)
        self.decoy_image = getattr(assets, "decoy_img", None)
        self.darkness = Darkness()      # (8.11) Night Bloom's dark arena (darkness.py)
        self.song = None                # (10.11) a song fight (the Mascot): song/fight.py - set by Game
        self.core = None                # (10.11) Milo's fight (core_fight.py) - set by Game
        self.void = None                # (11.11) the Void's fight (void_fight.py) - set by Game
        self.skip_end_screen = False    # (10.11) Milo: no "Win! CLICK" at the real end

    def setup_room(self, biome):
        """(8.11) A normal fight: a bigger room for more than 3 enemies (the camera follows you) and, sometimes,
        obstacles in the biome's look (see rooms.py)."""
        sw, sh = self.view.get_size()
        w, h = ROOMS.room_size(len(self.enemies), (sw, sh))
        if (w, h) != (sw, sh):
            self.screen = pygame.Surface((w, h))
            for e in self.enemies:                      # the spawn ring grows with the room
                e.x, e.y = e.x * w / sw, e.y * h / sh
        self.walls, start = ROOMS.make_obstacles(biome, (w, h))
        self.player.x, self.player.y = start                  # the middle, or next to a pillar standing there
        for _ in range(3):
            for e in self.enemies:
                self.push_out_of_walls(e)
        self.follow_camera(instant=True)

    def follow_camera(self, instant=False):
        """Big room: the camera moves smoothly after the player and stops at the room's edges."""
        (w, h), (sw, sh) = self.screen.get_size(), self.view.get_size()
        fx, fy = self.void.camera.focus((self.player.x, self.player.y)) if self.void else (self.player.x, self.player.y)
        goal = (min(max(0, fx - sw / 2), w - sw), min(max(0, fy - sh / 2), h - sh))
        k = 1 if instant else CAMERA_EASE
        self.cam = [self.cam[0] + (goal[0] - self.cam[0]) * k, self.cam[1] + (goal[1] - self.cam[1]) * k]
        self.player.cam = (int(self.cam[0]), int(self.cam[1]))     # aiming: the mouse is on the screen

    def draw_view(self):
        """Big room: shows the part of the room around the player + arrows to the enemies off the screen."""
        sw, sh = self.view.get_size()
        cx, cy = int(self.cam[0]), int(self.cam[1])
        zoom, turn = self.void.camera.lens() if self.void else (1.0, 0.0)
        if zoom == 1.0 and turn == 0.0:
            self.view.blit(self.screen, (0, 0), pygame.Rect(cx, cy, sw, sh))
        else:
            self.draw_view_through_lens(cx, cy, zoom, turn)
        for e in self.enemies:
            if getattr(e, "hidden", False):
                continue
            ex, ey = e.x - cx, e.y - cy
            if -e.width < ex < sw + e.width and -e.width < ey < sh + e.width:
                continue
            a = math.atan2(ey - sh / 2, ex - sw / 2)
            k = min((sw / 2 - 30) / max(1e-6, abs(math.cos(a))), (sh / 2 - 30) / max(1e-6, abs(math.sin(a))))
            px, py = sw / 2 + math.cos(a) * k, sh / 2 + math.sin(a) * k
            tip = (px + math.cos(a) * 14, py + math.sin(a) * 14)
            left = (px + math.cos(a + 2.5) * 12, py + math.sin(a + 2.5) * 12)
            right = (px + math.cos(a - 2.5) * 12, py + math.sin(a - 2.5) * 12)
            pygame.draw.polygon(self.view, ARROW_COLOR, (tip, left, right))

    def clip_to_camera(self):
        """(11.11) Big room: only the part the camera shows is drawn (a 2 x 2 room drew 4 screens a frame)."""
        if self.screen is not self.view:
            self.screen.set_clip(pygame.Rect(int(self.cam[0]) - 2, int(self.cam[1]) - 2,
                                             self.view.get_width() + 4, self.view.get_height() + 4))

    def draw_view_through_lens(self, cx, cy, zoom, turn):
        """(11.11) The Void's camera: closer (zoom) and a little turned (degrees) round the middle of the view.
        Turned, it looks a bit closer still, so the corners never show what is outside the room."""
        sw, sh = self.view.get_size()
        a = math.radians(abs(turn))
        zoom = max(zoom, math.cos(a) + sw / sh * math.sin(a))
        w, h = int(sw / zoom), int(sh / zoom)
        rw, rh = self.screen.get_size()
        x = min(max(0, cx + (sw - w) // 2), rw - w)
        y = min(max(0, cy + (sh - h) // 2), rh - h)
        picture = pygame.transform.scale(self.screen.subsurface(pygame.Rect(x, y, w, h)), (sw, sh))
        if turn:
            picture = pygame.transform.rotate(picture, turn)
        self.view.blit(picture, picture.get_rect(center=(sw // 2, sh // 2)))

    def target(self):
        """What the enemies go for: the Mascot Plush while it lives, else the player."""
        return self.decoy if self.decoy and self.decoy.alive else self.player

    def can_run(self):
        return CAN_RUN_FROM_BOSS or not self.boss

    def handle_events(self, events, mouse_btn_pressed):
        self.trying_to_run = self.can_run() and pygame.key.get_pressed()[RUN_KEY]
        if self.void and self.void.dead:                  # (11.11) "Game Over" in the Void: a click = the checkpoint
            if any(e.type == pygame.MOUSEBUTTONDOWN for e in events):
                self.void.click(self, pygame.time.get_ticks())
            return
        if self.core and self.core.shows_fake_win:
            if any(e.type == pygame.MOUSEBUTTONDOWN for e in events):
                self.core.click()
                self.win_screen = None                       # (it was only a fake win)
            return
        if self.trying_to_run or self.song or (self.core and not self.core.allows_shooting) \
                or (self.void and not self.void.allows_shooting):
            return   # no shooting while trying to run (or in a song fight: you only dodge)

        # (11.11) the left mouse button, or the Shoot key from Settings (controls.py; not set by default)
        for event in events:
            clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            if (clicked or KEYS.pressed(event, "shoot")) and not self.player.automatic_weapon:
                self.fire()

        # automatic weapons while the button is held; a started burst always finishes
        held = mouse_btn_pressed[0] or KEYS.holding(pygame.key.get_pressed(), "shoot")
        if (held and self.player.automatic_weapon) or self.player.bursting():
            self.fire()

    def fire(self):
        multiple, new_projectile = self.player.shoot()
        if new_projectile is not None:
            self.sfx.play("shoot")
            if multiple:
                self.player_projectiles.extend(new_projectile)
            else:
                self.player_projectiles.append(new_projectile)

    def update(self):
        self.timer += 1
        if self.core and self.core.holds_time:          # (10.11) Milo rewinds time: only that happens now
            self.update_core()
            return
        if self.void and self.void.holds_world:          # (11.11) "Game Over" in the Void waits for a click
            return
        for waiting in self.pending_bullets[:]:
            waiting[0] -= 1
            if waiting[0] <= 0:
                self.pending_bullets.remove(waiting)
                now = pygame.time.get_ticks()
                for p in waiting[1]:
                    p.shot_time = now                    # their range counts from now
                self.enemy_projectiles.extend(waiting[1])
                if len(waiting) > 4:
                    self.death_blast(waiting[2], waiting[4])
        for waiting in self.pending_explosions[:]:
            waiting[0] -= 1
            if waiting[0] <= 0:
                self.pending_explosions.remove(waiting)
                self.explosion(waiting[1], waiting[2], None, waiting[3], waiting[4], True)
                self.sfx.play("explosion")
        if self.timer == 1 and "flavour" in self.player.trinket_effect and not self.song:
            self.flavoured_candy(self.player.trinket_effect["flavour"][0])
        if self.timer == 1 and "decoy" in self.player.trinket_effect and self.enemies:
            self.decoy = Decoy.drop(self.screen, self.player, self.enemies, self.player.trinket_effect["decoy"][0], self.decoy_image)
        if self.trying_to_run and not self.finished:
            if self.timer % 20 == 0:
                self.sfx.play("run")
            if random.random() < (RUN_CHANCE_HARD_MODE if self.hard_mode else RUN_CHANCE):
                self.escaped = True
                self.finished = True
                return
        keys = pygame.key.get_pressed()
        self.arena = {}
        for e in self.enemies:                          # what the bosses' arena does now (ice floor, snowstorm)
            self.arena.update(getattr(e, "arena", {}))
        if self.arena.get("belts"):
            self.last_belts = self.arena["belts"]
        elif getattr(self, "last_belts", None):
            self.arena["belts"] = self.last_belts      # (8.11) the belts stay after the boss is gone
        self.player.ice = bool(self.arena.get("ice"))
        if self.darkness.update(self.arena.get("darkness"), self.player, self.screen.get_size(), self.timer):
            self.thunder()
        self.player.move(keys, self.screen)
        self.walls = getattr(self, "walls", [])
        for wall in self.walls[:]:                      # ice walls melt / break (room walls stay, crates break)
            if wall.get("solid"):
                continue
            wall["life"] -= 1
            wall["hits"] = max(0, wall["hits"])
            if wall["life"] <= 0 or wall["hits"] <= 0:
                self.walls.remove(wall)
        self.push_out_of_walls(self.player)
        self.update_belts()
        if self.screen is not self.view:
            self.follow_camera()
        self.update_cracks()
        self.update_nozzles()
        self.release_fireflies()
        self.update_song()
        self.update_core()
        self.update_void()
        if OPT.get("damage_numbers"):
            self.damage_numbers.update(self.enemies)
        if len(self.enemies) > 32:
            # hard cap: newest extra enemies just vanish (no death attacks, so no chain spawning)
            del self.enemies[32:]

        targets = [e for e in self.enemies if not getattr(e, "untouchable", False)]   # (11.11) the Void's end
        for projectile in self.player_projectiles[:]:
            projectile.update(targets)
            wall = self.wall_at(projectile.x, projectile.y)
            if wall:                                    # your shot cracks the ice wall / a crate (room walls: just stops)
                if not wall.get("solid"):
                    wall["hits"] = max(0, wall["hits"] - 1)
                self.player_projectiles.remove(projectile)
                self.sfx.play("hit")
                continue
            if (
                projectile.x < 0
                or projectile.x > self.screen.get_width()
                or projectile.y < 0
                or projectile.y > self.screen.get_height()
            ):
                self.player_projectiles.remove(projectile)
                continue

            proj_expire, effect = projectile.check_duration()
            if not proj_expire:
                
                if "explosion" in effect:
                    effect["explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect["explosion"],None, effects=effect)
                    self.sfx.play("explosion") 
                self.player_projectiles.remove(projectile)
                continue
           
            for enemy in targets:

                special_effect = projectile.deal_damage(enemy)
                #special_effect -> [name,effect] (and also (T/F) if it hit an enemy) name in (zap, pierce, explosion) effect = []

                if special_effect:
                    if special_effect[0] != "pierce":
                        self.player_projectiles.remove(projectile)
                    else:
                        if special_effect[1]:
                            self.player_projectiles.remove(projectile)


                    if special_effect[0] == "zap":
                        self.zap(special_effect[1], enemy)
                        self.sfx.play(f"zap{random.randint(1,3)}")
                    elif special_effect[0] == "explosion":
                        self.explosion((projectile.x,projectile.y), special_effect[1],enemy, effects=projectile.effects)
                        self.sfx.play("explosion")     
                    else:
                        self.sfx.play("hit")
                    break
        if self.scripted_end_reached():
            self.win = True
            self.finished = True


        if self.player.thorns_pending:
            self.shoot_thorns()
        for projectile in self.enemy_projectiles[:]:
            if "frost" in self.player.armor_effect:

                dx = self.player.x - projectile.x
                dy = self.player.y - projectile.y

                dist = math.sqrt(dx**2 + dy**2)
                current_speed = math.sqrt(projectile.vx**2 + projectile.vy**2)

                if current_speed > 0:
                    dir_x = projectile.vx / current_speed
                    dir_y = projectile.vy / current_speed

                    if dist < self.player.armor_effect["frost"][0]:
                        projectile.speed = projectile.og_speed / 2
                    else:
                        projectile.speed = projectile.og_speed

                    projectile.vx = dir_x * projectile.speed
                    projectile.vy = dir_y * projectile.speed
    
            target = self.target()
            projectile.update([target])
            if getattr(projectile, "edge_bounces", 0):
                projectile.bounce_off_edges()               # (13.11) e.g. Prism's row fired backwards
            if self.left_room(projectile):                  # (11.11) gone out of the room for good: forget it
                self.enemy_projectiles.remove(projectile)
                continue
            wall = None if "throw" in projectile.effects or getattr(projectile, "wall_pass", False) \
                else self.wall_at(projectile.x, projectile.y)
            if wall and getattr(projectile, "wall_bounce", False):
                projectile.bounce_off(wall["rect"])             # (8.11) Frozen Orb's bullets bounce off
            elif wall:
                self.enemy_projectiles.remove(projectile)       # stopped by a wall (thrown bombs fly over)
                continue
            kids = projectile.split_now()               # (7.11) a splitting bullet bursts into smaller ones
            if kids is not None:
                self.slow_bullets(kids)
                self.enemy_projectiles.extend(kids)
                self.enemy_projectiles.remove(projectile)
                continue
            proj_expire, effect = projectile.check_duration()
            if not proj_expire:
                kids = projectile.land_children()       # (7.11) a thrown bomb throws out a ring where it lands
                self.slow_bullets(kids)
                self.enemy_projectiles.extend(kids)
                if "explosion" in effect and "contact_only" not in effect:   # (11.11) small grenades: only on you
                    effect["explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect["explosion"],"player", effects=effect)
                    self.sfx.play("explosion") 
                elif explosion_look(effect):               # nova_ / (12.11) frost_ (Frost Golem's winter blasts)
                    look = explosion_look(effect)
                    effect[look + "explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect[look + "explosion"],"player",type=look, effects=effect)
                    self.sfx.play("explosion") 
                self.enemy_projectiles.remove(projectile)
                continue   # already removed - must not be checked for a hit (double remove crash)

            if target is not self.player and "throw" not in projectile.effects and projectile.check_collision(target):
                if target.take_damage(projectile.damage):  # the plush soaks the shot (no status effects)
                    self.enemy_projectiles.remove(projectile)      # (while it blinks, shots fly through it)
                    self.sfx.play("hit")
                    continue

            owner = getattr(projectile, "friendly_fire", None)
            if owner is not None and self.friendly_fire_hit(projectile, owner):
                continue

            if not getattr(projectile, "grazed", False) and \
                    self.player.width * 1.3 <= math.dist((projectile.x, projectile.y), (self.player.x, self.player.y)) \
                    < self.player.width * SG.CLOSE_CALL_DISTANCE:
                projectile.grazed = True                     # a near miss (counted for the Bullet Time sigil)
                self.near_misses += 1
                # Close Call sigil: it reloads the weapon - (8.11) at most once a second, and only when it helps
                if "close_call" in self.player.sigils and self.player.reload_left() > 0 \
                        and self.timer - getattr(self, "close_call_at", -10 ** 9) >= SG.CLOSE_CALL_COOLDOWN:
                    self.close_call_at = self.timer
                    self.player.reload_now()
                    self.sfx.play("gain_effect")

            player_hit = projectile.deal_damage(self.player)

            if player_hit:

                if player_hit[0] == "static":

                    self.zap([999,1.0,player_hit[1]],self.player, reach=0)

                if player_hit[0] == "explosion":

                    self.explosions.append([player_hit[1][0],(projectile.x,projectile.y),24,None])
                    self.sfx.play("explosion")

                if projectile in self.enemy_projectiles:
                    self.enemy_projectiles.remove(projectile)
                self.sfx.play("player_hit")

        frozen = "headstart" in self.player.sigils and self.timer <= SG.HEADSTART_FRAMES   # Headstart sigil
        for enemy in self.enemies[:]:   # copy: enemies get added/removed inside the loop
            if frozen or (self.void and self.void.freezes_boss and enemy is self.void.boss):
                continue
            target = self.target()
            self.move_enemy(enemy, target)                  # (8.11) with the walls in mind (wall_tactics.py)
            enemy.behind_wall = not TACTICS.sees((enemy.x, enemy.y), (target.x, target.y), getattr(self, "walls", []))
            enemy._walls = getattr(self, "walls", [])          # (8.11) new ice walls keep away from the standing ones
            if self.easy_mode and not enemy.easy:
                enemy.make_easy()                             # (12.11) fewer bullets in its attacks
            pace = DIFF.cooldown_mult(self.difficulty, enemy.type == "boss")
            proj,enemies = enemy.attack(self.timer, self.player, pace, self.enemy_db, aim=target)
            if self.hard_mode and enemy.type == "boss":
                reach_far(proj)
            self.slow_bullets(proj)
            if getattr(enemy, "name", None) in WALL_BOUNCE:
                for p in proj:
                    p.wall_bounce = True                      # (8.11) Frozen Orb: its bullets bounce off walls
            if getattr(enemy, "name", None) in WALL_PASS:
                for p in proj:
                    p.wall_pass = True                        # (8.11) the Generator stands still: its bullets go through
            if "friendly_fire" in self.player.trinket_effect and "confusion" in enemy.effects:
                for p in proj:
                    p.friendly_fire = enemy          # Magic Ring: a confused enemy's shots also hurt the others
            if target is not self.player and self.timer % 10 == 0 and math.dist((enemy.x, enemy.y), (target.x, target.y)) < enemy.width + target.width:
                target.take_damage(enemy.contact_dmg)      # biting the plush
            self.enemy_projectiles.extend(proj)
            enemies = self.within_product_limits(enemies)
            for e in enemies:
                if getattr(e, "belt_entry", False):
                    self.put_on_belt(e)                         # (8.11) a product comes in at the start of a belt
            self.enemies.extend(enemies)
            if enemy.new_nozzles:                           # (8.11) Assembly Line's wall nozzles
                for nozzle in enemy.new_nozzles:
                    self.start_nozzles(nozzle)
                enemy.new_nozzles = []
            if enemy.new_cracks:                            # Frost Golem's ground cracks
                for crack in enemy.new_cracks:
                    self.add_crack(crack)
                enemy.new_cracks = []
            if enemy.new_walls:                             # Frost Golem's ice walls
                self.walls.extend(enemy.new_walls)
                enemy.new_walls = []
                self.sfx.play("explosion")
            self.push_out_of_walls(enemy)
            if enemy.phase_event:                           # a boss changed phase (7.11): a breath, a flash
                enemy.phase_event = False
                self.enemy_projectiles = []
                self.phase_flash = PHASE_FLASH if OPT.get("flashes") else 0     # (11.11) Settings: flashes
                self.phase_changed = True                   # (11.11) Game may pause here (Settings)
                self.sfx.play("boss_phase" if "boss_phase" in self.sfx.sfx else "overclock")
            if enemy.hp <= 0:    
                self.kill_enemy(enemy)
                if enemy.type == "boss":                    # (8.11) its machines and products go with it
                    for other in self.enemies:
                        if getattr(other, "machine", False) or getattr(other, "ride_off", False) or other in enemy.guards \
                                or (getattr(other, "owner", None) is enemy and enemy.name not in HELPERS_STAY):
                            other.remove_me = True
        self.hold_anchored()
        gone = [e for e in self.enemies if getattr(e, "remove_me", False)]
        for e in gone:                                      # taken away quietly (rebuilt machines, products off the belt)
            self.enemies.remove(e)

        # any damage source (bullets, explosions, contact, poison...) is checked here
        if self.song:
            self.song.count_hit(self.player)            # (10.11) a song fight: hits are only counted
        self.check_player_death()

    # enemy collision
        for i, enemy1 in enumerate(self.enemies):
            for enemy2 in self.enemies[i + 1:]:
                dx = enemy2.x - enemy1.x
                dy = enemy2.y - enemy1.y

                distance = math.sqrt(dx**2 + dy**2)
                min_distance = enemy1.width + enemy2.width

                if distance < min_distance:
                    if distance == 0:
                        distance = 0.1
                        dx = random.choice([-1, 1])
                        dy = random.choice([-1, 1])

                    overlap = min_distance - distance

                    move_x = (dx / distance) * overlap * 0.5
                    move_y = (dy / distance) * overlap * 0.5
                    enemy1.x -= move_x
                    enemy1.y -= move_y
                    enemy2.x += move_x
                    enemy2.y += move_y

        for enemy in self.enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y

            distance = math.sqrt(dx**2 + dy**2)
            min_distance = enemy.width + self.player.width*0.66

            if distance < min_distance:
                if distance == 0:
                    distance = 0.1
                    dx = random.choice([-1, 1])
                    dy = random.choice([-1, 1])

                overlap = min_distance - distance

                # Wektor przesunięcia
                move_x = (dx / distance) * overlap
                move_y = (dy / distance) * overlap

                enemy.x += move_x * 0.5
                enemy.y += move_y * 0.5
                self.player.x -= move_x * 0.5
                self.player.y -= move_y * 0.5
           
    # --- boss arenas (7.11): ice walls, snowstorm ----------------------------------------------------------
    def pause(self):
        """(10.11) ESC: the fight stands still (Game stops updating it); the clocks that run on real time wait."""
        self.paused_at = pygame.time.get_ticks()

    def resume(self):
        """Everything timed in real ms goes on from where it was (bullets' range, the song)."""
        waited = pygame.time.get_ticks() - self.paused_at
        for p in self.player_projectiles + self.enemy_projectiles:
            p.shot_time += waited
        self.player.wait(waited)                     # (11.11) the weapon's reload waits too (no pause-shot-pause)
        if self.song:
            self.song.clock.start_ms += waited

    def scripted_end_reached(self):
        """All enemies gone - or, in a scripted fight (song / Milo), the script says it's over."""
        script = self.core or self.void
        if script:
            if script.finished:
                self.skip_end_screen = True
            return script.finished
        return len(self.enemies) == 0 and (self.song is None or self.song.finished)

    def update_core(self):
        """(10.11) Milo's fight: the heart's beat and everything on it (core_fight.py)."""
        if self.core is None:
            return
        hp_before = self.player.hp
        self.core.update(self)
        if self.player.hp < hp_before:
            self.sfx.play("player_hit")                    # hit by a cable / a shock wave (bullets play it themselves)
        for name, volume in self.core.sounds:
            if name in self.sfx.sfx:
                self.sfx.play(name, volume)

    def update_void(self):
        """(11.11) The Void's fight: its script (void_fight.py)."""
        if self.void is None:
            return
        hp_before = self.player.hp
        self.void.update(self, pygame.time.get_ticks())
        if self.player.hp < hp_before:
            self.sfx.play("player_hit")

    def update_song(self):
        """(10.11) A song fight: the song's attacks for this frame (song/fight.py)."""
        if self.song is None:
            return
        hp_before = self.player.hp
        bullets = self.song.update(pygame.time.get_ticks(), self.player, self.enemy_projectiles)
        if self.player.hp < hp_before:
            self.sfx.play("player_hit")                    # hit by a laser / shape (bullets play it themselves)
        self.slow_bullets(bullets)                          # (Bullet Time still works)
        self.enemy_projectiles.extend(bullets)
        for name in self.song.sounds:
            self.sfx.play(f"mascot_{name}", SONG_SFX_VOLUME.get(name, 0.5))
        self.money = self.song.gold                         # the reward goes with the grade

    def hold_anchored(self):
        """(8.11) Anchored enemies (Assembly Line's core and machines) stay where they first stood."""
        for e in self.enemies:
            if getattr(e, "anchored", False):
                if e.anchor is None:
                    e.anchor = (e.x, e.y)
                e.x, e.y = e.anchor

    def draw_darkness(self):
        """(8.11) The dark arena over everything; the boss bar stays readable."""
        if not self.darkness.active:
            return
        boss = next((e for e in self.enemies if e.type == "boss"), None)
        self.darkness.draw(self.screen, self.player, boss, self.player_projectiles + self.enemy_projectiles)
        if boss is not None:
            boss.hp_bar(self.screen)

    def release_fireflies(self):
        """(8.11) Firefly Jar: every few seconds a firefly flies off at the nearest enemy."""
        jar = self.player.trinket_effect.get("fireflies")
        if not jar or not self.enemies or self.timer % jar[0]:
            return
        target = self.nearest_within(self.enemies, (self.player.x, self.player.y), 0)
        self.player_projectiles.append(prjt(self.player.x, self.player.y, target.x, target.y, FIREFLY_SPEED,
                                            self.player.damage * jar[1], "player", 10, 4000,
                                            self.enemy_db.bullet_type_info, ["normal_yellow"],
                                            effects={"homing": [0.35, 0.35]}))

    def move_enemy(self, enemy, target):
        """(8.11) One enemy's step: chasers walk round the walls, shooters keep you in sight, throwers stay in cover
        (wall_tactics.py)."""
        walls = getattr(self, "walls", [])
        plan = TACTICS.plan(enemy, target, walls, self.screen.get_size(), self.timer)
        before = (enemy.x, enemy.y)
        if plan.chase:
            self.walk_straight(enemy, plan.goal)
        else:
            enemy.move(*plan.goal, self.screen)
        if TACTICS.step_breaks_rule(plan, enemy, before, target, walls):
            enemy.x, enemy.y = before

    def walk_straight(self, enemy, goal):
        """The enemy walks at `goal` whatever its own way of moving is (it keeps its speed)."""
        own = enemy.movement_type
        enemy.movement_type = "to_player_normal"
        try:
            enemy.move(*goal, self.screen)
        finally:
            enemy.movement_type = own

    # --- conveyor belts and wall nozzles (8.11, Assembly Line) ------------------------------------------------
    def belt_lanes(self):
        """[(top px, bottom px, dir)] of the belts in this arena now, or []."""
        belts = getattr(self, "arena", {}).get("belts")
        if not belts:
            return []
        h = self.screen.get_height()
        flip = self.belt_flipped(belts)
        return [(top * h, bottom * h, -d if flip else d) for top, bottom, d in belts["lanes"]]

    def belt_flipped(self, belts):
        rev = belts.get("reverse")
        if not rev:
            return False
        if getattr(self, "belt_since", None) is None:
            self.belt_since = self.timer
        return ((self.timer - self.belt_since) // rev[0]) % 2 == 1

    def update_belts(self):
        """The belts carry you, the small enemies (not the boss / its machines) and the enemy bullets."""
        lanes = self.belt_lanes()
        if not lanes:
            self.belt_since = None
            return
        speed = self.arena["belts"]["speed"]
        w = self.screen.get_width()
        def lane_of(y):
            return next((d for top, bottom, d in lanes if top <= y <= bottom), 0)
        d = lane_of(self.player.y)
        if d:
            self.player.x = min(w - self.player.width, max(self.player.width, self.player.x + d * speed))
        for e in self.enemies[:]:
            if e.type == "boss" or getattr(e, "machine", False):
                continue
            d = lane_of(e.y)
            if d:
                e.x = min(w - e.width, max(e.width, e.x + d * speed))
                if getattr(e, "ride_off", False):
                    e.belt_travel = getattr(e, "belt_travel", 0) + speed
                    at_end = e.x <= e.width + 1 if d < 0 else e.x >= w - e.width - 1
                    if at_end and e.belt_travel > 200:
                        e.remove_me = True                  # carried off the far end of the belt
        for p in self.enemy_projectiles:
            d = lane_of(p.y)
            if d:
                p.x += d * speed * BELT_BULLETS
                if hasattr(p, "base_x"):
                    p.base_x += d * speed * BELT_BULLETS

    def within_product_limits(self, spawned):
        """Drops new products over PRODUCT_LIMITS (counting the ones already in the fight)."""
        counts = {}
        for e in self.enemies:
            counts[e.name] = counts.get(e.name, 0) + 1
        kept = []
        for e in spawned:
            limit = PRODUCT_LIMITS.get(getattr(e, "name", None))
            if limit is not None and counts.get(e.name, 0) >= limit:
                continue
            counts[e.name] = counts.get(e.name, 0) + 1
            kept.append(e)
        return kept

    def put_on_belt(self, e):
        lanes = self.belt_lanes()
        if not lanes:
            return
        top, bottom, d = random.choice(lanes)
        if tuple(e.color) == (255, 255, 255):                  # a normal enemy (scrap beetle, robo-bomber): a colour
            e.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        w = self.screen.get_width()
        e.x = e.width + 2 if d > 0 else w - e.width - 2
        e.y = random.uniform(top + e.width, bottom - e.width) if bottom - top > 2 * e.width else (top + bottom) / 2

    def start_nozzles(self, spec):
        """Nozzles at the start of n random belts glow for `warn` frames, then shoot a stream along the belt.
        Vents (spec "vent"): spots in the bottom edge glow, then shoot up."""
        self.nozzles = getattr(self, "nozzles", [])
        if spec.get("rain"):                                # (8.11) rows from the walls: shown first, then fly
            self.nozzles.append({"rain": True, "warn": spec["warn"], "bullets": spec["bullets"]})
            return
        if spec.get("vent"):
            if self.vent_busy(spec.get("pattern")):
                return                                      # (8.11) one ring and one row from below at a time
            w, h = self.screen.get_size()
            for _ in range(spec.get("count", 1)):
                self.nozzles.append({"vent": True, "x": random.uniform(0.12, 0.88) * w, "y": h - 14, "warn": spec["warn"],
                                     "left": spec["bullets"] if spec.get("pattern") == "line" else 1, "next": 0, "spec": spec})
            return
        lanes = self.belt_lanes()
        if not lanes or any(not n.get("vent") for n in self.nozzles):
            return                                      # (8.11) only one belt shoots at a time
        for top, bottom, d in random.sample(lanes, min(spec.get("lanes", 1), len(lanes))):
            self.nozzles.append({"top": top, "bottom": bottom, "dir": d, "warn": spec["warn"], "left": spec["bullets"],
                                 "next": 0, "spec": spec})

    def vent_busy(self, pattern):
        return any(n.get("vent") and n["spec"].get("pattern") == pattern for n in getattr(self, "nozzles", []))

    def thunder(self):
        """(8.11) Night Bloom's lightning: a random thunder sound (if Filip's files are there)."""
        names = [n for n in ("strike1", "strike2") if n in self.sfx.sfx]
        if names:
            self.sfx.play(random.choice(names))

    def draw_rain_warnings(self):
        """(8.11) Where the rows from the walls will come from: blinking marks at the walls (seen in the dark)."""
        if (self.timer // 5) % 2:
            return
        for n in getattr(self, "nozzles", []):
            if n.get("rain") and n["warn"] > 0:
                for b in n["bullets"]:
                    tip = (b.x + b.dir_x * RAIN_MARK, b.y + b.dir_y * RAIN_MARK)
                    pygame.draw.line(self.screen, RAIN_WARNING, (b.x, b.y), tip, 6)

    def update_nozzles(self):
        w = self.screen.get_width()
        for n in getattr(self, "nozzles", [])[:]:
            if n["warn"] > 0:
                n["warn"] -= 1
                continue
            if n.get("rain"):
                self.enemy_projectiles.extend(n["bullets"])
                self.nozzles.remove(n)
                continue
            if n["next"] > 0:
                n["next"] -= 1
                continue
            spec = n["spec"]
            if n.get("vent"):
                x, y = n["x"], n["y"]
                if spec.get("pattern") == "line":               # a row at you
                    a = math.atan2(self.player.y - y, self.player.x - x)
                    angles = [a]
                else:                                          # a half ring, upwards
                    k = spec["bullets"]
                    angles = [math.pi + math.pi * (i + 0.5) / k for i in range(k)]
                for a in angles:
                    self.enemy_projectiles.append(prjt(x, y, x + math.cos(a) * 1000, y + math.sin(a) * 1000, spec["speed"],
                                                       spec["damage"], "enemy", spec["width"], spec["range"],
                                                       self.enemy_db.bullet_type_info, spec["type"],
                                                       effects=spec.get("effects", {})))    # (11.11) e.g. glue
                n["left"] -= 1
                n["next"] = spec.get("every", 4)
                if n["left"] <= 0:
                    self.nozzles.remove(n)
                continue
            x = 4 if n["dir"] > 0 else w - 4
            rows = spec.get("rows", 1)
            for r in range(rows):
                y = n["top"] + (n["bottom"] - n["top"]) * (r + 1) / (rows + 1)
                self.enemy_projectiles.append(prjt(x, y, x + n["dir"] * 1000, y, spec["speed"], spec["damage"], "enemy",
                                                   spec["width"], spec["range"], self.enemy_db.bullet_type_info, spec["type"]))
            n["left"] -= 1
            n["next"] = spec["every"]
            if n["left"] <= 0:
                self.nozzles.remove(n)

    def draw_belts(self):
        lanes = self.belt_lanes()
        if not lanes:
            return
        w = self.screen.get_width()
        belts = self.arena["belts"]
        speed = belts["speed"]
        rev = belts.get("reverse")
        warn = False
        if rev and getattr(self, "belt_since", None) is not None:
            t = (self.timer - self.belt_since) % rev[0]
            warn = t >= rev[0] - rev[1] and (self.timer // 8) % 2 == 0          # about to turn round: arrows blink
        step = 80
        for top, bottom, d in lanes:
            rect = pygame.Rect(0, int(top), w, int(bottom - top))
            pygame.draw.rect(self.screen, BELT_COLOR, rect)
            pygame.draw.line(self.screen, BELT_EDGE, rect.topleft, rect.topright, 6)
            pygame.draw.line(self.screen, BELT_EDGE, rect.bottomleft, rect.bottomright, 6)
            show = -d if warn else d
            off = (self.timer * speed * d) % step
            cy, hh = rect.centery, rect.height * 0.28
            colour = (255, 190, 90) if warn else BELT_ARROW
            for x in range(-step, w + step, step):
                x0 = x + off
                pygame.draw.lines(self.screen, colour, False,
                                  [(x0 - show * 12, cy - hh), (x0 + show * 12, cy), (x0 - show * 12, cy + hh)], 6)
        for n in getattr(self, "nozzles", []):                 # vents in the bottom edge: glow before they shoot
            if n.get("vent"):
                hot = n["warn"] > 0 and (self.timer // 4) % 2 == 0
                pygame.draw.rect(self.screen, NOZZLE_HOT if hot or n["warn"] <= 0 else NOZZLE_COLOR, (n["x"] - 26, n["y"] - 10, 52, 24), 0, 6)
                pygame.draw.rect(self.screen, BELT_EDGE, (n["x"] - 26, n["y"] - 10, 52, 24), 3, 6)
        for top, bottom, d in lanes:                           # the nozzles in the side walls (start of every belt)
            cy = (top + bottom) / 2
            for n_x in (0, w - 26):
                hot = any(not n.get("vent") and n["top"] == top and (n["dir"] > 0) == (n_x == 0) for n in getattr(self, "nozzles", []))
                pygame.draw.rect(self.screen, NOZZLE_HOT if hot and (self.timer // 4) % 2 == 0 else NOZZLE_COLOR,
                                 (n_x, cy - 22, 26, 44), 0, 4)
                pygame.draw.rect(self.screen, BELT_EDGE, (n_x, cy - 22, 26, 44), 3, 4)

    def add_crack(self, crack, sound=True):
        """A ground crack starts (Frost Golem; 10.11 also Milo's heart): {x, y, angle, speed, max, every, start, bullets}."""
        crack.update(length=crack["start"], next=crack["start"] + crack["every"], segs=[], life=CRACK_FADE)
        self.cracks = getattr(self, "cracks", []) + [crack]
        if sound:
            self.sfx.play("explosion")

    def update_cracks(self):
        """Ground cracks grow along the floor and throw out bullets to both sides as they go."""
        for crack in getattr(self, "cracks", [])[:]:
            if crack["length"] < crack["max"]:
                crack["length"] = min(crack["max"], crack["length"] + crack["speed"])
                ca, sa = math.cos(crack["angle"]), math.sin(crack["angle"])
                while crack.get("bullets") and crack["next"] <= crack["length"]:
                    px, py = crack["x"] + ca * crack["next"], crack["y"] + sa * crack["next"]
                    spec = crack["bullets"]
                    for side in (1, -1):
                        a = crack["angle"] + side * math.pi / 2
                        self.enemy_projectiles.append(prjt(px, py, px + math.cos(a) * 1000, py + math.sin(a) * 1000,
                                                           spec["speed"], spec["damage"], "enemy", spec["width"],
                                                           spec["range"], self.enemy_db.bullet_type_info, spec["type"],
                                                           effects=copy.deepcopy(spec.get("effects", {}))))
                    crack["next"] += crack["every"]
                w, h = self.screen.get_size()
                ex, ey = crack["x"] + ca * crack["length"], crack["y"] + sa * crack["length"]
                if not (0 <= ex <= w and 0 <= ey <= h):
                    crack["max"] = crack["length"]               # it runs off the arena: done
            else:
                crack["life"] -= 1
                if crack["life"] <= 0:
                    self.cracks.remove(crack)
                    continue
            if crack.get("damage") and self.crack_touches(crack, self.player):
                hp_before = self.player.hp
                self.player.take_damage(crack["damage"], {})
                if self.player.hp < hp_before:
                    self.sfx.play("player_hit")

    def crack_touches(self, crack, body):
        """(10.11) Milo's cracks hurt to touch while they run and a moment after (then they only fade)."""
        if crack["length"] >= crack["max"] and crack["life"] < CRACK_FADE - CRACK_HURTS_AFTER:
            return False
        ca, sa = math.cos(crack["angle"]), math.sin(crack["angle"])
        along = (body.x - crack["x"]) * ca + (body.y - crack["y"]) * sa
        if not crack["start"] <= along <= crack["length"]:
            return False
        across = abs((body.x - crack["x"]) * sa - (body.y - crack["y"]) * ca)
        return across < CRACK_WIDTH + body.width * 0.6

    def draw_cracks(self):
        """Like a zap, but every piece stays the same in its place (picked once)."""
        segments = self.assets.crack_segments if self.assets else []
        for crack in getattr(self, "cracks", []):
            ca, sa = math.cos(crack["angle"]), math.sin(crack["angle"])
            n = int((crack["length"] - crack["start"]) // 60)
            while len(crack["segs"]) < n:
                crack["segs"].append(random.randrange(len(segments)) if segments else 0)
            alpha = 255 if crack["length"] < crack["max"] else int(255 * crack["life"] / CRACK_FADE)
            for i, k in enumerate(crack["segs"]):
                d = crack["start"] + 30 + i * 60
                x, y = crack["x"] + ca * d, crack["y"] + sa * d
                if segments:
                    img = pygame.transform.rotate(segments[k], -math.degrees(crack["angle"]))
                    img.set_alpha(alpha)
                    self.screen.blit(img, img.get_rect(center=(x, y)))
                else:
                    pygame.draw.line(self.screen, (40, 40, 50), (x - ca * 30, y - sa * 30), (x + ca * 30, y + sa * 30), 3)

    def left_room(self, p):
        """A bullet far outside the room and still flying away (bullets coming in from outside are kept)."""
        w, h = self.screen.get_size()
        return (p.x < -OUT_OF_ROOM and p.vx <= 0) or (p.x > w + OUT_OF_ROOM and p.vx >= 0) \
            or (p.y < -OUT_OF_ROOM and p.vy <= 0) or (p.y > h + OUT_OF_ROOM and p.vy >= 0)

    def wall_at(self, x, y):
        for wall in getattr(self, "walls", []):
            if wall["rect"].collidepoint(x, y):
                return wall
        return None

    def push_out_of_walls(self, body):
        """Keeps a round body (the player, an enemy) out of the ice walls."""
        for wall in getattr(self, "walls", []):
            r = wall["rect"]
            cx, cy = min(max(body.x, r.left), r.right), min(max(body.y, r.top), r.bottom)
            dx, dy = body.x - cx, body.y - cy
            d = math.hypot(dx, dy)
            if d < body.width:
                if d == 0:                                  # the centre is inside: out the nearest side
                    sides = [(body.x - r.left, -1, 0), (r.right - body.x, 1, 0), (body.y - r.top, 0, -1), (r.bottom - body.y, 0, 1)]
                    depth, sx, sy = min(sides)
                    body.x += sx * (depth + body.width)
                    body.y += sy * (depth + body.width)
                else:
                    body.x += dx / d * (body.width - d)
                    body.y += dy / d * (body.width - d)
                if hasattr(body, "slide_x"):
                    body.slide_x = body.slide_y = 0.0

    def draw_ice_wall_sprite(self, wall):
        """The Frost Golem's ice wall as a picture (cracked after half its hits); False = no picture."""
        cracked = wall["max"] and wall["hits"] <= wall["max"] / 2
        name = "ice_wall_cracked" if cracked and FIGHT_SPRITES.object_picture("ice_wall_cracked", (1, 1)) else "ice_wall"
        picture = FIGHT_SPRITES.object_picture(name, wall["rect"].size)
        if picture is None:
            return False
        picture.set_alpha(int(255 * min(1.0, wall["life"] / 40)))     # melts away at the end
        self.screen.blit(picture, wall["rect"].topleft)
        return True

    def draw_walls(self):
        for wall in getattr(self, "walls", []):
            if wall.get("theme"):                          # (8.11) room obstacles in the biome's look
                ROOMS.draw_obstacle(self.screen, wall)
                continue
            r = wall["rect"]
            if self.draw_ice_wall_sprite(wall):            # (13.11) combat/objects/ice_wall(.png / _cracked.png)
                continue
            fade = min(1.0, wall["life"] / 40)
            colour = (int(150 + 60 * (1 - fade)), int(205 + 30 * (1 - fade)), 245)
            pygame.draw.rect(self.screen, colour, r, 0, 6)
            pygame.draw.rect(self.screen, (90, 150, 200), r, 3, 6)
            cracks = min(wall["max"], wall["max"] - wall["hits"])   # more cracks the more you hit it (a shotgun: max)
            for i in range(cracks):
                k = (i + 1) / (wall["max"] + 1)
                if r.w > r.h:
                    x = r.left + r.w * k
                    pygame.draw.line(self.screen, (60, 110, 160), (x, r.top + 4), (x + 8, r.bottom - 4), 2)
                else:
                    y = r.top + r.h * k
                    pygame.draw.line(self.screen, (60, 110, 160), (r.left + 4, y), (r.right - 4, y + 8), 2)

    def draw_blizzard(self):
        on, every = self.arena.get("blizzard", (0, 1))
        t = self.timer % every
        if t >= on:
            return
        k = min(1.0, t / 40, (on - t) / 40)              # the storm comes and goes smoothly
        sw, sh = self.screen.get_size()
        fog = pygame.Surface((sw, sh), pygame.SRCALPHA)
        fog.fill((235, 240, 248, int(250 * k)))
        for r, a in ((BLIZZARD_SIGHT, 170), (BLIZZARD_SIGHT - 45, 90), (BLIZZARD_SIGHT - 90, 0)):   # a soft hole around you
            pygame.draw.circle(fog, (235, 240, 248, int(a * k)), (self.player.x, self.player.y), r)
        self.screen.blit(fog, (0, 0))
        SNOW.draw(self.screen, 255 * k)                   # Filip's falling snow over the storm
        for e in self.enemies:                            # the boss bar stays readable
            if e.type == "boss":
                e.hp_bar(self.screen)

    def flavoured_candy(self, frames):
        """Flavoured Candy (7.11, Shroom Mother's trinket): a random effect for `frames` at the start of the fight -
        half good, half bad (the burn can kill you if you are already hurt)."""
        p = self.player
        good = random.random() < 0.5
        kind = random.choice(FLAVOURS_GOOD if good else FLAVOURS_BAD)
        if kind == "invulnerable":
            p.imm_frames = max(p.imm_frames, INVULN_FLAVOUR)
        elif kind == "regen":
            p.effects["regen"] = [frames, p.max_hp * 0.03]               # +3% max HP a second
        elif kind == "burn":
            p.effects["burn"] = [frames, p.max_hp * 0.015]               # 40 ticks: 60% max HP over 10 s
        elif kind == "confusion":
            p.effects["confusion"] = [frames // 2, 1.0]
        else:
            p.effects[kind] = [frames, FLAVOUR_STRENGTH[kind]]
        self.sfx.play("gain_effect")
        self.flavour_note = [f"Flavoured Candy: {kind}", 150, good]

    def kill_enemy(self, enemy):
        # the ONE place where an enemy dies: sound, death attacks, item drop roll, removal
        if enemy not in self.enemies or getattr(enemy, "undying", False):
            return                                      # (10.11 Milo: his fight script decides when he falls)
        self.sfx.play("enemy_death")
        self.on_death_synergies(enemy)
        dash = enemy.attacks.get("dash")
        if enemy.name == "firefly_queen" and dash and dash.get("is_bursting") and \
                dash["windup"] < dash.get("dash_t", 0) <= dash["windup"] + dash["dash_frames"]:
            self.feats.add("firefly_dash")             # killed in the middle of a dash (Lucky Coin sigil)
        projectiles,enemies_spawn = enemy.attack(self.timer, enemy_db=self.enemy_db)
        self.slow_bullets(projectiles)
        if getattr(enemy, "name", None) in WALL_BOUNCE:
            for p in projectiles:
                p.wall_bounce = True
        if getattr(enemy, "name", None) in WALL_PASS:
            for p in projectiles:
                p.wall_pass = True
        blast = enemy.attacks.get("death_blast")
        if blast:                        # (7.11) a blast that pushes everyone away - comes with the same warning
            blast = {**blast, "damage": blast["damage"] * enemy.damage}
            self.pending_bullets.append([DEATH_ATTACK_DELAY, projectiles, (enemy.x, enemy.y), enemy.width, blast])
        elif projectiles:                # its death attack: a short warning (pulsing ring) first, then the bullets
            self.pending_bullets.append([DEATH_ATTACK_DELAY, projectiles, (enemy.x, enemy.y), enemy.width])
        self.enemies.extend(enemies_spawn)
        self.enemies.remove(enemy)
        drops = [] if getattr(enemy, "no_drops", False) else self.enemy_db.roll_drops(enemy)
        self.loot.extend(drops)
        self.remember_defeated(enemy, drops)

    def remember_defeated(self, enemy, drops):
        """(11.11) For the win screen's table: one row per kind of enemy (how many, its gold, its drops)."""
        name = getattr(enemy, "name", "?")
        row = self.defeated.get(name)
        if row is None:
            title = getattr(enemy, "boss_name", None) or name.replace("_", " ").title()
            row = self.defeated[name] = WIN.Defeated(name, title, tuple(enemy.color[:3]))
        row.count += 1
        row.gold += enemy.money if getattr(enemy, "pays", False) else 0
        row.drops += drops

    # --- the reward (11.11) --------------------------------------------------------------------------------------
    def flawless(self):
        return self.player.hp == self.player.max_hp

    def gold_multiplier(self):
        """Everything the gold is multiplied by: a normal fight's luck, Flawless (not in hard mode), the trinkets,
        Game's (Lucky Coin). A boss: only Game's; (12.11) Milo and the Void: no gold at all."""
        hard = HARD_GOLD if self.hard_mode else 1.0              # (12.11)
        if self.boss in NO_GOLD_BOSSES:
            return 0
        if self.boss:
            return self.gold_mult * hard
        mult = self.money_mult * self.gold_mult * hard
        if not self.hard_mode and self.flawless():
            mult *= FLAWLESS_GOLD
        if "enemy_gold" in self.player.trinket_effect:
            mult *= 1 + self.player.trinket_effect["enemy_gold"][0]
        return mult

    def reward_money(self):
        """The gold you get for this fight (fixed when the win screen came up)."""
        if self.win_screen:
            return self.win_screen.total_gold
        return int(self.money * self.gold_multiplier())

    def start_win_screen(self):
        mult = self.gold_multiplier()
        rows = list(self.defeated.values())
        for row in rows:
            row.gold = int(row.gold * mult)
        self.win_screen = WIN.WinScreen(self.font_win, getattr(self, "floor", None) or (230, 250, 200),
                                        int(self.money * mult), self.flawless(), rows,
                                        list(self.loot), self.item_icon, self.rarity, self.sfx)

    def check_player_death(self):
        # Emergency Protocol (Mecha-King Armor) saves the player once per fight
        if self.player.hp > 0 or self.finished:
            return
        if self.player.emergency_used == 1:
            self.enemy_projectiles = []
            self.sfx.play("emergency")
            self.player.emergency_used = 0
            self.player.effects["speed"] = [180,0.33]
            self.player.hp = self.player.max_hp*0.15
        elif self.void and self.void.catch_death(self, pygame.time.get_ticks()):
            return                                      # (11.11) the Void: a life gone - "Game Over", then the checkpoint
        else:
            self.win = False
            self.finished = True
            self.player_died = True           # (8.11) "Game Over" even if something heals him on the end screen

    def draw(self):

        self.clip_to_camera()
        # (8.11) the floor has the colour of the biome's ground (Game sets `floor`); ice arena: light blue
        floor = getattr(self, "floor", None) or (230, 250, 200)
        if self.song:
            floor = SONG.FLOOR
        if self.void:
            self.void.draw_world(self.screen)               # (11.11) the islands over the abyss (no floor under them)
        elif not FIGHT_SPRITES.draw_floor(self.screen, FIGHT_SPRITES.floor_name(self)):     # (13.11) its picture
            self.screen.fill(floor if not getattr(self, "arena", {}).get("ice") else (214, 236, 248))
        self.draw_belts()
        self.draw_cracks()
        self.draw_walls()
        if self.song:
            self.song.draw_world(self.screen)
        if self.core:
            self.core.draw_world(self.screen, self.core_layer())
        if self.decoy:
            self.decoy.draw(self.screen, self.timer)
        for frames, _, pos, size, *blast in self.pending_bullets:  # warning before a death attack
            pulse = 1 + 0.25 * math.sin(frames * 0.9)
            pygame.draw.circle(self.screen, (255, 60, 60), pos, int((size + 6) * pulse), 3)
        if "frost" in self.player.armor_effect:
            pygame.draw.circle(self.screen, (40, 120, 220), (self.player.x, self.player.y),
                               self.player.armor_effect["frost"][0], FROST_RING_WIDTH)     # (13.11) was 8 px
        if self.player.draw(self.screen):
            self.check_player_death()
        for enemy in self.enemies[:]:
            if getattr(enemy, "hidden", False):             # (11.11) the Void, gone at the very end
                continue
            if enemy.draw(self.screen):
                self.kill_enemy(enemy)
        self.draw_bullets()                                 # (13.11) over the enemies (and you)
        if OPT.get("damage_numbers"):
            self.damage_numbers.draw(self.screen)
        if self.song and OPT.get("flashes"):
            self.song.draw_flash(self.screen)
        if self.void:
            self.void.draw_over(self.screen, self.player, pygame.time.get_ticks())
        self.draw_darkness()
        self.draw_rain_warnings()                           # (over the dark: you always see where rows come from)
        if getattr(self, "arena", {}).get("blizzard") and not (self.finished and not self.win) and OPT.get("weather"):
            self.draw_blizzard()                            # (boss arena) a snowstorm over everything (not on the death screen)
        

        note = getattr(self, "flavour_note", None)           # Flavoured Candy: what it did this time
        if note and note[1] > 0:
            note[1] -= 1
            label = self.font_heavy["small"].render(note[0], True, (40, 140, 60) if note[2] else (170, 40, 40))
            self.screen.blit(label, label.get_rect(midbottom=(self.player.x, self.player.y - self.player.width - 22)))
        for zap_data in self.zapped_enemies[:]:
            if zap_data["duration"] > 0:

                if zap_data["start_enemy"] in self.enemies:
                    start_pos = (zap_data["start_enemy"].x, zap_data["start_enemy"].y)
                    zap_data["last_start_pos"] = start_pos
                else:
                    start_pos = zap_data["last_start_pos"]

                if zap_data["end_enemy"] in self.enemies:
                    end_pos = (zap_data["end_enemy"].x, zap_data["end_enemy"].y)
                    zap_data["last_end_pos"] = end_pos
                else:
                    end_pos = zap_data["last_end_pos"]

                self.ZapEffect(start_pos, end_pos, self.poison_segments if zap_data.get("poison") else None)
                zap_data["duration"] -= 1
                if zap_data["duration"] <= 0:
                    self.zapped_enemies.remove(zap_data)

        self.ExplosionEffect()
        if self.trying_to_run and not self.finished:
            for i in range(12):                             # dashed ring around the player = "trying to run away"
                angle = math.radians(i * 30 + self.timer * 6)
                x = self.player.x + math.cos(angle) * (self.player.width + 14)
                y = self.player.y + math.sin(angle) * (self.player.width + 14)
                pygame.draw.circle(self.screen, (70, 70, 70), (x, y), 4)

        world = self.screen                                 # (8.11) from here on: on the display, not in the room
        if world is not self.view:
            self.draw_view()
        self.screen = self.view
        self.draw_hud()
        self.screen = world
        self.motion_blur.apply(self.view, OPT.blur_strength("fight"))       # (11.11) Settings: motion blur (the display)
        pygame.display.flip()

    def core_layer(self):
        """A see-through picture of the arena's size (Milo's lasers and waves are drawn on it)."""
        if getattr(self, "_core_layer", None) is None or self._core_layer.get_size() != self.screen.get_size():
            self._core_layer = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        return self._core_layer

    def draw_bullets(self):
        for projectile in self.player_projectiles:
            projectile.draw(self.screen)
        for projectile in self.enemy_projectiles:
            if self.void and self.void.pale:
                self.void.draw_bullet_outline(self.screen, projectile)   # (11.11) the Pale World: outlines only
            else:
                projectile.draw(self.screen)

    def draw_hud(self):
        if getattr(self, "phase_flash", 0) > 0:             # boss phase change: a white flash fading out
            self.phase_flash -= 1
            veil = pygame.Surface(self.screen.get_size())
            veil.fill((255, 255, 255))
            veil.set_alpha(int(200 * self.phase_flash / PHASE_FLASH))
            self.screen.blit(veil, (0, 0))

        if self.trying_to_run and not self.finished:
            run_text = self.font_heavy["mid"].render("Running away...", True, (60, 60, 60))
            self.screen.blit(run_text, (self.screen.get_width() / 2 - run_text.get_width() / 2, self.screen.get_height() / 12))
        elif self.boss and not self.finished and pygame.key.get_pressed()[RUN_KEY] and not self.can_run():
            no_run = self.font_heavy["mid"].render("You can't run from a boss!", True, (150, 20, 30))
            self.screen.blit(no_run, (self.screen.get_width() / 2 - no_run.get_width() / 2, self.screen.get_height() / 12))

        if self.song and not self.finished:
            self.song.draw_hud(self.screen, self.font_heavy["small"])
        if self.core:
            self.core.draw_hud(self.screen)
        if self.void:
            if self.void.shows_boss_bar:
                self.void.boss.hp_bar(self.screen)          # (a big arena: the bar on the screen, not in the world)
            self.void.draw_hud(self.screen)
            if self.void.dead:
                self.void.draw_dead(self.screen, self.font_heavy["giant"])
        if self.win and self.song:
            self.song.draw_result(self.screen, self.font_heavy)
        elif (self.win and not self.skip_end_screen) or (self.core and self.core.shows_fake_win):   # (12.11) endings: none
            if self.win_screen is None:
                self.start_win_screen()
            self.win_screen.update()
            self.win_screen.draw(self.screen)

        elif self.finished:

            # died = Game Over; ran away = just "CLICK" to go on
            end_text = self.font_heavy["giant"].render("Game Over" if getattr(self, "player_died", False) else "CLICK", True, (255,255,255))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/2 - end_text.get_height()/2))

    def zap(self, effect, enemy_hit, reach=None):
        """A chain of lightning from enemy_hit: effect = [jumps, share of the damage, damage].
        (8.11 nerf) each jump only to an enemy within `reach` px of the last one (ZAP_REACH; None = anywhere),
        and every jump hits ZAP_FALLOFF x weaker than the one before."""
        reach = ZAP_REACH if reach is None else reach
        jumps, share, damage = effect[0], effect[1], effect[2]
        left = [e for e in self.enemies if e is not enemy_hit]
        source = enemy_hit
        hit = damage * share
        for _ in range(jumps):
            target = self.nearest_within(left, (source.x, source.y), reach)
            if target is None:
                return                                    # nothing close enough: the chain ends
            target.take_damage(hit)
            self.zapped_enemies.append({"start_enemy": source, "end_enemy": target, "duration": 8,
                                        "last_start_pos": (source.x, source.y), "last_end_pos": (target.x, target.y)})
            left.remove(target)
            source = target
            hit *= ZAP_FALLOFF

    @staticmethod
    def nearest_within(candidates, point, reach):
        """The candidate nearest to `point`, if it is within `reach` px (reach 0 or less = any distance)."""
        best = min(candidates, key=lambda e: math.dist(point, (e.x, e.y)), default=None)
        if best is None or (reach > 0 and math.dist(point, (best.x, best.y)) > reach):
            return None
        return best

    def death_blast(self, pos, blast):
        """(7.11) Firefly Queen's death: everything within the radius is pushed away (enemies get no damage);
        the player also takes the damage."""
        r = blast["radius"]
        self.explosions.append([r, pos, 24, "nova_"])
        self.sfx.play("explosion")
        sw, sh = self.screen.get_size()
        for thing in [self.player] + self.enemies:
            d = math.dist(pos, (thing.x, thing.y))
            if d > r + thing.width:
                continue
            if thing is self.player:
                self.player.take_damage(blast["damage"], {})
            ux, uy = ((thing.x - pos[0]) / d, (thing.y - pos[1]) / d) if d > 1 else (1, 0)
            thing.x = min(sw - thing.width, max(thing.width, thing.x + ux * blast["push"]))
            thing.y = min(sh - thing.width, max(thing.width, thing.y + uy * blast["push"]))

    def slow_bullets(self, projectiles):
        """Bullet Time sigil: enemy bullets fly slower."""
        if "bullet_time" not in self.player.sigils:
            return
        for p in projectiles:
            p.speed *= SG.BULLET_TIME_SPEED
            p.og_speed *= SG.BULLET_TIME_SPEED
            p.vx *= SG.BULLET_TIME_SPEED
            p.vy *= SG.BULLET_TIME_SPEED

    # --- trinket synergies (6.11) ------------------------------------------------------------------
    def shoot_thorns(self):
        """Rose: the player got hit - thorns fly out all around (fixed damage)."""
        self.player.thorns_pending = False
        count, dmg = self.player.trinket_effect["thorns"][:2]
        for i in range(count):
            a = math.tau * i / count
            tx, ty = self.player.x + math.cos(a) * 1000, self.player.y + math.sin(a) * 1000
            self.player_projectiles.append(prjt(self.player.x, self.player.y, tx, ty, 12, dmg, "player", 12, 900,
                                                self.player.bullet_type_info, ["flower_pink"], {"pierce": [1]}))

    def friendly_fire_hit(self, projectile, owner):
        """Magic Ring: a confused enemy's bullet hits another enemy (still flies at the player too)."""
        for enemy in self.enemies[:]:
            if enemy is not owner and projectile.check_collision(enemy):
                enemy.take_damage(projectile.damage)
                if projectile in self.enemy_projectiles:
                    self.enemy_projectiles.remove(projectile)
                if enemy.hp <= 0:
                    self.kill_enemy(enemy)
                return True
        return False

    def on_death_synergies(self, enemy):
        """Fire Ring / Toxic Ring: whatever kills a burning / poisoned enemy, it passes on - with a FRESH duration
        (the weapon's full one), so it doesn't run out right away."""
        trinket = self.player.trinket_effect
        if "burn_burst" in trinket and "burn" in enemy.effects:
            # Fire Ring: a burning enemy bursts - everyone around catches fire (weaker burn)
            radius, share = trinket["burn_burst"]
            duration = self.player.weapon_effect.get("burn", [SPREAD_MIN_FRAMES])[0]
            self.explosion((enemy.x, enemy.y), [radius, 0, 0], enemy,
                           effects={"burn": [max(SPREAD_MIN_FRAMES, duration), max(1, enemy.effects["burn"][1] * share)]})
        if "poison_spread" in trinket and "poison" in enemy.effects:
            # Toxic Ring: the poison jumps to the nearest enemies
            radius, count = trinket["poison_spread"][0], (trinket["poison_spread"][1] if len(trinket["poison_spread"]) > 1 else 2)
            duration = self.player.weapon_effect.get("poison", [SPREAD_MIN_FRAMES])[0]
            near = sorted((math.dist((o.x, o.y), (enemy.x, enemy.y)), i) for i, o in enumerate(self.enemies)
                          if o is not enemy and o.hp > 0)
            for dist, i in near[:count]:
                if dist <= radius:
                    other = self.enemies[i]
                    other.effects["poison"] = [max(SPREAD_MIN_FRAMES, int(duration)), enemy.effects["poison"][1]]
                    self.zapped_enemies.append({"start_enemy": enemy, "end_enemy": other, "duration": 8, "poison": True,
                                                "last_start_pos": (enemy.x, enemy.y), "last_end_pos": (other.x, other.y)})

    def explosion(self, pos, exp_effect, enemy_hit, type=None, effects=None, cluster=False):
        # exp_effect -> [width,dmg_mult,dmg]
        # effects -> status effects of the projectile that exploded (applied to everything caught in it)
        effects = effects if effects is not None else {}
        if enemy_hit != "player" and not cluster and exp_effect[1] and "cluster" in self.player.trinket_effect:
            # Atom: the player's explosions throw out smaller ones around them
            count, share = self.player.trinket_effect["cluster"]
            for k in range(count):                       # one after another, a moment later (update() sets them off)
                a, d = random.uniform(0, math.tau), random.uniform(0.6, 1.3) * exp_effect[0]
                self.pending_explosions.append([CLUSTER_DELAY * (k + 1), (pos[0] + math.cos(a) * d, pos[1] + math.sin(a) * d),
                                                [max(10, int(exp_effect[0] * 0.5)), exp_effect[1] * share, exp_effect[2]],
                                                type, effects])

        if enemy_hit != "player":
            e = self.enemies[:]
            if enemy_hit in e:
                e.remove(enemy_hit)
        
        self.explosions.append([exp_effect[0],pos,24,type])
        w = exp_effect[0]
        
        if enemy_hit != "player" and len(e) > 0:
            
            for enemy in e:

                dx = enemy.x - pos[0]
                dy = enemy.y - pos[1]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist <= w + enemy.width*0.5:
                    enemy.take_damage(exp_effect[2]*exp_effect[1],copy.deepcopy(effects))

                    if enemy.hp <= 0:
                        self.kill_enemy(enemy)

        elif enemy_hit == "player":
            dx = self.player.x - pos[0]
            dy = self.player.y - pos[1]
            dist = math.sqrt(dx*dx + dy*dy)

            if dist <= w + self.player.width*0.5:
                self.player.take_damage(exp_effect[2]*exp_effect[1],copy.deepcopy(effects))
            if self.decoy and self.decoy.alive and math.dist(pos, (self.decoy.x, self.decoy.y)) <= w + self.decoy.width*0.5:
                self.decoy.take_damage(exp_effect[2]*exp_effect[1])
                    


    
    def ZapEffect(self, start_pos, end_pos, segments=None):

        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dist = math.sqrt(dx*dx + dy*dy)

        if dist == 0:
            return

        zap_length = 64
        amount = max(1,math.ceil(dist / zap_length))

        angle = math.degrees(math.atan2(-dy, dx))

        for i in range(amount):
            progress = (i + 0.5) / amount

            x = start_pos[0] + dx * progress
            y = start_pos[1] + dy * progress

            zap_img = random.choice(segments or self.segments)
            
            zap_img = pygame.transform.rotate(zap_img, angle)

            rect = zap_img.get_rect(center=(x, y))

            self.screen.blit(zap_img, rect)

    def ExplosionEffect(self): 
        # exp -> [width,pos,time,nova]
        for exp in self.explosions:

            w = exp[0]
            pos = exp[1]

            if exp[2] > 0 and not self.screen.get_clip().inflate(w * 2, w * 2).collidepoint(pos):
                exp[2] -= 1                                 # (11.11) off the camera: it goes on, not drawn
            elif exp[2] > 0:

                stage = math.ceil(exp[2]/4)
                frames = self.explosion_looks.get(exp[3], self.explosion_img)
                img = pygame.transform.scale(frames[6-stage],(w*2,w*2))
                rect = img.get_rect(center=pos)

                if exp[2]>8:

                    pygame.draw.circle(self.screen,(240,170,160),pos,w,w//15)

                self.screen.blit(img, rect)
                exp[2] -= 1

            else:

                self.explosions.remove(exp)
