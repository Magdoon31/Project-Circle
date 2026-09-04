import pygame, math, random
from game.combat.projectile import projectile as prjt

class Shooter :
    def __init__(self, x, y, active_items):
        self.x = x
        self.y = y
        self.width = 25
        self.hp = 100 + (active_items["armor"].bonus_hp if active_items["armor"] else 0)
        self.max_hp = self.hp
        self.defence = (active_items["armor"].defense if active_items["armor"] else 0)
        self.speed = 10
        self.rate_of_fire = (active_items["weapon"].rate_of_fire if active_items["weapon"] else 99999)
        self.last_shot_time = 0
        self.damage = (active_items["weapon"].damage if active_items["weapon"] else 0)
        self.type = "player"
        self.range = (active_items["weapon"].range//active_items["weapon"].bullet_speed if active_items["weapon"] else 0)
        self.bullet_size = (active_items["weapon"].bullet_size if active_items["weapon"] else 0)
        self.bullet_speed = (active_items["weapon"].bullet_speed if active_items["weapon"] else 0)
        self.automatic_weapon = (active_items["weapon"].automatic if active_items["weapon"] else False)
        self.recoil = (active_items["weapon"].recoil if active_items["weapon"] else 0)
        self.weapon_effect = (active_items["weapon"].effect if active_items["weapon"] else None)
        self.armor_effect = (active_items["armor"].effect if active_items["armor"] else None)
        self.trinket_effect = (active_items["trinket"].effect if active_items["trinket"] else None)


    def draw(self, screen, difficulty):
        pygame.draw.circle(screen, (200, 50, 50), (self.x, self.y), self.width)
        self.hp_bar(screen, difficulty)
    def move(self, keys, screen):
        vx = 0
        vy = 0

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
        if pygame.time.get_ticks() - self.last_shot_time >= self.rate_of_fire * 1000:  
            mouse_x, mouse_y = pygame.mouse.get_pos()   

            if self.weapon_effect[0] not in ("shotgun_r6","shotgun_s4"):
                    angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                    recoil_angle = math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))
                    angle += recoil_angle
                    target_x = self.x + math.cos(angle) * 1000
                    target_y = self.y + math.sin(angle) * 1000

                    projectile = prjt(self.x, self.y, target_x, target_y, self.bullet_speed, self.damage, "player", self.bullet_size, self.range)
                    self.last_shot_time = pygame.time.get_ticks()
                    return False, projectile
            
            elif self.weapon_effect[0][:7] == "shotgun":
                projectiles = []
                if self.weapon_effect[0][-2] == "r":
                    for i in range(int(self.weapon_effect[0][-1])):
                        angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                        recoil_angle = math.radians(random.uniform(-self.recoil / 2, self.recoil / 2))
                        angle += recoil_angle
                        target_x = self.x + math.cos(angle) * 1000
                        target_y = self.y + math.sin(angle) * 1000
                        
                        projectile = prjt(self.x, self.y, target_x, target_y, self.bullet_speed, self.damage, "player", self.bullet_size, self.range)
                        projectiles.append(projectile)
                
                elif self.weapon_effect[0][-2] == "s":
                    shots = int(self.weapon_effect[0][-1])
                    angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
                    angle += math.radians(-self.recoil//2)
                    for i in range(shots):
                        angle += math.radians(self.recoil/shots)
                        target_x = self.x + math.cos(angle) * 1000
                        target_y = self.y + math.sin(angle) * 1000
                        projectile = prjt(self.x, self.y, target_x, target_y, self.bullet_speed, self.damage, "player", self.bullet_size, self.range)
                        projectiles.append(projectile)

                self.last_shot_time = pygame.time.get_ticks()
                return True, projectiles
        return False, None
    def take_damage(self, amount, effects):
        self.hp -= max(amount-self.defence, 1)
        if self.hp <= 0:
            self.hp = 0
            return True
        return False
    def hp_bar(self, screen,difficulty):
        bar_width = 50
        bar_height = 5
        fill_width = int(bar_width * self.hp / (self.max_hp))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width // 2, self.y - self.width - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width // 2, self.y - self.width - 10, fill_width, bar_height))
    

        