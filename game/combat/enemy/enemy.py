import pygame, math, random
from game.combat.projectile import projectile as prjt

class Enemy:
    def __init__(self, x, y, hp, width, type, speed, money, attacks):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = self.hp
        self.width = width
        self.type = type
        self.speed = speed
        self.og_speed = speed
        self.attacks = attacks
        self.money = money
        self.color = (255,255,255)
        self.effects = {}      

    def draw(self, screen, hard_mode = False):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.width)
        effect_del = []
        if self.effects:
            for effect_name, effect in self.effects.items():
                if effect_name == "slow":
                    self.speed = self.og_speed * (1-effect[1])

                effect[0] -= 1/60 if not hard_mode else 1/50
                if effect[0] <= 0:
                    effect_del.append(effect_name)
            for name in effect_del:
                if name == "slow":
                    self.speed = self.og_speed
                self.effects.pop(name)
            print(self.effects)
                

    def take_damage(self, amount, effects):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0
        if effects:
            for effect_name, effect in effects.items():
                if effect_name in ("slow"):
                    self.effects[effect_name] = effect
        


    def move(self, target_x, target_y, screen):
        dx = target_x - self.x
        dy = target_y - self.y

        length = math.sqrt(dx*dx + dy*dy)

        if length != 0:
            dx /= length
            dy /= length
        self.x += dx * self.speed
        self.y += dy * self.speed
        if self.x < 0 + self.width:
            self.x = 0 + self.width
        if self.x > screen.get_width()-self.width:
            self.x = screen.get_width()-self.width
        if self.y < 0 + self.width:
            self.y = 0 + self.width
        if self.y > screen.get_height()-self.width:
            self.y = screen.get_height()-self.width

    def attack(self, player = None, hard_mode = False):
        projectiles = []
        current_time = pygame.time.get_ticks()
        for attack_name, attack_info in self.attacks.items():
            if attack_name == "death_spiral" and self.hp == 0:
                for angle in range(0, 360,30):
                    rad = math.radians(angle)
                    proj_x = self.x + math.cos(rad) * self.width
                    proj_y = self.y + math.sin(rad) * self.width

                    target_x = self.x + math.cos(rad) * 1000
                    target_y = self.y + math.sin(rad) * 1000

                    projectile = prjt(proj_x, proj_y, target_x, target_y, self.attacks["death_spiral"]["speed"], self.attacks["death_spiral"]["damage"], "enemy", self.attacks["death_spiral"]["width"], self.attacks["death_spiral"]["range"])
                    projectiles.append(projectile)
                break
            elif current_time - attack_info["last_used"] >= attack_info["cooldown"] - (200 if hard_mode else 0) and player:
                if attack_name == "basic": 
                    projectiles.append(prjt(self.x, self.y, player.x, player.y, attack_info["speed"], attack_info["damage"], "enemy", attack_info["width"], attack_info["range"]))
                    attack_info["last_used"] = current_time
                elif attack_name == "minigun":
                    if not attack_info["is_bursting"]:
                        if current_time - attack_info["last_used"] >= attack_info["cooldown"]:
                            attack_info["is_bursting"] = True
                            attack_info["burst_count"] = 0
                            attack_info["last_shot"] = current_time
                            attack_info["last_used"] = current_time

                    if attack_info["is_bursting"]:
                        
                        if current_time - attack_info["last_shot"] >= attack_info["burst_delay"]:
                            
                            attack_info["last_shot"] = current_time
                            attack_info["burst_count"] += 1
                            base_angle = math.atan2(player.y - self.y, player.x - self.x)
                            spread = math.radians(20)
                            random_offset = random.uniform(-spread, spread)
                            angle = base_angle + random_offset
                            vx = math.cos(angle)
                            vy = math.sin(angle)
                            proj_x = self.x + vx * self.width
                            proj_y = self.y + vy * self.width
                            target_x = self.x + vx * 1000
                            target_y = self.y + vy * 1000
                            projectile = prjt(proj_x,proj_y,target_x,target_y,attack_info["speed"],attack_info["damage"],"enemy",attack_info["width"], attack_info["range"])
                            projectiles.append(projectile)
                            if attack_info["burst_count"] >= attack_info["burst_max"]:
                                attack_info["is_bursting"] = False
                                attack_info["burst_count"] = 0
                                attack_info["last_used"] = current_time
                        
                elif attack_name == "spinner":
                    rnd = random.randint(-5,5)
                    for angle in range(0+rnd*20, 360+rnd*20, 360//attack_info["bullets"]):
                        rad = math.radians(angle)
                        proj_x = self.x + math.cos(rad) * self.width
                        proj_y = self.y + math.sin(rad) * self.width

                        target_x = self.x + math.cos(rad) * 1000
                        target_y = self.y + math.sin(rad) * 1000

                        projectile = prjt(proj_x, proj_y, target_x, target_y, attack_info["speed"], attack_info["damage"], "enemy", attack_info["width"], attack_info["range"])
                        projectiles.append(projectile)
                    attack_info["last_used"] = current_time
            
        if player and player.width + self.width > math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2):
            projectiles.append(prjt(player.x, player.y, player.x, player.y, 1, 2, "enemy", 1,1000))
                
        return projectiles

    def hp_bar(self, screen):
        if self.type == "boss":
            bar_width = screen.get_width() // 1.5
            bar_height = screen.get_height() // 30
            fill_width = int(bar_width * (self.hp/self.max_hp))
            pygame.draw.rect(screen, (255, 0, 0), (screen.get_width() // 2 - bar_width // 2, 20, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (screen.get_width() // 2 - bar_width // 2, 20, fill_width, bar_height))()