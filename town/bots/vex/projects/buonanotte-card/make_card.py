from PIL import Image, ImageDraw, ImageFont
W, H = 900, 600
img = Image.new("RGB", (W, H), (18, 22, 40))
d = ImageDraw.Draw(img)
def font(size, bold=False):
    return ImageFont.load_default(size=size)
d.rectangle([0, 0, W, 96], fill=(230, 60, 40))
d.text((30, 22), "DIEGO BUONANOTTE", font=font(46, True), fill=(255, 255, 255))
d.text((30, 120), "Attacking midfielder / winger, Argentine", font=font(26), fill=(230, 230, 240))
d.text((30, 160), "Born 19 April 1988 (per FotMob / Sofascore)", font=font(22), fill=(170, 180, 210))
d.text((30, 215), "Clubs listed across sources:", font=font(24, True), fill=(255, 220, 90))
clubs = "O'Higgins, Union La Calera, Sporting Cristal, Universidad Catolica,\nAEK Athens, Granada, Quilmes, Pachuca, Malaga, River Plate,\nDeportes Temuco (presented early 2025)"
d.multiline_text((30, 255), clubs, font=font(22), fill=(235, 235, 245), spacing=10)
d.rectangle([30, 430, W - 30, 520], outline=(230, 60, 40), width=3)
d.text((50, 445), "Sources disagree", font=font(24, True), fill=(255, 255, 255))
d.text((50, 482), "on squad numbers and ages. Not checked live.", font=font(22), fill=(200, 200, 215))
d.text((30, 548), "VEX CARD, not an official record. Sources: ESPN, FotMob, Sofascore, La Tercera.", font=font(18), fill=(140, 150, 180))
img.save("/work/projects/buonanotte-card/card.png")
print("ok", img.size)
