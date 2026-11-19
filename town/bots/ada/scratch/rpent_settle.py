# Sparse plane check (B3/S23, no wrap): when does the R-pentomino stabilise, and how many cells remain?
from collections import Counter
cells = {(1,0),(2,0),(0,1),(1,1),(1,2)}
def step(s):
    c = Counter((x+dx, y+dy) for x, y in s for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy)
    return {p for p, n in c.items() if n == 3 or (n == 2 and p in s)}
hist = {}
s = cells
for gen in range(1, 1201):
    s = step(s)
    hist[gen] = frozenset(s)
    if gen in (300, 1103, 1200):
        print('gen', gen, 'live', len(s))
# find first generation after which the board never changes again (checked up to 1200)
last_change = max(g for g in range(1, 1200) if hist[g] != hist[g+1])
print('last change at gen', last_change, '-> stable from gen', last_change+1)
print('period-2 from 1103?', all(hist[g] == hist[g+2] for g in range(1103, 1199)))
print('changes after 1103:', sum(hist[g] != hist[g+1] for g in range(1103, 1199)))
