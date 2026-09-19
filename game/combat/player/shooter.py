import pygame, math, random
from game.combat.projectile import projectile as prjt

class Shooter :
    def __init__(self, x, y, active_items, sfx, bullet_type_info):
        self.x = x
        self.y = y
        self.width = 25
        self.hp = 50 + (active_items["armor"].bonus_hp if active_items["armor"] else 0)
        self.max_hp = self.hp
        self.defence = (active_items["armor"].defense if active_items["armor"] else 0)
        self.og_defence = self.defence
        self.speed = 8
        self.og_speed = self.speed
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
        self.bullet_type = (active_items["weapon"].bullet_type if active_items["weapon"] else "normal_red")

        self.automatic_weapon = (active_items["weapon"].automatic if active_items["weapon"] else False)
        self.recoil = (active_items["weapon"].recoil if active_items["weapon"] else 0)

        self.weapon_effect = (active_items["weapon"].effect if active_items["weapon"] else {})
        self.armor_effect = (active_items["armor"].effect if active_items["armor"] else {})
        self.trinket_effect = (active_items["trinket"].effect if active_items["trinket"] else {})

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
        print(self.weapon_effect,self.armor_effect,self.trinket_effect)

        for effect_name, effect in self.armor_effect.items():

            if effect_name in ("speed","strength","slow"):
                if effect_name in self.effects:
                    self.effects[effect_name][0]+=effect[0]
                    self.effects[effect_name][1]+=effect[1]
                else:
                    self.effects[effect_name] = effect


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


        for effect_name, effect in self.trinket_effect.items():
            if effect_name in ("speed","strength","slow"):
                if effect_name in self.effects:
                    self.effects[effect_name][0]+=effect[0]
                    self.effects[effect_name][1]+=effect[1]
                else:
                    self.effects[effect_name] = effect

            elif effect_name in ("recoil"):

                self.recoil += effect[0]

            elif effect_name in ("poison_up","slow_up","explosion_up","zap_up") and effect_name[:-3] in self.weapon_effect:

                self.weapon_effect[effect_name[:-3]][0] += effect[0]
                self.weapon_effect[effect_name[:-3]][1] += effect[1]
            

            elif effect_name == "ghost_up" and "ghost" in self.weapon_effect:

                self.weapon_effect["pierce"][0] += effect[0]
                self.weapon_effect["weakness"][1] += effect[1]
                self.weapon_effect["glued"][1] += effect[1]

            elif effect_name == "slow_on_glue" and "glue" in self.weapon_effect:

                if "slow" in self.weapon_effect: 
                    self.weapon_effect["slow"][0] += effect[0]
                    self.weapon_effect["slow"][1] += effect[1]
                else:
                    self.weapon_effect["slow"][0] = effect[0]
                    self.weapon_effect["slow"][1] = effect[1]
            
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



        self.leftover_dmg_hurted_dmg = 0

        

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
            "boost":        (225, 190, 60)    # darker yellow
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
            self.imm_frames = 20
            if ("dodge" in self.armor_effect and random.random() > self.armor_effect["dodge"][0]) or "dodge" not in self.armor_effect:

                self.nodmg_time = 0
                self.imm_frames = 10 if "imm_frames" not in self.trinket_effect else self.trinket_effect["imm_frames"][0]

                amount = max(amount-self.defence, 1)
                if "guard" in self.armor_effect and self.hp > self.armor_effect["guard"][0]:
                    amount *= 1-self.armor_effect["guard"][1]

                if amount < 1:
                    amount = 1
                self.hp -= amount

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

                            if effect_name in ("slow","poison","weakness","glued", "burn", "acid"):
                                if self.effects[effect_name][0] != "inf":
                                    self.effects[effect_name][0] *= self.debuff_time
                            elif effect_name in ("speed","strength","boost"):
                                if self.effects[effect_name][0] != "inf":
                                    self.effects[effect_name][0] *= self.buff_time
                        elif effect_name == "hurted_dmg":

                            hurted_dmg_info = [math.floor((amount+self.leftover_dmg_hurted_dmg)/5),amount%5]
                            self.leftover_dmg_hurted_dmg += hurted_dmg_info[1]
                            self.leftover_dmg_hurted_dmg %= 5

                        elif effect_name in ("binded","confusion"):
                            rnd = random.random()
                            if rnd < effect[1]*(self.bind_chance if effect_name == "binded" else self.confusion_chance):
                                self.effects[effect_name] = effect
                                self.effects[effect_name][0] *= self.debuff_time
                        
                if "hurted_dmg" in self.trinket_effect:
                    self.og_damage*=(1+self.trinket_effect["hurted_dmg"][0]*hurted_dmg_info[0])
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
            self.effects["speed"] = [2,0.0]

        if "berserk" in self.armor_effect and self.hp < self.armor_effect["berserk"][0]:

            dmg_mult *= self.armor_effect["berserk"][1]

        if "regen" in self.armor_effect and self.hp < self.max_hp*self.armor_effect["regen"][0] and self.regen_timer >= 30:

            print("yes")
            self.hp += self.armor_effect["regen"][1]
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

        self.x += vx * self.speed
        self.y += vy * self.speed
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
        
        if pygame.time.get_ticks() - self.last_shot_time >= self.rate_of_fire * 1000 and not binded:  
            mouse_x, mouse_y = pygame.mouse.get_pos()   
            if "shotgun" not in self.weapon_effect:
                    angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                    recoil_angle = math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))
                    angle += recoil_angle
                    target_x = self.x + math.cos(angle) * 1000
                    target_y = self.y + math.sin(angle) * 1000

                    projectile = prjt(self.x, self.y, target_x, target_y, 
                                      self.bullet_speed, self.damage*random.randint(int(self.dmg_mult[0]*100),int(self.dmg_mult[1]*100))//100, "player", 
                                      self.bullet_size, self.range, self.bullet_type_info, 
                                      self.bullet_type, self.weapon_effect)
                    self.last_shot_time = pygame.time.get_ticks()
                    return False, projectile
            
            elif "shotgun" in self.weapon_effect:
                projectiles = []
                if self.weapon_effect["shotgun"][0] == "r":
                    for i in range(self.weapon_effect["shotgun"][1]):
                        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                        recoil_angle = math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))
                        angle += recoil_angle
                        target_x = self.x + math.cos(angle) * 1000
                        target_y = self.y + math.sin(angle) * 1000
                        projectile = prjt(self.x, self.y, target_x, target_y, 
                                          self.bullet_speed, self.damage*random.randint(int(self.dmg_mult[0]*100),int(self.dmg_mult[1]*100))//100, "player", 
                                          self.bullet_size, self.range, self.bullet_type_info,
                                          self.bullet_type, self.weapon_effect)
                        projectiles.append(projectile)
                
                elif self.weapon_effect["shotgun"][0] == "s":
                    shots = self.weapon_effect["shotgun"][1]
                    angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                    angle += math.radians(-self.recoil//2)
                    for i in range(shots):
                        angle += math.radians(self.recoil/shots)
                        target_x = self.x + math.cos(angle) * 1000
                        target_y = self.y + math.sin(angle) * 1000
                        projectile = prjt(self.x, self.y, target_x, target_y, 
                                          self.bullet_speed, self.damage*random.randint(int(self.dmg_mult[0]*100),int(self.dmg_mult[1]*100))//100, "player", 
                                          self.bullet_size, self.range, self.bullet_type_info,
                                          self.bullet_type, self.weapon_effect)
                        projectiles.append(projectile)

                self.last_shot_time = pygame.time.get_ticks()
                return True, projectiles
        return False, None
    
    def hp_bar(self, screen):
        bar_width = 50
        bar_height = 5
        fill_width = int(bar_width * self.hp / (self.max_hp))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width // 2, self.y - self.width - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width // 2, self.y - self.width - 10, fill_width, bar_height))
    

        