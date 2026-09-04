import pygame
from game.states import GameState
from game.combat.combat import Combat
from game.combat.player.shooter import Shooter
from game.map.map import Map
from game.map.map_ui import MapUI
from game.map.player import Player
from game.inventory.inventory import Inventory
from game.inventory.inventory_ui import Inventory_ui
from game.lib.sfx_manager import SFXManager
from game.lib.music_manager import MusicManager
from game.menu.menu import Menu
from game.menu.settings_manager import SettingsManager
from game.menu.save_manager import SaveManager


class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.font = pygame.font.SysFont(None, 60)
        self.state = GameState.MENU
        self.running = True
        self.clock = pygame.time.Clock()
        self.sfx = SFXManager()
        self.music = MusicManager()

        self.map = Map(self.screen)
        self.map_ui = MapUI(self.screen)
        self.player = Player(128,128,self.map)
        self.map.player = self.player
        self.map_ui.player = self.player

        self.player_in_combat = None
        self.combat = None

        self.inventory = Inventory(self.screen)
        self.inventory_ui = Inventory_ui(self.screen,self.inventory,self.sfx)

        self.save_manager = SaveManager(self.player, self.inventory, self.map)

        self.settings = SettingsManager(self.music, self.sfx)
        self.settings.settings_data_render()
        self.music.update_volume()
        self.sfx.update_volume()

        self.menu = Menu(self.screen,self.sfx,self.music, self.save_manager)
        self.music.play("menu")

        
        self.save = 0

    def run(self):
        while self.running:
            keys = pygame.key.get_pressed()
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    self.settings.settings_data_save()
                    self.save_manager.save_game(self.save)

            if self.state == GameState.MENU:
                self.update_menu(events, keys, mouse_pos)

            elif self.state == GameState.MAP:
                self.update_map(events, keys, mouse_pos)

            elif self.state == GameState.COMBAT:
                self.update_combat(events, keys)

            elif self.state == GameState.INVENTORY:
                self.update_inventory(events, mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def update_menu(self, events, keys, pos):
        change_state, save_nr = self.menu.handle_click(pos, events)
        self.menu.draw()
        if change_state == "start_game":
            self.save_manager.load_game(save_nr, self)
            print(self.inventory.active_items)
            self.inventory.active_weapon = self.inventory.active_items["weapon"]
            self.inventory.active_armor = self.inventory.active_items["armor"]
            self.inventory.active_trinket = self.inventory.active_items["trinket"]
            self.save = save_nr
            self.state = GameState.MAP
            self.music.stop()
            self.music.play(self.player.biome)
        elif change_state == "play":
            self.menu.page = "save_load"
        elif change_state == "achievements":
            self.menu.page = "achievements"
        elif change_state == "options":
            self.menu.page = "options"
        elif change_state == "main":
            self.menu.page = "main"
        elif change_state == "quit":
            self.settings.settings_data_save()
            self.running = False

    def update_map(self, events, keys, mouse_pos):
        change_state = self.map_ui.handle_click(mouse_pos,events)
        
        if self.map_ui.page == "map":
                    self.map.draw()
                    self.player.draw(self.screen)
                    fight = self.player.move(keys)

        self.map_ui.draw()
        
        if self.map_ui.page == "map" and fight not in (True,False):
            self.player_in_combat = Shooter(300,300,self.inventory.active_items)
        if self.map_ui.page == "map" and fight == "boss1":
            self.state = GameState.COMBAT
            self.combat = Combat(self.screen, self.player_in_combat,"boss1", "easy",self.sfx)
            self.music.stop()
            self.music.play("boss_fight1")
        if change_state == "inventory":
            self.state = GameState.INVENTORY
        elif change_state == "menu":
            self.state = GameState.MENU
            self.music.stop()
            self.music.play("menu")
            self.menu.page = "main"
            self.map_ui.page = "map"
        elif change_state == "quit":
            self.settings.settings_data_save()
            self.save_manager.save_game(self.save)
            self.running = False
        elif change_state == "save":
            self.settings.settings_data_save()
            self.save_manager.save_game(self.save)


    def update_combat(self, events, keys):

        mouse_btn_pressed = pygame.mouse.get_pressed()

        self.combat.handle_events(events, mouse_btn_pressed)
        self.combat.update()
        self.combat.draw()

        if self.combat.finished:
            self.state = GameState.MAP
            self.music.stop()
            self.music.play(self.player.biome)
            if self.combat.win:
                if self.combat.enemy == "boss1":
                    # self.map.layout[8] = self.map.layout[8][:8] + "1" + self.map.layout[8][8 + 1:]
                    self.player.money+=100
            else:
                self.player.set_position(128,128)
            self.player_in_combat = None
            

    def update_inventory(self, events, mouse_pos):
        self.inventory_ui.draw()
        change_state = self.inventory_ui.handle_click(mouse_pos, events)
        if change_state == "map":
            self.state = GameState.MAP
            self.inventory_ui.selected_slot = None
            self.inventory.selected_item = None
