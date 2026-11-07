# Simple seeded 2D noise (value noise + octaves). No external libraries (easier with PyInstaller).
import math, random


class ValueNoise:
    def __init__(self, seed):
        rnd = random.Random(seed)
        self.perm = list(range(256))
        rnd.shuffle(self.perm)
        self.perm += self.perm
        self.values = [rnd.random() * 2 - 1 for _ in range(256)]

    def _lattice(self, x, y):
        return self.values[self.perm[(self.perm[x & 255] + y) & 255]]

    def noise(self, x, y):
        # smooth noise in range ~[-1, 1], features about 1 unit apart
        x0, y0 = math.floor(x), math.floor(y)
        fx, fy = x - x0, y - y0
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a = self._lattice(x0, y0) + (self._lattice(x0 + 1, y0) - self._lattice(x0, y0)) * sx
        b = self._lattice(x0, y0 + 1) + (self._lattice(x0 + 1, y0 + 1) - self._lattice(x0, y0 + 1)) * sx
        return a + (b - a) * sy

    def fractal(self, x, y, octaves=4, persistence=0.5):
        total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
        for _ in range(octaves):
            total += self.noise(x * freq, y * freq) * amp
            norm += amp
            amp *= persistence
            freq *= 2
        return total / norm


def coarse_field(noise, scale, width, height, step=4):
    """noise.fractal sampled every `step` tiles and smoothly interpolated (fast); field[y][x] ~ -0.6..0.6"""
    cw, ch = width // step + 2, height // step + 2
    coarse = [[noise.fractal(cx * step / scale, cy * step / scale) for cx in range(cw)] for cy in range(ch)]
    field = [[0.0] * width for _ in range(height)]
    for y in range(height):
        cy, fy = divmod(y, step)
        ty = fy / step
        row0, row1 = coarse[cy], coarse[cy + 1]
        out = field[y]
        for x in range(width):
            cx, fx = divmod(x, step)
            tx = fx / step
            a = row0[cx] + (row0[cx + 1] - row0[cx]) * tx
            b = row1[cx] + (row1[cx + 1] - row1[cx]) * tx
            out[x] = a + (b - a) * ty
    return field
