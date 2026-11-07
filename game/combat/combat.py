import copy
import math
import random

import pygame
from game.combat.decoy import Decoy
from game.combat.projectile import projectile as prjt
from game.inventory import sigils as SG

# RUNNING AWAY: hold R in a normal fight. Every frame there is a chance to escape (no win, no death).
# While holding R the player can't shoot.
RUN_KEY = pygame.K_r
RUN_CHANCE = 0.006            # per frame of holding R (~1.4 s on average)
RUN_CHANCE_HARD_MODE = 0.004  # ~2 s on average
CAN_RUN_FROM_BOSS = False
DEATH_ATTACK_DELAY = 18      # frames (0.3 s) between a death and its death attack (warning ring)
CLUSTER_DELAY = 8           # Atom: frames between its small explosions (0.13 s)
SPREAD_MIN_FRAMES = 180     # Fire / Toxic Ring: a passed-on burn / poison lasts at least 3 s
# Flavoured Candy: what it can do at the start of a fight (good / bad, 50:50)
FLAVOURS_GOOD = ["strength", "speed", "regen", "invulnerable"]
FLAVOURS_BAD = ["burn", "slow", "weakness", "confusion"]
FLAVOUR_STRENGTH = {"strength": 0.3, "speed": 0.25, "slow": 0.3, "weakness": 0.3}
INVULN_FLAVOUR = 180            # frames
PHASE_FLASH = 18              # frames of the white flash when a boss changes phase
FLAWLESS_GOLD = 1.2           # no damage taken in a normal fight: x1.2 gold (not in hard mode)     # bosses are only fought on purpose (you walk into them)


class Combat:

    def __init__(self, screen, player, enemies, enemy_db, hard_mode, sfx=None, boss=None, assets=None):
        self.screen = screen
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
        self.money_boost_applied = False

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
        self.money_mult = random.randint(10,40)*0.05
        self.money_mult_og = self.money_mult

        self.hard_mode = hard_mode
        self.timer = 0

        self.segments = assets.zap_segments
        self.poison_segments = assets.poison_zap_segments
        self.zapped_enemies = []
        self.explosion_img = assets.explosion_img
        self.nova_explosion_img = assets.nova_explosion_img
        self.explosions = []
        self.pending_explosions = []
        self.near_misses = 0          # enemy bullets that flew right past the player (Bullet Time sigil)
        self.feats = set()            # sigil feats done in this fight, e.g. "firefly_dash" (Game.after_fight_sigils)
        self.pending_bullets = []     # death attacks waiting to go off ([frames left, bullets, pos, size])  # Atom: small explosions waiting to go off ([frames left, pos, effect, type, effects])
        self.decoy = None             # Mascot Plush: dropped on the first frame (the enemies are known by then)
        self.decoy_image = getattr(assets, "decoy_img", None)

    def target(self):
        """What the enemies go for: the Mascot Plush while it lives, else the player."""
        return self.decoy if self.decoy and self.decoy.alive else self.player

    def can_run(self):
        return CAN_RUN_FROM_BOSS or not self.boss

    def handle_events(self, events, mouse_btn_pressed):
        self.trying_to_run = self.can_run() and pygame.key.get_pressed()[RUN_KEY]
        if self.trying_to_run:
            return   # no shooting while trying to run

        for event in events:
                
            if event.type == pygame.MOUSEBUTTONDOWN and not self.player.automatic_weapon:
                if event.button == 1:
                    multiple, new_projectile = self.player.shoot()      
                    if new_projectile is not None:
                        self.sfx.play("shoot")
                        if multiple:
                            self.player_projectiles.extend(new_projectile)
                        else:
                            self.player_projectiles.append(new_projectile)

        # automatic weapons while the button is held; a started burst always finishes
        if (mouse_btn_pressed[0] and self.player.automatic_weapon) or self.player.bursting():
            multiple, new_projectile = self.player.shoot()      
            if new_projectile is not None:
                self.sfx.play("shoot")
                if multiple:
                    self.player_projectiles.extend(new_projectile)
                else:
                    self.player_projectiles.append(new_projectile)

    def update(self):
        self.timer += 1
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
        if self.timer == 1 and "flavour" in self.player.trinket_effect:
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
        self.player.move(keys, self.screen)
        if len(self.enemies) > 32:
            # hard cap: newest extra enemies just vanish (no death attacks, so no chain spawning)
            del self.enemies[32:]

        for projectile in self.player_projectiles[:]:
            projectile.update(self.enemies)
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
           
            for enemy in self.enemies:

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
        if len(self.enemies) == 0:
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
                if "explosion" in effect:
                    effect["explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect["explosion"],"player", effects=effect)
                    self.sfx.play("explosion") 
                elif "nova_explosion" in effect:
                    effect["nova_explosion"].append(projectile.damage)
                    self.explosion((projectile.x,projectile.y), effect["nova_explosion"],"player",type="nova_", effects=effect)
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
                if "close_call" in self.player.sigils:       # Close Call sigil: it reloads the weapon
                    self.player.reload_now()
                    self.sfx.play("gain_effect")

            player_hit = projectile.deal_damage(self.player)

            if player_hit:

                if player_hit[0] == "static":

                    self.zap([999,1.0,player_hit[1]],self.player)

                if player_hit[0] == "explosion":

                    self.explosions.append([player_hit[1][0],(projectile.x,projectile.y),24,None])
                    self.sfx.play("explosion")

                if projectile in self.enemy_projectiles:
                    self.enemy_projectiles.remove(projectile)
                self.sfx.play("player_hit")

        frozen = "headstart" in self.player.sigils and self.timer <= SG.HEADSTART_FRAMES   # Headstart sigil
        for enemy in self.enemies[:]:   # copy: enemies get added/removed inside the loop
            if frozen:
                continue
            target = self.target()
            enemy.move(target.x, target.y, self.screen)
            proj,enemies = enemy.attack(self.timer, self.player, self.hard_mode, self.enemy_db, aim=target)
            self.slow_bullets(proj)
            if "friendly_fire" in self.player.trinket_effect and "confusion" in enemy.effects:
                for p in proj:
                    p.friendly_fire = enemy          # Magic Ring: a confused enemy's shots also hurt the others
            if target is not self.player and self.timer % 10 == 0 and math.dist((enemy.x, enemy.y), (target.x, target.y)) < enemy.width + target.width:
                target.take_damage(enemy.contact_dmg)      # biting the plush
            self.enemy_projectiles.extend(proj)
            self.enemies.extend(enemies)
            if enemy.phase_event:                           # a boss changed phase (7.11): a breath, a flash
                enemy.phase_event = False
                self.enemy_projectiles = []
                self.phase_flash = PHASE_FLASH
                self.sfx.play("boss_phase" if "boss_phase" in self.sfx.sfx else "overclock")
            if enemy.hp <= 0:    
                self.kill_enemy(enemy)

        # any damage source (bullets, explosions, contact, poison...) is checked here
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
        if enemy not in self.enemies:
            return
        self.sfx.play("enemy_death")
        self.on_death_synergies(enemy)
        dash = enemy.attacks.get("dash")
        if enemy.name == "firefly_queen" and dash and dash.get("is_bursting") and \
                dash["windup"] < dash.get("dash_t", 0) <= dash["windup"] + dash["dash_frames"]:
            self.feats.add("firefly_dash")             # killed in the middle of a dash (Lucky Coin sigil)
        projectiles,enemies_spawn = enemy.attack(self.timer, enemy_db=self.enemy_db)
        self.slow_bullets(projectiles)
        blast = enemy.attacks.get("death_blast")
        if blast:                        # (7.11) a blast that pushes everyone away - comes with the same warning
            blast = {**blast, "damage": blast["damage"] * enemy.damage}
            self.pending_bullets.append([DEATH_ATTACK_DELAY, projectiles, (enemy.x, enemy.y), enemy.width, blast])
        elif projectiles:                # its death attack: a short warning (pulsing ring) first, then the bullets
            self.pending_bullets.append([DEATH_ATTACK_DELAY, projectiles, (enemy.x, enemy.y), enemy.width])
        self.enemies.extend(enemies_spawn)
        self.enemies.remove(enemy)
        self.loot.extend(self.enemy_db.roll_drops(enemy))

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
        else:
            self.win = False
            self.finished = True

    def draw(self):

        self.screen.fill((230, 250, 200))
        for projectile in self.player_projectiles:
            projectile.draw(self.screen)
        for projectile in self.enemy_projectiles:
            projectile.draw(self.screen)
        if self.decoy:
            self.decoy.draw(self.screen, self.timer)
        for frames, _, pos, size, *blast in self.pending_bullets:  # warning before a death attack
            pulse = 1 + 0.25 * math.sin(frames * 0.9)
            pygame.draw.circle(self.screen, (255, 60, 60), pos, int((size + 6) * pulse), 3)
        if "frost" in self.player.armor_effect:
            pygame.draw.circle(self.screen,(40,120,220),(self.player.x,self.player.y),self.player.armor_effect["frost"][0],8)
        if self.player.draw(self.screen):
            self.check_player_death()
        for enemy in self.enemies[:]:
            if enemy.draw(self.screen):
                self.kill_enemy(enemy)
        

        note = getattr(self, "flavour_note", None)           # Flavoured Candy: what it did this time
        if note and note[1] > 0:
            note[1] -= 1
            label = self.font_heavy["small"].render(note[0], True, (40, 140, 60) if note[2] else (170, 40, 40))
            self.screen.blit(label, label.get_rect(midbottom=(self.player.x, self.player.y - self.player.width - 22)))
        if getattr(self, "phase_flash", 0) > 0:             # boss phase change: a white flash fading out
            self.phase_flash -= 1
            veil = pygame.Surface(self.screen.get_size())
            veil.fill((255, 255, 255))
            veil.set_alpha(int(200 * self.phase_flash / PHASE_FLASH))
            self.screen.blit(veil, (0, 0))
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
            # dashed ring around the player + text = "trying to run away"
            for i in range(12):
                angle = math.radians(i * 30 + self.timer * 6)
                x = self.player.x + math.cos(angle) * (self.player.width + 14)
                y = self.player.y + math.sin(angle) * (self.player.width + 14)
                pygame.draw.circle(self.screen, (70, 70, 70), (x, y), 4)
            run_text = self.font_heavy["mid"].render("Running away...", True, (60, 60, 60))
            self.screen.blit(run_text, (self.screen.get_width() / 2 - run_text.get_width() / 2, self.screen.get_height() / 12))
        elif self.boss and not self.finished and pygame.key.get_pressed()[RUN_KEY] and not self.can_run():
            no_run = self.font_heavy["mid"].render("You can't run from a boss!", True, (150, 20, 30))
            self.screen.blit(no_run, (self.screen.get_width() / 2 - no_run.get_width() / 2, self.screen.get_height() / 12))

        if self.win:

            pygame.draw.rect(self.screen,(200,200,200),(self.screen.get_width()/2 - self.screen.get_width()/12, self.screen.get_height()/3, self.screen.get_width()/6,self.screen.get_height()/2.9),0,10)
            end_title = self.font_heavy["mid"].render("Win!", True, (0,0,0))

            flawless_text = self.font_heavy["mid"].render("Flawless!!", True, (255,255,255))
            is_flawless = self.player.hp == self.player.max_hp
            if not self.money_boost_applied and not self.boss:
                if not self.hard_mode and is_flawless:
                    self.money_mult *= FLAWLESS_GOLD
                if "enemy_gold" in self.player.trinket_effect:
                    self.money_mult *= 1+self.player.trinket_effect["enemy_gold"][0]
                self.money_boost_applied = True
            # just the money you get (bonuses already in it; "Flawless!!" is written under it)
            end_text = self.font_light["mid"].render(f"{int(self.money*self.money_mult if not self.boss else self.money)}$", True, (0,0,0))
  
                
            self.screen.blit(end_title, (self.screen.get_width()/2 - end_title.get_width()/2, self.screen.get_height()/2 - end_title.get_height()*3))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/2 - end_text.get_height()/2))

            if is_flawless:      
                self.screen.blit(flawless_text, (self.screen.get_width()/2 - flawless_text.get_width()/2, self.screen.get_height()/2 + end_text.get_height()*2))

            # dropped items, in the lower part of the win box (under "Flawless!!")
            loot_y = self.screen.get_height()/2 + end_text.get_height()*3.6
            for name in self.loot:
                loot_text = self.font_heavy["small"].render(f"New item: {name}", True, (110,40,130))
                self.screen.blit(loot_text, (self.screen.get_width()/2 - loot_text.get_width()/2, loot_y))
                loot_y += loot_text.get_height()*1.2

            end_text = self.font_heavy["giant"].render("CLICK", True, (255,255,255))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/1.3))

        elif self.finished:

            # died = Game Over; ran away = just "CLICK" to go on
            end_text = self.font_heavy["giant"].render("Game Over" if self.player.hp <= 0 else "CLICK", True, (255,255,255))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/2 - end_text.get_height()/2))

        pygame.display.flip()

    def zap(self, effect, enemy_hit):

        e = self.enemies.copy()

        if len(e) > 1:

            if enemy_hit in e:
                e.remove(enemy_hit)
                next_enemy = enemy_hit
            else:
                next_enemy = None

            last_enemy = enemy_hit
            pos = (enemy_hit.x,enemy_hit.y)

            for i in range(effect[0]):
                if len(e) > 0:
                    dist = 0
                    nearest = 9999
                    for enemy in e:

                        dx = pos[0] - enemy.x
                        dy = pos[1] - enemy.y
                        dist = math.sqrt(dx*dx+dy*dy)
                        if dist < nearest:
                            nearest = dist
                            next_enemy = enemy
                        
                    if next_enemy and next_enemy in self.enemies:
                        self.enemies[self.enemies.index(next_enemy)].take_damage(effect[2]*effect[1])

                    self.zapped_enemies.append({
                        "start_enemy": last_enemy,
                        "end_enemy": next_enemy,
                        "last_start_pos": (last_enemy.x, last_enemy.y),
                        "last_end_pos": (next_enemy.x, next_enemy.y),
                        "duration": 8
                    })

                    last_enemy = next_enemy
                    next_enemy = None
                    e.remove(last_enemy)

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

            if exp[2] > 0:

                stage = math.ceil(exp[2]/4)
                if exp[3]:
                    img = pygame.transform.scale(self.nova_explosion_img[6-stage],(w*2,w*2))
                else:
                    img = pygame.transform.scale(self.explosion_img[6-stage],(w*2,w*2))
                rect = img.get_rect(center=pos)

                if exp[2]>8:

                    pygame.draw.circle(self.screen,(240,170,160),pos,w,w//15)

                self.screen.blit(img, rect)
                exp[2] -= 1

            else:

                self.explosions.remove(exp)
