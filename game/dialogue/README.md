# Dialogues — how to write them

A dialogue is one JSON file in `game/dialogue/data/<id>.json`. Which NPC starts which dialogue:
`NPC_DIALOGUES` in `game/dialogue/speakers.py` (NPC id → dialogue id). Speakers (name, talk sound,
colour) are also in `speakers.py`.

On the dialogue screen only the person you talk to is shown (big, in the middle) — never the player.
Every line has a **pose** of that person → picture `assets/img/dialogue/<partner>/<pose>.png`
(e.g. `milo/neutral.png`, `milo/scary.png`). Missing picture → placeholder figure with the file name on it.

Example: `data/test_milo.json`.

## Structure

```json
{
    "partner": "milo",
    "music": "dialogue",
    "start": [
        {"if": {"flag": "talked:milo"}, "goto": "again"},
        "intro"
    ],
    "nodes": {
        "intro": {
            "do": {"flag": "talked:milo"},
            "lines": [
                {"who": "milo", "pose": "wave", "text": "Hello."},
                {"who": "player", "pose": "listening", "text": "Hi."},
                {"who": "milo", "pose": "scary", "voice": "scary", "speed": 0.5, "text": "STOP LOOKING."},
                {"who": "milo", "pose": "neutral", "if": {"item": "Old Note"}, "text": "Only said when you carry the Old Note."}
            ],
            "choices": [
                {"text": "Who are you?", "goto": "who"},
                {"text": "Give him the note.", "if": {"item": "Old Note"}, "do": {"take": "Old Note", "flag": "lore_used:Old Note"}, "goto": "note"},
                {"text": "Bye.", "goto": "end"}
            ]
        }
    }
}
```

- **partner** — who is shown (optional: otherwise the first speaker who isn't the player).
- **music** — music while talking (a name in `MusicManager`, optional). Default: `"dialogue"` from
  `speakers.py` — a placeholder: put a file at `assets/music/dialogue/dialogue.mp3` and it plays;
  without the file the biome music just keeps playing.
  (11.11) `"music": "silence"` = no music at all while talking (the biome music comes back after).
- **start** — the first node. Either a name (`"intro"`), or a list checked from the top: the first
  `{"if": ..., "goto": ...}` that is true wins, a plain name at the end is the default.
- **node** — `lines` are said one after another. After them: `choices` (the player answers), or
  `"then": "<node>"`, or nothing / `"then": "end"` = the talk ends.
- **line** — `who` (a speaker from `speakers.py`), `text`, `pose` (the partner's picture for this line —
  also on the player's lines: how the partner reacts; stays until a line changes it), optional `voice` (another talk sound of that
  speaker, e.g. Milo's `"scary"`), `speed` (1 = normal, 0.5 = slower), `if`, `do`.
  `\n` in the text = new row.
- **horror** (optional, on a line, `true`) — the background goes completely black and the music goes silent for
  this line (comes back on the next one). Lines with Milo's `"voice": "scary"` do it automatically.
- **voiceover** (optional, on a line) — a recorded file in `assets/voice/` (e.g. `"voiceover": "milo_core_1.wav"`):
  it plays instead of the talk sound. Only for important moments (endings ...). Missing file = normal talk sound.
- **choice** — `text`, `goto` (`"end"` ends the talk), optional `if` (answer shown only when true), `do`.

## Conditions (`if`) and effects (`do`)

Values can be one name or a list.

| `if` | true when |
|---|---|
| `"flag": "x"` | the game remembers flag `x` |
| `"not_flag": "x"` | it doesn't |
| `"item": "Old Note"` | the player has the item (inventory or equipped) |
| `"not_item": "..."` | the player doesn't have it |
| `"quest": "hook"` / `"not_quest"` | the quest is active / isn't |
| `"quest_step": ["hook", "find"]` | the quest is at this step |
| `"quest_done": "hook"` / `"not_quest_done"` | the quest was finished / wasn't |
| `"seed_choice": {"key": "hook_holder", "options": ["bramble", "dot"], "is": "dot"}` | the world seed picked this option (the same for the whole world) |
| `"any": [ {...}, {...} ]` | at least one of these conditions is true |
| `"money_at_least": 30` | the player has at least this much gold |
| `"counter_at_least": ["gus_talks", 10]` | a saved counter reached this number (see `"count"`) |
| `"counter_below": ["hal_antennas", 2]` | a saved counter is still below this number |
| `"item_count": ["Glowing Sprout", 3]` | you have at least this many of the item |

| `do` | what it does |
|---|---|
| `"flag": "x"` | remember `x` (saved in the save file, the same for the whole world) |
| `"clear_flag": "x"` | forget `x` |
| `"give": "Peace Gun"` | give an item |
| `"take": "Old Note"` | take one item away |
| `"gold_piles": 2` | give gold: 2 "piles" of the biome the player is in |
| `"music": "the_void"` | (10.11) from this line on this music plays (a name in `MusicManager`); after the talk the biome's music comes back |
| `"open": "boss_fight"` | (10.11) after the talk the boss fight starts (Milo: `BOSS_TALKS` in game.py) |
| `"count": "gus_talks"` | add 1 to a saved counter (e.g. how many times you talked to someone) |
| `"pay": 30` | take gold from the player (check `money_at_least` first) |
| `"reveal_map": "surface:rainbow_fields"` | uncover a zone on the world map (M) |
| `"quest": {"drop": "ink"}` | remove a quest from the list WITHOUT finishing it (can be started again) |
| `"quest": {"start": "hook"}` | start a quest ("New Quest" at the bottom, listed in the inventory) |
| `"quest": {"step": ["hook", "return"]}` | move the quest to the next step |
| `"quest": {"finish": "hook"}` | finish it (removed from the list, flag `quest_done:hook`) |
| `"minigame": {"type": "memory", "win": "won", "lose": "lost"}` | (on a choice) play a minigame (`memory`, `sudoku_think`, `sudoku_speed`, `wires_4` / `wires_5` / `wires_6` = Hal's antennas, always free, `fishing` = Oliver, pays out the catch itself, `wheel_10` / `wheel_50` / `wheel_100` = Lucky's wheel, the number is the stake), then go on at the win / lose node |

Quests are defined in `game/quests.py` (title + text of every step).

**Barks:** `"random_line": true` on a node = say ONE of its lines, picked at random (for "small talk").
**then** can also be a list like `start` (`[{"if": ..., "goto": ...}, "default"]`).
If the only answers left would just end the talk ("Bye."), the talk ends without showing them.

Flags set by the game: `boss:<zone>` when that boss is beaten (e.g. `boss:candy`).

`do` works on a node (when it starts), on a line (when it is said) and on a choice (when picked).

Flags used by the game: `void_unlocked`, `lore_used:<item>` (all 3 lore items → Secret Ending).

## Controls (for testing)

Space / Enter / E = show the whole line at once, press again = next line.
There is **no button that skips a whole dialogue** (on purpose).
Answers: W/S (and A/D for the second column) or arrows + Space/Enter, or 1–6 (no mouse). At most 6 answers: 3 per column, 2 columns. `"goto"` / `"then"` can also be `"dialogue:<file>"`: the talk goes straight on with another dialogue file (from its `start`), as one conversation.
`"switch_partner": true` at the top of a file: a talk between two NPCs - the picture always shows the one who speaks.

Answers are shown at once and can be moved through at once, but CONFIRMING works only after a short moment,
so spamming Space never picks one by accident.

## Pictures and sounds

- Talk sounds: `assets/sfx/dialogue/` (set per speaker in `speakers.py`).
- Pictures: `assets/img/dialogue/<partner>/<pose>.png`. Any size — scaled to ~60% of the screen
  height, standing on the text box. Without a picture a placeholder figure is drawn.
