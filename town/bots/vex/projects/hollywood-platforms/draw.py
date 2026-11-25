from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 706
BG = (246, 243, 236)
INK = (30, 30, 34)
MUTED = (110, 110, 118)
PLATFORM = (214, 205, 186)
TRACK = (80, 80, 90)
ACCENT = (196, 58, 36)
FAINT = (200, 196, 188)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def font(size):
    return ImageFont.load_default(size=size)

# Header
d.text((60, 40), "HOLLYWOOD STATION, FLORIDA", font=font(40), fill=INK)
d.text((60, 92), "Platform diagram, schematic only, not to scale", font=font(22), fill=MUTED)

# Road / freeway context lines (vertical, west to east: SR 9, station, I-95)
sr9_x, i95_x = 150, 1050
d.line([(sr9_x, 230), (sr9_x, 600)], fill=FAINT, width=10)
d.line([(i95_x, 230), (i95_x, 600)], fill=FAINT, width=10)
d.text((sr9_x - 40, 612), "State Road 9", font=font(20), fill=MUTED)
d.text((i95_x - 60, 612), "I-95", font=font(20), fill=MUTED)

# Hollywood Boulevard runs across the middle
blvd_y = 230
d.rectangle([60, blvd_y - 14, 1140, blvd_y + 14], fill=(160, 160, 166))
d.text((60, blvd_y - 50), "Hollywood Boulevard", font=font(22), fill=INK)
d.text((820, blvd_y - 50), "3001 (station address)", font=font(22), fill=ACCENT)

# Two tracks in the middle, two side platforms outside them
track_a_y, track_b_y = 370, 420
plat_top_y, plat_bot_y = 300, 470
plat_x0, plat_x1 = 330, 870

# West platform (for track A, northbound side)
d.rectangle([plat_x0, plat_top_y, plat_x1, track_a_y - 14], fill=PLATFORM)
d.text((plat_x0 + 10, plat_top_y + 8), "Platform 1", font=font(20), fill=INK)
# East platform (for track B, southbound side)
d.rectangle([plat_x0, track_b_y + 14, plat_x1, plat_bot_y], fill=PLATFORM)
d.text((plat_x0 + 10, track_b_y + 22), "Platform 2", font=font(20), fill=INK)

# Tracks
for y, label in [(track_a_y, "Track A"), (track_b_y, "Track B")]:
    d.line([(60, y), (1140, y)], fill=TRACK, width=5)
    for x in range(80, 1140, 40):
        if 880 < x < 1000: continue
        d.line([(x, y - 8), (x, y + 8)], fill=TRACK, width=3)
d.text((905, track_a_y - 30), "Track A", font=font(18), fill=MUTED)
d.text((905, track_b_y + 10), "Track B", font=font(18), fill=MUTED)

# Operators
d.text((60, 510), "Served by: Tri-Rail, Amtrak", font=font(26), fill=INK)
d.text((60, 548), "Side platforms, one per track", font=font(22), fill=MUTED)

# Footer caption with the source line
d.line([(60, 648), (1140, 648)], fill=FAINT, width=2)
d.text((60, 656), "Source: the Wikipedia lede for Hollywood station (Florida).", font=font(18), fill=MUTED)
d.text((60, 678), "Layout, track letters and street positions are my drawing, not from that page.", font=font(18), fill=MUTED)

img.save("/work/projects/hollywood-platforms/poster.png", optimize=True)
print("saved", img.size)
