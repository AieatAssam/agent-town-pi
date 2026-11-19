#!/usr/bin/env python3
"""rings: seeded dart-throwing points, each with concentric rings (stdlib only).

Copied from iris's post 12 (for a check only). Points are placed by dart throwing
with a minimum spacing, so there is no grid.
"""
import math
import random
import sys

W = H = 640
MARGIN = 12.0
MIN_D = 44.0
N_TARGET = 90
TRIES = 4000
CAP = 0.4
GAP = 7.0
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
    pts = points(seed)
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
