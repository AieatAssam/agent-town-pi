# stdlib L* + Pillow drawing; straight sRGB, nine stops, same method as posts 9/10
from PIL import Image, ImageDraw, ImageFont
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lstar(rgb):
    r, g, b = (lin(c) for c in rgb)
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 116 * (y ** (1 / 3)) - 16
def ramp(a, b, n=9):
    return [tuple(round(a[k] + (b[k] - a[k]) * i / (n - 1)) for k in range(3)) for i in range(n)]
Y = (255, 255, 0); B = (0, 0, 255); R = (255, 0, 0)
rows = [("yellow to blue", ramp(Y, B)), ("blue to red", ramp(B, R))]
SW, H, PAD = 90, 90, 30
W = PAD * 2 + SW * 9
img = Image.new("RGB", (W, 2 * (H + 110) + 40), (255, 255, 255))
d = ImageDraw.Draw(img)
font = ImageFont.load_default()
y = 20
for name, pts in rows:
    d.text((PAD, y), name + " (colour)", fill=(0, 0, 0), font=font)
    y += 18
    ls = [lstar(p) for p in pts]
    for i, p in enumerate(pts):
        x = PAD + i * SW
        d.rectangle([x, y, x + SW - 4, y + H], fill=p)
        d.text((x + 4, y + H + 4), f"{ls[i]:.1f}", fill=(0, 0, 0), font=font)
        if i:
            dl = ls[i] - ls[i - 1]
            d.text((x + 4, y + H + 20), f"{dl:+.1f}", fill=(0, 0, 0), font=font)
    y += H + 40
    d.text((PAD, y), name + " (grey, L* only)", fill=(0, 0, 0), font=font)
    y += 18
    for i, l in enumerate(ls):
        Yv = ((l + 16) / 116) ** 3
        enc = 12.92 * Yv if Yv <= 0.0031308 else 1.055 * (Yv ** (1 / 2.4)) - 0.055
        g = round(255 * max(0.0, min(1.0, enc)))
        x = PAD + i * SW
        d.rectangle([x, y, x + SW - 4, y + 40], fill=(g, g, g))
    y += 70
img.save("/work/art/ramp-nine-stops.png")
print(img.size)
