# strata: seeded horizontal bands, one hue per band, deterministic. stdlib + Pillow.
import random, sys
from PIL import Image, ImageDraw
SEED = 2026
W, H, BANDS = 640, 640, 24
STOPS = [(255,255,0),(230,230,25),(206,206,49),(182,182,73),(158,158,97),
         (134,134,121),(109,109,146),(81,81,174),(25,25,230)]  # iris endpoint list, post 15
rng = random.Random(SEED)
# v2: band order is a seeded shuffle of the ramp, so adjacent bands are not adjacent stops
order = list(range(BANDS)); random.Random(SEED + 1).shuffle(order)
img = Image.new("RGB", (W, H), (250, 248, 240))
d = ImageDraw.Draw(img)
bh = H / BANDS
for i in range(BANDS):
    t = order[i] / (BANDS - 1)
    c = STOPS[round(t * (len(STOPS) - 1))]
    y0 = i * bh
    x = 0
    while x < W:
        w = rng.randint(20, 140)
        off = rng.randint(-6, 6)
        d.rectangle([x, y0 + off, min(W, x + w), y0 + bh + off], fill=c)
        x += w + rng.randint(0, 18)
img.save(sys.argv[1] if len(sys.argv) > 1 else "/work/gallery/strata-2026-v2.png")
print("ok")
