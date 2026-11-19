#!/usr/bin/env python3
"""Quarter-circle Truchet tiles, seeded. Iris, gallery piece 1.

Stdlib only, deterministic: the same seed always gives the same SVG bytes.

    python3 -I truchet.py SEED > truchet-SEED.svg
    python3 -I truchet.py 2026 > truchet-2026.svg
"""
import sys

GRID = 16          # tiles per side
CELL = 40.0        # user units per tile
PAD = 24.0         # margin
STROKE = 7.0       # stroke width of each arc
PAPER = "#f4efe6"
INK = "#1d3b4f"
ACCENT = "#c2553a"
ACCENT_ODDS = 16   # about 1 tile in 16 is drawn in the accent colour


class XorShift32:
    """Small, fixed generator, so output does not depend on the Python version."""

    def __init__(self, seed):
        x = (seed & 0xFFFFFFFF) or 0x9E3779B9
        # Warm up so that small seeds (1, 2, 3...) do not look alike.
        for _ in range(8):
            x = self._step(x)
        self.x = x

    @staticmethod
    def _step(x):
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        return x

    def below(self, n):
        self.x = self._step(self.x)
        return self.x % n


def fmt(v):
    """Fixed-precision number, trailing zeros trimmed, so output is stable."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def arcs(orientation, ox, oy):
    """Two quarter-circle arcs for one tile, as SVG path data.

    Orientation 0 has arcs centred on the top-left and bottom-right corners;
    orientation 1 has them centred on the top-right and bottom-left corners.
    The sweep flags are chosen so each arc bows toward the tile centre.
    """
    h = 0.5 * CELL
    if orientation == 0:
        a = (ox + h, oy, 1, ox, oy + h, 1)               # centre (0,0)
        b = (ox + CELL, oy + h, 0, ox + h, oy + CELL, 0)  # centre (1,1)
    else:
        a = (ox + h, oy, 0, ox + CELL, oy + h, 0)         # centre (1,0)
        b = (ox, oy + h, 1, ox + h, oy + CELL, 1)         # centre (0,1)
    out = []
    for x0, y0, sweep, x1, y1, _ in (a, b):
        out.append(
            f"M{fmt(x0)} {fmt(y0)}A{fmt(h)} {fmt(h)} 0 0 {sweep} {fmt(x1)} {fmt(y1)}"
        )
    return out


def build(seed):
    rng = XorShift32(seed)
    width = 2 * PAD + GRID * CELL
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{fmt(width)}" height="{fmt(width)}" '
        f'viewBox="0 0 {fmt(width)} {fmt(width)}">',
        f'<title>Truchet quarter turns, seed {seed}</title>',
        f'<rect width="100%" height="100%" fill="{PAPER}"/>',
        f'<g fill="none" stroke-width="{fmt(STROKE)}" stroke-linecap="butt">',
    ]
    ink_paths, accent_paths = [], []
    for j in range(GRID):
        for i in range(GRID):
            orientation = rng.below(2)
            accent = rng.below(ACCENT_ODDS) == 0
            ox = PAD + i * CELL
            oy = PAD + j * CELL
            (accent_paths if accent else ink_paths).extend(arcs(orientation, ox, oy))
    parts.append(f'<path stroke="{INK}" d="{"".join(ink_paths)}"/>')
    if accent_paths:
        parts.append(f'<path stroke="{ACCENT}" d="{"".join(accent_paths)}"/>')
    parts.append("</g></svg>")
    return "\n".join(parts) + "\n"


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: truchet.py SEED\n")
        return 2
    try:
        seed = int(argv[1])
    except ValueError:
        sys.stderr.write("SEED must be an integer\n")
        return 2
    sys.stdout.write(build(seed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
