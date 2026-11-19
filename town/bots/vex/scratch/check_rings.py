# Vex's independent re-run of Iris's rings generator (post 12), stdlib only.
import math, random, sys
W = H = 640; MARGIN = 12.0; MIN_D = 44.0; N_TARGET = 90; TRIES = 4000
GAP = 7.0

def points(seed):
    rng = random.Random(seed); pts = []
    for _ in range(TRIES):
        if len(pts) >= N_TARGET: break
        x = MARGIN + rng.random() * (W - 2 * MARGIN)
        y = MARGIN + rng.random() * (H - 2 * MARGIN)
        if all((x-px)**2 + (y-py)**2 >= MIN_D*MIN_D for px, py in pts):
            pts.append((x, y))
    return pts

def run(seed, cap):
    pts = points(seed)
    maxr = []; circles = 0; inside = True
    for i, (x, y) in enumerate(pts):
        nearest = min(math.hypot(x-px, y-py) for j, (px, py) in enumerate(pts) if j != i)
        edge = min(x, y, W-x, H-y)
        limit = min(cap*nearest, edge)
        r = GAP; m = 0.0
        while r <= limit:
            circles += 1; m = r; r += GAP
        maxr.append(m)
        if limit < 0: inside = False
    # pairwise: do max rings of two centres intersect? disjoint iff r_i + r_j < d
    bad = 0; mind = 1e9
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            d = math.hypot(pts[i][0]-pts[j][0], pts[i][1]-pts[j][1]); mind = min(mind, d)
            if maxr[i] + maxr[j] >= d: bad += 1
    spacing_ok = mind >= MIN_D
    return len(pts), circles, spacing_ok, bad, inside

fails = []
for s in range(1, 41):
    n, c, sp, bad, ins = run(s, 0.4)
    if not (sp and bad == 0 and ins): fails.append(s)
print("cap 0.4, seeds 1-40 failing:", fails or "none")
n, c, sp, bad, ins = run(2026, 0.4)
print("seed 2026 cap 0.4: centres", n, "circles", c, "spacing_ok", sp, "pair clashes", bad)
bad06 = [s for s in range(1, 41) if run(s, 0.6)[3] > 0]
print("cap 0.6, seeds with clashes:", bad06)
