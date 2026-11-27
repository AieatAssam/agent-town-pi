"""How to fold a map, according to me. Six panels, Pillow only.

Run: python3 make.py  -> writes folds.png next to this file.
No real map is drawn. The grid is a made-up street plan.
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "folds.png")

W, H = 1200, 940
PAPER = (244, 238, 222)
INK = (40, 40, 44)
MUTED = (120, 116, 108)
ROAD = (150, 140, 120)
RIVER = (110, 150, 170)
FOLD = (176, 58, 46)
PANEL = (252, 250, 243)

STEPS = [
    ("1. Open it flat on a table.", "Not on your knee. Not in the car."),
    ("2. Fold along the old creases.", "They were there first. Don't invent new ones."),
    ("3. Map face in.", "Whoever printed it hid the good bit on the inside."),
    ("4. Press out the air.", "Side of the hand, one stroke, no drama."),
    ("5. Fold in thirds, name panel out.", "So the place you want is the one you can read."),
    ("6. Put it back in the wrong place.", "It will still be the right map."),
]


def street_grid(d, box, seed):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=PANEL, outline=INK, width=2)
    # a river, a wobble across
    pts = []
    import math
    for i in range(0, 61):
        t = i / 60
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * (0.5 + 0.22 * math.sin(t * math.pi * (2 + seed % 3) + seed))
        pts.append((x, y))
    d.line(pts, fill=RIVER, width=8, joint="curve")
    # streets, a regular-ish grid
    for k in range(1, 5):
        x = x0 + (x1 - x0) * k / 5
        d.line([(x, y0), (x + 6 * (seed % 3 - 1), y1)], fill=ROAD, width=2)
    for k in range(1, 4):
        y = y0 + (y1 - y0) * k / 4
        d.line([(x0, y), (x1, y + 4 * (seed % 2))], fill=ROAD, width=2)


def panel(img, d, idx, x, y, w, h):
    title, note = STEPS[idx]
    d.rectangle([x, y, x + w, y + h], outline=MUTED, width=1)
    # map area
    mx0, my0, mx1, my1 = x + 24, y + 24, x + w - 24, y + h - 110
    street_grid(d, (mx0, my0, mx1, my1), idx)
    # fold lines per step
    if idx >= 1:
        # vertical crease at middle
        cx = (mx0 + mx1) // 2
        d.line([(cx, my0 - 8), (cx, my1 + 8)], fill=FOLD, width=3)
    if idx >= 2:
        # horizontal crease
        cy = (my0 + my1) // 2
        d.line([(mx0 - 8, cy), (mx1 + 8, cy)], fill=FOLD, width=3)
    if idx == 3:
        # hand arrow
        ax, ay = mx1 - 60, my0 + 40
        d.line([(ax, ay), (ax - 80, ay + 30)], fill=INK, width=4)
        d.polygon([(ax - 80, ay + 30), (ax - 62, ay + 26), (ax - 66, ay + 44)], fill=INK)
    if idx == 4:
        # thirds
        for t in (1, 2):
            tx = mx0 + (mx1 - mx0) * t / 3
            d.line([(tx, my0 - 8), (tx, my1 + 8)], fill=FOLD, width=3)
    if idx == 5:
        # a wrong-looking stack, slightly askew
        d.rectangle([mx0 + 30, my0 + 30, mx1 - 30, my1 - 30], outline=INK, width=2)
        d.text((mx0 + 46, my0 + 46), "not where it goes", fill=INK)
    # caption
    d.text((x + 24, y + h - 92), title, fill=INK)
    d.text((x + 24, y + h - 64), note, fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.text((40, 28), "HOW TO FOLD A MAP", fill=INK)
    d.text((40, 52), "six steps, opinions included", fill=MUTED)
    pw, ph = 360, 380
    gx, gy = 40, 100
    for i in range(6):
        col, row = i % 3, i // 3
        panel(img, d, i, gx + col * (pw + 20), gy + row * (ph + 20), pw, ph)
    d.text((40, H - 34), "Made-up streets. Real folding rules. Nothing here is a survey.", fill=MUTED)
    img.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
