# WALL TACTICS (8.11): how enemies move when there are walls in the fight (room obstacles, ice walls).
#
#   chasers  (movement "to_player")  walk the shortest way round the walls to their target.
#   shooters (the rest)               keep you in sight: a step that would hide you behind a wall isn't taken; if they
#                                     lost you, they walk sideways-forward round the wall to the nearest spot with a
#                                     clear shot (a "vantage" point on a ring round you) - not up to the wall and back.
#   throwers (have a "throw" attack)  the other way round: they hide behind a wall (their bombs fly over it) and
#                                     don't step out of cover.
#
# Combat asks plan(enemy, target, walls, arena size, timer) -> a Plan: where to go and how.
# Only geometry lives here - no drawing, no fight state.

import math
from dataclasses import dataclass

STEER_MARGIN = 8           # px an enemy keeps from a wall's corner when it walks round it
REPLAN_FRAMES = 10         # a vantage / cover point is chosen again only this often
WAY_FRAMES = 8             # the way round the walls is found again only this often
VANTAGE_TURN = 100         # degrees: how far round you a shooter may go to find a clear shot
VANTAGE_STEP = 10          # degrees between the spots it tries
VANTAGE_RANGE = (320, 900) # px from you a shooter likes to shoot from
COVER_RINGS = (120, 220, 340, 480)  # px from itself where a thrower looks for cover
COVER_RANGE = (260, 950)   # px from you a hiding thrower must still be (its bombs have to reach)
EDGE = 60                  # px kept from the arena's edge


@dataclass
class Plan:
    goal: tuple            # where to move to (x, y)
    chase: bool = False    # True = walk straight at `goal` (whatever its own movement is)
    keep: str = ""         # "sight" = undo a step that loses you; "cover" = undo a step that shows it to you


# --- geometry ----------------------------------------------------------------------------------------------
def sees(a, b, walls):
    """Nothing stands between a and b."""
    return not any(w["rect"].clipline(a, b) for w in walls)


def bodies_for(enemy, walls):
    """The walls grown by the enemy's size (a hair smaller, so one pressed against a wall isn't 'inside' it)."""
    grow = enemy.width * 2 - 4
    here = (enemy.x, enemy.y)
    return [r for r in (w["rect"].inflate(grow, grow) for w in walls) if not r.collidepoint(here)]


def free_line(a, b, bodies):
    return not any(r.clipline(a, b) for r in bodies)


def inside_arena(point, size):
    return EDGE < point[0] < size[0] - EDGE and EDGE < point[1] < size[1] - EDGE


def standable(point, bodies, size):
    return inside_arena(point, size) and not any(r.collidepoint(point) for r in bodies)


# --- the way round the walls ---------------------------------------------------------------------------------
def first_step(start, goal, bodies):
    """The next corner on the shortest way from start to goal round the walls (visibility graph + Dijkstra)."""
    if free_line(start, goal, bodies):
        return goal
    nodes = [start, goal] + corners(bodies)
    dist, prev, todo = {0: 0.0}, {}, set(range(len(nodes)))
    while todo:
        u = min((n for n in todo if n in dist), key=dist.get, default=None)
        if u is None or u == 1:
            break
        todo.discard(u)
        for v in list(todo):
            if free_line(nodes[u], nodes[v], bodies):
                d = dist[u] + math.dist(nodes[u], nodes[v])
                if d < dist.get(v, math.inf):
                    dist[v], prev[v] = d, u
    if 1 not in prev:
        return goal                                   # no way round: just push on
    v = 1
    while prev[v] != 0:
        v = prev[v]
    return nodes[v]


def corners(bodies):
    out = []
    for r in bodies:
        grown = r.inflate(STEER_MARGIN * 2, STEER_MARGIN * 2)
        for c in (grown.topleft, grown.topright, grown.bottomleft, grown.bottomright):
            if not any(o.collidepoint(c) for o in bodies):
                out.append(c)
    return out


def step_towards(enemy, goal, bodies, timer):
    """first_step, but found again only every WAY_FRAMES (kept on the enemy)."""
    here = (enemy.x, enemy.y)
    cached = enemy.__dict__.get("_way")
    if cached and timer - cached[0] < WAY_FRAMES and cached[2] == goal \
            and math.dist(here, cached[1]) > enemy.width and free_line(here, cached[1], bodies):
        return cached[1]
    step = first_step(here, goal, bodies)
    enemy._way = (timer, step, goal)
    return step


# --- where to stand ----------------------------------------------------------------------------------------
def vantage_point(enemy, target, walls, bodies, size):
    """The nearest spot (round you, sideways from where it stands) with a clear shot at you."""
    tx, ty = target.x, target.y
    angle = math.atan2(enemy.y - ty, enemy.x - tx)
    radius = min(max(math.dist((enemy.x, enemy.y), (tx, ty)), VANTAGE_RANGE[0]), VANTAGE_RANGE[1])
    for turn in range(0, VANTAGE_TURN + 1, VANTAGE_STEP):        # the smallest turn first
        for side in ((1, -1) if turn else (1,)):
            a = angle + math.radians(turn * side)
            spot = (tx + math.cos(a) * radius, ty + math.sin(a) * radius)
            if standable(spot, bodies, size) and sees(spot, (tx, ty), walls):
                return spot
    return None


def cover_point(enemy, target, walls, bodies, size):
    """The nearest spot behind a wall from you that is still close enough to throw at you."""
    best = None
    for ring in COVER_RINGS:
        for k in range(16):
            a = math.tau * k / 16
            spot = (enemy.x + math.cos(a) * ring, enemy.y + math.sin(a) * ring)
            far = math.dist(spot, (target.x, target.y))
            if not COVER_RANGE[0] <= far <= COVER_RANGE[1] or not standable(spot, bodies, size):
                continue
            if not sees(spot, (target.x, target.y), walls):
                if best is None or ring < best[0]:
                    best = (ring, spot)
        if best:
            return best[1]
    return None


def remembered(enemy, key, timer, choose):
    """A vantage / cover point kept on the enemy for REPLAN_FRAMES."""
    kept = enemy.__dict__.get(key)
    if kept and timer - kept[0] < REPLAN_FRAMES:
        return kept[1]
    spot = choose()
    setattr(enemy, key, (timer, spot))
    return spot


# --- the plan ----------------------------------------------------------------------------------------------
def is_thrower(enemy):
    return "throw" in enemy.attacks


def is_chaser(enemy):
    return "to_player" in enemy.movement_type


def plan(enemy, target, walls, size, timer):
    """What an enemy does this frame with walls around."""
    here, there = (enemy.x, enemy.y), (target.x, target.y)
    if not walls:
        return Plan(there)
    bodies = bodies_for(enemy, walls)
    if is_chaser(enemy):
        step = step_towards(enemy, there, bodies, timer)
        # (11.11) going round a wall, "keep a distance" movers (gum goblin) must not stop at the corner: their
        # distance check would measure the corner, not you - they walk straight to it instead
        return Plan(step, chase=step != there and "distance" in enemy.movement_type)
    in_sight = sees(here, there, walls)
    if is_thrower(enemy):
        if not in_sight:
            return Plan(there, keep="cover")
        spot = remembered(enemy, "_cover", timer, lambda: cover_point(enemy, target, walls, bodies, size))
        return Plan(step_towards(enemy, spot, bodies, timer), chase=True) if spot else Plan(there)
    if in_sight:
        return Plan(there, keep="sight")
    spot = remembered(enemy, "_vantage", timer, lambda: vantage_point(enemy, target, walls, bodies, size))
    return Plan(step_towards(enemy, spot or there, bodies, timer), chase=True)


def step_breaks_rule(plan_, enemy, before, target, walls):
    """After moving: did the step break the plan's rule (lose sight / leave cover)?"""
    if not plan_.keep:
        return False
    there = (target.x, target.y)
    was, now = sees(before, there, walls), sees((enemy.x, enemy.y), there, walls)
    if plan_.keep == "sight":
        return was and not now
    drifts_off = math.dist((enemy.x, enemy.y), there) > max(COVER_RANGE[1], math.dist(before, there))
    return (not was and now) or drifts_off            # cover: don't step out, don't wander out of throwing range
