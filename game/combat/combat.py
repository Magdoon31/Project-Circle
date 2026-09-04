import pygame
from game.combat.enemy.enemy import Enemy


class Combat:

    def __init__(self, screen, player, enemies, difficulty="easy", sfx=None):
        self.screen = screen
        self.difficulty = difficulty
        self.player = player
        self.boss = Enemy(900, 800,500,40,"boss",5,100,{"basic" : {"damage": 30, "cooldown": 2000, "last_used": 2000, "width": 30, "speed": 9, "range": 2000}, 
            "spinner" : {"damage": 20, "cooldown": 3200, "last_used": 3200, "width": 24, "speed": 6, "range": 2000},
            "spinner" : {"damage": 10, "cooldown": 2800, "last_used": 2800, "width": 15, "speed": 7, "range": 2000},
            "minigun": {"damage": 10,"cooldown": 2500,"last_used": 2500,"width": 5,"speed": 10,"burst_count": 0,"burst_max": 30,"burst_delay": 30,"last_shot": 2500,"is_bursting": False, "range": 2000}})
        self.player_projectiles = []
        self.enemy_projectiles = []

        self.timer = pygame.time.get_ticks()
        self.enemies = enemies
        self.win = False
        self.finished = False

        self.sfx = sfx
        
        self.sfx.load_sfx("shoot", "assets/sfx/combat/player_shoot.mp3")
        self.sfx.load_sfx("explosion", "assets/sfx/combat/explosion.mp3")
        self.sfx.load_sfx("hit", "assets/sfx/combat/player_hit.mp3")

        self.player.hp = 100
        self.money = 0

    def handle_events(self, events, mouse_btn_pressed):

        

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.finished = True
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
                    self.sfx.play("hit")
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
            if len(self.enemies) == 0:
                self.win = True
                self.finished = True


        for projectile in self.enemy_projectiles[:]:
            projectile.update()

            if not projectile.check_duration():
                self.enemy_projectiles.remove(projectile)

            if projectile.deal_damage(self.player):
                self.enemy_projectiles.remove(projectile)
                self.sfx.play("hit")
                if self.player.hp <= 0:

                    self.win = False
                    self.finished = True
        for enemy in self.enemies:
            enemy.move(self.player.x, self.player.y, self.screen)
            self.enemy_projectiles.extend(enemy.attack(self.player))

    def draw(self):

        self.screen.fill((0, 0, 0))
        for projectile in self.player_projectiles:
            projectile.draw(self.screen)
        for projectile in self.enemy_projectiles:
            projectile.draw(self.screen)
        self.player.draw(self.screen, self.difficulty)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        pygame.display.flip()