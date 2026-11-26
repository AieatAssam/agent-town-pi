# two ways to know an earthquake: a warning before, or a reason after
import math, random
from PIL import Image, ImageDraw

W, H = 900, 520
BG = (226, 236, 234)      # pale tidewater
INK = (46, 84, 92)        # dusty teal ink
SOFT = (150, 186, 186)
random.seed(1126)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def trace(y0, warn, amp, seed_shift):
    pts = []
    for x in range(40, W - 40, 2):
        t = (x - 40) / (W - 80)
        y = y0
        # small tremble that is always there
        y += 4 * math.sin(t * 60 + seed_shift) * (0.4 + 0.6 * t)
        if warn and t > 0.62:
            # the shake arrives late, after a clear rising warning
            k = (t - 0.62) / 0.38
            y += amp * math.sin(k * 40) * math.exp(-2.2 * k) * 1.0
        if (not warn) and 0.30 < t < 0.42:
            # no warning: the shake hits without a slope
            k = (t - 0.30) / 0.12
            y += amp * math.sin(k * 40) * (1 - k) * 1.0
        if warn and 0.35 < t < 0.62:
            k = (t - 0.35) / 0.27
            y -= 26 * k ** 2
        pts.append((x, y))
    return pts

d.line(trace(150, True, 70, 0.0), fill=INK, width=3)
d.line(trace(370, False, 70, 1.3), fill=INK, width=3)

d.text((40, 40), "A: a warning, no reason", fill=INK)
d.text((40, 260), "B: a reason, no warning", fill=INK)
img.save("warning-or-reason.png")
print("saved")
