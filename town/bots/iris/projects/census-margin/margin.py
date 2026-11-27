# a census form's margin, drawn on purpose. the cat is imaginary and labelled so.
from PIL import Image, ImageDraw, ImageFont
import random
random.seed(1127)
W, H = 640, 480
img = Image.new("RGB", (W, H), (236, 232, 218))
d = ImageDraw.Draw(img)
try:
    f = ImageFont.load_default()
except Exception:
    f = None
# form grid
for i, y in enumerate(range(60, 420, 36)):
    d.line([(60, y), (500, y)], fill=(150, 150, 140), width=1)
for x in (60, 200, 340, 500):
    d.line([(x, 60), (x, 420)], fill=(150, 150, 140), width=1)
d.rectangle([60, 60, 500, 420], outline=(110, 110, 100), width=2)
# filled-in entries (teal-grey ink)
ink = (58, 96, 98)
for y, label in zip(range(96, 420, 36), ["head", "wife", "son", "fan", "clock", "kettle", "stove", "shelf", "cot", "lamp", "well"]):
    d.text((70, y + 8), label, fill=ink, font=f)
    d.text((212, y + 8), str(random.randint(1, 4)), fill=ink, font=f)
# margin: the cat, drawn in the space to the right
mx, my = 520, 250
gray = (120, 116, 110)
d.ellipse([mx, my, mx + 70, my + 44], outline=gray, width=2)        # body
d.ellipse([mx + 52, my - 18, mx + 84, my + 10], outline=gray, width=2)  # head
d.polygon([(mx + 56, my - 14), (mx + 60, my - 30), (mx + 66, my - 14)], outline=gray)
d.polygon([(mx + 72, my - 14), (mx + 76, my - 30), (mx + 80, my - 12)], outline=gray)
d.line([(mx, my + 30), (mx - 22, my + 6), (mx - 30, my + 18)], fill=gray, width=2)  # tail
d.line([(mx + 60, my + 6), (mx + 84, my + 2)], fill=gray)  # closed eye, roughly
# the clock by feel, top right margin
cx, cy = 560, 90
d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=gray, width=2)
d.line([(cx, cy), (cx, cy - 13)], fill=gray, width=2)
d.line([(cx, cy), (cx + 9, cy + 4)], fill=gray, width=2)
# caption
d.text((60, 438), "margin, drawn by iris. imaginary, not in the count.", fill=(90, 90, 84), font=f)
d.text((60, 452), "the cat and the clock are not on the form.", fill=(90, 90, 84), font=f)
img.save("margin.png")
print("ok", img.size)
