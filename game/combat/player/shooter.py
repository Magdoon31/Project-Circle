import pygame, math, random
from game.combat.projectile import projectile as prjt

class Shooter :
    def __init__(self, x, y, active_items, sfx):
        self.x = x
        self.y = y
        self.width = 25
        self.hp = 100 + (active_items["armor"].bonus_hp if active_items["armor"] else 0)
        self.max_hp = self.hp
        self.defence = (active_items["armor"].defense if active_items["armor"] else 0)
        self.og_defence = self.defence
        self.speed = 10
        self.og_speed = self.speed
        self.rate_of_fire = (active_items["weapon"].rate_of_fire if active_items["weapon"] else 99999)
        self.og_rate_of_fire = self.rate_of_fire
        self.last_shot_time = 0
        self.damage = (active_items["weapon"].damage if active_items["weapon"] else 0)
        self.og_damage = self.damage
        self.type = "player"
        self.range = (active_items["weapon"].range//active_items["weapon"].bullet_speed if active_items["weapon"] else 0)
        self.bullet_size = (active_items["weapon"].bullet_size if active_items["weapon"] else 0)
        self.bullet_speed = (active_items["weapon"].bullet_speed if active_items["weapon"] else 0)
        self.automatic_weapon = (active_items["weapon"].automatic if active_items["weapon"] else False)
        self.recoil = (active_items["weapon"].recoil if active_items["weapon"] else 0)
        self.weapon_effect = (active_items["weapon"].effect if active_items["weapon"] else None)
        self.armor_effect = (active_items["armor"].effect if active_items["armor"] else None)
        self.trinket_effect = (active_items["trinket"].effect if active_items["trinket"] else None)
        self.color = (active_items["weapon"].color if active_items["weapon"] else (0,0,0))
        self.effects = {}
        self.sfx = sfx


    def draw(self, screen):
        pygame.draw.circle(screen, (200, 50, 50), (self.x, self.y), self.width)
        self.hp_bar(screen)
        effect_del = []
        print(self.effects)
        if self.effects:
            for effect_name, effect in self.effects.items():
                if effect_name == "slow":
                    self.speed = self.og_speed * (1-effect[1])
                elif effect_name == "poison" and effect[0] % 30 == 0:
                    self.sfx.play("dmg_effect")
                    self.hp -= effect[1]
                elif effect_name == "weakness":
                    self.damage = self.og_damage * (1-effect[1])
                elif effect_name == "glued":
                    self.rate_of_fire = self.og_rate_of_fire * (1+effect[1])
                elif effect_name == "burn" and effect[0] % 6 == 0:
                    self.sfx.play("dmg_effect")
                    self.hp -= effect[1]
                elif effect_name == "acid":
                    self.defence = self.og_defence * (1-effect[1])


                effect[0] -= 1

                if effect[0] <= 0:
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
    def move(self, keys, screen):
        vx = 0
        vy = 0

        confusion = False

        for effect_name, effect in self.effects.items():
            if effect_name == "confusion":
                confusion = True
            
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

        binded = False
        for effect_name, effect in self.effects.items():
            if effect_name == "binded":
                binded = True

        if pygame.time.get_ticks() - self.last_shot_time >= self.rate_of_fire * 1000 and not binded:  
            mouse_x, mouse_y = pygame.mouse.get_pos()   

            if next(iter(self.weapon_effect), None)  not in ("shotgun_r6","shotgun_s4"):
                    angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                    recoil_angle = math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))
                    angle += recoil_angle
                    target_x = self.x + math.cos(angle) * 1000
                    target_y = self.y + math.sin(angle) * 1000

                    projectile = prjt(self.x, self.y, target_x, target_y, self.bullet_speed, self.damage, "player", self.bullet_size, self.range, self.color, self.weapon_effect)
                    self.last_shot_time = pygame.time.get_ticks()
                    return False, projectile
            
            elif next(iter(self.weapon_effect), None)[:7] == "shotgun":
                projectiles = []
                if next(iter(self.weapon_effect), None)[-2] == "r":
                    for i in range(int(next(iter(self.weapon_effect), None)[-1])):
                        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                        recoil_angle = math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))
                        angle += recoil_angle
                        target_x = self.x + math.cos(angle) * 1000
                        target_y = self.y + math.sin(angle) * 1000
                        
                        projectile = prjt(self.x, self.y, target_x, target_y, self.bullet_speed, self.damage, "player", self.bullet_size, self.range, self.color, self.weapon_effect)
                        projectiles.append(projectile)
                
                elif next(iter(self.weapon_effect), None)[-2] == "s":
                    shots = int(next(iter(self.weapon_effect), None)[-1])
                    angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                    angle += math.radians(-self.recoil//2)
                    for i in range(shots):
                        angle += math.radians(self.recoil/shots)
                        target_x = self.x + math.cos(angle) * 1000
                        target_y = self.y + math.sin(angle) * 1000
                        projectile = prjt(self.x, self.y, target_x, target_y, self.bullet_speed, self.damage, "player", self.bullet_size, self.range, self.color, self.weapon_effect)
                        projectiles.append(projectile)

                self.last_shot_time = pygame.time.get_ticks()
                return True, projectiles
        return False, None
    def take_damage(self, amount, effects):
        self.hp -= max(amount-self.defence, 1)
        if effects:
            for effect_name, effect in effects.items():
                # slow - slow, poison - deal dmg every 0.5s, weakness - less dmg, glued - less fire_rate,
                # confusion - reverse inputs, binded - can't shoot, burn - deal dmg every 0.1s, acid - less def
                if effect_name in ("slow","poison","weakness","glued","confusion","binded", "burn", "acid"):
                    self.effects[effect_name] = effect
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
    def hp_bar(self, screen):
        bar_width = 50
        bar_height = 5
        fill_width = int(bar_width * self.hp / (self.max_hp))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width // 2, self.y - self.width - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width // 2, self.y - self.width - 10, fill_width, bar_height))
    

        