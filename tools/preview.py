# Renders a prefab (later also a generated map) to a PNG image - for checking maps without starting the game.
# Usage (from the project folder):  python -m tools.preview village_start
#                                    python -m tools.preview structures     (all structures on one sheet)
# Output: tools/output/<name>.png

import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
from game.world.tiles import TILES, MARKERS, EMPTY, tile_color
from game.world.prefab import load_prefab, load_prefab_file, PREFAB_DIR, all_structures, boss_building

CELL = 16
MARKER_COLORS = {"player_start": (255, 230, 0), "npc": (255, 80, 255), "exit": (255, 60, 60),
                 "boss": (120, 0, 0), "portal": (140, 60, 255), "gold": (255, 215, 0), "item": (0, 230, 255)}


def render_rows(rows, markers=None, cell=CELL, biome="village"):
    width, height = max(len(r) for r in rows), len(rows)
    surface = pygame.Surface((width * cell, height * cell))
    surface.fill((25, 25, 30))
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            rect = (x * cell, y * cell, cell, cell)
            if char == EMPTY:
                if (x + y) % 2 == 0:
                    pygame.draw.rect(surface, (35, 35, 42), rect)   # checker = empty, generator fills it
                continue
            if char in MARKERS:
                pygame.draw.rect(surface, tile_color(MARKERS[char]["becomes"] or "_", biome), rect)
                pygame.draw.circle(surface, MARKER_COLORS[MARKERS[char]["name"]], (x * cell + cell // 2, y * cell + cell // 2), cell // 2 - 1)
                continue
            pygame.draw.rect(surface, tile_color(char, biome), rect)
    return surface


def structures_sheet():
    pygame.font.init()
    font = pygame.font.Font(None, 22)
    small = pygame.font.Font(None, 18)
    # all structures (game + mods) and the boss buildings of every biome
    prefabs = sorted(all_structures(), key=lambda p: (p.list_setting("biomes")[0], p.name))
    for biome in ("village", "rainbow_fields", "sugarwood_grove", "silverpine_tundra", "underground_garden"):
        b = boss_building(biome)
        if b:
            b.settings["biomes"] = biome
            prefabs.append(b)
    cell, cols, box_w, box_h = 12, 7, 17 * 12 + 20, 13 * 12 + 54
    rows = (len(prefabs) + cols - 1) // cols
    sheet = pygame.Surface((cols * box_w, rows * box_h))
    sheet.fill((15, 15, 18))
    for i, p in enumerate(prefabs):
        bx, by = (i % cols) * box_w, (i // cols) * box_h
        img = render_rows(p.rows, cell=cell, biome=p.list_setting("biomes")[0])
        sheet.blit(img, (bx + 10, by + 44))
        sheet.blit(font.render(p.name, True, (240, 240, 240)), (bx + 10, by + 6))
        biomes = ", ".join(b.replace("silverpine_tundra", "tundra").replace("sugarwood_grove", "candy").replace("rainbow_fields", "rainbow")
                           .replace("underground_garden", "garden").replace("toy_factory", "factory") for b in p.list_setting("biomes"))
        sheet.blit(small.render(biomes, True, (160, 160, 170)), (bx + 10, by + 24))
    return sheet


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "village_start"
    # a single file from anywhere (e.g. your mod):  python -m tools.preview mods/structures/my_shrine.txt
    if name.endswith(".txt"):
        prefab = load_prefab_file(name)
        os.makedirs(os.path.join("tools", "output"), exist_ok=True)
        out = os.path.join("tools", "output", f"{prefab.name}.png")
        pygame.image.save(render_rows(prefab.rows, biome=(prefab.list_setting("biomes") or ["village"])[0]), out)
        print(f"{prefab.name}: {prefab.width}x{prefab.height}, markers {prefab.markers}, items {prefab.list_setting('items')}, npcs {prefab.list_setting('npcs')}")
        print("saved", out)
        return
    os.makedirs(os.path.join("tools", "output"), exist_ok=True)
    if name == "structures":
        out = os.path.join("tools", "output", "structures.png")
        pygame.image.save(structures_sheet(), out)
        print("saved", out)
        return
    prefab = load_prefab(name)
    surface = render_rows(prefab.rows)
    os.makedirs(os.path.join("tools", "output"), exist_ok=True)
    out = os.path.join("tools", "output", f"{name}.png")
    pygame.image.save(surface, out)
    print(f"{prefab.name}: {prefab.width}x{prefab.height} tiles, markers: {prefab.markers}")
    print("saved", out)


if __name__ == "__main__":
    main()
