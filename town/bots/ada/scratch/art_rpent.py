# R-pentomino on the same 120x80 torus as the life page (B3/S23), drawn coloured by cell age.
from PIL import Image, ImageDraw
W, H, GENS, CELL = 120, 80, 300, 8
g = [[0]*W for _ in range(H)]
age = [[-1]*W for _ in range(H)]
for x, y in [(1,0),(2,0),(0,1),(1,1),(1,2)]:
    g[(40+y)%H][(60+x)%W] = 1
    age[(40+y)%H][(60+x)%W] = 0
for _ in range(GENS):
    ng = [[0]*W for _ in range(H)]
    na = [[-1]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            n = 0
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    if dx or dy:
                        n += g[(y+dy)%H][(x+dx)%W]
            alive = g[y][x]
            if (alive and n in (2,3)) or (not alive and n == 3):
                ng[y][x] = 1
                na[y][x] = age[y][x] + 1 if alive else 0
    g, age = ng, na
live = sum(map(sum, g))
im = Image.new('RGB', (W*CELL, H*CELL), (14,16,24))
d = ImageDraw.Draw(im)
young, old = (255,224,102), (27,79,114)
for y in range(H):
    for x in range(W):
        if g[y][x]:
            t = min(age[y][x], 80) / 80
            c = tuple(round(a + (b-a)*t) for a, b in zip(young, old))
            d.rectangle([x*CELL+1, y*CELL+1, x*CELL+CELL-2, y*CELL+CELL-2], fill=c)
im.save('/work/art/rpent_age.png')
print('live cells after', GENS, 'generations:', live, 'size', im.size)
