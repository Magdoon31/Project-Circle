import pygame, math, random, hashlib
from game.states import GameState
from game.combat.combat import Combat
from game.combat.player.shooter import Shooter
from game.map.map import Map, BOSS_NAME, LEVEL_TITLES, LEVELS
from game.map.map_ui import MapUI
from game.map.world_map import WorldMap
from game.map.player import Player
from game.inventory.inventory import Inventory
from game.inventory.inventory_ui import Inventory_ui
from game.lib.sfx_manager import SFXManager
from game.lib.music_manager import MusicManager
from game.menu.menu import Menu
from game.menu.settings_manager import SettingsManager
from game.menu.save_manager import SaveManager
from game.combat.enemy.enemy_database import EnemyDB, SPAWNS
from game.combat.bullet_types import BulletTypes
from game.combat.combat_assets import CombatAssets
from game.dialogue.dialogue import Dialogue, DialogueContext, reserve_talk_channel
from game.dialogue.speakers import NPC_DIALOGUES
from game.quests import QuestLog, QUESTS
from game.minigames.memory import Memory
from game.minigames.sudoku import Sudoku
from game.minigames.wires import Wires
from game.minigames.fishing import Fishing
from game.minigames.wheel import Wheel
from game.world import loot
from game.story.milo import milo_npcs, path_locks, choose_path
from game.story.wren import wren_npcs, auto_npc_near
from game.story.garden import garden_npcs, PaleAltar
from game.story import ferris as FERRIS
from game.shop.shop import Shop
from game.shop.stock import ShopStock
from game.shop import stock as S
from game.inventory.sigils import Sigils, ALL_SIGILS, HAGGLER_PRICE, LUCKY_COIN_REROLLS, LUCKY_COIN_GOLD
from game.inventory import sigils as SG

ESCAPE_GRACE_FRAMES = 180   # after running away: no random fight for the next 3 s of walking

# MINIGAMES: the first game ever is free; after that every game costs coins, and the price grows with every WIN
# (base + step * wins) until it isn't worth it. Sudoku stays worth it longer (it's skill based).
MINIGAME_PRICES = {"memory": (4, 5), "sudoku": (8, 6), "fishing": (30, 0)}
# a break after playing: seconds of PLAY TIME (walking on the map + fights; not dialogues or menus)
MINIGAME_COOLDOWNS = {"fishing": 5 * 60}     # family: (base, step per win)

NO_FIGHT_LEVELS = {"lunapark"}       # no random fights there (the Mascot boss is still there)
MASCOT_PRIZE = "Mascot Plush"        # the Mascot (lunapark boss) gives this the first time it is beaten
LOCKED_PATH_MESSAGE = "This way is shut. Finish the path you chose first."
SHOP_KEY = pygame.K_b                     # opens the shop (game/shop) anywhere on the map, like the Shop button
VISIT_FLAG_ZONES = {"separated", "lunapark", "garden", "core", "candy", "factory"}   # flag "visited:<zone>" (the shopkeeper's mood)
NO_FIGHTS_BEFORE_FLAG = "talked:milo_village"     # monsters don't attack until the player has talked to Milo

INTRO_FRAMES = 180          # start of a NEW game: the world fades in from black (no dialogue, can't move)

# AUTOSAVE: after a won boss fight, after going through a portal, when leaving to the main menu,
# and every AUTOSAVE_MINUTES of walking on the map. 0 = no timed autosave.
AUTOSAVE_MINUTES = 3

# TEST ONLY: number keys teleport to a zone (biome itself comes from the tile). False before release.
DEBUG_BIOME_KEYS = True
BIOME_KEYS = {
    pygame.K_1: ("surface", "village"), pygame.K_2: ("surface", "rainbow_fields"), pygame.K_3: ("surface", "candy"),
    pygame.K_4: ("surface", "separated"), pygame.K_5: ("surface", "tundra"), pygame.K_6: ("surface", "tundra_pass"),
    pygame.K_7: ("cellar", "factory"), pygame.K_8: ("cellar", "garden"), pygame.K_9: ("core", "core"),
    pygame.K_MINUS: ("void", "void"),
}
# TEST ONLY: key 0 gives the story items (where they really come from is not decided yet)
DEBUG_STORY_ITEMS_KEY = pygame.K_0
STORY_ITEMS = ["Peace Gun", "Broken Bulb", "Cassette Tape", "Old Note",
               "Meter"]   # Meter: the Foreman's part from the shop - TEST ONLY until the shop exists
SECRET_HINTS = {"core_vault": "The gold is still lying on the ground"}   # bumping into a closed secret way
SELL_SHARE = 0.25           # the buyer pays 25% of the shop price
SIGIL_POPUP_FRAMES = 180    # "New Sigil" on the screen for 3 s
MINIGAME_FADE_MS = 800      # the music fades out this long before a minigame's countdown (then the minigame music)
# TEST ONLY: key F starts a normal fight right away (enemies of the biome you stand in)
DEBUG_FIGHT_KEY = pygame.K_f
PEACE_GUN = "Peace Gun"
LORE_ITEMS = ["Broken Bulb", "Cassette Tape", "Old Note"]   # all 3 used at NPCs -> Secret Ending (Void boss)

# TEMPORARY ending screens (the real endings come later)
ENDINGS = {
    "main": ("MAIN ENDING", "(work in progress)"),
    "extra": ("EXTRA ENDING", "(work in progress)"),
    "secret": ("SECRET ENDING", "(work in progress)"),
}


class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.font = pygame.font.SysFont(None, 60)
        self.state = GameState.MENU
        self.running = True
        self.clock = pygame.time.Clock()
        reserve_talk_channel()         # before any sound plays: one mixer channel only for dialogue talk sounds
        self.sfx = SFXManager()
        self.music = MusicManager()

        self.map = Map(self.screen)
        self.map_ui = MapUI(self.screen, self.sfx)
        self.world_map = WorldMap(self.screen)
        self.shop = None               # Shop screen, made on first use (needs the item database)
        self.shop_stock = None
        self.player = Player(128,128,self.map)
        self.map.player = self.player
        self.map_ui.player = self.player

        self.player_in_combat = None
        self.combat = None
        # loaded once here and shared - not on every fight
        self.bullet_type_info = BulletTypes()
        self.combat_assets = CombatAssets(self.sfx)
        self.enemy_db = EnemyDB(self.sfx, self.bullet_type_info)

        self.hard_mode = False
        self.timer = 0

        self.inventory = Inventory(self.screen)
        self.map.item_db = self.inventory.ItemDB   # item icons lying on the map
        self.sigils = Sigils()         # permanent upgrades (game/inventory/sigils.py), saved in counters["sigils"]
        self.inventory_ui = Inventory_ui(self.screen,self.inventory,self.sfx)
        self.inventory_ui.sigils = self.sigils

        self.save_manager = SaveManager(self.player, self.inventory, self.map)

        self.settings = SettingsManager(self.music, self.sfx)
        self.settings.settings_data_render()
        self.music.update_volume()
        self.sfx.update_volume()

        self.menu = Menu(self.screen,self.sfx,self.music, self.save_manager)
        self.music.play("menu_intro")
        
        self.save = 0
        self.active_boss_gate = None   # gate whose boss is being fought
        self.current_music = None
        self.last_portal = None
        self.autosave_timer = 0        # frames on the map since the last save
        self.dialogue = None           # the conversation running right now (full screen over the map)
        self.minigame = None           # minigame started from a dialogue (memory, sudoku)
        self.minigame_music = None     # "waiting" (countdown) -> "playing" -> "done" (result shown)
        self.minigame_keeps_music = False   # True for minigames that keep the biome music (fishing)
        self.minigame_fade = 0         # frames the biome music still fades out before the minigame starts
        self.quests = QuestLog()
        self.counters = {}             # saved numbers, e.g. "memory_plays", "sudoku_wins"
        self.map_ui.quests = self.quests        # short quest list on the map, under the Menu button
        self.intro_frames = 0
        self.talk_npc = None           # NPC close enough to talk to (E)
        self.last_boss = None          # boss touched last frame - a fight starts only when you walk INTO a boss
        self.trinket_effects = {}
        self.sigil_popup = None        # [sigil id, frames left] - "New Sigil" in the middle of the map screen
        self.sigil_queue = []          # more sigils found at once (shown one after another)

        self.sfx.load_sfx("use", "assets/sfx/UI/use.wav")
        for name, path in (("coin_pickup", "assets/sfx/map/coin_pickup.mp3"), ("buy", "assets/sfx/map/buy.wav"),
                           ("buy_minigame", "assets/sfx/minigames/buy_minigame.wav"),
                           ("bonus1", "assets/sfx/map/bonus1.wav"), ("bonus2", "assets/sfx/map/bonus2.wav"),
                           ("new_item", "assets/sfx/UI/new_item.wav"),
                           ("sigil_pickup", "assets/sfx/map/sigil_pickup.wav")):
            try:
                self.sfx.load_sfx(name, path)
            except (pygame.error, FileNotFoundError):
                pass
        for path in ("assets/sfx/map/pale_orb.wav", "assets/sfx/map/pale_orb_equip.wav"):   # the Pale Orb shows up
            try:
                self.sfx.load_sfx("pale_orb", path)
                break
            except (pygame.error, FileNotFoundError):
                pass
        self.pale_altar = PaleAltar()

    def run(self):
        while self.running:
            self.trinket_effects = {}           # both trinkets (the 2nd one: Spare Pocket sigil)
            for t in (self.inventory.active_trinket2, self.inventory.active_trinket):
                if t:
                    self.trinket_effects.update(t.effect)
            self.timer += 1
            self.music.update()            # crossfades (e.g. into the shop and back)
            self.counters["sigils"] = self.sigils.to_dict()     # sigils are saved with the game (counters)
            keys = pygame.key.get_pressed()
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    self.settings.settings_data_save()
                    self.save_manager.save_game(self.save, self.hard_mode)

            if self.state == GameState.MENU:
                self.update_menu(events, keys, mouse_pos)
                if self.timer == 254:
                    self.music.stop("menu_intro")
                    self.music.play("menu_loop")

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
        change_state, save_nr, self.hard_mode = self.menu.handle_click(pos, events)
        self.menu.draw()
        if change_state == "start_game":
            # making the world takes ~1 s - show something meanwhile (a saved world is rebuilt, a new one generated)
            self.screen.fill((0, 0, 0))
            text = "Loading terrain..." if self.save_manager.has_world(save_nr) else "Generating world..."
            loading = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(loading, loading.get_rect(center=self.screen.get_rect().center))
            pygame.display.flip()

            self.save_manager.load_game(save_nr, self)
            self.inventory.active_weapon = self.inventory.active_items["weapon"]
            self.inventory.active_armor = self.inventory.active_items["armor"]
            self.inventory.active_trinket = self.inventory.active_items["trinket"]
            self.inventory.active_trinket2 = self.inventory.active_items.get("trinket2")
            self.sigils.load(self.counters.get("sigils"))
            self.inventory.pocket = self.sigils.on("spare_pocket")

            self.save = save_nr
            self.state = GameState.MAP
            self.dialogue = self.minigame = None
            self.intro_frames = INTRO_FRAMES if self.save_manager.started_new else 0

            self.player.biome = self.map.biome_at(self.player.x, self.player.y) or "village"
            self.current_music = self.player.biome
            self.last_portal = None
            self.music.stop()
            self.music.play(self.player.biome)
            self.timer = 0

        elif change_state == "quit":

            self.settings.settings_data_save()
            self.running = False

    def update_map(self, events, keys, mouse_pos):
        self.refresh_talk_background()
        # a minigame from a dialogue: it takes all input; afterwards the dialogue goes on
        if self.minigame:
            if self.minigame_fade > 0:                    # the music goes quiet first, then the countdown starts
                self.minigame_fade -= 1
                self.screen.blit(self.dialogue.background, (0, 0))
                return
            self.minigame.handle_events(events)
            self.minigame.update()
            self.minigame.draw()
            if self.music.has("minigame") and not self.minigame_keeps_music:
                if self.minigame_music == "waiting" and not self.minigame.counting_down and self.minigame.result is None:
                    self.music.play("minigame")               # countdown over: the music starts
                    self.minigame_music = "playing"
                elif self.minigame_music == "playing" and self.minigame.result is not None:
                    self.music.stop()                         # game over: the music stops
                    self.minigame_music = "done"
            if self.minigame.finished:
                won = self.minigame.won
                reward = getattr(self.minigame, "reward", 0)     # minigames that pay out themselves (fishing)
                if getattr(self.minigame, "won_sigil", None):     # Lucky's wheel: the "?" field
                    self.award_sigil(self.minigame.won_sigil)
                family = self.minigame_family
                self.minigame = None
                if self.music.has("minigame") and not self.minigame_keeps_music:   # back to the dialogue / biome music
                    self.music.stop()
                    self.music.play(self.dialogue.music if self.music.has(self.dialogue.music) else self.player.biome)
                    self.current_music = self.player.biome
                if won:
                    self.counters[f"{family}_wins"] = self.counters.get(f"{family}_wins", 0) + 1
                if reward:                                    # e.g. the wheel's x0.5 pays back even when "lost"
                    self.player.money += reward
                    self.sfx.play("coin_pickup")
                    self.map_ui.show_message(f"+{reward}$", 90)
                self.dialogue.resume(won)
            return
        # a conversation is running: it takes all input, the world is paused
        if self.dialogue and self.dialogue.pending_minigame:
            self.start_minigame(self.dialogue.pending_minigame)
            return
        if self.dialogue:
            self.dialogue.handle_events(events)
            horror = self.dialogue.horror and not self.dialogue.finished
            if horror != getattr(self, "music_muted", False):
                self.music.mute(horror)
                self.music_muted = horror
            if not self.dialogue.finished:
                self.dialogue.update()
                self.dialogue.draw()
                return
            if self.music.has(self.dialogue.music):           # dialogue music -> back to the biome music
                self.music.stop()
                self.music.play(self.player.biome)
            self.dialogue = None
            self.player.encounter_grace = ESCAPE_GRACE_FRAMES     # no fight right after talking
            if getattr(self, "after_talk", None) == "shortcuts":     # Ferris: his shortcut map
                self.after_talk = None
                self.open_world_map(ferris=True)
                return
            events = []                  # the key that closed the talk (e.g. "2" for an answer) must not reach the map
        # world map (M) open: it takes all input, the game world is paused
        if self.world_map.is_open:
            if self.world_map.handle_events(events, self.map):
                self.world_map.close()
                if self.world_map.teleport_request:
                    self.debug_teleport(*self.world_map.teleport_request)
                    return
                if self.world_map.shortcut_request:
                    self.use_shortcut(self.world_map.shortcut_request)
                    return
            self.world_map.draw(self.map)
            return
        # the shop: its own screen, the world waits
        if self.shop and self.shop.is_open:
            self.update_shop(events, mouse_pos)
            return
        if self.map_ui.page == "map" and any(e.type == pygame.KEYDOWN and e.key == SHOP_KEY for e in events):
            self.open_shop()
            return
        if self.map_ui.page == "map" and any(e.type == pygame.KEYDOWN and e.key == pygame.K_m for e in events):
            self.open_world_map()
            return

        change_state = self.map_ui.handle_click(mouse_pos,events)
        on_map = self.map_ui.page == "map"

        if DEBUG_BIOME_KEYS and on_map:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key in BIOME_KEYS:
                    self.teleport_to_zone(*BIOME_KEYS[event.key])
                elif event.type == pygame.KEYDOWN and event.key == DEBUG_STORY_ITEMS_KEY:
                    owned = self.owned_item_names()
                    self.give_items([self.inventory.ItemDB.get_item(n) for n in STORY_ITEMS if n not in owned])
                    for sigil in ALL_SIGILS:                 # TEST: all sigils too
                        self.sigils.give(sigil)
                    self.counters["sigils"] = self.sigils.to_dict()
                    self.map_ui.show_message("TEST: story items + all sigils", 120)
                elif event.type == pygame.KEYDOWN and event.key == DEBUG_FIGHT_KEY and not self.dialogue:
                    if self.player.biome in SPAWNS and self.map.level not in NO_FIGHT_LEVELS:
                        self.start_fight()
                        return
                    self.map_ui.show_message("TEST: no fights here", 90)

        event = None
        if on_map and self.intro_frames > 0:
            # start of a new game: the world fades in from black, the player waits
            self.intro_frames -= 1
            self.map.reveal_around_player()
            self.map.draw()
            self.player.draw(self.screen)
            self.map.draw_overlay()
            fade = pygame.Surface(self.screen.get_size())
            fade.set_alpha(int(255 * min(1.0, self.intro_frames / (INTRO_FRAMES * 0.75))))
            self.screen.blit(fade, (0, 0))
            return
        if on_map:
            self.autosave_timer += 1
            if AUTOSAVE_MINUTES and self.autosave_timer >= AUTOSAVE_MINUTES * 60 * 60:
                self.autosave()
            # trinket "map_memory" (Eyeballs): seconds the world map remembers places in the Void
            self.map.memory_bonus_ms = self.trinket_effects.get("map_memory", [0])[0] * 1000
            if NO_FIGHTS_BEFORE_FLAG not in self.map.flags:
                self.player.encounter_grace = max(self.player.encounter_grace, 2)   # no monsters before talking to Milo
            self.map.confine = self.start_confine()
            self.map.confine_hit = False
            self.update_story()
            self.map.lock_hit = False
            self.map.secret_hit = None
            event = self.player.move(keys)
            if self.map.confine_hit and self.map_ui.message_timer <= 0:
                self.map_ui.show_message("Maybe talk to Milo first...", 120)
            elif self.map.lock_hit and self.map_ui.message_timer <= 0:
                self.map_ui.show_message(LOCKED_PATH_MESSAGE, 150)
            elif self.map.secret_hit and self.map_ui.message_timer <= 0:
                self.map_ui.show_message(SECRET_HINTS.get(self.map.secret_hit, "..."), 150)
            self.map.reveal_around_player()
            self.map.draw()
            self.player.draw(self.screen)
            self.map.draw_overlay()          # e.g. cellar darkness - under the UI
            auto = auto_npc_near(self.map.npcs(), self.map.tile_at(self.player.x, self.player.y))
            if auto:
                self.start_dialogue(auto)                 # e.g. the overheard Wren x Milo argument
                return
            self.talk_npc = self.map.npc_near(self.player.x, self.player.y, self.player.radius)
            if self.talk_npc:
                self.map.draw_talk_prompt(self.talk_npc)
                if any(e.type == pygame.KEYDOWN and e.key == pygame.K_e for e in events):
                    self.start_dialogue(self.talk_npc)
            self.check_map_contacts()
            if self.pale_altar.update(self):               # "Only the innocent may see what is true."
                if "pale_orb" in self.sfx.sfx:
                    self.sfx.play("pale_orb")
                self.map_ui.show_message("Something pale appears on the stone.", 150)
            # music follows the biome of the tile the player stands on
            if self.player.biome != self.current_music:
                self.current_music = self.player.biome
                self.music.stop()
                self.music.play(self.player.biome)

        self.map_ui.draw()
        self.draw_sigil_popup()

        if self.dialogue:
            pass                                         # a talk just started - no fight this frame
        elif on_map and event == "fight" and self.map.level not in NO_FIGHT_LEVELS:
            self.start_fight()
        elif on_map and self.state == GameState.MAP:
            gate = self.map.boss_at(self.player.x, self.player.y, self.player.radius)
            if gate and gate is not self.last_boss:
                self.start_boss_fight(gate)
            self.last_boss = gate

        if change_state == "inventory":

            self.state = GameState.INVENTORY
            self.inventory_ui.page = "items"         # always opens on the items, not on the sigils

        elif change_state == "shop":

            self.open_shop()

        elif change_state == "menu":

            self.autosave(show=False)
            self.state = GameState.MENU
            self.music.stop()
            self.timer = 0
            self.music.play("menu_intro")

            self.menu.page = "main"
            self.map_ui.page = "map"

        elif change_state == "quit":

            self.settings.settings_data_save()
            self.save_manager.save_game(self.save, self.hard_mode)
            self.running = False

        elif change_state == "save":

            self.settings.settings_data_save()
            self.save_manager.save_game(self.save, self.hard_mode)
            self.autosave_timer = 0
            self.map_ui.show_saved("Game saved")

    def autosave(self, show=True):
        # saves into the current slot; a small "Saving..." note in the corner (doesn't hide other messages)
        if self.save not in (1, 2, 3):
            return
        self.save_manager.save_game(self.save, self.hard_mode)
        self.settings.settings_data_save()
        self.autosave_timer = 0
        if show:
            self.map_ui.show_saved()


    def update_combat(self, events, keys):

        mouse_btn_pressed = pygame.mouse.get_pressed()

        self.combat.handle_events(events, mouse_btn_pressed)
        self.combat.update()
        self.player.play_time += 1 / 60          # fights count as play time too (e.g. minigame breaks)
        self.combat.draw()

        if self.combat.finished and self.combat.escaped:
            # ran away: straight back to the map, no reward, no penalty, a short break from random fights
            self.music.stop()
            self.state = GameState.MAP
            self.music.play(self.player.biome)
            self.player.encounter_grace = ESCAPE_GRACE_FRAMES
            self.map_ui.show_message("You got away!", 90)
            self.player_in_combat = None
            return

        if self.combat.finished:
            self.music.stop()
            if not self.combat.win:
                self.combat.sfx.play("death")

            end_screen = True
            i = 1

            while end_screen:
                i += 1
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN and i > 30:
                        end_screen = False
                    elif event.type == pygame.QUIT:
                        end_screen = False
                        self.running = False
                        self.settings.settings_data_save()
                self.combat.draw()
                self.clock.tick(60)   # without this the loop runs as fast as possible (100% CPU)

            self.state = GameState.MAP
            self.music.play(self.player.biome)
            self.after_fight_sigils(self.combat.win)
            if self.combat.win:
                self.give_items([self.inventory.ItemDB.get_item(name) for name in self.combat.loot])
                if self.combat.boss:
                    self.player.money += int(self.combat.money * self.fight_gold_mult())
                    # beaten boss disappears (until the next normal fight), its gate opens for good
                    gate = self.active_boss_gate
                    self.map.beat_boss(gate)
                    self.map.refresh_overview_gates()
                    self.active_boss_gate = None
                    self.after_boss(gate)
                    self.autosave()
                else:
                    self.player.money += int(self.combat.money * self.combat.money_mult * self.fight_gold_mult())
                    wins = self.counters.setdefault("biome_wins", {})          # (7.11) won normal fights per biome (shop rares)
                    wins[self.player.biome] = wins.get(self.player.biome, 0) + 1
            else:
                # lost: back to the village start (on the surface)
                if self.map.level != "surface":
                    self.map.switch_level("surface")
                self.player.set_position(*self.map.start_position())
                self.active_boss_gate = None
            self.player_in_combat = None
            

    def after_boss(self, gate):
        # what beating a boss does (story bosses are marked by "name" in the gate)
        self.map.flags.add(f"boss:{gate['from']}")         # e.g. "boss:candy" - dialogues can react to it
        if gate.get("name") == "Milo":
            weapon = self.inventory.active_weapon
            if weapon is not None and weapon.name == PEACE_GUN:
                self.map.flags.add("void_unlocked")
                self.map_ui.show_message("Something opened beneath the core...")
            else:
                self.show_ending("main")
        elif gate.get("name") == "Mascot":
            if "mascot:prize" not in self.map.flags:          # the prize only once (it respawns for grinding)
                self.map.flags.add("mascot:prize")
                self.give_item(self.inventory.ItemDB.get_item(MASCOT_PRIZE))
        elif gate.get("name") == "Void":
            self.show_ending("secret" if self.secret_ending_ready() else "extra")
        elif gate["cells"]:
            self.map_ui.show_message("The passage is open!")

    def secret_ending_ready(self):
        # the 3 lore items must be USED at NPCs during the game (author's idea, not made yet).
        # Each use will set a flag "lore_used:<item>" - until then this is always False -> Extra Ending.
        return all(f"lore_used:{name}" in self.map.flags for name in LORE_ITEMS)

    def show_ending(self, kind):
        # TEMPORARY ending screen: title + "work in progress", click (after 1 s) to go back to the game
        title, subtitle = ENDINGS[kind]
        small = pygame.font.SysFont(None, 40)
        self.music.stop()
        frames = 0
        while True:
            frames += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.settings.settings_data_save()
                    return
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN) and frames > 60:
                    self.music.play(self.player.biome)
                    return
            self.screen.fill((0, 0, 0))
            centre = self.screen.get_rect().center
            for text, font, colour, dy in ((title, self.font, (255, 255, 255), -40), (subtitle, small, (170, 170, 170), 20),
                                           ("click to continue", small, (110, 110, 110), 120)):
                img = font.render(text, True, colour)
                self.screen.blit(img, img.get_rect(center=(centre[0], centre[1] + dy)))
            pygame.display.flip()
            self.clock.tick(60)

    def refresh_talk_background(self):
        """The dimmed map behind a talk / minigame is a picture - when the money changes (paying, a prize)
        it is drawn again, so the money in the corner is always the money now."""
        if not self.dialogue or self.dialogue.background_money == self.player.money:
            return
        self.map.draw()
        self.player.draw(self.screen)
        self.map.draw_overlay()
        self.map_ui.draw()
        self.dialogue.set_background(self.screen)
        if self.minigame:
            self.minigame.background = self.dialogue.background

    def start_dialogue(self, npc):
        dialogue_id = npc.get("dialogue") or NPC_DIALOGUES.get(npc["id"])
        if not dialogue_id:
            self.map_ui.show_message("...", 90)            # this NPC has nothing to say yet
            return
        self.player.vx = self.player.vy = 0.0
        self.map_ui.draw()                               # the dimmed background includes the UI as it is now
        context = DialogueContext(
            has_flag=lambda f: f in self.map.flags, set_flag=self.map.flags.add, clear_flag=self.map.flags.discard,
            has_item=lambda name: name in self.owned_item_names(),
            give_item=lambda name: self.give_item(self.inventory.ItemDB.get_item(name)),
            take_item=self.take_item,
            quests=self.quests, add_gold_piles=self.add_gold_piles, seed_choice=self.seed_choice,
            on_new_quest=lambda q: self.map_ui.show_quest_note(f"New Quest: {QUESTS[q]['title']}"),
            format_text=self.dialogue_text,
            reveal_zone=self.reveal_map_zone,
            get_money=lambda: self.player.money, pay=self.pay,
            get_counter=lambda name: self.counters.get(name, 0),
            count_item=lambda name: self.owned_item_counts().get(name, 0),
            add_counter=lambda name: self.counters.__setitem__(name, self.counters.get(name, 0) + 1),
            on_quest_done=lambda q: self.map_ui.show_quest_note(f"Quest complete: {QUESTS[q]['title']}"),
            give_sigil=self.award_sigil, open_screen=lambda name: setattr(self, "after_talk", name))
        self.dialogue = Dialogue(self.screen, dialogue_id, context, self.sfx.sfx_volume)
        if self.music.has(self.dialogue.music):               # PLACEHOLDER: no dialogue music file yet -> biome music stays
            self.music.stop()
            self.music.play(self.dialogue.music)

    def minigame_price(self, family):
        if family not in MINIGAME_PRICES:
            return 0                                         # quest minigames (Hal's wires) are always free
        if not self.counters.get(f"{family}_plays"):
            return 0                                         # the first game is free
        holder_game = {"bramble": "sudoku", "dot": "memory"}[self.seed_choice("hook_holder", ["bramble", "dot"])]
        if self.quests.active.get("hook") == "find" and family == holder_game:
            return 0                                         # the Hook game is free while looking for it (no soft-lock)
        base, step = MINIGAME_PRICES[family]
        return base + step * self.counters.get(f"{family}_wins", 0)

    def minigame_resting(self, family):
        # True while the minigame is on its break (MINIGAME_COOLDOWNS)
        return self.player.play_time < self.counters.get(f"{family}_ready_at", 0)

    def start_minigame(self, spec):
        kind = spec["type"]
        family = kind.split("_")[0]
        if self.minigame_resting(family):
            self.dialogue.resume_at(spec.get("resting", "end"))    # e.g. Oliver: "The fish need a rest."
            return
        # Lucky's wheel: the price is the stake ("wheel_50" = 50$)
        price = int(kind.split("_")[1]) if family == "wheel" else self.minigame_price(family)
        if price > self.player.money:
            self.dialogue.resume_at(spec.get("poor", "end"))      # not enough coins
            return
        self.player.money -= price
        if price:
            self.map_ui.show_message(f"-{price}$", 90)
            self.sfx.play("buy_minigame")
        if family in MINIGAME_COOLDOWNS:
            self.counters[f"{family}_ready_at"] = self.player.play_time + MINIGAME_COOLDOWNS[family]
        self.minigame_keeps_music = family in ("fishing", "wheel")   # the biome music just keeps playing
        self.minigame_fade = 0
        if self.music.has("minigame") and not self.minigame_keeps_music:   # music fades out, silence during the countdown
            self.music.fade_out(MINIGAME_FADE_MS)
            self.minigame_fade = MINIGAME_FADE_MS * 60 // 1000
        self.minigame_music = "waiting"
        self.counters[f"{family}_plays"] = self.counters.get(f"{family}_plays", 0) + 1
        self.minigame_family = family
        volume = self.sfx.sfx_volume
        if kind == "memory":
            self.minigame = Memory(self.screen, self.dialogue.background, volume)
        elif kind.startswith("sudoku"):
            # a hard puzzle takes a moment to make
            self.screen.blit(self.dialogue.background, (0, 0))
            text = self.font.render("Bramble is writing a puzzle...", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=self.screen.get_rect().center))
            pygame.display.flip()
            self.minigame = Sudoku(self.screen, self.dialogue.background, kind.split("_", 1)[1], volume)
        elif kind == "fishing":                           # Oliver's ice hole: one cast per payment
            self.minigame = Fishing(self.screen, self.dialogue.background, volume)
        elif family == "wheel":                           # Lucky's wheel of fortune (stake in the name)
            self.minigame = Wheel(self.screen, self.dialogue.background, int(kind.split("_")[1]), volume,
                                  sigil=None if "haggler" in self.sigils.owned else "haggler")   # the "?" field
        elif kind.startswith("wires"):                    # "wires_5" = Hal's antenna with 5 wires
            self.minigame = Wires(self.screen, self.dialogue.background, int(kind.split("_")[1]), volume)
        else:
            self.dialogue.resume(False)

    def luck(self):
        """The player's luck: Dices (trinket) + Lucky Charm (sigil). Used by the shop shelves and enemy drops (loot.py)."""
        return self.trinket_effects.get("luck", [0])[0] + (1 if self.sigils.on("lucky_charm") else 0)

    def fight_gold_mult(self):
        return LUCKY_COIN_GOLD if self.sigils.on("lucky_coin") else 1.0      # Lucky Coin sigil

    # --- the shop ----------------------------------------------------------------------------------
    # --- sigils (7.11): how they are found - see game/inventory/sigils.py and the project's SIGILS.md --------
    def award_sigil(self, sigil_id):
        """The player finds a sigil: sound + "New Sigil" in the middle of the screen (not switched on by itself)."""
        if not self.sigils.give(sigil_id):
            return False
        self.counters["sigils"] = self.sigils.to_dict()
        self.sfx.play("sigil_pickup")
        self.sigil_queue.append(sigil_id)
        return True

    def after_fight_sigils(self, won):
        combat, biome = self.combat, self.player.biome
        if "firefly_dash" in combat.feats:
            self.award_sigil("lucky_coin")
        if biome == "the_core" and combat.near_misses >= SG.NEAR_MISSES:
            self.award_sigil("bullet_time")
        hp = self.player_in_combat.hp if self.player_in_combat else 0
        if won and biome == "silverpine_tundra" and 0 < hp <= self.player_in_combat.max_hp * SG.CLOSE_CALL_HP:
            self.award_sigil("close_call")

    def draw_sigil_popup(self):
        if not self.sigil_popup and self.sigil_queue:
            self.sigil_popup = [self.sigil_queue.pop(0), SIGIL_POPUP_FRAMES]
        if not self.sigil_popup:
            return
        sigil_id, left = self.sigil_popup
        self.sigil_popup[1] -= 1
        if self.sigil_popup[1] <= 0:
            self.sigil_popup = None
        t = SIGIL_POPUP_FRAMES - left
        alpha = int(255 * min(1.0, t / 20, left / 30))
        sw, sh = self.screen.get_size()
        size = sh // 5
        column = SG.COLUMN_OF[sigil_id]
        layer = pygame.Surface((sw, sh), pygame.SRCALPHA)
        img = self.inventory_ui.sigil_image(SG.IMAGE_OF[sigil_id], size, SG.COLUMN_COLOURS[column])
        centre = (sw // 2, sh // 2 - sh // 20)
        pygame.draw.circle(layer, (25, 15, 40, 170), centre, int(size * 0.8))
        if img:
            layer.blit(img, img.get_rect(center=centre))
        title = self.font.render("New Sigil", True, (220, 205, 250))
        name = self.font.render(SG.NAMES[sigil_id], True, SG.COLUMN_COLOURS[column])
        layer.blit(title, title.get_rect(center=(sw // 2, centre[1] + int(size * 0.9))))
        layer.blit(name, name.get_rect(center=(sw // 2, centre[1] + int(size * 0.9) + title.get_height() + 6)))
        layer.set_alpha(alpha)
        self.screen.blit(layer, (0, 0))

    # --- Ferris's shortcuts (7.11, game/story/ferris.py) and selling (shop, Sell page) -----------------------
    def open_world_map(self, ferris=False):
        owned = self.counters.get("shortcuts", [])
        shortcuts = []
        for sc, have in FERRIS.available(self.map.flags, owned):
            if sc["level"] not in self.map.viewable_levels() and sc["level"] != self.map.level:
                continue
            world = self.map.world if sc["level"] == self.map.level else self.map.view(sc["level"]).world
            shortcuts.append({**sc, "tile": FERRIS.tile_of(sc, world), "owned": have, "price": FERRIS.price(sc)})
        self.world_map.shortcuts = shortcuts
        self.world_map.get_money = lambda: self.player.money
        self.world_map.open(self.map, ferris=ferris)
        self.player.vx = self.player.vy = 0.0
        self.world_map.draw(self.map)

    def use_shortcut(self, shortcut_id):
        sc = FERRIS.BY_ID[shortcut_id]
        owned = self.counters.setdefault("shortcuts", [])
        if shortcut_id not in owned:
            cost = FERRIS.price(sc)
            if self.player.money < cost:
                return
            self.player.money -= cost
            owned.append(shortcut_id)
            message = "Ferris drops you off and is gone."
        else:
            message = "You take the shortcut."
        world = self.map.world if sc["level"] == self.map.level else self.map.view(sc["level"]).world
        tile = FERRIS.tile_of(sc, world)
        if tile is None:
            return
        self.debug_teleport(sc["level"], tile)          # (the same jump as the test teleport: nearest free tile)
        self.map_ui.show_message(message, 150)
        self.autosave()

    def sell_price(self, name):
        """What the buyer pays (None = he won't take it: story / quest items, things with no biome)."""
        biome = next((b for b, items in loot.ITEMS_BY_BIOME.items() if name in items), None)
        if biome is None or name in loot.NOT_RANDOM:
            return None
        return S.round10(S.price_of(name, biome) * SELL_SHARE)

    def sell_item(self, item, price):
        self.inventory.remove_item(item)
        if self.inventory.selected_item is item:
            self.inventory.selected_item = None
        self.player.money += price

    def open_shop(self):
        if NO_FIGHTS_BEFORE_FLAG not in self.map.flags:
            self.map_ui.show_message("Maybe talk to Milo first...", 120)
            return
        if self.shop is None:
            self.shop = Shop(self.screen, self.inventory.ItemDB, self.sfx.sfx_volume)
        self.player.vx = self.player.vy = 0.0
        self.shop_stock = ShopStock(self.counters.get("shop"))
        self.shop.volume = self.sfx.sfx_volume
        self.shop.open(self.shop_stock, {
            "flags": self.map.flags, "owned": set(self.owned_item_names()), "active_quests": set(self.quests.active),
            "level": self.map.level, "get_money": lambda: self.player.money,
            "pay": lambda amount: setattr(self.player, "money", max(0, self.player.money - amount)),
            "give": lambda name: self.give_item(self.inventory.ItemDB.get_item(name)),
            "inventory_full": self.inventory.is_full, "play_sfx": self.sfx.play,
            "price_mult": HAGGLER_PRICE if self.sigils.on("haggler") else 1.0,              # Haggler sigil
            "extra_rerolls": LUCKY_COIN_REROLLS if self.sigils.on("lucky_coin") else 0,      # Lucky Coin sigil
            "luck": self.luck(), "wins": self.counters.get("biome_wins", {}),
            "can_sell": "boss:rainbow_fields" in self.map.flags,                 # the Sell page (7.11)
            "inventory": lambda: list(self.inventory.items), "sell_price": self.sell_price, "sell": self.sell_item})
        self.counters["shop"] = self.shop_stock.to_dict()
        self.music.fade_to("shop")

    def update_shop(self, events, mouse_pos):
        leave = self.shop.handle_events(events, mouse_pos)
        self.shop.update()
        self.shop.draw()
        self.counters["shop"] = self.shop_stock.to_dict()       # saved with the game (shelves, rerolls)
        if leave:
            self.shop.close()
            self.music.fade_back()
            self.player.encounter_grace = ESCAPE_GRACE_FRAMES     # no fight the moment you step out

    def update_story(self):
        # Milo's place and the path locks depend on the level, beaten bosses and where the player stands
        tx, ty = self.map.tile_at(self.player.x, self.player.y)
        w = self.map.world
        zone = w.zones[ty][tx] if 0 <= tx < w.width and 0 <= ty < w.height else None
        if zone in VISIT_FLAG_ZONES:
            self.map.flags.add(f"visited:{zone}")          # e.g. the shopkeeper gets calmer after the Separated Village
        new_path = choose_path(self.map.level, self.map.flags, zone)
        if new_path:
            self.map.flags.add(new_path)                  # the first way walked into = the chosen path
        key = (self.map.level, id(w), frozenset(f for f in self.map.flags if f.startswith(("boss:", "path:", "wren:", "ring:"))), zone)
        if key == getattr(self, "_story_key", None):
            return
        self._story_key = key
        extra, hidden = milo_npcs(self.map.level, w, self.map.flags)
        extra, wren_hidden = wren_npcs(self.map.level, w, self.map.flags, extra)    # Wren (and Milo arguing with her)
        extra, garden_hidden = garden_npcs(self.map.level, w, self.map.flags, extra)  # the whisper in the mushroom ring
        extra, _ = FERRIS.ferris_npcs(self.map.level, w, self.map.flags, extra)       # Ferris (shortcuts) in the Village
        self.map.extra_npcs, self.map.hidden_npcs = extra, hidden | wren_hidden | garden_hidden
        self.map.locked_gates, self.map.locked_portals = path_locks(self.map.level, w, self.map.flags, zone)
        self.map.refresh_npcs()

    def start_confine(self):
        # before the first talk with Milo the player stays inside the fenced square around the start
        if NO_FIGHTS_BEFORE_FLAG in self.map.flags or self.map.level != "surface":
            return None
        rect = getattr(self.map.world, "start_fence", None)
        if not rect:
            return None
        tx, ty = self.map.tile_at(self.player.x, self.player.y)
        x, y, w, h = rect
        return rect if x <= tx < x + w and y <= ty < y + h else None     # (not after a test teleport elsewhere)

    def pay(self, amount):
        self.player.money = max(0, self.player.money - amount)
        self.map_ui.show_message(f"-{amount}$", 90)
        self.sfx.play("buy")

    def reveal_map_zone(self, level, zone):
        self.map.reveal_zone(level, zone)
        self.map_ui.show_quest_note(f"Map updated: {zone.replace('_', ' ').title()}")

    def dialogue_text(self, text):
        # placeholders in dialogue texts: {price:memory}, {price:sudoku}
        if "{price:" in text:
            for family in MINIGAME_PRICES:
                price = self.minigame_price(family)
                shown = "come back later" if self.minigame_resting(family) else ("free" if price == 0 else f"{price}$")
                text = text.replace(f"{{price:{family}}}", shown)
        return text

    def add_gold_piles(self, piles):
        # reward from dialogues: n "piles" of gold of the biome the player is in (same ranges as gold on the ground)
        biome = self.player.biome if self.player.biome in loot.GOLD_RANGES else "village"
        amount = sum(loot.roll_gold(biome, random) for _ in range(piles))
        self.player.money += amount
        self.map_ui.show_message(f"+{amount}$", 120)
        self.sfx.play(random.choice(["bonus1", "bonus2"]))

    def seed_choice(self, key, options):
        # the same pick for the same world (e.g. who in the Village has the Angler's Hook)
        digest = hashlib.sha256(f"{self.map.seed}:{key}".encode()).digest()
        return options[int.from_bytes(digest[:4], "big") % len(options)]

    def take_item(self, name):
        # removes one item with this name (from the grid first, then from what is equipped)
        for item in self.inventory.items:
            if item.name == name:
                self.inventory.remove_item(item)
                return True
        for slot, item in self.inventory.active_items.items():
            if item is not None and item.name == name:
                self.inventory.active_items[slot] = None
                setattr(self.inventory, f"active_{slot}", None)
                return True
        return False

    def owned_item_counts(self):
        counts = {}
        for item in self.inventory.items + self.inventory.equipped():
            if item is not None:
                counts[item.name] = counts.get(item.name, 0) + 1
        return counts

    def owned_item_names(self):
        equipped = self.inventory.equipped()
        return {item.name for item in self.inventory.items + equipped if item is not None}

    def give_item(self, item):
        return self.give_items([item])

    def give_items(self, items):
        # single entry point for NEW items (drops, later: shop, secrets)
        # full inventory (16) -> the item is turned into money instead
        messages = []
        all_added = True
        for item in items:
            if item is None:
                continue
            money = self.inventory.give_item(item)
            if money:
                self.player.money += money
                messages.append(f"Inventory full - {item.name} turned into {money}$")
                all_added = False
            else:
                messages.append(f"New item: {item.name}")
        if messages and any(not m.startswith("Inventory full") for m in messages):
            self.sfx.play("new_item")
        if messages:
            self.map_ui.show_message("   |   ".join(messages))
        return all_added

    def new_shooter(self):
        return Shooter(self.screen.get_width()//2, self.screen.get_height()//2, self.inventory.active_items, self.sfx,
                       self.bullet_type_info, self.sigils.active_set())

    def start_fight(self):
        self.player.vx = self.player.vy = 0.0   # no sliding after the fight
        self.map.respawn_bosses()               # beaten bosses come back (their gates stay open)
        # standing on a boss spot right now doesn't start a boss fight after this one - walk away first
        self.last_boss = self.map.boss_at(self.player.x, self.player.y, self.player.radius)
        self.player_in_combat = self.new_shooter()
        self.enemy_db.active_quests = set(self.quests.active)          # quest-only drops (e.g. Gus's Sugar Crystal)
        self.enemy_db.skip_items = set(self.owned_item_names())
        self.enemy_db.owned_counts = self.owned_item_counts()
        self.enemy_db.dropped_now = set()
        self.enemy_db.luck = self.luck()
        self.combat = Combat(self.screen, self.player_in_combat, [], self.enemy_db, self.hard_mode, self.sfx, assets=self.combat_assets)
        enemies, money = self.enemy_db.provoke_enemies(self.player.biome, self.hard_mode, self.screen)
        self.combat.enemies.extend(enemies)
        self.combat.money = money
        self.state = GameState.COMBAT
        self.music.stop()
        self.music.play(f"boss_fight{random.randint(1,2)}")

    def start_boss_fight(self, gate):
        boss_name = BOSS_NAME   # TEMPORARY: the same boss everywhere
        self.active_boss_gate = gate
        self.player.vx = self.player.vy = 0.0
        self.player_in_combat = self.new_shooter()
        boss = self.enemy_db.get_boss(boss_name)
        self.combat = Combat(self.screen, self.player_in_combat, [boss], self.enemy_db, self.hard_mode, self.sfx, boss_name, assets=self.combat_assets)
        self.combat.money += boss.money
        self.state = GameState.COMBAT
        self.music.stop()
        self.music.play(f"boss_fight{random.randint(1,2)}")
        # if the player loses or flees later, step back from the boss so the fight doesn't restart instantly
        bx, by = self.map.tile_centre(gate["boss"])
        dx, dy = self.player.x - bx, self.player.y - by
        dist = math.hypot(dx, dy) or 1
        back = self.player.x + dx / dist * self.map.tile_size, self.player.y + dy / dist * self.map.tile_size
        if self.map.can_stand(back[0], back[1], self.player.radius):
            self.player.set_position(*back)

    def check_map_contacts(self):
        # gold / items on the ground: picked up by walking over them
        self.map.quest_steps = dict(self.quests.active)              # quest -> current step (world map markers)
        self.map.active_quests = set(self.quests.active)          # quest items (e.g. the Foreman's Gear) show up
        self.map.discover_secrets()                                # secret places show up when you step in
        for pickup in self.map.pickups_at(self.player.x, self.player.y, self.player.radius):
            self.map.collected.add(pickup["pos"])
            if pickup["type"] == "sigil":                          # a shrine / secret pedestal
                self.award_sigil(pickup["sigil"])
            elif pickup["type"] == "gold":
                self.player.money += pickup["amount"]
                self.sfx.play("coin_pickup")
                self.map_ui.show_message(f"+{pickup['amount']}$", 90)
                if self.map.level == "core" and all(p["pos"] in self.map.collected
                                                    for p in self.map.world.pickups if p["type"] == "gold"):
                    self.map.flags.add("open:core_vault")          # all the Core's gold: the vault wall lets you in
            else:
                self.give_item(self.inventory.ItemDB.get_item(pickup["item"]))
        # portals: travel between the surface and the cellar
        portal = self.map.portal_at(self.player.x, self.player.y, self.player.radius)
        if portal and portal is not self.last_portal:
            self.use_portal(portal)
            return
        self.last_portal = portal

    def use_portal(self, portal):
        target_level = portal["leads_to"].split(":")[0]
        if tuple(portal["pos"]) in self.map.locked_portals:
            self.map_ui.show_message(LOCKED_PATH_MESSAGE, 150)
            self.last_portal = portal
            return
        if not self.map.portal_open(portal):
            self.map_ui.show_message(portal.get("sealed_text", "It's sealed. Something keeps it shut..."), 150)
            self.last_portal = portal
            return
        if target_level not in LEVELS:
            self.map_ui.show_message("The way down is not finished yet... (coming soon)", 150)
            self.last_portal = portal
            return
        # the key the other level uses to find the arrival point: "<this level>:<this portal's zone>"
        # (portals that lead to the surface already say where on the surface they lead)
        if target_level == "surface":
            arrival_key = portal["leads_to"]
        else:
            arrival_key = f"{self.map.level}:{portal['zone']}"
        if arrival_key == "surface:tundra_pass":
            self.map.flags.add("arrived:garden_tundra")      # Ferris's shortcut to the Garden's Tundra side
        self.change_level(target_level, arrival_key)
        self.autosave()

    def change_level(self, level, arrival_key=None):
        if not self.map.is_built(level):
            # first visit: the level is generated now (~1-2 s) - the music cuts out meanwhile
            self.music.stop()
            self.current_music = None             # the biome music starts again on the new level
            self.screen.fill((0, 0, 0))
            text = self.font.render("Going deeper...", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=self.screen.get_rect().center))
            pygame.display.flip()
        self.map.switch_level(level)
        pos = self.map.arrival_position(arrival_key) if arrival_key else self.map.start_position()
        self.player.set_position(*pos)
        self.player.encounter_grace = ESCAPE_GRACE_FRAMES      # no fight right at the arrival
        self.last_portal = None
        self.map_ui.show_message(LEVEL_TITLES[level], 120)

    def debug_teleport(self, level, tile):
        # TEST ONLY (world map, right click): jump to that tile, or the nearest one the player can stand on
        if self.map.level != level:
            self.change_level(level)
        tx, ty = tile
        for r in range(0, 12):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    pos = self.map.tile_centre((tx + dx, ty + dy))
                    if self.map.can_stand(pos[0], pos[1], self.player.radius):
                        self.player.set_position(*pos)
                        self.player.vx = self.player.vy = 0.0
                        self.last_portal = self.map.portal_at(pos[0], pos[1], self.player.radius)   # don't jump on through a portal
                        self.player.encounter_grace = ESCAPE_GRACE_FRAMES
                        self.map_ui.show_message("[TEST] Teleported", 60)
                        return
        self.map_ui.show_message("[TEST] Can't stand there", 60)

    def teleport_to_zone(self, level, zone):
        if self.map.level != level:
            self.change_level(level)
        pos = self.map.zone_spawn(zone)
        if pos:
            self.player.set_position(*pos)
            self.map_ui.show_message(f"[TEST] Teleported: {zone.replace('_', ' ').title()}", 90)

    def update_inventory(self, events, mouse_pos):
        self.inventory_ui.draw()
        change_state = self.inventory_ui.handle_click(mouse_pos, events)
        self.counters["sigils"] = self.sigils.to_dict()                 # saved with the game
        if change_state == "map":
            self.state = GameState.MAP
            self.inventory_ui.selected_slot = None
            self.inventory.selected_item = None
