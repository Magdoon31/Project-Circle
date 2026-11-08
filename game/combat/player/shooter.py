import pygame, math, random, copy
from game.combat.projectile import projectile as prjt
from game.inventory import sigils as SG

IMM_AFTER_HIT = 30                 # frames you can't be hurt after a hit (0.5 s; Magic Dust: 80)
# How fast you speed up / slow down (share of the speed per frame). The slide distance goes with (1 - k) / k.
COMBAT_GRIP = (0.5, 0.25)          # (8.11) a light slide: 1/3 of the map's (map: ACCELERATION 0.25, FRICTION 0.1)
ICE_GRIP = (0.083, 0.055)          # ice floor (a boss arena): 1.1x the old ice slide (was 0.09, 0.06)
INFINITE_FRAMES = 60 * 60 * 60     # "never wears off" in a fight (1 hour) - Toxic Gas

class Shooter :
    def __init__(self, x, y, active_items, sfx, bullet_type_info, sigils=()):
        self.sigils = set(sigils)          # ids of the active sigils (game/inventory/sigils.py)
        self.x = x
        self.y = y
        self.width = 25
        self.hp = 50 + (active_items["armor"].bonus_hp if active_items["armor"] else 0)
        self.max_hp = self.hp
        self.defence = (active_items["armor"].defense if active_items["armor"] else 0)
        self.og_defence = self.defence
        self.speed = 8
        self.og_speed = self.speed
        self.ice = False                   # slippery floor (set by Combat from the boss arena)
        self.slide_x = self.slide_y = 0.0  # your sliding speed (a little everywhere, a lot on ice)
        self.rate_of_fire = (active_items["weapon"].rate_of_fire if active_items["weapon"] else 99999)

        self.og_rate_of_fire = self.rate_of_fire
        self.last_shot_time = 0
        self.damage = (active_items["weapon"].damage if active_items["weapon"] else 0)
        self.dmg_mult = [1.0,1.0]
        self.og_damage = self.damage
        self.type = "player"


        self.range = (active_items["weapon"].range//active_items["weapon"].bullet_speed if active_items["weapon"] else 0)
        self.bullet_size = (active_items["weapon"].bullet_size if active_items["weapon"] else 0)
        self.bullet_speed = (active_items["weapon"].bullet_speed if active_items["weapon"] else 0)
        self.bullet_type_info = bullet_type_info
        self.bullet_type = (active_items["weapon"].bullet_type if active_items["weapon"] else ["normal_red"])

        self.automatic_weapon = (active_items["weapon"].automatic if active_items["weapon"] else False)
        self.recoil = (active_items["weapon"].recoil if active_items["weapon"] else 0)

        # deepcopy: buffs below modify these dicts, and must not leak into the item itself
        self.weapon_effect = copy.deepcopy(active_items["weapon"].effect) if active_items["weapon"] else {}
        self.armor_effect = copy.deepcopy(active_items["armor"].effect) if active_items["armor"] else {}
        self.trinket_effect = {}
        for trinket in (active_items.get("trinket2"), active_items["trinket"]):   # 2nd slot: Spare Pocket sigil
            if trinket:
                self.trinket_effect.update(copy.deepcopy(trinket.effect))      # (same effect twice: the 1st slot's)

        self.bind_chance = 1.0
        self.confusion_chance = 1.0
        self.debuff_time = 1.0
        self.buff_time = 1.0
        self.imm_frames = 10
        self.nodmg_time = 0
        self.regen_timer = 0
        self.overclock_timer = 120
        self.rnd_buff_timer = 120
        self.emergency_used = 1 if "emergency" in self.armor_effect else 0

        self.effects = {}
        self.sfx = sfx

        for effect_name, effect in self.armor_effect.items():

            if effect_name in ("speed","strength","slow"):
                self.add_passive_effect(effect_name, effect)


            elif effect_name in ("poison_up","slow_up","explosion_up","zap_up") and effect_name[:-3] in self.weapon_effect:
                self.weapon_effect[effect_name[:-3]][0] += effect[0]
                self.weapon_effect[effect_name[:-3]][1] += effect[1]
            

            elif effect_name == "ghost_up" and "pierce" in self.weapon_effect and "weakness" in self.weapon_effect and "glued" in self.weapon_effect:

                self.weapon_effect["pierce"][0] += effect[0]
                self.weapon_effect["weakness"][1] += effect[1]
                self.weapon_effect["glued"][1] += effect[1]
            
            elif effect_name == "hitbox":
                self.width *= effect[0]

            elif effect_name == "bullseye":
                self.weapon_effect["bullseye"] = effect

            elif effect_name == "confusion_chance":
                self.confusion_chance *= effect[0]
            elif effect_name in ("bind_chance", "binded_chance"):
                self.bind_chance *= effect[0]


        for effect_name, effect in self.trinket_effect.items():
            if effect_name in ("speed","strength","slow"):
                self.add_passive_effect(effect_name, effect)

            elif effect_name == "recoil":

                self.recoil += effect[0]

            elif effect_name in ("poison_up","slow_up","explosion_up","zap_up") and effect_name[:-3] in self.weapon_effect:

                self.weapon_effect[effect_name[:-3]][0] += effect[0]
                self.weapon_effect[effect_name[:-3]][1] += effect[1]
            

            elif effect_name == "ghost_up" and "pierce" in self.weapon_effect and "weakness" in self.weapon_effect and "glued" in self.weapon_effect:

                self.weapon_effect["pierce"][0] += effect[0]
                self.weapon_effect["weakness"][1] += effect[1]
                self.weapon_effect["glued"][1] += effect[1]

            elif effect_name == "toxic_gas":
                # Toxic Gas: the weapon's poison never wears off (+dmg); no poison -> a small one
                bonus, small_time, small_dmg = effect
                if "poison" in self.weapon_effect:
                    self.weapon_effect["poison"][0] = INFINITE_FRAMES
                    self.weapon_effect["poison"][1] += bonus
                else:
                    self.weapon_effect["poison"] = [small_time, small_dmg]

            elif effect_name == "slow_on_glue" and "glued" in self.weapon_effect:
                # glued enemies also get slowed: same duration as glue, effect[0] = -speed%
                glue_time = self.weapon_effect["glued"][0]
                if "slow" in self.weapon_effect:
                    self.weapon_effect["slow"][0] = max(self.weapon_effect["slow"][0], glue_time)
                    self.weapon_effect["slow"][1] += effect[0]
                else:
                    self.weapon_effect["slow"] = [glue_time, effect[0]]
            
            elif effect_name == "debuff_time":
                self.debuff_time = effect[0]
            elif effect_name == "buff_time":
                self.buff_time = effect[0]

            elif effect_name == "rnd_dmg":

                self.dmg_mult = [1-effect[0],1+effect[1]]

            elif effect_name == "dmg_to_undead":
                self.weapon_effect[effect_name] = effect

            elif effect_name == "hitbox":
                self.width *= effect[0]

            elif effect_name == "confusion_chance":
                self.confusion_chance *= effect[0]
            elif effect_name in ("bind_chance", "binded_chance"):
                self.bind_chance *= effect[0]

            # --- trinket synergies (6.11) ---
            elif effect_name == "homing_light" and "homing" not in self.weapon_effect:
                self.weapon_effect["homing"] = list(effect)        # Holy Orb: [turn speed, turn speed at undead]
            elif effect_name == "shotgun_up" and "shotgun" in self.weapon_effect:
                self.weapon_effect["shotgun"][1] += effect[0]       # Martini: +1 pellet
            elif effect_name == "glued_vuln" and "glued" in self.weapon_effect:
                self.weapon_effect["glued_vuln"] = list(effect)     # Tape: glued enemies take +10% dmg
            elif effect_name == "slow_vuln":
                self.weapon_effect["slow_vuln"] = list(effect)      # Ice Mix: slowed enemies take more dmg
            elif effect_name == "electric_up" and "zap" in self.weapon_effect:
                self.og_damage *= 1 + effect[0]                     # Power Bank: electric weapons hit harder
                self.damage = self.og_damage

        # --- sigils ---
        if "steady_hands" in self.sigils:
            self.recoil = 0
        if "overflow" in self.sigils and "shotgun" in self.weapon_effect:
            self.weapon_effect["shotgun"][1] += 1
        if "vigor" in self.sigils:
            self.hp = self.max_hp = self.max_hp * SG.VIGOR_HP
        if "might" in self.sigils:
            self.og_damage *= SG.MIGHT_DMG
            self.damage = self.og_damage
        if "swift" in self.sigils:
            self.speed *= SG.SWIFT_SPEED
            self.og_speed = self.speed

        self.leftover_dmg_hurted_dmg = 0
        self.thorns_pending = False                 # Rose: Combat shoots the thorns when this is True
        # D20: every N s the next shot is doubled (two bullets side by side)
        self.double_every = self.trinket_effect["double_shot"][0] * 1000 if "double_shot" in self.trinket_effect else None
        self.last_double = -10 ** 9
        # burst weapons (weapon effect "burst": [shots, seconds between them]) - same DPS as without bursts
        self.burst_left = 0
        self.burst_start = -10 ** 9

    def add_passive_effect(self, effect_name, effect):
        # stacks armor + trinket passives ("inf" duration stays "inf")
        effect = list(effect)
        if effect_name in self.effects:
            current = self.effects[effect_name]
            if current[0] != "inf" and effect[0] != "inf":
                current[0] += effect[0]
            else:
                current[0] = "inf"
            current[1] += effect[1]
        else:
            self.effects[effect_name] = effect

        

    def draw_effects(self, screen):
        EFFECT_COLORS = {
            "slow":         (50, 110, 205),   # blue
            "weakness":     (190, 190, 190),  # light_gray
            "glued":        (255, 210, 40),   # yellow
            "confusion":    (170, 80, 255),   # purple
            "binded":       (130, 80, 40),    # brown
            "acid":         (190, 190, 90),   # green/yellow ish
            "poison":       (70, 200, 80),    # green
            "burn":         (220,120,30),     # red/orange
            "speed":        (90, 170, 255),   # cyan
            "strength":     (245, 50, 20),    # red  
            "boost":        (225, 190, 60),   # darker yellow
            "focus":        (255, 255, 255)   # white
        }

        for i, effect in enumerate(self.effects.keys()):
            if effect in EFFECT_COLORS:
                radius = self.width + (i+1) * 6
                pygame.draw.circle(screen, EFFECT_COLORS[effect], (int(self.x), int(self.y)), radius, 3)


    def draw(self, screen):
        if self.imm_frames > 0:
            if (self.imm_frames//5)%2 == 0:
                pygame.draw.circle(screen, (200, 50, 50), (self.x, self.y), self.width)
        else:
            pygame.draw.circle(screen, (200, 50, 50), (self.x, self.y), self.width)
        self.draw_effects(screen)
        self.hp_bar(screen)
        die = self.handle_effects()[1]
        self.imm_frames -= 1
        self.nodmg_time +=1
        self.regen_timer +=1
        self.overclock_timer +=1
        self.rnd_buff_timer +=1
        if self.regen_timer > 60:
            self.regen_timer = 60
        if self.imm_frames < 0:
            self.imm_frames = 0
        return die

    def take_damage(self, amount, effects):
        if self.imm_frames <= 0:
            self.imm_frames = IMM_AFTER_HIT                 # (also after a dodge)
            hurted_dmg_info = [1]
            last_health = self.hp
            if ("dodge" in self.armor_effect and random.random() > self.armor_effect["dodge"][0]) or "dodge" not in self.armor_effect:

                self.nodmg_time = 0
                self.imm_frames = IMM_AFTER_HIT if "imm_frames" not in self.trinket_effect else self.trinket_effect["imm_frames"][0]

                if "close_call" in self.sigils:            # (8.11) Close Call's price: enemies hurt you more
                    amount *= SG.CLOSE_CALL_HURT
                amount = max(amount-self.defence, 1)
                if "guard" in self.armor_effect and self.hp >= self.max_hp * self.armor_effect["guard"][0]:
                    amount *= 1-self.armor_effect["guard"][1]

                if amount < 1:
                    amount = 1
                self.hp -= amount
                if "thorns" in self.trinket_effect:
                    self.thorns_pending = True              # Rose
                if "speed_on_hit" in self.trinket_effect:   # Cotton Candy: any hit makes you faster for a moment
                    self.effects["speed"] = [int(120 * self.buff_time), self.trinket_effect["speed_on_hit"][0]]

                if self.hp < 0:
                    self.hp = 0
                if effects:
                    for effect_name, effect in effects.items():             
                        if effect_name in ("slow", "poison", "weakness", "glued", "burn", "acid", "speed", "strength", "boost"):

                            if not ((f"{effect_name}_imm" in self.armor_effect) or (f"{effect_name}_imm" in self.trinket_effect)):
                                self.effects[effect_name] = []

                                if f"less_{effect_name}" in self.trinket_effect: 
                                    for i, stat in enumerate(effect):
                                        self.effects[effect_name].append(max(0,stat - self.trinket_effect[f"less_{effect_name}"][i]))
                                elif f"less_{effect_name}" in self.armor_effect:
                                    for i, stat in enumerate(effect):
                                        self.effects[effect_name].append(max(0,stat - self.armor_effect[f"less_{effect_name}"][i]))
                                else:
                                    self.effects[effect_name] = effect

                            if effect_name in self.effects and self.effects[effect_name][0] != "inf":
                                # int(): poison/burn tick on "time % 60 == 0", so time must stay an integer
                                if effect_name in ("slow","poison","weakness","glued", "burn", "acid"):
                                    self.effects[effect_name][0] = int(self.effects[effect_name][0] * self.debuff_time)
                                elif effect_name in ("speed","strength","boost"):
                                    self.effects[effect_name][0] = int(self.effects[effect_name][0] * self.buff_time)
                        elif effect_name in ("binded","confusion"):
                            rnd = random.random()
                            if rnd < effect[1]*(self.bind_chance if effect_name == "binded" else self.confusion_chance):
                                self.effects[effect_name] = effect
                                self.effects[effect_name][0] = int(self.effects[effect_name][0] * self.debuff_time)
                        
                if "hurted_dmg" in self.trinket_effect:

                    pct_before = last_health / self.max_hp
                    pct_after = self.hp / self.max_hp
                    
                    step = self.trinket_effect["hurted_dmg"][1]
                    steps_before = math.floor(pct_before / step)
                    steps_after = math.floor(pct_after / step)
                    
                    steps = steps_before - steps_after
                    
                    if steps > 0:
                      
                        bonus_per_trigger = self.trinket_effect["hurted_dmg"][0]
                        self.og_damage *= (1 + bonus_per_trigger * steps)

                if "explosion" in effects:
                    return ["explosion", effects["explosion"]]
                if "static" in self.armor_effect:
                    return ["static",self.armor_effect["static"][0]*amount]

            
                return [True]
        return False

    def handle_effects(self, check = False):

        effect_del = []
        text = []
        speed_mult = 1.0
        dmg_mult = 1.0
        rof_mult = 1.0

        if "focus" in self.armor_effect and self.nodmg_time >= self.armor_effect["focus"][0]:

            speed_mult *= 1+self.armor_effect["focus"][1]
            dmg_mult *= 1+self.armor_effect["focus"][2]
            rof_mult *= 1-self.armor_effect["focus"][3]
            self.effects["focus"] = [2,0.0]   # only shows the indicator ring

        if "berserk" in self.armor_effect and self.hp < self.max_hp * self.armor_effect["berserk"][0]:

            dmg_mult *= 1 + self.armor_effect["berserk"][1]

        if "regen" in self.armor_effect and self.hp < self.max_hp*self.armor_effect["regen"][0] and self.regen_timer >= 30:

            self.hp = min(self.max_hp, self.hp + self.max_hp * self.armor_effect["regen"][1] / 100)   # % of max HP
            self.regen_timer = 0

        if "overclock" in self.armor_effect and self.overclock_timer >= self.armor_effect["overclock"][0]:

            self.effects["boost"] = [self.armor_effect["overclock"][1],self.armor_effect["overclock"][2]]
            self.overclock_timer = 0
            self.sfx.play("overclock")

        if "rnd_effect" in self.armor_effect and self.rnd_buff_timer >= self.armor_effect["rnd_effect"][0]:
            self.rnd_buff_timer = 0
            self.sfx.play("gain_effect")
            buffs = ["speed","boost","strength","regen"]
            debuffs = ["slow","glued","weakness","poison"]
            if self.armor_effect["rnd_effect"][1] == 0:
                rnd_effect = random.choice(debuffs)
            elif self.armor_effect["rnd_effect"][1] == 1:
                buffs.extend(debuffs)
                rnd_effect = random.choice(buffs)
            elif self.armor_effect["rnd_effect"][1] == 2:
                rnd_effect = random.choice(buffs)

            if rnd_effect in ("slow","speed","boost","glued","strength","weakness"):
                self.effects[rnd_effect] = [180,0.25]
            else:
                self.effects[rnd_effect] = [180,self.max_hp*0.05]
            

        if self.effects:
            for effect_name, effect in self.effects.items():

                if effect_name == "slow":
                    speed_mult -= effect[1]
                    if speed_mult < 0:
                        speed_mult = 0
                elif effect_name == "speed":
                    speed_mult += effect[1]

                elif effect_name == "poison" and effect[0] % 60 == 0 and not check:
                    self.sfx.play("posion_effect")
                    self.hp -= effect[1]

                if effect_name == "weakness":
                    dmg_mult -= effect[1]
                    if dmg_mult < 0:
                        dmg_mult = 0
                elif effect_name == "strength":
                    dmg_mult += effect[1]

                if effect_name == "glued":
                    rof_mult += effect[1]
                    if rof_mult < 0:
                        rof_mult = 0
                elif effect_name == "boost":
                    rof_mult -= effect[1]

                elif effect_name == "burn" and effect[0] % 15 == 0 and not check:
                    self.sfx.play("burn_effect")
                    self.hp -= effect[1]

                elif effect_name == "regen" and effect[0] % 60 == 0 and not check:
                    self.hp += effect[1]

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
                if name == "acid":
                    self.defence = self.og_defence
                self.effects.pop(name)
        self.speed = self.og_speed*speed_mult
        self.damage = self.og_damage*dmg_mult
        self.rate_of_fire = self.og_rate_of_fire*rof_mult
        return text, self.hp <= 0
        
    def move(self, keys, screen):
        vx = 0
        vy = 0

        confusion = "confusion" in self.handle_effects(True)[0]
            
        if confusion:
            if keys[pygame.K_s]:
                vy -= 1
            if keys[pygame.K_w]:
                vy += 1
            if keys[pygame.K_d]:
                vx -= 1
            if keys[pygame.K_a]:
                vx += 1
        else:
            if keys[pygame.K_w]:
                vy -= 1
            if keys[pygame.K_s]:
                vy += 1
            if keys[pygame.K_a]:
                vx -= 1
            if keys[pygame.K_d]:
                vx += 1

        length = math.sqrt(vx*vx + vy*vy)

        if length != 0:
            vx /= length
            vy /= length

        grip = ICE_GRIP if self.ice else COMBAT_GRIP     # ice: you speed up and stop slowly
        k = grip[0] if (vx or vy) else grip[1]
        self.slide_x += (vx * self.speed - self.slide_x) * k
        self.slide_y += (vy * self.speed - self.slide_y) * k
        if abs(self.slide_x) < 0.05:
            self.slide_x = 0.0
        if abs(self.slide_y) < 0.05:
            self.slide_y = 0.0
        self.x += self.slide_x
        self.y += self.slide_y
        if self.x < 0 + self.width:
            self.x = 0 + self.width
        if self.x > screen.get_width()-self.width:
            self.x = screen.get_width()-self.width
        if self.y < 0 + self.width:
            self.y = 0 + self.width
        if self.y > screen.get_height()-self.width:
            self.y = screen.get_height()-self.width
    def shoot(self):
        binded = "binded" in self.handle_effects(True)[0]
        now = pygame.time.get_ticks()
        if binded:
            return False, None
        if "burst" in self.weapon_effect:
            # a burst of N shots close together, then a pause: one burst per N x rate of fire (same DPS)
            shots, gap = self.weapon_effect["burst"]
            if self.burst_left > 0:
                if now - self.last_shot_time < gap * 1000:
                    return False, None
                self.burst_left -= 1
            else:
                if now - self.burst_start < self.rate_of_fire * shots * 1000:
                    return False, None
                self.burst_start = now
                self.burst_left = shots - 1
        elif now - self.last_shot_time < self.rate_of_fire * 1000:
            return False, None
        self.last_shot_time = now
        projectiles = self.make_projectiles()
        if self.double_every and now - self.last_double >= self.double_every:
            # D20: the same shot again, a bit to the side (two bullets next to each other)
            self.last_double = now
            projectiles += [self.side_copy(p) for p in projectiles]
        return True, projectiles

    def reload_left(self):
        """ms until the weapon can shoot again (0 = ready)."""
        now = pygame.time.get_ticks()
        if "burst" in self.weapon_effect:
            shots, gap = self.weapon_effect["burst"]
            if self.burst_left > 0:
                return max(0, gap * 1000 - (now - self.last_shot_time))
            return max(0, self.rate_of_fire * shots * 1000 - (now - self.burst_start))
        return max(0, self.rate_of_fire * 1000 - (now - self.last_shot_time))

    def reload_now(self):
        """Close Call sigil: the weapon is ready to shoot again right now."""
        self.last_shot_time = self.burst_start = -10 ** 9
        self.burst_left = 0

    def bursting(self):
        """True while a burst is still being fired (Combat keeps shooting even without the mouse)."""
        return self.burst_left > 0

    def side_copy(self, p):
        angle = math.atan2(p.target_y - p.y, p.target_x - p.x)
        off = max(10, self.bullet_size * 1.6)
        dx, dy = -math.sin(angle) * off, math.cos(angle) * off
        p.x -= dx / 2
        p.y -= dy / 2
        p.start_x, p.start_y = p.x, p.y
        return prjt(p.x + dx, p.y + dy, p.target_x + dx, p.target_y + dy, self.bullet_speed, p.damage, "player",
                    self.bullet_size, self.range, self.bullet_type_info, self.bullet_type, self.weapon_effect)

    def shot_damage(self):
        return self.damage * random.randint(int(self.dmg_mult[0] * 100), int(self.dmg_mult[1] * 100)) / 100

    def make_projectiles(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cam = getattr(self, "cam", (0, 0))           # (8.11) big fight rooms: the screen shows a part of the room
        mouse_x, mouse_y = mouse_x + cam[0], mouse_y + cam[1]
        base = math.atan2(mouse_y - self.y, mouse_x - self.x)
        angles = []
        if "shotgun" not in self.weapon_effect:
            angles = [base + math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))]
        elif self.weapon_effect["shotgun"][0] == "r":
            angles = [base + math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))
                      for _ in range(self.weapon_effect["shotgun"][1])]
        elif self.weapon_effect["shotgun"][0] == "s":
            shots = self.weapon_effect["shotgun"][1]
            angle = base + math.radians(-self.recoil / 2 - (self.recoil / shots) / 2)
            for _ in range(shots):
                angle += math.radians(self.recoil / shots)
                angles.append(angle)
        projectiles = []
        for angle in angles:
            target_x = self.x + math.cos(angle) * 1000
            target_y = self.y + math.sin(angle) * 1000
            projectiles.append(prjt(self.x, self.y, target_x, target_y, self.bullet_speed, self.shot_damage(), "player",
                                    self.bullet_size, self.range, self.bullet_type_info, self.bullet_type,
                                    self.weapon_effect))
        return projectiles

    def hp_bar(self, screen):
        bar_width = 50
        bar_height = 5
        fill_width = int(bar_width * self.hp / (self.max_hp))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width // 2, self.y - self.width - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width // 2, self.y - self.width - 10, fill_width, bar_height))
    

        