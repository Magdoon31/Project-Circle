# Renders the VOID map for a few seeds and checks it.
# Usage:  python -m tools.preview_void 1 2 3      Output: tools/output/void.png
#
# Checks: everything reachable, and the maze has no "leaks" (without the bridges the entrance island is closed).

import os, sys, time
import pygame
from game.world.void_map import VoidMap
from tools.preview_cellar import render

CELL = int(os.environ.get("CELL", 4))


def check(world):
    start = world.arrivals["core:core"]
    reach = world.flood(start)
    missing = [p for p in world.important_points() if p not in reach]
    # leak test: remove every bridge -> the player must be stuck on the entrance island
    saved = [row[:] for row in world.tiles]
    for row in world.tiles:
        for x, t in enumerate(row):
            if t == "=":
                row[x] = "~"
    closed = world.flood(start)
    world.tiles = saved
    leak = any(world.owner.get(c, world.entrance_island) != world.entrance_island for c in closed)
    return not missing and not leak, len(missing), leak


def main():
    seeds = [int(s) for s in sys.argv[1:]] or [1, 2, 3]
    font = pygame.font.Font(None, 30)
    images = []
    for seed in seeds:
        t = time.time()
        world = VoidMap(seed)
        took = time.time() - t
        ok, missing, leak = check(world)
        size = len(world.region)        # the land (islands + cracks), not the abyss around it
        dead_ends = sum(1 for i in world.reached_islands if len(world.graph[i]) == 1)
        depth = world.island_depth[world.boss_island]
        print(f"seed {seed}: {took:.1f}s | void {size} tiles (~{size / 299:.0f} screens) | {len(world.reached_islands)} islands, "
              f"{len(world.bridges)} bridges, {dead_ends} dead ends | boss {depth} bridges from the entrance | "
              f"shrine {world.shrine_step[0]}/{world.shrine_step[1]} | unreachable {missing} | leak {leak} | failed bridges {getattr(world, 'failed_bridges', 0)} | paths cut {world.paths_cut} | "
              f"{'OK' if ok else 'PROBLEM'}")
        img = render(world, CELL)
        img.blit(font.render(f"seed {seed}", True, (255, 255, 255)), (8, 8))
        images.append(img)
    gap = 12
    out = pygame.Surface((len(images) * (images[0].get_width() + gap) - gap, images[0].get_height()))
    for i, img in enumerate(images):
        out.blit(img, (i * (img.get_width() + gap), 0))
    os.makedirs(os.path.join("tools", "output"), exist_ok=True)
    path = os.path.join("tools", "output", "void.png")
    pygame.image.save(out, path)
    print("saved", path)


if __name__ == "__main__":
    pygame.font.init()
    main()
