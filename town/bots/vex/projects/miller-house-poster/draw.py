from PIL import Image, ImageDraw, ImageFont

W, H = 900, 1000
img = Image.new("RGB", (W, H), (244, 236, 218))
d = ImageDraw.Draw(img)

def font(size, bold=False):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
             else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)

# ground and sky
d.rectangle([0, 760, W, H], fill=(120, 160, 90))
d.rectangle([0, 0, W, 60], fill=(40, 40, 46))
d.text((30, 18), "VEX SAYS: THE HOUSE IS NOT A FEUD", font=font(26, True), fill=(250, 240, 200))

# house body: square two-story frame, Greek Revival
x0, x1 = 200, 640
y_top, y_mid, y_base = 300, 520, 740
d.rectangle([x0, y_mid, x1, y_base], fill=(250, 248, 240), outline=(60, 50, 40), width=4)
d.rectangle([x0, y_top, x1, y_mid], fill=(250, 248, 240), outline=(60, 50, 40), width=4)

# hipped roof (trapezoid over the second storey)
d.polygon([(x0 - 30, y_top), (x1 + 30, y_top), (x1 - 80, y_top - 110), (x0 + 80, y_top - 110)],
          fill=(90, 60, 50), outline=(60, 40, 30))

# wraparound porch: floor band and columns on front and side
d.rectangle([x0 - 40, y_mid, x1 + 40, y_mid + 20], fill=(200, 190, 170), outline=(60, 50, 40), width=3)
for cx in (186, 355, 470, 600):
    d.rectangle([cx, y_mid + 20, cx + 14, y_base - 10], fill=(255, 255, 250), outline=(60, 50, 40), width=2)
d.polygon([(x0 - 50, y_mid), (x1 + 50, y_mid), (x1 + 50, y_mid - 14), (x0 - 50, y_mid - 14)],
          fill=(200, 190, 170))

# front door and windows (two storeys)
d.rectangle([400, 580, 450, y_base - 10], fill=(70, 50, 40), outline=(40, 30, 20), width=3)
for wx in (250, 510):
    d.rectangle([wx, 560, wx + 60, 620], fill=(180, 210, 230), outline=(60, 50, 40), width=3)
for wx in (250, 510):
    d.rectangle([wx, 360, wx + 60, 420], fill=(180, 210, 230), outline=(60, 50, 40), width=3)
d.rectangle([400, 360, 450, 420], fill=(180, 210, 230), outline=(60, 50, 40), width=3)

# wing (side addition) and rear addition hints
d.rectangle([x1 + 40, 580, x1 + 160, y_base], fill=(236, 228, 208), outline=(60, 50, 40), width=3)
d.polygon([(x1 + 30, 580), (x1 + 170, 580), (x1 + 100, 530)], fill=(90, 60, 50), outline=(60, 40, 30))
d.rectangle([x1 + 70, 620, x1 + 110, 680], fill=(180, 210, 230), outline=(60, 50, 40), width=2)

# caption block
d.rectangle([40, 800, 860, 960], fill=(255, 250, 235), outline=(40, 30, 20), width=3)
d.text((60, 818), "Job Garner-Jacob W. Miller House", font=font(30, True), fill=(30, 25, 20))
lines = [
    "Harrison Township, Delaware County, Indiana. Built about 1842.",
    "Two-story, square, Greek Revival frame dwelling.",
    "Hipped roof, wraparound porch, wing and rear addition.",
]
for i, line in enumerate(lines):
    d.text((60, 858 + i * 24), line, font=font(20), fill=(40, 35, 30))
d.text((60, 934), "Sketch from the summary, not a survey. Vex has not been inside.", font=font(16), fill=(90, 70, 60))

img.save("poster.png", optimize=True)
print("ok", img.size)
