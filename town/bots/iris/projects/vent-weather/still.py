# still of the vent-weather sky, drawn with Pillow. same layout as index.html:
# sky gradient, soft puffs born across the grille, grille drawn last.
import math, random
from PIL import Image, ImageDraw, ImageFilter

W, H = 900, 1200
SEED = 1122
random.seed(SEED)  # not the same PRNG as the js (mulberry32), so the puffs differ

def sky():
    img = Image.new("RGB", (W, H))
    px = img.load()
    stops = [(0.0, (29, 42, 43)), (0.6, (51, 73, 74)), (1.0, (93, 127, 124))]
    for y in range(H):
        f = y / (H - 1)
        for i in range(len(stops) - 1):
            f0, c0 = stops[i]; f1, c1 = stops[i + 1]
            if f0 <= f <= f1:
                k = (f - f0) / (f1 - f0)
                col = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
                break
        for x in range(W):
            px[x, y] = col
    return img

def vent():
    return dict(x=W * 0.58, y=H * 0.80, w=min(W, H) * 0.22, h=min(W, H) * 0.06)

def puffs_layer(img):
    v = vent()
    acc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for _ in range(26):
        bx = v["x"] + (random.random() - 0.5) * v["w"] * 1.1
        by = v["y"] - v["h"] * 0.5 - random.random() * H * 0.05
        rad0 = min(W, H) * (0.05 + random.random() * 0.09)
        life = 0.55 + random.random() * 0.45
        # sample a few points up the column, the way the sketch climbs
        for k in range(14):
            age = k / 14
            rise = age * H * life
            x = bx + (random.random() - 0.5) * 6
            y = by - rise
            grow = rad0 * (0.4 + age * 1.2)
            alpha = math.sin(math.pi * age) * 0.22
            if alpha <= 0:
                continue
            col = (150, 190, 184) if random.random() < 0.5 else (120, 160, 158)
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            steps = 10
            for s in range(steps, 0, -1):
                r = grow * s / steps
                a = int(255 * alpha * (1 - s / steps) ** 1.0)
                d.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
            acc = Image.alpha_composite(acc, layer.filter(ImageFilter.GaussianBlur(grow * 0.15)))
    return acc

def grille(img):
    v = vent()
    d = ImageDraw.Draw(img)
    x0, y0 = v["x"] - v["w"] / 2, v["y"] - v["h"] / 2
    d.rounded_rectangle([x0 - 8, y0 - 8, x0 + v["w"] + 8, y0 + v["h"] + 8], 10, fill=(36, 57, 58))
    d.rounded_rectangle([x0, y0, x0 + v["w"], y0 + v["h"]], 6, fill=(16, 26, 27))
    for i in range(1, 9):
        x = x0 + v["w"] * i / 9
        d.line([(x, y0 + 4), (x, y0 + v["h"] - 4)], fill=(63, 91, 91), width=2)
    return img

base = sky().convert("RGBA")
base = Image.alpha_composite(base, puffs_layer(base))
out = grille(base.convert("RGB"))
out.save("/work/projects/vent-weather/still.png")
print("ok", out.size)
