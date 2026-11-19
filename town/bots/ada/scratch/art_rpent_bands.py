# R-pentomino, same torus as the life page (B3/S23, 300 gens), coloured in three age bands with a legend.
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
            n = sum(g[(y+dy)%H][(x+dx)%W] for dy in (-1,0,1) for dx in (-1,0,1) if dx or dy)
            alive = g[y][x]
            if (alive and n in (2,3)) or (not alive and n == 3):
                ng[y][x] = 1
                na[y][x] = age[y][x] + 1 if alive else 0
    g, age = ng, na
BANDS = [(0, 9, (255,224,102), 'newborn 0-9'), (10, 99, (230,126,34), 'young 10-99'), (100, 10**9, (27,79,114), 'old 100+')]
def band(a):
    for lo, hi, c, _ in BANDS:
        if lo <= a <= hi:
            return c
LEG = 56
im = Image.new('RGB', (W*CELL, H*CELL + LEG), (14,16,24))
d = ImageDraw.Draw(im)
for y in range(H):
    for x in range(W):
        if g[y][x]:
            d.rectangle([x*CELL+1, y*CELL+1, x*CELL+CELL-2, y*CELL+CELL-2], fill=band(age[y][x]))
for i, (_, _, c, label) in enumerate(BANDS):
    x0 = 12 + i*320
    d.rectangle([x0, H*CELL+14, x0+26, H*CELL+40], fill=c)
    d.text((x0+36, H*CELL+20), label, fill=(230,230,230))
im.save('/work/art/rpent_bands.png')
print('live', sum(map(sum, g)), 'size', im.size)
