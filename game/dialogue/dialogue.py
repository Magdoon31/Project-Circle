# DIALOGUES - full-screen conversations: the map is dimmed, the person you talk to stands big in the middle
# (the player is never shown), text box at the bottom.
#
# A dialogue is a JSON file in game/dialogue/data/<id>.json (see game/dialogue/README.md for the format).
# Every line names the POSE of the person you talk to -> picture assets/img/dialogue/<speaker>/<pose>.png
# (until the pictures exist a placeholder figure with the pose name is drawn).
# Text is typed letter by letter with the speaker's talk sound; the player can answer with choices.
#
# Controls: Space / Enter / E / left click = show the whole line at once, then go on
#           (there is NO button that skips a whole dialogue - author's decision)
#           keyboard only (no mouse): Space/Enter for lines; answers: W/S or arrows + Space/Enter, or 1-9

import json, math, os, random
import pygame
from game.dialogue.speakers import SPEAKERS, SOUND_DIR, IMAGE_DIR, DEFAULT_POSE, DEFAULT_DIALOGUE_MUSIC
from game import controls as KEYS
from game.menu import options as OPT

DATA_DIR = os.path.join("game", "dialogue", "data")
VOICE_DIR = os.path.join("assets", "voice")      # recorded voiceovers: "voiceover": "milo_core_1.wav" in a line

TEXT_SPEEDS = {"slow": 0.5, "normal": 1.0, "fast": 2.0, "instant": 10 ** 6}    # (11.11) x TYPE_SPEED
TYPE_SPEED = 0.66           # letters per frame (60 fps -> ~40 letters per second) - author's value
SOUND_EVERY = 2             # the talk sound starts again every N typed letters (spaces don't count) - continuous chatter
PUNCTUATION_PAUSE = {".": 12, "!": 12, "?": 12, ",": 5, ";": 7, ":": 7}   # extra frames after these
LINE_END_DELAY = 8          # frames after a line is fully typed before it can be closed
CHOICE_DELAY = 40           # frames before the answers react (spamming Space doesn't pick one by accident)
DIM_ALPHA = 175             # how dark the map behind gets
TALK_CHANNEL = 0            # mixer channel reserved for talk sounds (see reserve_talk_channel)

MAX_CHOICES = 6             # answers shown at once: up to 3 in a column, 2 columns
CHOICE_ROWS = 3

ADVANCE_KEYS = (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e)


def reserve_talk_channel():
    """Call ONCE at the start, before any music plays: keeps channel 0 only for talk sounds.
    (Without it the music could be on channel 0 - the talk sound would be silent and stop the music.)"""
    pygame.mixer.set_reserved(TALK_CHANNEL + 1)


def load_dialogue(dialogue_id):
    with open(os.path.join(DATA_DIR, f"{dialogue_id}.json"), encoding="utf-8") as f:
        return json.load(f)


def as_list(value):
    return value if isinstance(value, list) else [value]


class DialogueContext:
    """What a dialogue may check and change in the game (flags, items, quests, gold). Game passes one in."""
    def __init__(self, has_flag, set_flag, clear_flag, has_item, give_item, take_item,
                 quests=None, add_gold_piles=None, seed_choice=None, on_new_quest=None, on_quest_done=None,
                 format_text=None, reveal_zone=None, get_money=None, pay=None, drop_quest=None,
                 get_counter=None, add_counter=None, count_item=None, give_sigil=None, open_screen=None,
                 play_music=None):
        self.has_flag, self.set_flag, self.clear_flag = has_flag, set_flag, clear_flag
        self.has_item, self.give_item, self.take_item = has_item, give_item, take_item
        self.quests = quests                    # QuestLog
        self.add_gold_piles = add_gold_piles    # n -> gives n piles of gold of the biome the player is in
        self.seed_choice = seed_choice          # (key, options) -> one option, always the same for this world
        self.on_new_quest = on_new_quest        # called with the quest id ("New Quest" note)
        self.on_quest_done = on_quest_done      # called with the quest id ("Quest complete" note)
        self.format_text = format_text or (lambda t: t)   # fills placeholders like {price:memory}
        self.reveal_zone = reveal_zone          # (level, zone) -> uncovers that part of the world map
        self.get_money, self.pay = get_money, pay
        self.drop_quest = drop_quest            # quest id -> removed from the list (not finished)
        self.get_counter = get_counter or (lambda name: 0)     # saved numbers, e.g. how many times you talked to Gus
        self.add_counter = add_counter
        self.count_item = count_item or (lambda name: 1 if has_item(name) else 0)
        self.give_sigil = give_sigil            # sigil id -> the player gets that sigil
        self.open_screen = open_screen          # name -> a screen opens after the talk (e.g. Ferris: "shortcuts")
        self.play_music = play_music            # (10.11) name -> this music plays from now on (e.g. Milo says "Void")

    def check(self, cond):
        """All must be true (values may be lists):
           flag / not_flag, item / not_item, quest / not_quest (active), quest_step: [id, step],
           quest_done / not_quest_done, seed_choice: {"key": ..., "options": [...], "is": ...},
           any: [cond, cond, ...] (at least one true), counter_at_least / counter_below: [name, n], item_count: [item, n]"""
        if not cond:
            return True
        q = self.quests
        done = lambda i: self.has_flag(f"quest_done:{i}")
        ok = (all(self.has_flag(f) for f in as_list(cond.get("flag", [])))
              and not any(self.has_flag(f) for f in as_list(cond.get("not_flag", [])))
              and all(self.has_item(i) for i in as_list(cond.get("item", [])))
              and not any(self.has_item(i) for i in as_list(cond.get("not_item", [])))
              and all(done(i) for i in as_list(cond.get("quest_done", [])))
              and not any(done(i) for i in as_list(cond.get("not_quest_done", []))))
        if ok and q is not None:
            ok = (all(i in q.active for i in as_list(cond.get("quest", [])))
                  and not any(i in q.active for i in as_list(cond.get("not_quest", []))))
            if ok and "quest_step" in cond:
                qid, step = cond["quest_step"]
                ok = q.active.get(qid) == step
        if ok and "money_at_least" in cond and self.get_money:
            ok = self.get_money() >= cond["money_at_least"]
        if ok and "counter_at_least" in cond:
            name, n = cond["counter_at_least"]
            ok = self.get_counter(name) >= n
        if ok and "item_count" in cond:                 # ["Glowing Sprout", 3]: you have at least 3
            name, n = cond["item_count"]
            ok = self.count_item(name) >= n
        if ok and "counter_below" in cond:
            name, n = cond["counter_below"]
            ok = self.get_counter(name) < n
        if ok and "any" in cond:                       # at least one of the listed conditions
            ok = any(self.check(c) for c in cond["any"])
        if ok and "seed_choice" in cond and self.seed_choice:
            sc = cond["seed_choice"]
            ok = self.seed_choice(sc["key"], sc["options"]) == sc["is"]
        return ok

    def apply(self, effects):
        """flag / clear_flag, give / take (items), sigil (id), open (screen after the talk), gold_piles: n,
           quest: {"start": id} | {"step": [id, step]} | {"finish": id}   (values may be lists)."""
        if not effects:
            return
        for f in as_list(effects.get("flag", [])):
            self.set_flag(f)
        for f in as_list(effects.get("clear_flag", [])):
            self.clear_flag(f)
        for i in as_list(effects.get("give", [])):
            self.give_item(i)
        for i in as_list(effects.get("take", [])):
            self.take_item(i)
        for name in as_list(effects.get("open", [])):           # "open": "shortcuts" - after the talk
            if self.open_screen:
                self.open_screen(name)
        for name in as_list(effects.get("music", [])):         # (10.11) "music": "the_void" - from this line on
            if self.play_music:
                self.play_music(name)
        for sigil in as_list(effects.get("sigil", [])):         # "sigil": "overflow"
            if self.give_sigil:
                self.give_sigil(sigil)
        for name in as_list(effects.get("count", [])):           # counter +1 (saved)
            if self.add_counter:
                self.add_counter(name)
        for zone in as_list(effects.get("reveal_map", [])):     # "surface:rainbow_fields"
            if self.reveal_zone:
                self.reveal_zone(*zone.split(":", 1))
        if effects.get("pay") and self.pay:
            self.pay(effects["pay"])
        if effects.get("gold_piles") and self.add_gold_piles:
            self.add_gold_piles(effects["gold_piles"])
        quest = effects.get("quest")
        if quest and self.quests is not None:
            if "start" in quest and self.quests.start(quest["start"]) and self.on_new_quest:
                self.on_new_quest(quest["start"])
            if "step" in quest:
                self.quests.step(*quest["step"])
            if "drop" in quest:
                self.quests.finish(quest["drop"])           # off the list, NOT done - can be started again
            if "finish" in quest:
                self.quests.finish(quest["finish"])
                self.set_flag(f"quest_done:{quest['finish']}")
                if self.on_quest_done:
                    self.on_quest_done(quest["finish"])


class Dialogue:
    def __init__(self, screen, dialogue_id, context, sfx_volume=1.0):
        self.screen = screen
        self.id = dialogue_id
        self.data = load_dialogue(dialogue_id)
        self.ctx = context
        self.sfx_volume = sfx_volume
        self.finished = False
        self.horror = False
        self.pending_minigame = None    # {"type": ..., "win": node, "lose": node} - Game runs it, then calls resume()
        # music while talking: "music" in the dialogue file, or the default one (Game plays it if it exists)
        self.music = self.data.get("music", DEFAULT_DIALOGUE_MUSIC)
        sw, sh = screen.get_size()
        self.font = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(18, sh // 28))
        self.font_name = pygame.font.Font("assets/font/Nexa-Heavy.ttf", max(16, sh // 32))
        self.font_small = pygame.font.Font("assets/font/Nexa-ExtraLight.ttf", max(12, sh // 50))
        # the map as it was when the talk started, dimmed (Game redraws it when the money changes: set_background)
        self.set_background(screen)
        self.sounds, self.images = {}, {}
        # the person you talk to (the only one shown): "partner" in the file, or the first one who isn't the player
        self.partner = self.data.get("partner") or self._first_partner()
        self.pose = DEFAULT_POSE
        self.timer = 0
        self.goto(self._start_node())

    def set_background(self, picture):
        """The dimmed map behind the talk (and behind its minigames). money = the money shown on it."""
        self.background = picture.copy()
        dim = pygame.Surface(self.background.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, DIM_ALPHA))
        self.background.blit(dim, (0, 0))
        self.background_money = self.ctx.get_money() if self.ctx and self.ctx.get_money else None

    def _first_partner(self):
        for node in self.data.get("nodes", {}).values():
            for line in node.get("lines", []):
                if line.get("who", "player") != "player":
                    return line["who"]
        return None

    # --- flow ---------------------------------------------------------------------------------
    def _start_node(self):
        return self._pick_target(self.data.get("start", "start"))

    def _pick_target(self, target):
        # "node"  or  [{"if": {...}, "goto": "node"}, ..., "default_node"]  (the first true one wins)
        if isinstance(target, str) or target is None:
            return target
        for option in target:
            if isinstance(option, str):
                return option
            if self.ctx.check(option.get("if")):
                return option["goto"]
        return "end"

    def goto(self, node_id):
        if node_id in (None, "end"):
            self.finish()
            return
        if node_id.startswith("dialogue:"):
            # go straight on with ANOTHER dialogue file, as one conversation (e.g. the argument -> Milo's warning)
            self.id = node_id.split(":", 1)[1]
            self.data = load_dialogue(self.id)
            self.partner = self.data.get("partner") or self._first_partner()
            self.goto(self._pick_target(self.data.get("start")))
            return
        self.node = self.data["nodes"][node_id]
        self.ctx.apply(self.node.get("do"))
        self.lines = [l for l in self.node.get("lines", []) if self.ctx.check(l.get("if"))]
        if self.node.get("random_line") and self.lines:
            self.lines = [random.choice(self.lines)]          # "barks": one of the lines, at random
        self.line_index = -1
        self.choices = None
        self.next_line()

    def next_line(self):
        self.line_index += 1
        if self.line_index < len(self.lines):
            self.start_line(self.lines[self.line_index])
            return
        choices = [c for c in self.node.get("choices", []) if self.ctx.check(c.get("if"))]
        if choices and all(c.get("goto", "end") == "end" and not c.get("do") for c in choices):
            choices = []                     # only "Bye"-like answers left -> just end, no pointless choice
        if choices:
            self.choices = choices[:MAX_CHOICES]
            self.selected = 0
            self.choice_timer = 0
            pygame.mixer.Channel(TALK_CHANNEL).stop()
        else:
            self.goto(self._pick_target(self.node.get("then", "end")))

    def start_line(self, line):
        self.line = line
        who = line.get("who", "player")
        self.speaker = SPEAKERS.get(who, SPEAKERS["player"])
        if self.data.get("switch_partner") and who != "player" and who != self.partner:
            self.partner = who               # talks between two NPCs: always the one who speaks is shown
        if "pose" in line:
            self.pose = line["pose"]       # the partner's pose stays until a line changes it
        self.text = self.ctx.format_text(line.get("text", ""))
        # HORROR moment: Milo's scary voice (or "horror": true) -> black background, Game mutes the music for this line
        self.horror = bool(line.get("horror", line.get("voice") == "scary"))
        self.shown = 0.0               # letters typed so far (float - grows by speed each frame)
        self.wait = 0                  # pause after punctuation
        self.end_timer = 0             # frames since the line was fully typed
        self.typed_since_sound = SOUND_EVERY   # the first letter makes a sound at once
        self.sound = self._sound(who, line.get("voice"))
        # VOICEOVER (recorded by the author, only for important moments): the file plays instead of the talk sound
        self.voiceover = None
        if line.get("voiceover"):
            path = os.path.join(VOICE_DIR, line["voiceover"])
            if os.path.exists(path):
                try:
                    self.voiceover = pygame.mixer.Sound(path)
                    channel = pygame.mixer.Channel(TALK_CHANNEL)
                    channel.set_volume(self.sfx_volume)
                    channel.play(self.voiceover)
                except pygame.error:
                    self.voiceover = None
        self.ctx.apply(line.get("do"))

    def finish(self):
        self.finished = True
        pygame.mixer.Channel(TALK_CHANNEL).stop()

    @property
    def typing(self):
        return self.choices is None and int(self.shown) < len(self.text)

    # --- assets ----------------------------------------------------------------------------------
    def _sound(self, who, voice):
        speaker = SPEAKERS.get(who, {})
        name = speaker.get("voices", {}).get(voice) if voice else None
        name = name or speaker.get("sound")
        if not name:
            return None
        if name not in self.sounds:
            try:
                self.sounds[name] = pygame.mixer.Sound(os.path.join(SOUND_DIR, name))
            except (pygame.error, FileNotFoundError):
                self.sounds[name] = None
        return self.sounds[name]

    def _image(self, who, pose, height):
        key = (who, pose, height)
        if key not in self.images:
            path = os.path.join(IMAGE_DIR, who, f"{pose}.png")
            image = None
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                image = pygame.transform.smoothscale(raw, (int(raw.get_width() * height / raw.get_height()), height))
            self.images[key] = image
        return self.images[key]

    # --- input + update ---------------------------------------------------------------------------
    def handle_events(self, events):
        for event in events:
            if self.choices is not None:
                # answers: keyboard only. Moving works at once, CONFIRMING only after a short moment
                # (so spamming Space through the lines never picks an answer by accident)
                if event.type != pygame.KEYDOWN:
                    continue
                ready = self.choice_timer >= CHOICE_DELAY
                if event.key in (KEYS.move_key("up"), pygame.K_UP):          # (11.11) the movement keys: Settings
                    self.selected = (self.selected - 1) % len(self.choices)
                elif event.key in (KEYS.move_key("down"), pygame.K_DOWN):
                    self.selected = (self.selected + 1) % len(self.choices)
                elif event.key in (KEYS.move_key("left"), pygame.K_LEFT, KEYS.move_key("right"), pygame.K_RIGHT) \
                        and len(self.choices) > CHOICE_ROWS:
                    other = (self.selected + CHOICE_ROWS) % (2 * CHOICE_ROWS)      # same row, other column
                    self.selected = min(other, len(self.choices) - 1)
                elif pygame.K_1 <= event.key <= pygame.K_9 and event.key - pygame.K_1 < len(self.choices):
                    if ready:
                        self.pick(event.key - pygame.K_1)
                    else:
                        self.selected = event.key - pygame.K_1     # too early to pick: just move there
                elif event.key in ADVANCE_KEYS and ready:
                    self.pick(self.selected)
            elif event.type == pygame.KEYDOWN and event.key in ADVANCE_KEYS:     # keyboard only, no mouse
                self.advance()
            if self.finished:
                return

    def advance(self):
        if self.typing:
            self.shown = len(self.text)          # show the whole line at once
            self.wait = 0
        elif self.end_timer >= LINE_END_DELAY:
            self.next_line()

    def pick(self, i):
        choice = self.choices[i]
        do = choice.get("do") or {}
        self.ctx.apply(do)
        if do.get("minigame"):
            self.pending_minigame = dict(do["minigame"])      # the talk waits; Game runs the minigame
            self.choices = None
            pygame.mixer.Channel(TALK_CHANNEL).stop()
            return
        self.goto(self._pick_target(choice.get("goto", "end")))

    def resume(self, won):
        """After a minigame: go on at its "win" / "lose" node."""
        game = self.pending_minigame
        self.pending_minigame = None
        self.goto(self._pick_target(game.get("win" if won else "lose", "end")))

    def resume_at(self, node):
        """The minigame didn't start (e.g. not enough coins): go on at this node."""
        self.pending_minigame = None
        self.goto(self._pick_target(node))

    def update(self):
        self.timer += 1
        if self.choices is not None:
            self.choice_timer += 1
            return
        if not self.typing:
            self.end_timer += 1
            return
        if self.wait > 0:
            self.wait -= 1
            return
        before = int(self.shown)
        self.shown = min(len(self.text), self.shown + TYPE_SPEED * TEXT_SPEEDS[OPT.get("text_speed")]
                         * self.line.get("speed", 1.0))         # (11.11) Settings: text speed
        for k, char in enumerate(self.text[before:int(self.shown)]):
            if not char.isspace():
                self.typed_since_sound += 1
                if self.typed_since_sound >= SOUND_EVERY and self.sound and not self.voiceover:
                    channel = pygame.mixer.Channel(TALK_CHANNEL)
                    channel.set_volume(self.sfx_volume)
                    channel.play(self.sound)        # restarts the sound - continuous chatter while typing
                    self.typed_since_sound = 0
            if char in PUNCTUATION_PAUSE and before + k + 1 < len(self.text):
                self.wait = PUNCTUATION_PAUSE[char]
                self.shown = float(before + k + 1)
                break

    # --- drawing ---------------------------------------------------------------------------------
    def draw(self):
        screen = self.screen
        sw, sh = screen.get_size()
        if self.horror and self.choices is None:
            screen.fill((0, 0, 0))                     # the world disappears for this line
        else:
            screen.blit(self.background, (0, 0))
        box = pygame.Rect(int(sw * 0.06), int(sh * 0.70), int(sw * 0.88), int(sh * 0.26))
        partner_talks = self.choices is None and self.line.get("who", "player") != "player"
        if self.partner:
            self._draw_partner(partner_talks, box.top)
        panel = pygame.Surface(box.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 235), panel.get_rect(), 0, 14)
        screen.blit(panel, box.topleft)
        pygame.draw.rect(screen, (255, 255, 255), box, 4, 14)
        pad = sh // 40
        if self.choices is None:
            self._draw_name_tag(box)
            self._draw_text(self.text[:int(self.shown)], box.inflate(-pad * 2, -pad * 2))
            if not self.typing and self.end_timer >= LINE_END_DELAY and self.timer // 25 % 2 == 0:
                tri_x, tri_y = box.right - pad * 1.6, box.bottom - pad * 1.3
                pygame.draw.polygon(screen, (255, 255, 255), [(tri_x - 10, tri_y - 8), (tri_x + 10, tri_y - 8), (tri_x, tri_y + 6)])
            hint = "Space - continue"
        else:
            self._draw_choices(box.inflate(-pad * 2, -pad * 2))
            hint = ("W/S/A/D or arrows" if len(self.choices) > CHOICE_ROWS else "W/S or arrows") + " - choose   |   Space / Enter / 1-6 - answer"
        hint_img = self.font_small.render(hint, True, (170, 170, 170))
        screen.blit(hint_img, (box.right - hint_img.get_width(), box.bottom + sh // 120))

    def _draw_partner(self, talking, floor_y):
        sw, sh = self.screen.get_size()
        height = int(sh * 0.62)
        bob = math.sin(self.timer / 7) * sh * 0.004 if talking and self.typing else 0
        centre_x = sw // 2
        bottom = floor_y + sh * 0.05 + bob
        image = self._image(self.partner, self.pose, height)
        if image is not None:
            self.screen.blit(image if talking else self._darker(image), image.get_rect(midbottom=(centre_x, bottom)))
            return
        # PLACEHOLDER (no picture yet): body + head in the speaker's colour, the pose name written on it
        color = SPEAKERS.get(self.partner, {}).get("color", (200, 200, 200))
        if not talking:
            color = tuple(int(c * 0.55) for c in color)
        body = pygame.Rect(0, 0, int(height * 0.42), int(height * 0.6))
        body.midbottom = (centre_x, bottom)
        pygame.draw.rect(self.screen, color, body, 0, int(height * 0.12))
        head_r = int(height * 0.17)
        head = (centre_x, int(body.top - head_r * 0.8))
        pygame.draw.circle(self.screen, color, head, head_r)
        outline = (255, 255, 255) if talking else (110, 110, 110)
        pygame.draw.rect(self.screen, outline, body, 3, int(height * 0.12))
        pygame.draw.circle(self.screen, outline, head, head_r, 3)
        for ex in (-head_r * 0.35, head_r * 0.35):
            pygame.draw.circle(self.screen, (20, 20, 25), (int(head[0] + ex), int(head[1] - head_r * 0.1)), max(3, head_r // 7))
        label = self.font_small.render(f"{self.partner}/{self.pose}.png", True, (0, 0, 0))
        self.screen.blit(label, label.get_rect(center=(centre_x, body.top + body.height * 0.3)))

    def _darker(self, image):
        dark = image.copy()
        dark.fill((140, 140, 140, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return dark

    def _draw_name_tag(self, box):
        who = self.line.get("who", "player")
        speaker = SPEAKERS.get(who, {})
        label = self.font_name.render(speaker.get("name", who), True, (0, 0, 0))
        tag = pygame.Rect(0, 0, label.get_width() + 36, label.get_height() + 14)
        tag.bottom = box.top + 6
        tag.left = box.left + 24
        pygame.draw.rect(self.screen, speaker.get("color", (255, 255, 255)), tag, 0, 10)
        pygame.draw.rect(self.screen, (255, 255, 255), tag, 3, 10)
        self.screen.blit(label, label.get_rect(center=tag.center))

    def _wrap(self, text, width):
        lines = []
        for paragraph in text.split("\n"):
            words, current = paragraph.split(" "), ""
            for word in words:
                test = word if not current else current + " " + word
                if self.font.size(test)[0] <= width or not current:
                    current = test
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        return lines

    def _draw_text(self, text, area):
        # wrap the WHOLE line first, so words don't jump to the next row while typing
        full = self._wrap(self.text, area.width)
        y, left = area.top, len(text)
        for row in full:
            part = row[:max(0, left)]
            if part:
                self.screen.blit(self.font.render(part, True, (255, 255, 255)), (area.left, y))
            left -= len(row) + 1
            y += self.font.get_linesize()

    def _draw_choices(self, area):
        # drawn at once, fully visible (they only start to REACT after CHOICE_DELAY - see handle_events)
        two_columns = len(self.choices) > CHOICE_ROWS
        column_width = area.width // 2 if two_columns else area.width
        for i, choice in enumerate(self.choices):
            col, row = divmod(i, CHOICE_ROWS)
            x = area.left + col * column_width
            y = area.top + row * self.font.get_linesize() * 1.15
            selected = i == self.selected
            color = (255, 230, 60) if selected else (200, 200, 200)
            text = ("> " if selected else "   ") + f"{i + 1}.  {self.ctx.format_text(choice['text'])}"
            font = self.font
            if font.size(text)[0] > column_width - 10:
                font = self.font_name                     # long answer in a narrow column: a bit smaller
            self.screen.blit(font.render(text, True, color), (x, y))
