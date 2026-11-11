# MOTION BLUR (11.11, Settings -> Video): the last frame is laid over the new one, faintly - moving things leave a
# short trail. One for the map and one for fights (Game / Combat call apply() just before the frame is shown).

TRAIL = {"off": 0, "light": 55, "strong": 110}      # how much of the frame before shows (0-255)


class MotionBlur:
    def __init__(self):
        self.last = None

    def apply(self, screen, strength):
        """strength: off / light / strong (options.blur_strength)."""
        if strength == "off":
            self.last = None
            return
        if self.last is not None and self.last.get_size() == screen.get_size():
            self.last.set_alpha(TRAIL[strength])
            screen.blit(self.last, (0, 0))
        self.last = screen.copy()
