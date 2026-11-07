# Renders the SURFACE map for a few seeds side by side.
# Usage:  python -m tools.preview_world 1 2 3 4      (seeds; default 1 2 3 4)
# Output: tools/output/surface.png
# Also checks: every gate really connects its two zones, and without gates the zones are closed.

import os, sys, time
from collections import deque
import pygame
from game.world import surface_layout as L
from game.world.surface_map import SurfaceMap
from game.world.tiles import tile_color

ZONE_COLORS = {
    "village": (120, 190, 90), "separated": (160, 210, 120), "rainbow_fields": (240, 170, 210),
    "candy": (190, 120, 70), "tundra": (190, 220, 240), "tundra_pass": (140, 180, 220),
}
CELL = int(os.environ.get("CELL", 3))


def render(world, cell=CELL):
    surf = pygame.Surface((world.width * cell, world.height * cell))
    for y in range(world.height):
        for x in range(world.width):
            char = world.tiles[y][x]
            surf.fill(tile_color(char, world.biome_at(x, y)), (x * cell, y * cell, cell, cell))
    px, py, pw, ph = L.village_prefab_rect()
    pygame.draw.rect(surf, (255, 230, 0), (px * cell, py * cell, pw * cell, ph * cell), 1)
    for gate in world.gates:
        if gate["boss"]:
            pygame.draw.circle(surf, (200, 0, 0), (gate["boss"][0] * cell, gate["boss"][1] * cell), 5)
            pygame.draw.circle(surf, (255, 255, 255), (gate["boss"][0] * cell, gate["boss"][1] * cell), 5, 1)
    dot = max(2, cell // 2)
    for pickup in world.pickups:
        color = (255, 215, 0) if pickup["type"] == "gold" else (0, 230, 255)
        pygame.draw.circle(surf, color, (pickup["pos"][0] * cell + cell // 2, pickup["pos"][1] * cell + cell // 2), dot)
    for npc in world.npcs:
        pygame.draw.circle(surf, (255, 80, 255), (npc["pos"][0] * cell + cell // 2, npc["pos"][1] * cell + cell // 2), dot + 1)
    for structure in world.structures:
        x, y, w, h = structure["rect"]
        pygame.draw.rect(surf, (255, 255, 255), (x * cell - 2, y * cell - 2, w * cell + 4, h * cell + 4), 1)
    for portal in world.portals:
        pygame.draw.circle(surf, (140, 60, 255), (portal["pos"][0] * cell, portal["pos"][1] * cell), 5)
        pygame.draw.circle(surf, (255, 255, 255), (portal["pos"][0] * cell, portal["pos"][1] * cell), 5, 1)
    return surf


from game.world.terrain import WALKABLE, important_points


def reachable(world, start, gates_open):
    passable = WALKABLE if gates_open else WALKABLE - {"|"}
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and 0 <= nx < world.width and 0 <= ny < world.height and world.tiles[ny][nx] in passable:
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def reachable_zones(world, start, gates_open):
    zones = {world.zones[y][x] for x, y in reachable(world, start, gates_open)}
    zones.discard(None)
    return zones


def main():
    seeds = [int(s) for s in sys.argv[1:]] or [1, 2, 3, 4]
    font = pygame.font.Font(None, 28)
    images = []
    for seed in seeds:
        t = time.time()
        world = SurfaceMap(seed)
        start = world.player_start
        open_ = reachable_zones(world, start, True)
        closed = reachable_zones(world, start, False)
        cells = reachable(world, start, True)
        lost = [p for p in important_points(world) if p not in cells]
        ok = open_ == set(L.ZONES) and closed == {"village"} and not lost
        print(f"seed {seed}: {time.time() - t:.1f}s | zones reachable {len(open_)}/{len(L.ZONES)} | closed gates -> {sorted(closed)} | "
              f"{len(world.structures)} structures, {len(world.pickups)} pickups, {len(world.npcs)} npcs | paths cut: {world.paths_cut} | unreachable: {len(lost)} | {'OK' if ok else 'PROBLEM'}")
        img = render(world)
        img.blit(font.render(f"seed {seed}", True, (255, 255, 255)), (8, 8))
        images.append(img)
    gap = 12
    out = pygame.Surface((len(images) * (images[0].get_width() + gap) - gap, images[0].get_height()))
    out.fill((0, 0, 0))
    for i, img in enumerate(images):
        out.blit(img, (i * (img.get_width() + gap), 0))
    os.makedirs(os.path.join("tools", "output"), exist_ok=True)
    path = os.path.join("tools", "output", "surface.png")
    pygame.image.save(out, path)
    print("saved", path)


if __name__ == "__main__":
    pygame.font.init()
    main()
