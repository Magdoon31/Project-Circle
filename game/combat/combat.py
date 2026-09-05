import math
import random

import pygame
from game.combat.enemy.enemy import Enemy


class Combat:

    def __init__(self, screen, player, enemies, hard_mode, sfx=None, boss=None):
        self.screen = screen
        self.player = player
        self.boss = boss
        self.player_projectiles = []
        self.enemy_projectiles = []

        self.timer = pygame.time.get_ticks()
        self.enemies = enemies
        self.win = False
        self.finished = False
        self.money_boost_applied = False

        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                            "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                            "giant" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",128),}
        
        self.sfx = sfx
        
        self.sfx.load_sfx("shoot", "assets/sfx/combat/player_shoot.mp3")
        self.sfx.load_sfx("explosion", "assets/sfx/combat/explosion.mp3")
        self.sfx.load_sfx("hit", "assets/sfx/combat/hit.wav")
        self.sfx.load_sfx("laser1", "assets/sfx/combat/laser1.mp3")
        self.sfx.load_sfx("laser2", "assets/sfx/combat/laser2.wav")
        self.sfx.load_sfx("laser3", "assets/sfx/combat/laser3.wav")
        self.sfx.load_sfx("run", "assets/sfx/combat/run.wav")
        self.sfx.load_sfx("death", "assets/sfx/combat/death.wav")
        self.sfx.load_sfx("enemy_death", "assets/sfx/combat/enemy_death.wav")
        self.sfx.load_sfx("player_hit", "assets/sfx/combat/player_hit.wav")
        self.sfx.load_sfx("bullet_burst", "assets/sfx/combat/bullet_burst.mp3")


        self.player.hp = 100
        self.money = 0
        self.money_mult = random.randint(10,40)

        self.hard_mode = hard_mode

    def handle_events(self, events, mouse_btn_pressed):

        

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

        if mouse_btn_pressed[0] and self.player.automatic_weapon:
            multiple, new_projectile = self.player.shoot()      
            if new_projectile is not None:
                self.sfx.play("shoot")
                if multiple:
                    self.player_projectiles.extend(new_projectile)
                else:
                    self.player_projectiles.append(new_projectile)

    def update(self):

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.screen)

        for projectile in self.player_projectiles[:]:
            projectile.update()
            if (
                projectile.x < 0
                or projectile.x > self.screen.get_width()
                or projectile.y < 0
                or projectile.y > self.screen.get_height()
            ):
                self.player_projectiles.remove(projectile)
                continue

            if not projectile.check_duration():
                self.player_projectiles.remove(projectile)
                continue
            for enemy in self.enemies:
                if projectile.deal_damage(enemy):
                    self.player_projectiles.remove(projectile)
                    if enemy.hp <= 0:    
                        projectiles = enemy.attack()
                        self.enemy_projectiles.extend(projectiles)
                        self.enemies.remove(enemy)
                        self.sfx.play("enemy_death")
                    else:
                        self.sfx.play("hit")
                    break
            if len(self.enemies) == 0:
                self.win = True
                self.finished = True


        for projectile in self.enemy_projectiles[:]:
            projectile.update()

            if not projectile.check_duration():
                self.enemy_projectiles.remove(projectile)

            if projectile.deal_damage(self.player):
                self.enemy_projectiles.remove(projectile)
                self.sfx.play("player_hit")
                if self.player.hp <= 0:
                    self.win = False
                    self.finished = True
        for enemy in self.enemies:
            enemy.move(self.player.x, self.player.y, self.screen)
            proj = enemy.attack(self.player, self.hard_mode)
            self.enemy_projectiles.extend(proj)
            pass

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

           
    def draw(self):

        self.screen.fill((0, 0, 0))
        for projectile in self.player_projectiles:
            projectile.draw(self.screen)
        for projectile in self.enemy_projectiles:
            projectile.draw(self.screen)
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen, self.hard_mode)
        if self.win:

            pygame.draw.rect(self.screen,(200,200,200),(self.screen.get_width()/2 - self.screen.get_width()/12, self.screen.get_height()/3, self.screen.get_width()/6,self.screen.get_height()/2.9),0,10)
            end_title = self.font_heavy["mid"].render("Win!", True, (0,0,0))

            flawless_text = self.font_heavy["mid"].render("Flawless!!", True, (255,255,255))
            is_flawless = self.player.hp == self.player.max_hp
            money_base = self.money*self.money_mult*0.05 if not self.boss else self.money
            if is_flawless and not self.hard_mode and not self.boss:

                end_text = self.font_light["mid"].render(f"{money_base}$ X 1.5!", True, (0,0,0))

                if not self.money_boost_applied:
                    self.money_mult *= 1.5
                    self.money_boost_applied = True

            else:
                end_text = self.font_light["mid"].render(f"{money_base}$", True, (0,0,0))
            self.screen.blit(end_title, (self.screen.get_width()/2 - end_title.get_width()/2, self.screen.get_height()/2 - end_title.get_height()*3))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/2 - end_text.get_height()/2))

            if is_flawless:      
                self.screen.blit(flawless_text, (self.screen.get_width()/2 - flawless_text.get_width()/2, self.screen.get_height()/2 + end_text.get_height()*2))

            end_text = self.font_heavy["giant"].render("CLICK", True, (255,255,255))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/1.3))

        elif self.finished:

            end_text = self.font_heavy["giant"].render("CLICK", True, (255,255,255))
            self.screen.blit(end_text, (self.screen.get_width()/2 - end_text.get_width()/2, self.screen.get_height()/2 - end_text.get_height()/2))

        pygame.display.flip()