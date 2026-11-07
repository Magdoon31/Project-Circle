# Renders the CELLAR map (Factory + Underground Garden) for a few seeds and checks it.
# Usage:  python -m tools.preview_cellar 1 2      Output: tools/output/cellar.png

import os, sys, time
import pygame
from game.world.cellar_map import CellarMap
from game.world.tiles import tile_color

CELL = int(os.environ.get("CELL", 3))


def render(world, cell=CELL):
    surf = pygame.Surface((world.width * cell, world.height * cell))
    for y in range(world.height):
        for x in range(world.width):
            surf.fill(tile_color(world.tiles[y][x], world.biome_at(x, y)), (x * cell, y * cell, cell, cell))
    dot = max(2, cell // 2 + 1)
    def c(pos):
        return pos[0] * cell + cell // 2, pos[1] * cell + cell // 2
    for p in world.pickups:
        pygame.draw.circle(surf, (255, 215, 0) if p["type"] == "gold" else (0, 230, 255), c(p["pos"]), dot)
    for st in world.structures:
        x, y, w, h = st["rect"]
        pygame.draw.rect(surf, (255, 255, 255), (x * cell - 2, y * cell - 2, w * cell + 4, h * cell + 4), 1)
    for n in world.npcs:
        pygame.draw.circle(surf, (255, 80, 255), c(n["pos"]), dot + 2)
    for g in world.gates:
        pygame.draw.circle(surf, (200, 0, 0), c(g["boss"]), 6)
        pygame.draw.circle(surf, (255, 255, 255), c(g["boss"]), 6, 1)
    for p in world.portals:
        pygame.draw.circle(surf, (140, 60, 255), c(p["pos"]), 7)
        pygame.draw.circle(surf, (255, 255, 255), c(p["pos"]), 7, 1)
    return surf


def check(world):
    a_factory = world.arrivals["surface:separated"]
    a_tundra = world.arrivals["surface:tundra_pass"]
    exit_portal = next(p["pos"] for p in world.portals if p["leads_to"] == "core:entry")
    reach_all = world.flood(a_factory, gates_open=True)
    missing = [p for p in world.important_points() if p not in reach_all]
    closed_f = world.flood(a_factory, gates_open=False)
    closed_t = world.flood(a_tundra, gates_open=False)
    factory_closed = all(world.zones[y][x] == "factory" for x, y in closed_f)
    tundra_side_no_factory = all(world.zones[y][x] == "garden" for x, y in closed_t) and exit_portal not in closed_t
    return not missing and factory_closed and tundra_side_no_factory, len(missing), factory_closed, tundra_side_no_factory


def main():
    seeds = [int(s) for s in sys.argv[1:]] or [1, 2]
    font = pygame.font.Font(None, 30)
    images = []
    for seed in seeds:
        t = time.time()
        world = CellarMap(seed)
        ok, missing, fc, tc = check(world)
        garden = sum(1 for row in world.zones for z in row if z == "garden")
        factory = sum(1 for row in world.zones for z in row if z == "factory")
        print(f"seed {seed}: {time.time() - t:.1f}s | factory {factory} tiles (~{factory / 299:.0f} screens), garden {garden} tiles (~{garden / 299:.0f} screens) | "
              f"{len(world.pickups)} pickups, {len(world.structures)} structures | unreachable {missing} | factory closed by its gate: {fc} | tundra side can't enter factory/exit: {tc} | "
              f"paths cut {world.paths_cut} | {'OK' if ok else 'PROBLEM'}")
        img = render(world)
        img.blit(font.render(f"seed {seed}", True, (255, 255, 255)), (8, 8))
        images.append(img)
    gap = 12
    out = pygame.Surface((len(images) * (images[0].get_width() + gap) - gap, images[0].get_height()))
    for i, img in enumerate(images):
        out.blit(img, (i * (img.get_width() + gap), 0))
    os.makedirs(os.path.join("tools", "output"), exist_ok=True)
    path = os.path.join("tools", "output", "cellar.png")
    pygame.image.save(out, path)
    print("saved", path)


if __name__ == "__main__":
    pygame.font.init()
    main()
