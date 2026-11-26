"""Pigeon ledger: a window box, two hours of sun, and a tally nobody asked for.

The counts below are invented for the picture. They are not a record.
Run: python3 make.py  -> writes ledger.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ledger.png")

W, H = 1200, 860
PAPER = (244, 238, 222)
INK = (40, 40, 44)
MUTED = (120, 116, 108)
RED = (176, 58, 46)
GREEN = (74, 120, 62)
TOMATO = (200, 66, 52)
PIGEON = (120, 124, 132)

# (day, tomatoes ripe that morning, tomatoes gone by evening, note)
ROWS = [
    ("Mon", 4, 0, ""),
    ("Tue", 3, 2, "one left on the rail"),
    ("Wed", 5, 4, "the gap is the shape of a pigeon"),
    ("Thu", 2, 2, "they came early"),
    ("Fri", 6, 5, "I counted twice"),
    ("Sat", 4, 4, "nothing on the rail. the pigeons wait."),
    ("Sun", 3, 3, "again"),
]

BOX_SUN_HOURS = 2


def font(size, bold=False):
    names = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]
        if bold
        else ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
    )
    for n in names:
        if os.path.exists(n):
            return ImageFont.truetype(n, size)
    # no TTF on this Pi: Pillow's built-in font scales with size if FreeType is present
    return ImageFont.load_default(size=size)


def draw_tomato(d, x, y, r):
    d.ellipse([x - r, y - r, x + r, y + r], fill=TOMATO)
    d.line([x, y - r, x, y - r - 8], fill=GREEN, width=4)
    d.ellipse([x - 10, y - r - 10, x + 2, y - r - 4], fill=GREEN)


def draw_pigeon_mark(d, x, y):
    # a plain grey blob with a beak: the whole bird, as far as this drawing goes
    d.ellipse([x - 22, y - 14, x + 22, y + 14], fill=PIGEON)
    d.ellipse([x + 14, y - 22, x + 34, y - 4], fill=PIGEON)
    d.polygon([(x + 32, y - 14), (x + 44, y - 12), (x + 32, y - 8)], fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    d.text((60, 40), "WINDOW BOX LEDGER", font=font(46, True), fill=INK)
    d.text((60, 102), f"sun: {BOX_SUN_HOURS} hours a day, west window, one box", font=font(22), fill=MUTED)
    d.text((60, 132), "made-up tally for the picture. not a measurement.", font=font(20), fill=MUTED)

    top = 200
    row_h = 66
    left = 60
    d.line([left, top - 14, W - 60, top - 14], fill=INK, width=2)
    d.text((left, top - 8), "day", font=font(20, True), fill=INK)
    d.text((left + 120, top - 8), "ripe", font=font(20, True), fill=INK)
    d.text((left + 420, top - 8), "eaten by pigeons", font=font(20, True), fill=INK)
    d.text((left + 760, top - 8), "note", font=font(20, True), fill=INK)

    for i, (day, ripe, eaten, note) in enumerate(ROWS):
        y = top + 46 + i * row_h
        d.text((left, y - 14), day, font=font(26, True), fill=INK)
        for k in range(ripe):
            cx = left + 140 + k * 34
            draw_tomato(d, cx, y, 11)
        # eaten: pigeon marks drawn along the same rail, from the right of the tomato run
        for k in range(eaten):
            draw_pigeon_mark(d, left + 420 + k * 58, y)
        d.text((left + 760, y - 14), note, font=font(20), fill=INK)
        d.line([left, y + 34, W - 60, y + 34], fill=(200, 194, 180), width=1)

    total_ripe = sum(r[1] for r in ROWS)
    total_eaten = sum(r[2] for r in ROWS)
    yb = top + 46 + len(ROWS) * row_h + 18
    d.line([left, yb - 10, W - 60, yb - 10], fill=INK, width=2)
    d.text((left, yb), f"ripe: {total_ripe}    eaten: {total_eaten}    left for me: {total_ripe - total_eaten}",
           font=font(28, True), fill=RED)
    d.text((left, yb + 44), "The pigeons got the tomatoes. Again.", font=font(24), fill=INK)

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
