import pygame, math, random, copy
from game.combat.projectile import projectile as prjt

CONTACT_KNOCKBACK = 45         # px the player is pushed away when an enemy touches them
TELEGRAPH_SPEED = 1.3          # a telegraphed (aimed) shot flies this much faster
AIM_LOCK_SHARE = 0.35          # the last 35% of the aiming time the line doesn't follow you any more
SPIRAL_GAP = 1 / 6             # share of a ring of bullets that is left out (at least 2 bullets)


def spiral_with_gap(items):
    """A ring of bullets with one gap in a random place."""
    n = len(items)
    if n < 6:
        return items
    gap = max(2, round(n * SPIRAL_GAP))
    start = random.randrange(n)
    skip = {(start + k) % n for k in range(gap)}
    return [x for i, x in enumerate(items) if i not in skip]


class Enemy:
    def __init__(self, x, y, hp, width, type, speed, contact_dmg, money, defence, species, movement_type, attacks, sfx, bullet_type_info):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = self.hp
        self.width = width
        self.type = type
        self.bullet_type_info = bullet_type_info
        self.species = species

        self.speed = speed
        self.og_speed = speed
        self.movement_type = movement_type

        self.death_attacks = [1,1]

        self.movement_timer = 0    # for jump movement
        self.random_dx = 0            
        self.random_dy = 0            
        self.zigzag_phase = 0 

        self.is_jumping = False
        self.jump_dx = 0
        self.jump_dy = 0

        self.damage = 1.0
        self.og_damage = self.damage   
        self.contact_dmg = contact_dmg

        self.defence = defence
        self.og_defence = self.defence

        self.rate_of_fire = 1.0
        self.og_rate_of_fire = self.rate_of_fire

        self.attacks = attacks
        self.money = money
        self.color = (255,255,255)
        self.effects = {}   
        self.attack_timer = 0 

        self.sfx = sfx
        self.name = ""   # database key, set by EnemyDB (used for item drops)
        self.aiming = None   # the attack being aimed right now (fast shots with a "telegraph" line)

    def draw(self, screen):
        if self.aiming:                                   # the aiming line of a fast shot
            a = self.aiming.get("aim_angle", 0)
            locked = self.aiming.get("aim_left", 0) <= self.aiming["telegraph"] * AIM_LOCK_SHARE
            end = (self.x + math.cos(a) * 2500, self.y + math.sin(a) * 2500)
            pygame.draw.line(screen, (255, 40, 40) if locked else (255, 130, 130), (self.x, self.y), end, 3 if locked else 1)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.width)
        self.hp_bar(screen)
        die = self.handle_effects()[1]  
        self.draw_effects(screen)
        return die

    def handle_effects(self, check = False):
        effect_del = []
        text = []
        if self.effects:
            for effect_name, effect in self.effects.items():
                if effect_name == "slow":
                    self.speed = self.og_speed * (1-effect[1])
                elif effect_name == "poison" and effect[0] % 60 == 0:
                    self.sfx.play("posion_effect")
                    self.hp -= effect[1]
                elif effect_name == "weakness":
                    self.damage = self.og_damage * (1-effect[1])
                elif effect_name == "glued":
                    self.rate_of_fire = self.og_rate_of_fire * (1-effect[1])
                elif effect_name == "burn" and effect[0] % 15 == 0:
                    self.sfx.play("burn_effect")
                    self.hp -= effect[1]
                elif effect_name == "acid":
                    self.defence = self.og_defence * (1-effect[1])
                elif effect_name == "confusion":
                    text.append("confusion")
                elif effect_name == "binded":
                    text.append("binded")
                

                if not check:
                    if effect[0] != "inf":
                        effect[0] -= 1

                if effect[0] != "inf" and effect[0] <= 0:
                    effect_del.append(effect_name)

            for name in effect_del:
                if name == "slow":
                    self.speed = self.og_speed
                elif name == "weakness":
                    self.damage = self.og_damage
                elif name == "glued":
                    self.rate_of_fire = self.og_rate_of_fire
                elif name == "acid":
                    self.defence = self.og_defence
                self.effects.pop(name)
        return text, self.hp <= 0
                

    def take_damage(self, amount, effects = {}):
        
             

        if effects:
            for effect_name, effect in effects.items():

                if effect_name in ("slow","poison","weakness","glued", "burn", "acid"):
                    self.effects[effect_name] = effect
                elif effect_name in ("binded","confusion"):        
                    rnd = random.random()
                    if rnd < effect[1] *(0.1 if self.type == "boss" else 1):
                        self.effects[effect_name] = effect
                elif effect_name == "dmg_to_undead" and self.species == "undead":
                    amount *= (1+effect[0])
                elif effect_name == "glued_vuln" and "glued" in self.effects:
                    amount *= (1+effect[0])                 # Tape
                elif effect_name == "slow_vuln" and "slow" in self.effects:
                    amount *= (1+effect[0])                 # Ice Mix
                elif effect_name == "bullseye" and self.hp <= self.max_hp*effect[0]:
                    self.hp = 0

        self.hp -= amount * 100 / (100 + max(0, self.defence))     # % defence: def 100 = half damage
        if self.hp < 0:
                    self.hp = 0 
        if effects:
            for effect_name, effect in effects.items():
                if effect_name in ("zap","explosion","pierce","knockback"):
                    return [effect_name, effect]
            
        return [True]


    def move(self, target_x, target_y, screen):
        if self.aiming:
            return                                        # stands still while aiming a fast shot

        confusion = "confusion" in self.handle_effects(True)[0]
        direction_modifier = -1 if confusion else 1
        self.movement_timer += 1
        dx, dy = 0, 0

        if "to_player" in self.movement_type or "away_player" in self.movement_type:
            dx = target_x - self.x
            dy = target_y - self.y
            
            if "away_player" in self.movement_type:
                dx = -dx
                dy = -dy
        elif "random" in self.movement_type:
            if self.movement_timer % 60 == 0 or (self.random_dx == 0 and self.random_dy == 0):
                angle = random.uniform(0, 2 * math.pi)
                self.random_dx = math.cos(angle)
                self.random_dy = math.sin(angle)
            dx = self.random_dx
            dy = self.random_dy

        length = math.sqrt(dx*dx + dy*dy)
        if length != 0:
            dx /= length
            dy /= length
        current_speed = self.speed

        if "distance" in self.movement_type:
            keep_distance = 200 if "to_player" in self.movement_type else 900
            if ((length < keep_distance and "to_player" in self.movement_type) or (length > keep_distance and "away_player" in self.movement_type)) and "random" not in self.movement_type:
                current_speed = 0 

        if "jump" in self.movement_type:
            
            cycle_duration = 100  
            rest_duration = 60   
            jump_duration = cycle_duration - rest_duration  
            cycle = self.movement_timer % cycle_duration
            
            if cycle < rest_duration:
                current_speed = 0
            elif cycle == rest_duration:
                self.jump_dx = dx
                self.jump_dy = dy
            else:
                jump_progress = (cycle - rest_duration) / jump_duration
                smooth_modifier = math.sin(jump_progress * math.pi)
                max_jump_multiplier = 3.5
                current_speed = self.speed * smooth_modifier * max_jump_multiplier

        if self.is_stopped_by_attack():
            current_speed = 0

        if "zigzag" in self.movement_type and length != 0:
            self.zigzag_phase += 0.08

            perpendicular_x = -dy
            perpendicular_y = dx
            
            zigzag_strength = 1.25  
            dx += perpendicular_x * math.sin(self.zigzag_phase) * zigzag_strength
            dy += perpendicular_y * math.sin(self.zigzag_phase) * zigzag_strength
            
            new_len = math.sqrt(dx*dx + dy*dy)
            if new_len != 0:
                dx /= new_len
                dy /= new_len

        self.x += (dx if not "jump" in self.movement_type else self.jump_dx) * current_speed * direction_modifier
        self.y += (dy if not "jump" in self.movement_type else self.jump_dy) * current_speed * direction_modifier

        if self.x < 0 + self.width:
            self.x = 0 + self.width
        if self.x > screen.get_width() - self.width:
            self.x = screen.get_width() - self.width
        if self.y < 0 + self.width:
            self.y = 0 + self.width
        if self.y > screen.get_height() - self.width:
            self.y = screen.get_height() - self.width

    def is_stopped_by_attack(self):
        # true while any attack is in its stop_move wait (before or after the shot)
        return any(attack_info.get("stop_phase") for attack_info in self.attacks.values())

    def attack_ready(self, attack_info, hard_mode, binded):
        """Returns True on the frame the attack should fire.

        stop_move: [frames BEFORE the shot, frames AFTER the shot] - the enemy stands still then.
        Order: cooldown (enemy moves) -> stand `before` frames -> SHOOT -> stand `after` frames -> cooldown starts.
        So the waiting time does NOT count towards the cooldown."""
        if attack_info.get("is_bursting"):
            return True
        cooldown_done = self.attack_timer - attack_info["last_used"] >= (attack_info["cooldown"] *(0.9 if hard_mode else 1.0)) * 60

        stop = attack_info.get("stop_move")
        if not stop:
            return cooldown_done

        phase = attack_info.get("stop_phase")
        if phase == "after":
            if not binded:
                attack_info["stop_timer"] -= 1
            if attack_info["stop_timer"] <= 0:
                attack_info["stop_phase"] = None
                attack_info["last_used"] = self.attack_timer   # cooldown starts only now
            return False

        if phase is None:
            if not cooldown_done:
                return False
            attack_info["stop_phase"] = "before"
            attack_info["stop_timer"] = stop[0]

        # phase "before"
        if not binded:
            attack_info["stop_timer"] -= 1
        if attack_info["stop_timer"] <= 0:
            attack_info["stop_phase"] = "after"
            attack_info["stop_timer"] = stop[1]
            return True
        return False

    def attack(self, timer, player = None, hard_mode = False, enemy_db = None, aim = None):
        # aim = what the shots go for (the player, or the Mascot Plush decoy while it lives); touching hurts only the player
        aim = aim or player

        binded = "binded" in self.handle_effects(True)[0]

        projectiles = []
        enemies = []
        if not binded:
            self.attack_timer +=1*self.rate_of_fire
        
        for attack_name, attack_info in self.attacks.items():
            if attack_name == "death_spiral" and self.hp <= 0 and self.death_attacks[0] == 1:
                self.death_attacks[0] = 0
                bullets = attack_info.get("bullets", 12)
                for i in spiral_with_gap(list(range(bullets))):    # a gap to slip through (6.11)

                    rad = math.radians(i * 360 / bullets)
                    proj_x = self.x + math.cos(rad) * self.width
                    proj_y = self.y + math.sin(rad) * self.width

                    target_x = self.x + math.cos(rad) * 1000
                    target_y = self.y + math.sin(rad) * 1000

                    projectile = prjt(proj_x, proj_y, target_x, target_y, self.attacks["death_spiral"]["speed"],
                                        self.attacks["death_spiral"]["damage"], "enemy",
                                        self.attacks["death_spiral"]["width"], self.attacks["death_spiral"]["range"],
                                        self.bullet_type_info, attack_info["type"], effects=attack_info["effects"])
                    projectiles.append(projectile)
            if attack_name == "death_spawn" and self.hp <= 0 and self.death_attacks[1] == 1:
                self.death_attacks[1] = 0
                for i in range(attack_info["amount"]):
                    enemy = enemy_db.get_enemy(attack_info["enemy_name"])
                    enemy.x = self.x + (-1)**i*20*i
                    enemy.y = self.y + (-1)**i*20*i
                    enemies.append(enemy)
            elif "death" not in attack_name and player and self.attack_ready(attack_info, hard_mode, binded):
                if attack_name == "basic" and attack_info.get("telegraph"):
                    # FAST SHOT (6.11): a red aiming line first (follows you, then locks), then a faster bullet
                    left = attack_info.get("aim_left")
                    if left is None:
                        left = attack_info["telegraph"]
                    left -= 1
                    if left > attack_info["telegraph"] * AIM_LOCK_SHARE:
                        attack_info["aim_angle"] = math.atan2(aim.y - self.y, aim.x - self.x)
                    if left > 0:
                        attack_info["aim_left"] = left
                        self.aiming = attack_info
                        continue
                    attack_info["aim_left"] = None
                    self.aiming = None
                    a = attack_info["aim_angle"]
                    projectiles.append(prjt(self.x, self.y, self.x + math.cos(a) * 1000, self.y + math.sin(a) * 1000,
                                            attack_info["speed"] * TELEGRAPH_SPEED, self.damage*attack_info["damage"], "enemy",
                                            attack_info["width"], attack_info["range"],
                                            self.bullet_type_info, attack_info["type"], effects=attack_info["effects"]))
                    attack_info["last_used"] = self.attack_timer
                elif attack_name == "basic": 
                    projectiles.append(prjt(self.x, self.y, aim.x, aim.y, attack_info["speed"],
                                            self.damage*attack_info["damage"], "enemy", 
                                            attack_info["width"], attack_info["range"], 
                                            self.bullet_type_info, attack_info["type"], effects=attack_info["effects"]))
                    attack_info["last_used"] = self.attack_timer
                elif attack_name == "minigun":
                    if not attack_info["is_bursting"]:
                        attack_info["is_bursting"] = True
                        attack_info["burst_count"] = 0
                        attack_info["last_shot"] = self.attack_timer
                        attack_info["last_used"] = self.attack_timer

                    if attack_info["is_bursting"]:
                        
                        if self.attack_timer - attack_info["last_shot"] >= attack_info["burst_delay"]*60:
                            
                            attack_info["last_shot"] = self.attack_timer
                            attack_info["burst_count"] += 1
                            base_angle = math.atan2(aim.y - self.y, aim.x - self.x)
                            spread = math.radians(attack_info.get("spread", 0))   # degrees
                            random_offset = random.uniform(-spread, spread)
                            angle = base_angle + random_offset
                            vx = math.cos(angle)
                            vy = math.sin(angle)
                            proj_x = self.x + vx * self.width
                            proj_y = self.y + vy * self.width
                            target_x = self.x + vx * 1000
                            target_y = self.y + vy * 1000
                            projectile = prjt(proj_x,proj_y,target_x,target_y,attack_info["speed"],
                                              self.damage*attack_info["damage"],"enemy",
                                              attack_info["width"], attack_info["range"], 
                                              self.bullet_type_info, attack_info["type"], effects=attack_info["effects"])
                            projectiles.append(projectile)
                            if attack_info["burst_count"] >= attack_info["burst_max"]:
                                attack_info["is_bursting"] = False
                                attack_info["burst_count"] = 0
                                attack_info["last_used"] = self.attack_timer
                        
                elif attack_name == "spiral":
                    rnd = random.randint(-5,5)
                    angles = list(range(0+rnd*20, 360+rnd*20, 360//attack_info["bullets"]))
                    for angle in spiral_with_gap(angles):          # a gap to slip through (6.11)
                        rad = math.radians(angle)
                        proj_x = self.x + math.cos(rad) * self.width
                        proj_y = self.y + math.sin(rad) * self.width

                        target_x = self.x + math.cos(rad) * 1000
                        target_y = self.y + math.sin(rad) * 1000

                        projectile = prjt(proj_x, proj_y, target_x, target_y, attack_info["speed"], 
                                          self.damage*attack_info["damage"], "enemy", 
                                          attack_info["width"], attack_info["range"], 
                                          self.bullet_type_info, attack_info["type"],  effects=attack_info["effects"])
                        projectiles.append(projectile)
                    attack_info["last_used"] = self.attack_timer
                elif attack_name == "spawn":
                    for i in range(attack_info["amount"]):
                        enemy = enemy_db.get_enemy(attack_info["enemy_name"])
                        enemy.x = self.x + (-1)**i*20*i
                        enemy.y = self.y + (-1)**i*self.width
                        enemies.append(enemy)
                    attack_info["last_used"] = self.attack_timer
                elif attack_name == "shotgun":

                    shots = attack_info["bullets"]
                    angle = math.atan2(aim.y - self.y, aim.x - self.x)
                    angle += math.radians(-attack_info["recoil"]//2)
                    angle += math.radians(-(attack_info["recoil"]/shots)/2)

                    proj_x = self.x + math.cos(angle) * self.width
                    proj_y = self.y + math.sin(angle) * self.width

                    for i in range(shots):
                        angle += math.radians(attack_info["recoil"]/shots)
                        target_x = self.x + math.cos(angle) * 1000
                        target_y = self.y + math.sin(angle) * 1000
                        projectile = prjt(proj_x,proj_y,target_x,target_y,attack_info["speed"],
                                        self.damage*attack_info["damage"],"enemy",
                                        attack_info["width"], attack_info["range"], 
                                        self.bullet_type_info, attack_info["type"], effects=attack_info["effects"])
                        projectiles.append(projectile)
                    attack_info["last_used"] = self.attack_timer
                elif attack_name == "mine": 
                    projectiles.append(prjt(self.x, self.y, self.x, self.y, 0,
                                            self.damage*attack_info["damage"], "enemy", 
                                            attack_info["width"], attack_info["exp_time"]*1000, 
                                            self.bullet_type_info, attack_info["type"], effects={**copy.deepcopy(attack_info.get("effects", {})), "explosion":[attack_info["radius"],1.0]}))
                    attack_info["last_used"] = self.attack_timer
                elif attack_name == "throw":   
                    angle = random.uniform(0, math.tau)
                    distance = math.sqrt(random.uniform(0, attack_info["recoil"]**2))

                    target_x = aim.x + math.cos(angle) * distance
                    target_y = aim.y + math.sin(angle) * distance
                    projectiles.append(prjt(self.x, self.y, target_x, target_y, 0,
                                            self.damage*attack_info["damage"], "enemy", 
                                            attack_info["width"], attack_info["fly_time"]*1000, 
                                            self.bullet_type_info, attack_info["type"], effects={**copy.deepcopy(attack_info.get("effects", {})), "throw":[1], f"{attack_info['exp_type']}explosion":[attack_info["radius"],1.0]}))
                    attack_info["last_used"] = self.attack_timer

        if player and player.width + self.width > math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2) and timer % 10 == 0 and "dmgless_contact" not in player.trinket_effect:
            hit = player.take_damage(self.contact_dmg, {})      # (Cotton Candy's speed boost: shooter.take_damage)
            if hit:
                self.sfx.play("hit")
                # touching = one hit (then the player's immunity frames) and a push away from the enemy
                d = math.dist((self.x, self.y), (player.x, player.y)) or 1
                player.x += (player.x - self.x) / d * CONTACT_KNOCKBACK
                player.y += (player.y - self.y) / d * CONTACT_KNOCKBACK
                
        return projectiles, enemies

    def hp_bar(self, screen):
        if self.type == "boss":
            bar_width = screen.get_width() // 1.5
            bar_height = screen.get_height() // 30
            fill_width = int(bar_width * (self.hp/self.max_hp))
            pygame.draw.rect(screen, (255, 0, 0), (screen.get_width() // 2 - bar_width // 2, 20, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (screen.get_width() // 2 - bar_width // 2, 20, fill_width, bar_height))

    def draw_effects(self, screen):
        EFFECT_COLORS = {
            "slow":      (50, 110, 205),   # blue
            "weakness":  (190, 190, 190),  # light_gray
            "glued":     (255, 210, 40),   # yellow
            "confusion": (170, 80, 255),   # purple
            "binded":    (130, 80, 40),    # brown
            "acid":      (190, 190, 90),   # green/yellow ish
            "poison":    (70, 200, 80),    # green
            "burn":      (220,120,30),     # red
        }

        for i, effect in enumerate(self.effects.keys()):
            if effect in EFFECT_COLORS:
                radius = self.width + (i+1) * 6
                pygame.draw.circle(screen, EFFECT_COLORS[effect], (int(self.x), int(self.y)), radius, 3)
