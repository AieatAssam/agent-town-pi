#!/usr/bin/env python3
"""rings: seeded dart-throwing points, each with concentric rings (stdlib only).

Points are placed by dart throwing with a minimum spacing, so there is no grid.
Each point's rings stop at 0.4 of its nearest-neighbour distance, and inside the
canvas. Because each radius is below 0.4 of the nearest distance, rings from two
neighbouring points cannot meet (r_i + r_j < d_ij).
Usage: python3 -I rings.py SEED > out.svg
"""
import math
import random
import sys

W = H = 640
MARGIN = 12.0
MIN_D = 44.0      # minimum spacing between centres
N_TARGET = 90
TRIES = 4000
CAP = 0.4         # ring radius limit as a fraction of nearest-neighbour distance
GAP = 7.0         # spacing between rings
INK = "#20303f"
PAPER = "#f6f3ea"


def points(seed):
    rng = random.Random(seed)
    pts = []
    for _ in range(TRIES):
        if len(pts) >= N_TARGET:
            break
        x = MARGIN + rng.random() * (W - 2 * MARGIN)
        y = MARGIN + rng.random() * (H - 2 * MARGIN)
        if all((x - px) ** 2 + (y - py) ** 2 >= MIN_D * MIN_D for px, py in pts):
            pts.append((x, y))
    return pts


def rings(seed):
    """Return a list of (cx, cy, r) for every ring, in point order."""
    pts = points(seed)
    if len(pts) < 2:
        return []  # a single centre has no neighbour, so no ring limit
    out = []
    for i, (x, y) in enumerate(pts):
        nearest = min(math.hypot(x - px, y - py)
                      for j, (px, py) in enumerate(pts) if j != i)
        edge = min(x, y, W - x, H - y)
        limit = min(CAP * nearest, edge)
        r = GAP
        while r <= limit:
            out.append((x, y, r))
            r += GAP
    return out


def build(seed):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d">' % (W, H, W, H),
        "<title>rings, seed %s</title>" % seed,
        '<rect width="%d" height="%d" fill="%s"/>' % (W, H, PAPER),
        '<g fill="none" stroke="%s" stroke-width="1">' % INK,
    ]
    for cx, cy, r in rings(seed):
        parts.append('<circle cx="%.2f" cy="%.2f" r="%.2f"/>' % (cx, cy, r))
    parts.append("</g></svg>")
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    sys.stdout.write(build(seed))
