#!/usr/bin/env python3
"""Poster for The King's Hall, Belfast. Only facts from the Wikipedia lead:
six event venues; RUAS moved in 1896 and out in 2012 (no claim of continuous sole ownership);
being re-developed as of 2021. Nothing else is claimed."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 800
BG = (238, 232, 218)
INK = (34, 34, 38)
MUTED = (110, 104, 96)
ACCENT = (150, 52, 40)
SOFT = (196, 186, 166)

def font(size, bold=False):
    return ImageFont.load_default(size=size)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.text((60, 50), "THE KING'S HALL, BELFAST", font=font(44), fill=INK)
d.text((60, 108), "A multi-purpose venue. Six event rooms. RUAS in the building 1896-2012.",
       font=font(22), fill=MUTED)

# Timeline 1880..2030
x0, x1, y = 90, 1110, 330
y0yr, y1yr = 1880, 2030
def xo(year):
    return x0 + (year - y0yr) / (y1yr - y0yr) * (x1 - x0)

d.line((x0, y, x1, y), fill=INK, width=3)
for yr in range(1900, 2031, 20):
    d.line((xo(yr), y - 8, xo(yr), y + 8), fill=INK, width=2)
    d.text((xo(yr) - 18, y + 16), str(yr), font=font(18), fill=MUTED)

# RUAS tenure band
d.rectangle((xo(1896), y - 22, xo(2012), y - 6), fill=SOFT)
d.text((xo(1896) + 12, y - 92), "RUAS in the building, 1896-2012",
       font=font(20), fill=INK)
d.text((xo(1896) + 12, y - 62), "(dates from the lead; the 116 is my subtraction)",
       font=font(16), fill=MUTED)

# markers
for yr, label in [(1896, "1896  RUAS moves in"), (2012, "2012  RUAS moves out")]:
    d.ellipse((xo(yr) - 7, y - 7, xo(yr) + 7, y + 7), fill=ACCENT)
d.text((xo(2012) - 270, y + 50), "2012  RUAS moves out", font=font(20), fill=ACCENT)
d.text((xo(1896) - 10, y + 50), "1896  RUAS moves in", font=font(20), fill=ACCENT)

# redevelopment, open-ended: a dashed stretch after 2012
xs = xo(2012)
for xx in range(int(xs) + 4, int(xo(2030)), 26):
    d.line((xx, y - 2, min(xx + 12, x1), y - 2), fill=ACCENT, width=3)
d.text((x1 - 520, y + 84),
       "2021: being re-developed (last word I have, no newer source)",
       font=font(18), fill=ACCENT)

# six venue boxes
d.text((60, 560), "SIX EVENT VENUES", font=font(22), fill=INK)
bx, by, bw, bh, gap = 60, 600, 165, 110, 18
for i in range(6):
    xx = bx + i * (bw + gap)
    d.rectangle((xx, by, xx + bw, by + bh), outline=INK, width=2)
    d.text((xx + 14, by + 16), f"Venue {i + 1}", font=font(20), fill=INK)
    d.text((xx + 14, by + 52), "name not given", font=font(16), fill=MUTED)
    d.text((xx + 14, by + 74), "in the blurb", font=font(16), fill=MUTED)

d.text((60, 748),
       "Source: the Wikipedia lead on The King's Hall. The blurb does not name the six venues, so neither does this poster.",
       font=font(16), fill=MUTED)

img.save("poster.png", optimize=True)
print("wrote poster.png", img.size)
