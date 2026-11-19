# R-pentomino on a 120x80 torus, B3/S23. Stdlib only. Checks Ada's torus numbers.
W, H = 120, 80
R = [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)]
cx, cy = W // 2, H // 2
live = frozenset(((x + cx) % W, (y + cy) % H) for x, y in R)

def step(cells):
    counts = {}
    for (x, y) in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    k = ((x + dx) % W, (y + dy) % H)
                    counts[k] = counts.get(k, 0) + 1
    return frozenset(k for k, n in counts.items()
                     if n == 3 or (n == 2 and k in cells))

seen = {live: 0}
pops = {0: len(live)}
cur = live
maxpop, maxgen = len(live), 0
first_repeat = None
for g in range(1, 1301):
    cur = step(cur)
    pops[g] = len(cur)
    if len(cur) > maxpop:
        maxpop, maxgen = len(cur), g
    if cur in seen and first_repeat is None:
        first_repeat = (g, seen[cur])
    seen.setdefault(cur, g)
    if g >= 1300:
        break
print("pop gen300", pops[300], "gen1000", pops[1000])
print("max pop", maxpop, "at gen", maxgen)
print("first repeat: gen", first_repeat[0], "equals gen", first_repeat[1] if first_repeat else None)
if first_repeat:
    print("live cells at repeat", len(cur))
