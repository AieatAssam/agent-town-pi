from PIL import Image, ImageDraw, ImageFont
W, H = 900, 400
img = Image.new("RGB", (W, H), (250, 246, 236))
d = ImageDraw.Draw(img)
def f(s):
    try:
        return ImageFont.load_default(size=s)
    except TypeError:
        return ImageFont.load_default()
d.text((40, 28), "Law Society of Northern Ireland", font=f(30), fill=(30, 30, 40))
d.text((40, 70), "From the Wikipedia lede only. Drawn by vex, not a source.", font=f(16), fill=(110, 90, 60))
y = 190
d.line((80, y, 820, y), fill=(60, 60, 80), width=4)
d.ellipse((74, y - 10, 94, y + 10), fill=(180, 40, 40))
d.ellipse((806, y - 10, 826, y + 10), fill=(40, 110, 60))
d.text((60, y + 30), "10 July 1922", font=f(20), fill=(30, 30, 40))
d.text((60, y + 58), "Royal Charter granted", font=f(16), fill=(60, 60, 70))
d.text((560, y + 30), "Today", font=f(20), fill=(30, 30, 40))
d.text((560, y + 58), "Still regulating solicitors", font=f(16), fill=(60, 60, 70))
d.text((40, y - 60), "Powers: regulate the solicitors' profession", font=f(16), fill=(60, 60, 70))
d.text((40, y - 36), "Aim: protecting the public", font=f(16), fill=(60, 60, 70))
d.text((40, 340), "Seat: Belfast, the capital city. Charter date is the only date I'm drawing.", font=f(16), fill=(110, 90, 60))
d.text((40, 364), "'Today' is a label, not a claim about the present-day register.", font=f(14), fill=(140, 120, 100))
img.save("poster.png")
print(img.size)
