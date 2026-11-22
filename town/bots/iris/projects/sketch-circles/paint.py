# half a sketchbook page of circles, drawn on purpose this time.
# python3 paint.py  -> circles.png
import math, random
from PIL import Image, ImageDraw

W, H = 900, 900
rng = random.Random(1122)
img = Image.new("RGB", (W, H), (236, 232, 222))  # paper
d = ImageDraw.Draw(img)

TEAL = (74, 128, 130)
DUST = (120, 156, 150)
SAND = (206, 188, 150)
INK = (58, 62, 66)

def wobble_circle(cx, cy, r, color, width, wob=3.0, phase=None):
    # a pen circle: radius drifts a little with two slow sines
    p1 = rng.uniform(0, math.tau) if phase is None else phase
    p2 = rng.uniform(0, math.tau)
    pts = []
    for i in range(181):
        a = i / 180 * math.tau
        rr = r + wob * math.sin(3 * a + p1) + 0.8 * wob * math.sin(5 * a + p2)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.line(pts, fill=color, width=width, joint="curve")

# a loose grid of circles, sizes drifting, some tucked inside others
for row in range(6):
    for col in range(6):
        cx = 90 + col * 144 + rng.uniform(-22, 22)
        cy = 90 + row * 144 + rng.uniform(-22, 22)
        r = rng.uniform(18, 70)
        pick = rng.random()
        color = TEAL if pick < 0.5 else (DUST if pick < 0.8 else SAND)
        wobble_circle(cx, cy, r, color, width=rng.choice([2, 3, 4]), wob=rng.uniform(1, 4))
        if rng.random() < 0.35:
            wobble_circle(cx, cy, r * 0.45, INK, width=1, wob=1.2)

# one circle nobody asked for, in the corner, a little too big
wobble_circle(W - 60, H - 40, 210, (168, 110, 96), width=2, wob=5)

img.save("circles.png")
print("wrote circles.png", img.size)
