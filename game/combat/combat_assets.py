import os
import pygame


class CombatAssets:
    """Everything a fight needs (sounds, images, fonts) - loaded ONCE at game start, shared by every Combat."""

    COMBAT_SFX = {
        "shoot": "assets/sfx/combat/player_shoot.mp3",
        "explosion": "assets/sfx/combat/explosion.wav",
        "hit": "assets/sfx/combat/hit.wav",
        "laser1": "assets/sfx/combat/laser1.mp3",
        "laser2": "assets/sfx/combat/laser2.wav",
        "laser3": "assets/sfx/combat/laser3.wav",
        "run": "assets/sfx/combat/run.wav",
        "death": "assets/sfx/combat/death.wav",
        "enemy_death": "assets/sfx/combat/enemy_death.wav",
        "player_hit": "assets/sfx/combat/player_hit.wav",
        "bullet_burst": "assets/sfx/combat/bullet_burst.mp3",
        "posion_effect": "assets/sfx/combat/posion_effect.mp3",
        "burn_effect": "assets/sfx/combat/burn_effect.mp3",
        "zap1": "assets/sfx/combat/zap_sfx1.mp3",
        "zap2": "assets/sfx/combat/zap_sfx2.mp3",
        "zap3": "assets/sfx/combat/zap_sfx3.mp3",
        "overclock": "assets/sfx/combat/overclock.mp3",
        "gain_effect": "assets/sfx/combat/effect_gain.wav",
        "emergency": "assets/sfx/combat/emergency.mp3",
    }
    # boss phase change (7.11): put a file here; without it the "overclock" sound plays
    OPTIONAL_SFX = {"boss_phase": "assets/sfx/combat/boss_phase.wav",
                    "strike1": "assets/sfx/combat/bosses/garden/strike1.mp3",     # (8.11) Night Bloom's lightning
                    "strike2": "assets/sfx/combat/bosses/garden/strike2.mp3",
                    "mascot_laser": "assets/sfx/combat/bosses/mascot/laser.ogg",     # (10.11) the Mascot's song fight
                    "mascot_circle": "assets/sfx/combat/bosses/mascot/circle.ogg",
                    "mascot_square": "assets/sfx/combat/bosses/mascot/square.ogg",
                    "core_heart": "assets/sfx/combat/bosses/core/heart.ogg"}     # (10.11) Milo's fight: the heart (louder when faster)

    def __init__(self, sfx):
        for name, path in self.COMBAT_SFX.items():
            sfx.load_sfx(name, path)
        for name, path in self.OPTIONAL_SFX.items():       # used only if the file is there
            try:
                sfx.load_sfx(name, path)
            except (pygame.error, FileNotFoundError):
                pass

        self.font_light = {"small" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",18),
                           "mid" : pygame.font.Font("assets/font/Nexa-ExtraLight.ttf",36),}
        self.font_heavy = {"small" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",18),
                           "mid" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",36),
                           "giant" : pygame.font.Font("assets/font/Nexa-Heavy.ttf",128),}

        self.zap_segments = [pygame.transform.scale(pygame.image.load(f"assets/img/combat/zap/zap{nr}.png"),(64,64)) for nr in range(1,5)]
        # (8.11) the Frost Golem's ground crack: 30x10 pieces, drawn x2 along the crack (one fixed piece per spot)
        self.crack_segments = []
        for nr in range(1, 5):
            try:
                self.crack_segments.append(pygame.transform.scale(pygame.image.load(f"assets/img/combat/crack/crack{nr}.png").convert_alpha(), (60, 20)))
            except (pygame.error, FileNotFoundError):
                pass
        # Toxic Ring passing poison on: green zaps (assets/img/combat/zap/poison_zap1-4.png)
        self.poison_zap_segments = [pygame.transform.scale(pygame.image.load(f"assets/img/combat/zap/poison_zap{nr}.png"),(64,64)) for nr in range(1,5)]
        self.explosion_img = [pygame.image.load(f"assets/img/combat/projectiles/boom{nr}.png") for nr in range(1,7)]
        self.nova_explosion_img = [pygame.image.load(f"assets/img/combat/projectiles/nova_boom{nr}.png") for nr in range(1,7)]
        # the Mascot Plush on the battlefield (decoy.py): its own sprite, or a drawn placeholder if there is none
        plush = "assets/img/combat/decoy.png"
        self.decoy_img = pygame.image.load(plush).convert_alpha() if os.path.exists(plush) else None
