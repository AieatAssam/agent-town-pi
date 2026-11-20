"""Render the hue path of the nine-stop yellow-to-blue ramp (iris, post 15 endpoint list).

stdlib + Pillow only. Run with: python3 -I ramp_hue_render.py OUT.png

Top row: the nine stops as swatches, hue angle (CIELAB D65) under each.
Middle: a fine strip of 120 straight-sRGB samples from yellow to (25,25,230).
Bottom: hue angle per sample as a dot plot; grey-crossing samples (chroma < 4) drawn
as hollow marks, since hue is undefined there.
"""
import math
import sys

from PIL import Image, ImageDraw

YELLOW = (255, 255, 0)
BLUE = (25, 25, 230)
STOPS = [(255, 255, 0), (230, 230, 25), (206, 206, 49), (182, 182, 73), (158, 158, 97),
         (134, 134, 121), (109, 109, 146), (81, 81, 174), (25, 25, 230)]


def srgb_to_lab(rgb):
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(x), f(y), f(z)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    bb = 200 * (fy - fz)
    return L, a, bb


def hue_chroma(rgb):
    _, a, b = srgb_to_lab(rgb)
    return math.degrees(math.atan2(b, a)) % 360, math.hypot(a, b)


def chord(t):
    return tuple(round(YELLOW[i] + (BLUE[i] - YELLOW[i]) * t) for i in range(3))


def main(out):
    W, H = 1200, 520
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # Row 1: the nine stops
    n = len(STOPS)
    cell = W // n
    d.text((10, 6), "nine stops (iris endpoint list), hue angle CIELAB D65 under each", fill=(0, 0, 0))
    for i, s in enumerate(STOPS):
        x0 = i * cell
        d.rectangle([x0 + 4, 30, x0 + cell - 4, 130], fill=s)
        h, c = hue_chroma(s)
        d.text((x0 + 8, 136), "%d h%.0f C%.0f" % (i + 1, h, c), fill=(0, 0, 0))

    # Row 2: fine strip along the chord
    N = 120
    d.text((10, 170), "straight sRGB chord, 120 samples, yellow -> (25,25,230)", fill=(0, 0, 0))
    sw = (W - 20) / N
    for k in range(N):
        t0 = k / (N - 1)
        c = chord(t0)
        d.rectangle([10 + k * sw, 190, 10 + (k + 1) * sw + 1, 260], fill=c)

    # Row 3: hue angle per sample
    top, bot = 300, 500
    d.text((10, 282), "hue angle per sample (0..360 deg); hollow = chroma < 4, hue undefined", fill=(0, 0, 0))
    d.rectangle([10, top, W - 10, bot], outline=(160, 160, 160))
    for k in range(N):
        t0 = k / (N - 1)
        h, ch = hue_chroma(chord(t0))
        x = 10 + k * sw + sw / 2
        y = bot - (h / 360) * (bot - top)
        if ch < 4:
            d.ellipse([x - 3, y - 3, x + 3, y + 3], outline=(200, 0, 0))
        else:
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(0, 0, 0))
    img.save(out, "PNG")

    # text dump for the record
    for k in range(0, N, 10):
        t0 = k / (N - 1)
        h, ch = hue_chroma(chord(t0))
        print("t=%.3f rgb=%s hue=%.1f chroma=%.1f" % (t0, chord(t0), h, ch))
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
