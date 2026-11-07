import pygame, math, random, copy
from game.combat.projectile import projectile as prjt

CONTACT_KNOCKBACK = 45         # px the player is pushed away when an enemy touches them
TELEGRAPH_SPEED = 1.3          # a telegraphed (aimed) shot flies this much faster
AIM_LOCK_SHARE = 0.35          # the last 35% of the aiming time the line doesn't follow you any more
PULSE = [45, 15]               # pulsing ring: frames flying out, frames flying back ("3 steps forward, 1 back")
MINE_CREEP = 1.2               # px per frame a mine crawls towards the player (the player runs 8)

# ATTACK TYPES (the key in the enemy's attack dict decides what it does):
#   basic, shotgun, spiral, minigun, mine, throw, spawn, death_spiral, death_spawn  (the old ones)
#   split     {"split": {"after": frames, "bullets", "speed", "damage", "width"[, "start", "type", "effects"]}}
#   pulse     {"bullets", "pulse": [out, back]}  a pulsing ring (smooth; [45, 15] = 3 steps forward, 1 back)
#   wall      {"bullets", "spacing": px, "gap": bullets}  a row across the way to you with a hole
#   sprinkler {"streams", "duration": s, "every": frames, "turn": degrees}  spinning streams (stands still meanwhile)
#   line      {"bullets", "every": frames}  a quick row aimed once - looks like a laser
#   wave      {"bullets", "every", "amp": px, "period": frames[, "double": True]}  a wobbling line (double = DNA)
#   throw + "ring": {...children...}  the bomb throws out a full ring where it lands
#   dash      {"dashes", "windup": frames, "distance": px, "dash_frames", "spiral": {bullets, damage, speed, width, range}}
#   death_blast {"radius", "damage", "push": px}  on death: a blast that pushes everyone away, hurts only the player
# Any attack can also have "repeat": [times, gap in s] - a series (the cooldown starts after the last one).



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
        self.glow = 0        # frames of glowing before a dash (Firefly Queen)
        self.screen_size = None   # set in move() - a dash stays on the screen

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
        self.screen_size = screen.get_size()
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
        # true while any attack is in its stop_move wait (before or after the shot), in a series, or spinning
        return any(info.get("stop_phase") or info.get("rep_left") or (info.get("is_bursting") and ("streams" in info or "dashes" in info))
                   for info in self.attacks.values())

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
                for i in range(bullets):                          # a full ring (7.11: no gap - only "pulse" has one)

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
            elif "death" not in attack_name and player:
                if attack_info.get("rep_left"):
                    # SERIES ("repeat": [times, gap in s]): the next shot of the series once its time comes
                    if self.attack_timer >= attack_info["rep_next"]:
                        new, spawned, done = self.fire(attack_name, attack_info, aim, enemy_db)
                        projectiles += new
                        enemies += spawned
                        if done:
                            attack_info["rep_left"] -= 1
                            attack_info["rep_next"] = self.attack_timer + attack_info["repeat"][1] * 60
                            attack_info["last_used"] = self.attack_timer       # the cooldown starts after the LAST one
                    continue
                if self.attack_ready(attack_info, hard_mode, binded):
                    new, spawned, done = self.fire(attack_name, attack_info, aim, enemy_db)
                    projectiles += new
                    enemies += spawned
                    if done and attack_info.get("repeat", [1])[0] > 1:
                        attack_info["rep_left"] = attack_info["repeat"][0] - 1
                        attack_info["rep_next"] = self.attack_timer + attack_info["repeat"][1] * 60

        if player and player.width + self.width > math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2) and timer % 10 == 0 and "dmgless_contact" not in player.trinket_effect:
            hit = player.take_damage(self.contact_dmg, {})      # (Cotton Candy's speed boost: shooter.take_damage)
            if hit:
                self.sfx.play("hit")
                # touching = one hit (then the player's immunity frames) and a push away from the enemy
                d = math.dist((self.x, self.y), (player.x, player.y)) or 1
                player.x += (player.x - self.x) / d * CONTACT_KNOCKBACK
                player.y += (player.y - self.y) / d * CONTACT_KNOCKBACK
                
        return projectiles, enemies


    # --- one attack going off ------------------------------------------------------------------------------
    def shot(self, angle, info, x=None, y=None, speed=None, effects=None):
        """One bullet of an attack, flying at `angle` (radians) from the enemy's edge (or from x, y)."""
        if x is None:
            x, y = self.x + math.cos(angle) * self.width, self.y + math.sin(angle) * self.width
        return prjt(x, y, x + math.cos(angle) * 1000, y + math.sin(angle) * 1000, speed or info["speed"],
                    self.damage * info["damage"], "enemy", info["width"], info["range"],
                    self.bullet_type_info, info["type"], effects=info.get("effects", {}) if effects is None else effects)

    def children(self, info, key):
        """The spec of the smaller bullets a bullet bursts into (split / a thrown bomb's ring)."""
        c = info[key]
        effects = {k: v for k, v in info.get("effects", {}).items() if k != "homing"} if c.get("effects") is None else c["effects"]
        return {"bullets": c["bullets"], "speed": c["speed"], "damage": self.damage * c["damage"], "width": c["width"],
                "range": c.get("range", info.get("range", 3000)), "type": c.get("type", info["type"]),
                "effects": effects, "start": c.get("start", 0)}

    def fire(self, name, info, aim, enemy_db):
        """Fires one attack. Returns (bullets, spawned enemies, done) - done = False while it is still going
        (aiming a fast shot, or a burst / spin / line that lasts a few frames)."""
        projectiles, enemies = [], []
        aim_angle = math.atan2(aim.y - self.y, aim.x - self.x)

        if name == "basic" and info.get("telegraph"):
            # FAST SHOT (6.11): a red aiming line first (follows you, then locks), then a faster bullet
            left = info.get("aim_left")
            if left is None:
                left = info["telegraph"]
            left -= 1
            if left > info["telegraph"] * AIM_LOCK_SHARE:
                info["aim_angle"] = aim_angle
            if left > 0:
                info["aim_left"] = left
                self.aiming = info
                return [], [], False
            info["aim_left"] = None
            self.aiming = None
            projectiles.append(self.shot(info["aim_angle"], info, self.x, self.y, info["speed"] * TELEGRAPH_SPEED))
            info["last_used"] = self.attack_timer

        elif name == "basic":
            projectiles.append(prjt(self.x, self.y, aim.x, aim.y, info["speed"],
                                    self.damage*info["damage"], "enemy",
                                    info["width"], info["range"],
                                    self.bullet_type_info, info["type"], effects=info["effects"]))
            info["last_used"] = self.attack_timer

        elif name == "split":
            # SPLIT (7.11): one bullet (may home a bit) that bursts into a ring of smaller ones after "after" frames
            p = self.shot(aim_angle, info)
            p.motion = {"kind": "split", "after": info["split"]["after"], "children": self.children(info, "split")}
            projectiles.append(p)
            info["last_used"] = self.attack_timer

        elif name == "pulse":
            # PULSING RING (7.11): a full ring that goes "3 steps forward, 1 back" (smoothly)
            n = info["bullets"]
            start = random.uniform(0, math.tau)
            for i in range(n):                                 # a full ring (no gap - 7.11)
                p = self.shot(start + i * math.tau / n, info)
                p.motion = {"kind": "pulse", "pulse": info.get("pulse", PULSE)}
                projectiles.append(p)
            info["last_used"] = self.attack_timer

        elif name == "wall":
            # WALL (7.11): a row of bullets across the way to the target, with one gap to step into
            n, spacing, gap = info["bullets"], info["spacing"], info.get("gap", 3)
            hole = random.randint(1, max(1, n - gap - 1))
            px, py = -math.sin(aim_angle), math.cos(aim_angle)
            bx, by = self.x + math.cos(aim_angle) * self.width, self.y + math.sin(aim_angle) * self.width
            for i in range(n):
                if hole <= i < hole + gap:
                    continue
                off = (i - (n - 1) / 2) * spacing
                projectiles.append(self.shot(aim_angle, info, bx + px * off, by + py * off))
            info["last_used"] = self.attack_timer

        elif name in ("sprinkler", "line", "wave"):
            # attacks that last a few frames: SPRINKLER (spinning streams), LINE (a quick row of bullets that looks
            # like a laser, aimed once), WAVE (like a line, but the bullets wobble - "double": two mirrored = DNA)
            if not info.get("is_bursting"):
                info["is_bursting"] = True
                info["burst_t"] = 0
                info["burst_angle"] = random.uniform(0, math.tau) if name == "sprinkler" else aim_angle
                info["burst_dir"] = random.choice((-1, 1))
            t = info["burst_t"]
            if t % info["every"] == 0:
                a = info["burst_angle"]
                if name == "sprinkler":
                    streams = info["streams"]
                    projectiles += [self.shot(a + k * math.tau / streams, info) for k in range(streams)]
                    info["burst_angle"] += math.radians(info["turn"]) * info["burst_dir"]
                elif name == "line":
                    projectiles.append(self.shot(a, info))
                else:
                    for sign in ((1, -1) if info.get("double") else (1,)):
                        p = self.shot(a, info)
                        p.motion = {"kind": "wave", "amp": info["amp"], "period": info["period"], "sign": sign}
                        projectiles.append(p)
            info["burst_t"] = t + 1
            length = info["duration"] * 60 if name == "sprinkler" else info["every"] * (info["bullets"] - 1) + 1
            if info["burst_t"] < length:
                return projectiles, enemies, False
            info["is_bursting"] = False
            info["last_used"] = self.attack_timer

        elif name == "dash":
            # SUN DASH (7.11, Firefly Queen - like the sun in ETG): "dashes" times: glow and aim ("windup" frames),
            # then a straight dash ("distance" px in "dash_frames"); after the last one a full "spiral" ring
            if not info.get("is_bursting"):
                info["is_bursting"] = True
                info["dash_left"] = info["dashes"]
                info["dash_t"] = 0
            t = info["dash_t"]
            info["dash_t"] = t + 1
            if t < info["windup"]:
                self.glow = info["windup"] - t                   # standing and glowing
                info["dash_angle"] = aim_angle
                return projectiles, enemies, False
            if t < info["windup"] + info["dash_frames"]:
                self.glow = 0
                step = info["distance"] / info["dash_frames"]
                self.x += math.cos(info["dash_angle"]) * step
                self.y += math.sin(info["dash_angle"]) * step
                if self.screen_size:
                    self.x = min(self.screen_size[0] - self.width, max(self.width, self.x))
                    self.y = min(self.screen_size[1] - self.width, max(self.width, self.y))
                return projectiles, enemies, False
            info["dash_left"] -= 1
            info["dash_t"] = 0
            if info["dash_left"] > 0:
                return projectiles, enemies, False
            sp = info["spiral"]
            start = random.uniform(0, math.tau)
            for i in range(sp["bullets"]):
                projectiles.append(self.shot(start + i * math.tau / sp["bullets"], {**sp, "type": sp.get("type", info["type"])}))
            info["is_bursting"] = False
            info["last_used"] = self.attack_timer

        elif name == "minigun":
            if not info["is_bursting"]:
                info["is_bursting"] = True
                info["burst_count"] = 0
                info["last_shot"] = self.attack_timer
                info["last_used"] = self.attack_timer
            if self.attack_timer - info["last_shot"] >= info["burst_delay"]*60:
                info["last_shot"] = self.attack_timer
                info["burst_count"] += 1
                spread = math.radians(info.get("spread", 0))   # degrees
                projectiles.append(self.shot(aim_angle + random.uniform(-spread, spread), info))
                if info["burst_count"] >= info["burst_max"]:
                    info["is_bursting"] = False
                    info["burst_count"] = 0
                    info["last_used"] = self.attack_timer
                    return projectiles, enemies, True
            return projectiles, enemies, False

        elif name == "spiral":
            rnd = random.randint(-5,5)
            angles = list(range(0+rnd*20, 360+rnd*20, 360//info["bullets"]))
            for angle in angles:                           # a full ring (7.11: no gap - only "pulse" has one)
                projectiles.append(self.shot(math.radians(angle), info))
            info["last_used"] = self.attack_timer

        elif name == "spawn":
            for i in range(info["amount"]):
                enemy = enemy_db.get_enemy(info["enemy_name"])
                enemy.x = self.x + (-1)**i*20*i
                enemy.y = self.y + (-1)**i*self.width
                enemies.append(enemy)
            info["last_used"] = self.attack_timer

        elif name == "shotgun":
            shots = info["bullets"]
            angle = aim_angle
            angle += math.radians(-info["recoil"]//2)
            angle += math.radians(-(info["recoil"]/shots)/2)
            proj_x = self.x + math.cos(angle) * self.width
            proj_y = self.y + math.sin(angle) * self.width
            for i in range(shots):
                angle += math.radians(info["recoil"]/shots)
                projectiles.append(self.shot(angle, info, proj_x, proj_y))
            info["last_used"] = self.attack_timer

        elif name == "mine":
            p = prjt(self.x, self.y, self.x, self.y, 0,
                     self.damage*info["damage"], "enemy",
                     info["width"], info["exp_time"]*1000,
                     self.bullet_type_info, info["type"], effects={**copy.deepcopy(info.get("effects", {})), "explosion":[info["radius"],1.0]})
            p.motion = {"kind": "creep", "speed": info.get("creep", MINE_CREEP)}     # mines crawl towards you (7.11)
            projectiles.append(p)
            info["last_used"] = self.attack_timer

        elif name == "throw":
            angle = random.uniform(0, math.tau)
            distance = math.sqrt(random.uniform(0, info["recoil"]**2))
            target_x = aim.x + math.cos(angle) * distance
            target_y = aim.y + math.sin(angle) * distance
            p = prjt(self.x, self.y, target_x, target_y, 0,
                     self.damage*info["damage"], "enemy",
                     info["width"], info["fly_time"]*1000,
                     self.bullet_type_info, info["type"], effects={**copy.deepcopy(info.get("effects", {})), "throw":[1], f"{info['exp_type']}explosion":[info["radius"],1.0]})
            if "ring" in info:                       # (7.11) where it lands: a full ring of bullets
                p.motion = {"kind": "land_ring", "children": self.children(info, "ring")}
            projectiles.append(p)
            info["last_used"] = self.attack_timer

        return projectiles, enemies, True

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
