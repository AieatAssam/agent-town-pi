# Vex: an Archimedean spiral "rant meter", drawn with Pillow. No grid.
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 640, 640
img = Image.new("RGB", (W, H), (250, 244, 232))
d = ImageDraw.Draw(img)
cx, cy = W / 2, H / 2 + 10

# One spiral of 1200 points, drawn as short segments with colour from calm to loud.
pts = []
for i in range(1200):
    t = i / 1200
    ang = t * 6 * math.pi
    r = 12 + t * 260
    pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang), t))
for (x0, y0, t0), (x1, y1, t1) in zip(pts, pts[1:]):
    col = (int(40 + 200 * t1), int(60 * (1 - t1)), int(120 * (1 - t1)))
    d.line([(x0, y0), (x1, y1)], fill=col, width=3)

# A ring of ticks around the outside: the "volume" dial. Not a grid.
for k in range(48):
    a = k / 48 * 2 * math.pi
    r1, r2 = 290, 290 + (18 if k % 6 == 0 else 8)
    d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
            (cx + r2 * math.cos(a), cy + r2 * math.sin(a))],
           fill=(30, 30, 30), width=3 if k % 6 == 0 else 1)

try:
    f = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
    s = ImageFont.truetype("DejaVuSans.ttf", 20)
except OSError:
    f = s = ImageFont.load_default()
d.rectangle([W/2-170, 22, W/2+170, 62], fill=(250, 244, 232))
d.text((W / 2, 36), "VEX RANT METER", fill=(30, 30, 30), font=f, anchor="mt")
d.rectangle([W/2-170, H-44, W/2+170, H-16], fill=(250, 244, 232))
d.text((W / 2, H - 30), "one spiral. zero grids.", fill=(120, 40, 40), font=s, anchor="mm")
img.save("/work/art/vex-spiral.png")
print("saved", img.size)
