"""Checks for gallery/rings.py (stdlib only). Prints ALL AS EXPECTED or the failures.

For seeds 1..40: centres keep MIN_D apart; every ring radius is <= CAP * nearest
neighbour distance and keeps the circle inside the canvas; rings from different
centres never meet (r_i + r_j < d_ij); output is deterministic.
"""
import math, os, sys
sys.path.insert(0, "/work/gallery")
import rings as R

fails = []
total = 0
for seed in range(1, 41):
    pts = R.points(seed)
    if len(pts) < 2:
        fails.append("seed %d: too few points" % seed); continue
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if math.dist(pts[i], pts[j]) < R.MIN_D - 1e-9:
                fails.append("seed %d: centres %d,%d closer than MIN_D" % (seed, i, j))
    nearest = [min(math.dist(p, q) for q in pts if q is not p) for p in pts]
    rs = R.rings(seed)
    total += len(rs)
    for cx, cy, r in rs:
        k = min(range(len(pts)), key=lambda k: (pts[k][0]-cx)**2 + (pts[k][1]-cy)**2)
        if r > R.CAP * nearest[k] + 1e-9:
            fails.append("seed %d: ring above cap" % seed)
        if cx - r < 0 or cy - r < 0 or cx + r > R.W or cy + r > R.H:
            fails.append("seed %d: ring leaves canvas" % seed)
    # pairwise: rings of different centres must not meet
    per = {}
    for cx, cy, r in rs:
        per.setdefault((cx, cy), []).append(r)
    centres = list(per)
    for a in range(len(centres)):
        for b in range(a + 1, len(centres)):
            ra = max(per[centres[a]]); rb = max(per[centres[b]])
            d = math.dist(centres[a], centres[b])
            if ra + rb >= d:
                fails.append("seed %d: outer rings of two points meet" % seed)
    if R.build(seed) != R.build(seed):
        fails.append("seed %d: not deterministic" % seed)

if total == 0:
    fails.append("no rings produced")
print("seeds 1..40, rings checked: %d" % total)
uniq = sorted(set(fails))
if not uniq:
    print("ALL AS EXPECTED")
else:
    print("%d distinct failure lines, first 3 shown:" % len(uniq))
    print("\n".join(uniq[:3]))
    sys.exit(1)
