# Torus check (B3/S23, 120x80 wrap, R-pentomino at centre). Reports population and first repeat of the whole board.
from collections import Counter
W, H = 120, 80
ox, oy = 60, 40
cells = {((x+ox) % W, (y+oy) % H) for x, y in {(1,0),(2,0),(0,1),(1,1),(1,2)}}
def step(s):
    c = Counter(((x+dx) % W, (y+dy) % H) for x, y in s for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy)
    return {p for p, n in c.items() if n == 3 or (n == 2 and p in s)}
seen = {frozenset(cells): 0}
s = cells
pops = {}
MAX = 5000
for gen in range(1, MAX+1):
    s = step(s)
    pops[gen] = len(s)
    key = frozenset(s)
    if key in seen:
        print('board repeats: gen', gen, 'equals gen', seen[key], '-> period', gen - seen[key])
        break
    seen[key] = gen
else:
    print('no repeat up to gen', MAX)
for g in (50, 100, 300, 500, 1000, 1103, 1200, 2000):
    if g in pops: print('gen', g, 'pop', pops[g])
print('max pop', max(pops.values()), 'at gen', max(pops, key=pops.get))
print('last gen computed', max(pops))
print('pop at 1044,1045,1046,1047:', [pops.get(g) for g in (1044,1045,1046,1047)])
