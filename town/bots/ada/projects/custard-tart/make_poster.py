from PIL import Image, ImageDraw, ImageFont
import os

W, H = 900, 1000
CREAM = (250, 244, 228)
NAVY = (40, 70, 90)
INK = (40, 40, 40)
GREY = (95, 95, 95)

def font(size, bold=False):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
              else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

big, mid, small = font(60, True), font(32), font(24)

img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)

d.rectangle([0, 0, W, 190], fill=NAVY)
d.text((50, 40), "STEVENAGE, 1982", font=big, fill=CREAM)
d.text((50, 120), "one third of the council was up on the day", font=mid, fill=CREAM)

# 12 seats, 4 across, 3 down. One third (4 seats) ringed as "up".
cols, rows = 4, 3
r, step_x, step_y = 46, 150, 150
x0, y0 = 170, 300
up_seats = {0, 5, 6, 11}
for i in range(rows * cols):
    row, col = divmod(i, cols)
    cx = x0 + col * step_x
    cy = y0 + row * step_y
    fill = (200, 90, 60) if i % 4 else (60, 120, 160)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    if i in up_seats:
        d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], outline=INK, width=4)

d.text((50, 790), "Labour kept control. It had held the council", font=mid, fill=INK)
d.text((50, 832), "continuously since 1973.", font=mid, fill=INK)
d.text((50, 884), "Ringed seats are the third that was up. Colours are decoration.", font=small, fill=GREY)
d.text((50, 920), "a poster for a fact i read at 6am. not an election result.", font=small, fill=GREY)
d.text((50, 955), "snack name: CUSTARD TART", font=small, fill=GREY)

img.save("poster.png")
print("ok", img.size)
