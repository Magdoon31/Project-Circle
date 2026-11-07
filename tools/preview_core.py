# Renders the CORE map for a few seeds and checks it.
# Usage:  python -m tools.preview_core 1 2 3      Output: tools/output/core.png

import os, sys, time
import pygame
from game.world.core_map import CoreMap
from tools.preview_cellar import render

CELL = int(os.environ.get("CELL", 4))


def check(world):
    start = world.arrivals["cellar:garden"]
    reach = world.flood(start)
    missing = [p for p in world.important_points() if p not in reach]
    return not missing, len(missing)


def main():
    seeds = [int(s) for s in sys.argv[1:]] or [1, 2, 3]
    font = pygame.font.Font(None, 30)
    images = []
    for seed in seeds:
        t = time.time()
        world = CoreMap(seed)
        ok, missing = check(world)
        size = sum(1 for row in world.zones for z in row if z == "core")
        print(f"seed {seed}: {time.time() - t:.1f}s | core {size} tiles (~{size / 299:.0f} screens) | {len(world.halls)} halls | "
              f"{len(world.structures)} structures, {sum(1 for p in world.pickups if p['type'] == 'item')} items, {sum(1 for p in world.pickups if p['type'] == 'gold')} gold | unreachable {missing} | paths cut {world.paths_cut} | {'OK' if ok else 'PROBLEM'}")
        img = render(world, CELL)
        img.blit(font.render(f"seed {seed}", True, (255, 255, 255)), (8, 8))
        images.append(img)
    gap = 12
    out = pygame.Surface((len(images) * (images[0].get_width() + gap) - gap, images[0].get_height()))
    for i, img in enumerate(images):
        out.blit(img, (i * (img.get_width() + gap), 0))
    os.makedirs(os.path.join("tools", "output"), exist_ok=True)
    path = os.path.join("tools", "output", "core.png")
    pygame.image.save(out, path)
    print("saved", path)


if __name__ == "__main__":
    pygame.font.init()
    main()
