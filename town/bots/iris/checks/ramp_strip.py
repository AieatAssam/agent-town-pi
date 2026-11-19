"""Draw two straight RGB ramps as strips, with a lightness bar under each.

Deterministic: no randomness. Needs Pillow.
Usage: python3 -I ramp_strip.py OUT.png
"""
import sys
sys.path.insert(0, "/work/checks")
from PIL import Image, ImageDraw
from ramp_lightness import lstar

W, H = 480, 150
N = 256

def strip(draw, y0, a, b):
    for i in range(N):
        t = i / (N - 1)
        c = tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))
        x0 = 20 + i * (440 / N)
        draw.rectangle([x0, y0, x0 + 440 / N + 1, y0 + 40], fill=c)
    for i in range(N):
        t = i / (N - 1)
        c = tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3))
        L = lstar(c)
        g = round(255 * L / 100)
        x0 = 20 + i * (440 / N)
        draw.rectangle([x0, y0 + 50, x0 + 440 / N + 1, y0 + 66], fill=(g, g, g))

def main(out):
    img = Image.new("RGB", (W, H), (244, 240, 230))
    d = ImageDraw.Draw(img)
    strip(d, 14, (255, 255, 0), (0, 0, 255))
    strip(d, 84, (0, 0, 255), (255, 0, 0))
    img.save(out, "PNG", optimize=True)
    print(out, img.size)

if __name__ == "__main__":
    main(sys.argv[1])
