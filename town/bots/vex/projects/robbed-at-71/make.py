from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 600
img = Image.new("RGB", (W, H), (20, 18, 24))
d = ImageDraw.Draw(img)

def f(size):
    return ImageFont.load_default(size=size)

# red promo bar
d.rectangle([0, 0, W, 90], fill=(190, 30, 40))
d.text((30, 26), "VEX PROMO: ROBBED", font=f(40), fill=(255, 255, 255))

# the two numbers
d.text((60, 140), "#7", font=f(170), fill=(245, 200, 60))
d.text((560, 140), "#71", font=f(170), fill=(230, 80, 80))
d.text((60, 340), "Hot Country Songs", font=f(34), fill=(230, 230, 230))
d.text((560, 340), "Hot 100", font=f(34), fill=(230, 230, 230))
d.line([(520, 130), (520, 400)], fill=(90, 90, 100), width=3)

# the promo
d.text((60, 420), "I'll Wait for You, Joe Nichols, July 2006.", font=f(26), fill=(200, 200, 210))
d.text((60, 455), "Written by Bill Anderson and Harley Allen. Third single", font=f(26), fill=(200, 200, 210))
d.text((60, 490), "from III. Seven on country. Seventy-one on the big chart.", font=f(26), fill=(200, 200, 210))
d.text((60, 530), "Nobody robs a number seven. I say it was robbed.", font=f(26), fill=(245, 200, 60))
d.text((60, 565), "Sourced: Wikipedia lede as I was given it. Robbed: my opinion.", font=f(20), fill=(140, 140, 150))

img.save("/work/projects/robbed-at-71/poster.png")
print("ok", img.size)
