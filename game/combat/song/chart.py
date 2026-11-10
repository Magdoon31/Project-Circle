# THE MASCOT'S CHART (10.11): what happens on which beat of its song (assets/music/bosses/lunapark/mascot.mp3,
# 56 bars, ~82 s). The beats come from the track's BEAT MAP (mascot.beats, measured: the tempo slowly goes from
# ~165.5 down to ~163 BPM; bar 1 starts 0.203 s in). Sections were measured from the track (loudness, kick, highs):
#   1-6 intro        7-10 build-up (kick from bar 8)     11-17 part A        18-26 part B (rising)
#   27-28 breath     29-36 strong                         37 breath           38-43 strong 2
#   44-47 breakdown (no highs, tension)                   48-53 climax (loudest)                 54-56 outro
# (10.11) The chart is ALWAYS THE SAME - only the very last circle aims at you - so it can be learnt like a Shapes and Beats level:
# who knows the fight knows where to stand. Still, no spot is safe for the whole song (the rotating beams sweep
# every spot; tested by standing still all over the arena).
#
# A cue = (beat it lands on, kind, settings). "warn" = beats of warning before it lands. Spots = share of the arena.
#   laser  {at: (x, y) | "player" (where you are when the warning starts), angle (deg: 0 across, 90 down), width, warn, hold}
#   grid   {angle, count, width, shift, warn, hold}           parallel lasers right across, gaps between them
#   shape  {at, form: "circle" | "square", size, warn, hold}
#   spin   {beats, arms, turn (deg per beat), rate (bullets per beat per arm), speed, start}   from the mascot
#   ring   {bullets, speed, start}                             from the mascot
#   walls  {side, gap_at (share along the edge), gap, speed, warn}   a row of bullets right across, one gap
#   move   {to: (x, y), beats}                                 the mascot moves
#   mood   {dark: 0..1, flash: True/False}                     the arena gets darker / flashes on every beat
#   end    {}                                                  the song is over: the fight is won

import random

from game.combat.song.clock import beat_of

SONG_FILE = "assets/music/bosses/lunapark/mascot.mp3"
BEAT_MAP = "assets/music/bosses/lunapark/mascot.beats"
BPM = 164.4                      # only if the beat map is missing: the average tempo ...
FIRST_BEAT_MS = 203              # ... and where bar 1 starts
SEED = 165                       # the "random" spots are always the same ones

# lasers that come one after another in part A / B / strong (spot, angle) - always in this order
LASER_ROUND = [((0.5, 0.75), 0), ((0.3, 0.5), 90), ((0.5, 0.5), 45), ((0.7, 0.5), 90),
               ((0.5, 0.25), 0), ((0.5, 0.5), 135), ((0.5, 0.5), 0), ((0.5, 0.5), 90)]
# where the chasing circles land, one after another (round the arena)
CIRCLE_ROUND = [(0.3, 0.7), (0.7, 0.7), (0.7, 0.35), (0.3, 0.35)]


def cue(bar, beat, kind, **settings):
    return (beat_of(bar, beat), kind, settings)


def laser(bar, beat, at, angle, warn=2, width=64):
    return cue(bar, beat, "laser", at=at, angle=angle, width=width, warn=warn, hold=0.5)


def round_laser(bar, beat, n):
    at, angle = LASER_ROUND[n % len(LASER_ROUND)]
    return laser(bar, beat, at, angle)


def circle(bar, beat, at, warn=2, size=95):
    return cue(bar, beat, "shape", at=at, form="circle", size=size, warn=warn, hold=0.5)


def round_circle(bar, beat, n, size=95):
    return circle(bar, beat, CIRCLE_ROUND[n % len(CIRCLE_ROUND)], size=size)


def walls(bar, side, gap_at, gap=180, speed=9):
    return cue(bar, 1, "walls", side=side, gap_at=gap_at, gap=gap, speed=speed, warn=2)


def sweep(bar, axis, spots):
    """One laser on every beat of the bar, stepping across: axis "x" = upright lasers at x = spots, "y" = across."""
    return [laser(bar, b, (x, 0.5) if axis == "x" else (0.5, x), 90 if axis == "x" else 0)
            for b, x in enumerate(spots, 1)]


# --- the sections ----------------------------------------------------------------------------------------------
def intro():
    """1-6: the mascot shows up; one thing at a time, to learn what a warning means (the first ones go
    right through where you start)."""
    return [cue(1, 1, "move", to=(0.5, 0.35), beats=4),
            laser(3, 1, (0.5, 0.8), 0), laser(4, 1, (0.5, 0.8), 90),
            laser(5, 1, (0.5, 0.75), 45), laser(5, 3, (0.5, 0.75), 135),
            cue(6, 1, "shape", at=(0.25, 0.3), form="square", size=150, warn=2, hold=1),
            cue(6, 1, "shape", at=(0.75, 0.7), form="square", size=150, warn=2, hold=1),
            circle(6, 3, (0.5, 0.8))]


def build_up():
    """7-10: circles go round the arena - every 2 beats, then a row of them on every beat; a slow ring on the
    long note (10)."""
    out = [round_circle(bar, b, n) for n, (bar, b) in enumerate((bar, b) for bar in (7, 8) for b in (1, 3))]
    out += [circle(9, b, (0.2 * b, 0.75), size=80) for b in (1, 2, 3, 4)]
    out += [cue(10, 1, "ring", bullets=20, speed=5), circle(10, 3, (0.5, 0.6))]
    return out


def part_a(rnd):
    """11-17: rotating beams from the mascot + a laser every bar; big squares on the long notes (12, 14)."""
    out = [cue(11, 1, "spin", beats=27, arms=2, turn=45, rate=4, speed=7)]
    out += [round_laser(bar, 1, bar - 11) for bar in range(11, 18)]
    for bar in (12, 14):
        for _ in range(2):
            out.append(cue(bar, 3, "shape", at=(rnd.uniform(0.15, 0.85), rnd.uniform(0.2, 0.8)), form="square",
                           size=130, warn=2, hold=1))
    return out


def part_b():
    """18-26: walls of bullets close in (one gap); 3 beams, the mascot moves round; two lasers a bar."""
    out = [cue(18, 1, "spin", beats=36, arms=3, turn=-50, rate=3, speed=7),
           cue(18, 1, "move", to=(0.25, 0.3), beats=2), cue(22, 1, "move", to=(0.75, 0.65), beats=2),
           cue(26, 1, "move", to=(0.5, 0.4), beats=2)]
    out += [walls(bar, side, gap_at) for bar, side, gap_at in
            ((18, "left", 0.5), (20, "top", 0.3), (22, "right", 0.7), (24, "bottom", 0.4), (26, "left", 0.6))]
    out += [round_laser(bar, b, n + 3) for n, (bar, b) in
            enumerate((bar, b) for bar in (19, 21, 23, 25) for b in (1, 3))]
    return out


def breath_1():
    """27-28: a breather - just two grids of lasers (stand in a gap)."""
    return [cue(27, 1, "grid", angle=90, count=8, width=70, shift=0.0, warn=3, hold=1),
            cue(28, 1, "grid", angle=0, count=5, width=70, shift=0.5, warn=3, hold=1)]


def strong_1():
    """29-36: part A and B together."""
    out = [cue(29, 1, "spin", beats=28, arms=2, turn=60, rate=4, speed=8),
           cue(29, 1, "move", to=(0.5, 0.5), beats=2)]
    out += [round_laser(bar, 1, bar - 29) for bar in range(29, 37)]
    out += [round_circle(bar, 3, bar - 29, size=85) for bar in range(29, 36)]
    out += [walls(bar, side, gap_at) for bar, side, gap_at in
            ((30, "top", 0.7), (32, "right", 0.3), (34, "bottom", 0.5))]
    out += [cue(36, 1, "ring", bullets=24, speed=6)]
    return out


def breath_2():
    """37: lasers corner to corner."""
    return [cue(37, 1, "grid", angle=45, count=7, width=60, shift=0.0, warn=3, hold=1)]


def strong_2(rnd):
    """38-43: the mascot jumps round and bursts into rings; an X of lasers where it landed."""
    out = []
    for bar in range(38, 44):
        spot = (rnd.uniform(0.2, 0.8), rnd.uniform(0.25, 0.75))
        out.append(cue(bar, 1, "move", to=spot, beats=1))
        out += [cue(bar, b, "ring", bullets=16, speed=7, start=11 * b + bar * 7) for b in (2, 4)]
        out += [laser(bar, 3, spot, 45), laser(bar, 3, spot, 135)]
    return out


def breakdown():
    """44-47: darker, slow, tense: 4 slow beams; squares land round the arena on beats 1 and 3."""
    spots = [(0.3, 0.3), (0.7, 0.7), (0.7, 0.3), (0.3, 0.7)]
    out = [cue(44, 1, "mood", dark=0.45, flash=False), cue(44, 1, "move", to=(0.5, 0.5), beats=2),
           cue(44, 1, "spin", beats=16, arms=4, turn=20, rate=3, speed=5)]
    out += [cue(bar, b, "shape", at=spots[n % 4], form="square", size=110, warn=2, hold=0.5)
            for n, (bar, b) in enumerate((bar, b) for bar in range(44, 48) for b in (1, 3))]
    return out


def climax():
    """48-53: the loudest part, but learnable: a laser on every beat stepping across the arena (always the same
    way - stand between them), 3 beams, a wall every 2 bars, the arena flashes on the beat."""
    out = [cue(48, 1, "mood", dark=0.0, flash=True),
           cue(48, 1, "spin", beats=24, arms=3, turn=50, rate=3, speed=8)]
    out += sweep(48, "x", (0.2, 0.4, 0.6, 0.8)) + sweep(49, "x", (0.8, 0.6, 0.4, 0.2))
    out += sweep(50, "y", (0.2, 0.4, 0.6, 0.8)) + sweep(51, "y", (0.8, 0.6, 0.4, 0.2))
    out += [laser(52, 1, (0.5, 0.5), 45), laser(52, 3, (0.5, 0.5), 135)]
    out += sweep(53, "x", (0.2, 0.4, 0.6, 0.8))
    out += [walls(48, "left", 0.5, gap=200, speed=8), walls(50, "bottom", 0.5, gap=200, speed=8),
            walls(52, "right", 0.5, gap=200, speed=8)]
    out += [cue(bar, 3, "ring", bullets=18, speed=7, start=bar * 13) for bar in (49, 51, 53)]
    return out


def outro():
    """54-56: it calms down; the last grids, then the song ends."""
    return [cue(54, 1, "mood", dark=0.0, flash=False),
            cue(54, 1, "ring", bullets=24, speed=6),
            cue(55, 1, "grid", angle=90, count=6, width=60, shift=0.5, warn=2, hold=1),
            cue(55, 3, "grid", angle=0, count=4, width=60, shift=0.0, warn=2, hold=1),
            circle(56, 1, "player", size=110),                     # the last one: where you stand
            cue(57, 1, "end")]


def mascot_chart():
    """All the cues of the fight, in the order they start (their warning)."""
    rnd = random.Random(SEED)
    cues = (intro() + build_up() + part_a(rnd) + part_b() + breath_1() + strong_1() + breath_2()
            + strong_2(rnd) + breakdown() + climax() + outro())
    return sorted(cues, key=lambda c: c[0] - c[2].get("warn", 0))
