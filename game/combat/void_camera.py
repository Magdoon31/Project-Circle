# THE VOID'S CAMERA (11.11, the interlude and the end): zoom, a little turn, and where it looks. VoidFight tells it
# what to do (a kick on a big beat, a slow zoom, look at the boss); Combat asks it lens() and focus() when it draws
# (Combat.draw_view / follow_camera). Never too much: the zoom stays within MAX_ZOOM, the turn within MAX_TURN.

MAX_ZOOM = 1.5
MAX_TURN = 3.0                    # degrees
SETTLE = 0.08                     # how quickly a kick's zoom dies away (share per frame) ...
TURN_SETTLE = 0.12                # ... and its turn (a turned picture costs much more to draw: keep it short)
STILL_ZOOM = 0.003                # closer to normal than this = normal (drawn the cheap way, no lens at all)
STILL_TURN = 0.15                 # degrees
EASE = 0.03                       # how quickly the base zoom / the focus change


class VoidCamera:
    def __init__(self):
        self.reset()

    def reset(self):
        self.base_zoom = self.zoom_goal = 1.0
        self.kick_zoom = self.kick_turn = 0.0
        self.look_at = None                       # (x, y) the camera looks at instead of you (None = at you)
        self.timer = 0

    # --- what VoidFight says ------------------------------------------------------------------------------------
    def kick(self, zoom=0.0, turn=0.0):
        """A short punch (a big beat): a bit closer, a bit turned, then it settles back."""
        self.kick_zoom = max(self.kick_zoom, zoom)
        self.kick_turn = turn or self.kick_turn

    def zoom_to(self, zoom):
        self.zoom_goal = zoom

    def look(self, at):
        self.look_at = at

    # --- every frame -------------------------------------------------------------------------------------------
    def update(self):
        self.timer += 1
        self.base_zoom += (self.zoom_goal - self.base_zoom) * EASE
        if abs(self.zoom_goal - self.base_zoom) < STILL_ZOOM:
            self.base_zoom = self.zoom_goal
        self.kick_zoom = self.kick_zoom * (1 - SETTLE) if self.kick_zoom > STILL_ZOOM else 0.0
        self.kick_turn = self.kick_turn * (1 - TURN_SETTLE) if abs(self.kick_turn) > STILL_TURN else 0.0

    # --- what Combat asks --------------------------------------------------------------------------------------
    def lens(self):
        """(zoom, turn in degrees) for drawing. (11.11) Turned only for a moment after a kick - turning the whole
        picture every frame made the end lag."""
        zoom = min(MAX_ZOOM, self.base_zoom + self.kick_zoom)
        return zoom, max(-MAX_TURN, min(MAX_TURN, self.kick_turn))

    def focus(self, player_pos):
        return self.look_at if self.look_at else player_pos
