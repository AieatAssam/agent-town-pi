# a seeded painting of the colour of the week, which still has no name
import random, math
from PIL import Image, ImageDraw, ImageFilter

SEED = 1120
W, H = 1200, 900
random.seed(SEED)

base = (92, 128, 128)     # dusty teal, gone quieter
ash = (176, 170, 160)     # warm grey near the edge
deep = (48, 70, 74)

img = Image.new("RGB", (W, H), ash)
px = img.load()
# vertical wash from ash at the top to deep teal at the bottom
for y in range(H):
    t = y / H
    c = tuple(int(ash[i] * (1 - t) + deep[i] * t) for i in range(3))
    for x in range(W):
        px[x, y] = c

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
# soft rain of strokes, each a blurred ellipse in the teal family
for _ in range(260):
    cx, cy = random.uniform(0, W), random.uniform(0, H)
    rx, ry = random.uniform(10, 120), random.uniform(3, 22)
    shade = random.uniform(-18, 18)
    col = tuple(max(0, min(255, int(base[i] + shade))) for i in range(3))
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col + (random.randint(20, 60),))
layer = layer.filter(ImageFilter.GaussianBlur(6))
img = Image.alpha_composite(img.convert("RGBA"), layer)

# a horizon line that wobbles like a sea seen from far off
d2 = ImageDraw.Draw(img)
pts = []
for x in range(0, W + 1, 4):
    y = 560 + 14 * math.sin(x / 47.0) + 6 * math.sin(x / 13.0 + 1.3)
    pts.append((x, y))
d2.line(pts, fill=(60, 88, 90, 255), width=3)

# a few pale specks, the way fan-vent clouds look up close
for _ in range(40):
    x, y = random.uniform(80, W - 80), random.uniform(60, H * 0.5)
    r = random.uniform(1.5, 4)
    d2.ellipse([x - r, y - r, x + r, y + r], fill=(214, 224, 218, 200))


def moth(img):
    # the bonus stage: a small moth over the sea, wings drawn as soft shapes
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(m)
    cx, cy = 820, 300
    wing = (36, 44, 46, 235)
    for sx in (-1, 1):
        md.polygon([(cx, cy), (cx + sx * 40, cy - 46), (cx + sx * 96, cy - 30),
                    (cx + sx * 74, cy + 6), (cx + sx * 44, cy + 30), (cx + sx * 12, cy + 12)], fill=wing)
        md.ellipse([cx + sx * 30 - 8, cy - 24, cx + sx * 30 + 8, cy - 8], fill=(210, 200, 170, 180))
    md.ellipse([cx - 5, cy - 26, cx + 5, cy + 26], fill=(20, 24, 26, 255))
    md.line([(cx - 2, cy - 26), (cx - 14, cy - 44)], fill=(20, 24, 26, 255), width=2)
    md.line([(cx + 2, cy - 26), (cx + 14, cy - 44)], fill=(20, 24, 26, 255), width=2)
    m = m.filter(ImageFilter.GaussianBlur(0.8))
    return Image.alpha_composite(img.convert("RGBA"), m)

moth(img).convert("RGB").save("/work/projects/unnamed-colour/moth.png", optimize=True)
print("saved")
