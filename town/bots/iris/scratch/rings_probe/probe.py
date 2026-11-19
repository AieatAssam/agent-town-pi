import sys, math
sys.path.insert(0, "/work/gallery")
import rings as R
# 1. centre counts for seeds 1..40 at the shipped settings
short = []
for s in range(1, 41):
    n = len(R.points(s))
    if n < R.N_TARGET:
        short.append((s, n))
print("seeds with fewer than 90 centres:", short)
print("seed 2026 centres:", len(R.points(2026)))
# 2. cap 0.6 failure pattern, same test as the checker (cap-only and meet-only)
R.CAP = 0.6
bad_meet, bad_cap = [], []
for s in range(1, 41):
    pts = R.points(s)
    nearest = [min(math.dist(p, q) for q in pts if q is not p) for p in pts]
    rs = R.rings(s)
    per = {}
    for cx, cy, r in rs:
        per.setdefault((cx, cy), []).append(r)
    cs = list(per)
    if any(r > 0.4 * 0 + 1e9 for _ in []): pass
    meet = False
    for a in range(len(cs)):
        for b in range(a+1, len(cs)):
            if max(per[cs[a]]) + max(per[cs[b]]) >= math.dist(cs[a], cs[b]):
                meet = True; break
        if meet: break
    if meet: bad_meet.append(s)
print("cap 0.6: seeds where outer rings of two centres meet:", bad_meet)
