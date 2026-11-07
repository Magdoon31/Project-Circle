# WORLD MAP (key M) - shows only the parts of the world the player has already seen.
# Mouse wheel: zoom (around the cursor) | drag with the mouse: move | Space: back to the player | M / Esc: close
# Tab / Q / E or clicking a tab at the top: look at another level you have been to (Surface, Cellar, Core, Void)
# TEST: right click = teleport to that place (DEBUG_CLICK_TELEPORT)

import pygame
from game.map.map import MAP_SHOWS

MIN_ZOOM_FACTOR = 1.0     # 1.0 = the whole world fits on the screen
MAX_ZOOM = 28             # screen pixels per tile
START_ZOOM = 9
DEBUG_REVEAL_KEY = True     # TEST ONLY: with the world map open (M), the ' key uncovers the whole level. False before release.
DEBUG_CLICK_TELEPORT = True # TEST ONLY: RIGHT click on the world map = teleport there (any level tab). False before release.
BACKGROUND = (18, 18, 22)   # same as the fog (map.FOG_COLOR) - unexplored land is invisible
# places shown on the map from FAR AWAY (even unexplored) while a quest is on one of the given steps:
#   structure -> (quest, steps, icon, label)
#   the sunken pier: the Gardener wants water from the end of it (gone once the water is taken: step "return")
STRUCTURE_MARKERS = {"sunken_pier": ("gardener", ("sprouts", "water"), "assets/img/map/water.png", "Lake")}
_marker_icons = {}


def _marker_icon(path):
    if path not in _marker_icons:
        try:
            _marker_icons[path] = pygame.image.load(path).convert_alpha()
        except (FileNotFoundError, pygame.error):
            _marker_icons[path] = None
    return _marker_icons[path]


class WorldMap:
    def __init__(self, screen):
        self.screen = screen
        self.is_open = False
        self.zoom = START_ZOOM
        self.centre = (0.0, 0.0)     # tile coordinates in the middle of the screen
        self.dragging = False
        self.drag_from = None
        self.font = pygame.font.Font("assets/font/Nexa-Heavy.ttf", 36)
        self.font_small = pygame.font.Font("assets/font/Nexa-ExtraLight.ttf", 22)
        self.view = None             # LevelView of the level being looked at
        self.teleport_request = None # TEST: (level, tile) after a right click
        self.tabs = []               # (rect, level name) of the level tabs at the top

    def open(self, game_map):
        self.is_open = True
        self.dragging = False
        if game_map.level in MAP_SHOWS:                     # e.g. in the lunapark: the Surface map
            self.view = game_map.view(MAP_SHOWS[game_map.level])
            w = self.view.world
            here = next((p["pos"] for p in w.portals if p["leads_to"].startswith(game_map.level + ":")), None)
            self.centre = (here[0] + 0.5, here[1] + 0.5) if here else (w.width / 2, w.height / 2)
            return
        self.view = game_map.view(game_map.level)
        self.centre_on_player(game_map)

    def show_level(self, game_map, name):
        if self.view and name == self.view.level:
            return
        if not game_map.is_built(name):
            # that level has to be generated first (~1 s)
            self.screen.fill(BACKGROUND)
            text = self.font.render("Loading map...", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=self.screen.get_rect().center))
            pygame.display.flip()
        self.view = game_map.view(name)
        if self.view.is_current:
            self.centre_on_player(game_map)
        else:
            w = self.view.world
            self.centre = (w.width / 2, w.height / 2)
            self.zoom = self.min_zoom(game_map)       # another level: show all of it first

    def cycle_level(self, game_map, step):
        names = game_map.viewable_levels()
        i = names.index(self.view.level) if self.view.level in names else 0
        self.show_level(game_map, names[(i + step) % len(names)])

    def close(self):
        self.is_open = False
        self.dragging = False

    def centre_on_player(self, game_map):
        self.centre = (game_map.player.x / game_map.tile_size, game_map.player.y / game_map.tile_size)

    def min_zoom(self, game_map):
        sw, sh = self.screen.get_size()
        world = self.view.world if self.view else game_map.world
        return min(sw / world.width, sh / world.height) * MIN_ZOOM_FACTOR

    def screen_to_tile(self, pos):
        sw, sh = self.screen.get_size()
        return self.centre[0] + (pos[0] - sw / 2) / self.zoom, self.centre[1] + (pos[1] - sh / 2) / self.zoom

    def tile_to_screen(self, tx, ty):
        sw, sh = self.screen.get_size()
        return sw / 2 + (tx - self.centre[0]) * self.zoom, sh / 2 + (ty - self.centre[1]) * self.zoom

    def handle_events(self, events, game_map):
        """Returns True when the map should close."""
        self.teleport_request = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_m, pygame.K_ESCAPE):
                    return True
                if event.key == pygame.K_SPACE:
                    self.show_level(game_map, game_map.level)
                    self.centre_on_player(game_map)
                if event.key in (pygame.K_TAB, pygame.K_e):
                    self.cycle_level(game_map, 1)
                if event.key == pygame.K_q:
                    self.cycle_level(game_map, -1)
                if DEBUG_REVEAL_KEY and (event.key == pygame.K_QUOTE or getattr(event, "unicode", "") == "'") and self.view.is_current:
                    game_map.reveal_all()
                    self.view = game_map.view(game_map.level)
            elif event.type == pygame.MOUSEWHEEL:
                # zoom around the mouse cursor: the tile under the cursor stays under it
                mouse = pygame.mouse.get_pos()
                before = self.screen_to_tile(mouse)
                factor = 1.2 ** event.y
                self.zoom = max(self.min_zoom(game_map), min(MAX_ZOOM, self.zoom * factor))
                after = self.screen_to_tile(mouse)
                self.centre = (self.centre[0] + before[0] - after[0], self.centre[1] + before[1] - after[1])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                tab = next((name for rect, name in self.tabs if rect.collidepoint(event.pos)), None)
                if tab:
                    self.show_level(game_map, tab)
                    continue
                self.dragging = True
                self.drag_from = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and DEBUG_CLICK_TELEPORT:
                tx, ty = self.screen_to_tile(event.pos)
                self.teleport_request = (self.view.level, (int(tx), int(ty)))   # Game does the jump
                return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                dx, dy = event.pos[0] - self.drag_from[0], event.pos[1] - self.drag_from[1]
                self.centre = (self.centre[0] - dx / self.zoom, self.centre[1] - dy / self.zoom)
                self.drag_from = event.pos
        self.clamp(game_map)
        return False

    def clamp(self, game_map):
        # keep the view on the world; if the whole world fits on the screen in one direction, centre it there
        sw, sh = self.screen.get_size()
        w, h = self.view.world.width, self.view.world.height
        cx = w / 2 if w * self.zoom <= sw else max(0, min(w, self.centre[0]))
        cy = h / 2 if h * self.zoom <= sh else max(0, min(h, self.centre[1]))
        self.centre = (cx, cy)

    def draw(self, game_map):
        self.clamp(game_map)
        screen = self.screen
        sw, sh = screen.get_size()
        screen.fill(BACKGROUND)
        view = self.view
        world = view.world

        # only the visible part of the overview picture is scaled (fast at any zoom)
        left, top = self.screen_to_tile((0, 0))
        right, bottom = self.screen_to_tile((sw, sh))
        x0, y0 = max(0, int(left)), max(0, int(top))
        x1, y1 = min(world.width, int(right) + 1), min(world.height, int(bottom) + 1)
        if x1 > x0 and y1 > y0:
            part = view.overview.subsurface((x0, y0, x1 - x0, y1 - y0))
            size = (max(1, round((x1 - x0) * self.zoom)), max(1, round((y1 - y0) * self.zoom)))
            screen.blit(pygame.transform.scale(part, size), self.tile_to_screen(x0, y0))

        # markers - only in explored places
        z = self.zoom
        r = max(4, z * 0.6)
        for portal in world.portals:
            if view.is_explored(portal["pos"]):
                pos = self.tile_to_screen(portal["pos"][0] + 0.5, portal["pos"][1] + 0.5)
                pygame.draw.circle(screen, (140, 60, 255), pos, r + 2)
                pygame.draw.circle(screen, (255, 255, 255), pos, r + 2, 2)
        for npc in (game_map.npcs() if view.is_current else world.npcs):
            if view.is_explored(npc["pos"]):
                pygame.draw.circle(screen, (230, 90, 230), self.tile_to_screen(npc["pos"][0] + 0.5, npc["pos"][1] + 0.5), r)
        # quest items (e.g. the Gardener's sprouts, the Foreman's gear): ALWAYS shown while their quest is active
        collected = view._lvl["collected"]
        for pickup in world.pickups:
            if pickup.get("quest") and pickup["quest"] in game_map.active_quests and tuple(pickup["pos"]) not in collected:
                pos = self.tile_to_screen(pickup["pos"][0] + 0.5, pickup["pos"][1] + 0.5)
                pulse = 2 + (pygame.time.get_ticks() // 300) % 3
                big = max(r, 9)                                   # easy to spot even when zoomed out
                pygame.draw.circle(screen, (255, 255, 255), pos, big + 4 + pulse)
                pygame.draw.circle(screen, (120, 230, 120), pos, big + 2 + pulse)
                icon = game_map.item_icon(pickup["item"])
                if icon:
                    size = max(12, int((big + 2) * 2))
                    small = pygame.transform.smoothscale(icon, (size, size))
                    screen.blit(small, small.get_rect(center=(int(pos[0]), int(pos[1]))))
        shown_markers = self.draw_structure_markers(world, game_map, r)
        for gate in world.gates:
            boss = gate["boss"]
            if boss and tuple(boss) not in view.away and (view.is_explored(boss) or view.memory_ms):
                # forgetful levels (the Void): the boss is ALWAYS shown, so you always know where you are going
                pos = self.tile_to_screen(boss[0] + 0.5, boss[1] + 0.5)
                pygame.draw.circle(screen, (170, 20, 30), pos, r + 3)
                pygame.draw.circle(screen, (255, 255, 255), pos, r + 3, 2)
        if view.is_current:                          # you are only drawn on the level you are in
            player = game_map.player
            ppos = self.tile_to_screen(player.x / game_map.tile_size, player.y / game_map.tile_size)
            pygame.draw.circle(screen, (255, 230, 60), ppos, max(5, z * 0.7))
            pygame.draw.circle(screen, (0, 0, 0), ppos, max(5, z * 0.7), 2)

        # title + help
        explored = view.explored_fraction()          # only walkable, reachable tiles count
        from game.map.map import LEVEL_TITLES
        title = self.font.render(f"World Map - {LEVEL_TITLES.get(view.level, '')}   {min(100, int(explored * 100))}% explored", True, (255, 255, 255))
        screen.blit(title, (sw // 50, sh // 40))
        self.draw_tabs(game_map, LEVEL_TITLES)
        help_text = self.font_small.render("Wheel: zoom   |   Drag: move   |   Tab / Q / E: other levels   |   Space: back to you   |   M / Esc: close", True, (200, 200, 200))
        screen.blit(help_text, (sw // 2 - help_text.get_width() // 2, sh - help_text.get_height() - sh // 40))
        legend = [((255, 230, 60), "You"), ((170, 20, 30), "Boss"), ((140, 60, 255), "Portal"), ((230, 90, 230), "NPC"),
                  ((120, 230, 120), "Quest item")]
        legend += shown_markers
        for i, (color, name) in enumerate(legend):
            y = sh // 40 + title.get_height() + 16 + i * 30
            if isinstance(color, pygame.Surface):                 # an icon (e.g. the water drop)
                screen.blit(pygame.transform.smoothscale(color, (22, 22)), (sw // 50 - 1, y))
            else:
                pygame.draw.circle(screen, color, (sw // 50 + 10, y + 11), 9)
            screen.blit(self.font_small.render(name, True, (230, 230, 230)), (sw // 50 + 28, y))

    def draw_structure_markers(self, world, game_map, r):
        """STRUCTURE_MARKERS: an icon over the middle of the structure, also in the fog. Returns legend entries."""
        legend = []
        for structure in getattr(world, "structures", []):
            marker = STRUCTURE_MARKERS.get(structure["name"])
            if not marker or game_map.quest_steps.get(marker[0]) not in marker[1]:
                continue
            quest, steps, path, label = marker
            icon = _marker_icon(path)
            x, y, w, h = structure["rect"]
            pos = self.tile_to_screen(x + w / 2, y + h / 2)
            pulse = 2 + (pygame.time.get_ticks() // 300) % 3
            size = int(max(r, 11) * 2 + pulse * 2)                # easy to spot even when zoomed out
            pygame.draw.circle(self.screen, (255, 255, 255), pos, size // 2 + 4)
            pygame.draw.circle(self.screen, (90, 170, 240), pos, size // 2 + 2)
            if icon:
                pic = pygame.transform.smoothscale(icon, (size, size))
                self.screen.blit(pic, pic.get_rect(center=(int(pos[0]), int(pos[1]))))
            if icon and (icon, label) not in legend:
                legend.append((icon, label))
        return legend

    def draw_tabs(self, game_map, titles):
        # one tab per visited level, top right; the level you are looking at is highlighted, yours has a dot
        sw, sh = self.screen.get_size()
        self.tabs = []
        x = sw - sw // 50
        for name in reversed(game_map.viewable_levels()):
            label = self.font_small.render(titles.get(name, name), True, (255, 255, 255))
            rect = pygame.Rect(0, sh // 40, label.get_width() + 28, label.get_height() + 12)
            rect.right = x
            selected = name == self.view.level
            pygame.draw.rect(self.screen, (90, 70, 140) if selected else (45, 45, 55), rect, border_radius=8)
            pygame.draw.rect(self.screen, (230, 230, 230) if selected else (110, 110, 120), rect, 2, border_radius=8)
            self.screen.blit(label, label.get_rect(center=rect.center))
            if name == game_map.level:
                pygame.draw.circle(self.screen, (255, 230, 60), (rect.left + 9, rect.centery), 4)
            self.tabs.append((rect, name))
            x = rect.left - 10
