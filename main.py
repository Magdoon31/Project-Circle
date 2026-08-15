import pygame

from lib.player.shooter import Shooter
from lib.player.projectile import projectile as prjt
from lib.sfx_manager import sfx_manager as sfx
from lib.boss.boss import Boss as boss

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()



sfx = sfx()
sfx.load_sfx("shoot", "assets/sfx/player_shoot.mp3")
sfx.load_sfx("explosion", "assets/sfx/explosion.mp3")
sfx.load_sfx("hit", "assets/sfx/player_hit.mp3")

running = True

font = pygame.font.SysFont(None, 60)

title_text = font.render("Boss Battle", True, (255, 255, 255))
instruction_text = font.render("Select difficulty:", True, (255, 255, 255))
easy_text = font.render("Easy", True, (255, 255, 255))
medium_text = font.render("Medium", True, (255, 255, 255))
hard_text = font.render("Hard", True, (255, 255, 255))
menu = True

while running:
    shooter = Shooter(400, 300)
    end = True
    game = True
    player_projectiles = []
    boss_projectiles = []
    win = False
    while menu:
        screen.fill((0, 0, 0))
        easy_box = pygame.draw.rect(screen, (10, 200, 10), (screen.get_width() // 5 - 150, screen.get_height()// 2, 120, 50))
        screen.blit(easy_text, easy_box.topleft + pygame.math.Vector2(10, 10))
        medium_box = pygame.draw.rect(screen, (200, 170, 10), (screen.get_width() // 2 - 150, screen.get_height()// 2, 180, 50))
        screen.blit(medium_text, medium_box.topleft + pygame.math.Vector2(10, 10))
        hard_box = pygame.draw.rect(screen, (200, 10, 10), (screen.get_width() * 4 // 5 - 150, screen.get_height()// 2 , 120, 50))
        screen.blit(hard_text, hard_box.topleft + pygame.math.Vector2(10, 10))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2 - 60, screen.get_height()// 5 + 50 ))
        screen.blit(instruction_text, (screen.get_width() // 2 - instruction_text.get_width() // 2 - 70, screen.get_height() // 3))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                running = False
                game = False
                end = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if easy_box.collidepoint(mouse_pos):
                        shooter.hp = 150
                        difficulty = "easy"
                        menu = False
                    elif medium_box.collidepoint(mouse_pos):
                        shooter.hp = 125
                        difficulty = "medium"
                        menu = False
                    elif hard_box.collidepoint(mouse_pos):
                        shooter.hp = 100
                        difficulty = "hard"
                        menu = False

    current_boss = boss(900, 800, difficulty)
    timer = pygame.time.get_ticks()
    menu = True
    shooter.hp = 100 if difficulty == "hard" else 125 if difficulty == "medium" else 150
    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
                running = False
                end = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game = False
                if event.key == pygame.K_r:
                    game = False
                    end = False
                    menu = False
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    new_proj = shooter.shoot("basic")
                    if new_proj is not None:
                        sfx.play_sfx("shoot")
                        player_projectiles.append((new_proj))
                elif event.button == 3:
                    new_proj = shooter.shoot("shotgun")
                    if new_proj is not None:
                        sfx.play_sfx("shoot")
                        player_projectiles.extend([(proj) for proj in new_proj])

        for proj in player_projectiles:
            if proj is not None:
                prjt.update(proj)
                if proj.x < 0 or proj.x > screen.get_width() or proj.y < 0 or proj.y > screen.get_height():
                    player_projectiles.remove(proj)
        keys = pygame.key.get_pressed()
        shooter.move(keys, screen)
        screen.fill((0, 0, 0))
        
        timer_text = font.render(f"{(pygame.time.get_ticks() - timer)//1000}:{pygame.time.get_ticks()%1000}", True, (255, 255, 255))
        timer_box = pygame.draw.rect(screen, (0, 0, 0), (screen.get_width() - 200, 20, 180, 50))
        screen.blit(timer_text, timer_box.topleft + pygame.math.Vector2(10, 10))
        for proj in player_projectiles:
            prjt.update(proj)
            prjt.draw(proj, screen)
            if prjt.deal_damage(proj, current_boss):
                sfx.play_sfx("hit")
                player_projectiles.remove(proj)
                if current_boss.take_damage(proj.damage):
                    sfx.play_sfx("explosion")
                    win = True
                    game = False
            if prjt.check_duration(proj, pygame.time.get_ticks()):
                if proj in player_projectiles:
                    player_projectiles.remove(proj)
            
        for proj in boss_projectiles:
            if prjt.deal_damage(proj, shooter):
                sfx.play_sfx("hit")
                boss_projectiles.remove(proj)
                if shooter.take_damage(proj.damage):
                    sfx.play_sfx("explosion")
                    win = False
                    game = False
            prjt.update(proj)
            prjt.draw(proj, screen) 
        shooter.draw(screen, difficulty)
        current_boss.draw(screen)
        current_boss.move(shooter.x, shooter.y, screen)
        boss_projectiles.extend(current_boss.attack(shooter))
        
        pygame.display.update()
        clock.tick(60)
    ending_text = ""
    if win:
        diff_mult = 1.25 if difficulty == "medium" else 1 if difficulty == "hard" else 1.5
        if difficulty == "easy":
            best_time = 20
        elif difficulty == "medium":
            best_time = 30
        else:        
            best_time = 40
        ending_text += "You win!"
        if shooter.hp == 100*diff_mult and (pygame.time.get_ticks() - timer)//1000 <= best_time:
            ending_text += "    RANK: SS!"
        elif shooter.hp == 100*diff_mult:
            ending_text += "    RANK: S!"
        elif shooter.hp > 70*diff_mult:
            ending_text += "    RANK: A!"
        elif shooter.hp > 30*diff_mult:
            ending_text += "    RANK: B!"
        elif shooter.hp > 0*diff_mult:
            ending_text += "    RANK: C!"
    else:
        ending_text += "You lose!"
    ending_text += "    Press Esc to continue"
    ending_text = font.render(ending_text, True, (255, 255, 255))
    
    while end:
        screen.fill((0,0,0))
        screen.blit(ending_text, (100,50))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = False
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    end = False
        pygame.display.update()
        clock.tick(60)