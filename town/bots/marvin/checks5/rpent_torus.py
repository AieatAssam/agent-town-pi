# B3/S23 on a W x H torus, R-pentomino at centre. Stdlib only.
import sys
W, H, GENS = 120, 80, 300
def step(g):
    n = [[0]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if g[y][x]:
                for dy in (-1,0,1):
                    for dx in (-1,0,1):
                        if dx or dy:
                            n[(y+dy)%H][(x+dx)%W] += 1
    return [[1 if (n[y][x]==3 or (n[y][x]==2 and g[y][x])) else 0 for x in range(W)] for y in range(H)]
g = [[0]*W for _ in range(H)]
cx, cy = W//2, H//2
for (dx,dy) in [(0,-1),(1,-1),(-1,0),(0,0),(0,1)]:
    g[cy+dy][cx+dx] = 1
seen = {}
pop = []
for t in range(GENS+1):
    key = tuple(map(tuple, g))
    if key in seen:
        print("cycle/fixed: gen", t, "repeats gen", seen[key]); break
    seen[key] = t
    pop.append(sum(map(sum, g)))
    g = step(g)
print("populations at gens 0,50,...:", [pop[i] for i in range(0, len(pop), 50)])
print("last gen computed:", len(pop)-1, "pop", pop[-1])
