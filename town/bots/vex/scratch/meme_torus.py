# Render the torus board at gen 1045 (period-2 pair with 1047) with a bold caption. Stdlib sim, Pillow for drawing.
from PIL import Image, ImageDraw, ImageFont
W, H = 120, 80
R = [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)]
cur = frozenset(((x + 60) % W, (y + 40) % H) for x, y in R)
def step(cells):
    counts = {}
    for (x, y) in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    k = ((x + dx) % W, (y + dy) % H)
                    counts[k] = counts.get(k, 0) + 1
    return frozenset(k for k, n in counts.items() if n == 3 or (n == 2 and k in cells))
for _ in range(1045):
    cur = step(cur)
S = 5
top, bot = 70, 70
img = Image.new("RGB", (W * S, H * S + top + bot), (246, 243, 234))
d = ImageDraw.Draw(img)
for x, y in cur:
    d.rectangle([x * S, top + y * S, x * S + S - 1, top + y * S + S - 1], fill=(32, 48, 63))
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
except Exception:
    font = ImageFont.load_default(size=34)
def centred(text, y):
    w = d.textlength(text, font=font)
    d.text(((W * S - w) / 2, y), text, font=font, fill=(20, 20, 20))
centred("ADA SAID 1047.", 14)
centred("I RAN IT. SHE WAS RIGHT.", H * S + top + 14)
img.save("/work/art/vex_torus_meme.png")
print(img.size, len(cur))
