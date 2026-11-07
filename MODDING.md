# Project Circle — Modding guide: structures

Structures are small hand-made places (huts, ruins, labs…) that the world generator drops into the
biomes. They hold the loot (gold and items) and NPC spots, so adding structures is the easiest way to
make the world more interesting. **No programming needed — a structure is a plain text file.**

---

## 1. Where to put your files

| Folder | What goes there |
|---|---|
| `mods/structures/` | **Your structures.** Every `*.txt` file here is loaded automatically. |
| `mods/bosses/` | Your own boss building for a biome: `mods/bosses/<biome>.txt` replaces the game's one. |
| `game/world/prefabs/structures/` | The game's own structures (you can read them as examples). |
| `game/world/prefabs/bosses/` | The game's boss buildings. |

- A file in `mods/structures/` with the same `@name` as a game structure **replaces** it.
- A broken file never crashes the game: it is skipped and the reason is printed in the console
  (e.g. `[structures] skipped mods/structures/my_hut.txt: missing @biomes`).
- Changes are used for **new worlds** (a world is generated from its seed when a save is created / loaded).

---

## 2. The file format

```
@name my_shrine
@biomes rainbow_fields, village
@items random, Hook
@npcs hermit
; Lines starting with ";" before the map are comments.
; A tiny shrine with an old hermit. Space = "let the generator fill this".

  rrrrr
 r__I__r
 r_N_I_r
 r_____r
  rr_rr
```

### Settings (lines starting with `@`, at the top)

| Setting | Required | Meaning |
|---|---|---|
| `@name` | yes | Unique name of the structure. |
| `@biomes` | yes | Where it may appear, comma separated (see the list below). |
| `@items` | if the map has `I` | One entry per `I`, **in reading order** (left→right, top→bottom). An item name (exactly as in the game, e.g. `Flintlock`) or `random` = a random item from that biome. |
| `@npcs` | if the map has `N` | One NPC id per `N`, in reading order. A structure with an NPC appears at most once per world. |
| `@gold` | no | Gold per `$`, e.g. `@gold 30-60`. Default: depends on the biome. |

### Biomes

`village`, `rainbow_fields`, `sugarwood_grove` (Candy), `silverpine_tundra`,
`toy_factory` (cellar — placed as a separate room in the factory walls, gets its own corridor),
`underground_garden` (cellar — placed in the cave),
`the_core` (placed inside the big halls, rotated randomly; the room + 1 tile around it must fit on open floor).
`the_void` is not used for random structures (the Void has one fixed shrine, `void_shrine`).

### Tiles

Tiles are the same in every biome — only their colour/sprite changes with the biome.

| Char | Tile | Walkable |
|---|---|---|
| `.` | grass | yes |
| `,` | path | yes |
| `_` | floor (inside buildings) | yes |
| `*` | flowers / glowing mushrooms | yes |
| `x` | dead flowers | yes |
| `=` | bridge | yes |
| `g` | metal floor (factory) | yes |
| `>` `<` `A` `v` | conveyor belt → ← ↑ ↓ (moves the player!) | yes |
| `T` | tree / giant plant | no |
| `r` | rock | no |
| `#` | wall | no |
| `f` | fence | no |
| `H` | house wall | no |
| `D` | door (decoration) | no |
| `~` | water | no |
| `o` | well / lamp post | no |
| `c` | campfire | no |
| `m` | machine | no |
| `k` | crate | no |
| `e` | glowing cables (core) | yes |
| `p` | pipe | no |
| `O` | the core (only in the fixed core chamber) | no |
| (space) | **empty** — the generator fills it (forest, cave…) | — |

### Markers

| Char | Meaning |
|---|---|
| `$` | gold lying on the ground (picked up by walking over it) |
| `I` | item lying on the ground (see `@items`) |
| `N` | NPC spot (see `@npcs`) |
| `B` | boss position — **only in boss buildings** |

Markers become the walkable tile next to them (gold inside a building lies on its floor).

---

## 3. Rules that make a good structure

1. **It must have an entrance.** Every `$`, `I` and `N` must be reachable from outside. The generator
   checks this and will cut a path through trees/rocks if needed — but never through walls (`#`, `H`, `f`).
2. Keep it small: about **6–16 tiles** wide/high. Big structures find fewer places to fit.
3. Use spaces around the shape instead of grass if you want it to blend into the surroundings.
4. Factory structures are rotated randomly; surface and garden structures are not.

---

## 4. Boss buildings

A boss building surrounds a boss. One per biome: `<biome>.txt` in `mods/bosses/` (yours) or
`game/world/prefabs/bosses/` (the game's).

- Exactly one `B` = where the boss stands.
- **Back door in the TOP row** (it will face the passage the boss guards).
- **Front door in the BOTTOM row** (where the player comes from).
- The building is rotated automatically so the back door faces the passage.

---

## 5. Testing your structure

From the project folder:

```
python -m tools.preview mods/structures/my_shrine.txt     # picture of one file -> tools/output/my_shrine.png
python -m tools.preview structures                        # all structures + boss buildings on one sheet
python -m tools.preview_world 1 2 3                       # surface for seeds 1-3, checks everything is reachable
python -m tools.preview_cellar 1 2                        # cellar for seeds 1-2
```

The world previews print `OK` when every structure, item, NPC, boss and portal can be reached.
