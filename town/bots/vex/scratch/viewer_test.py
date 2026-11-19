# Vex: 9-stop yellow->blue ramp, straight sRGB, three rows: colour, grey (Rec.709 Y), deuteranopia sim (Machado 2009, sev 1.0, linear RGB)
from PIL import Image, ImageDraw, ImageFont
def lin(c):
    c /= 255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def enc(v):
    v = max(0.0, min(1.0, v))
    return 255*(12.92*v if v <= 0.0031308 else 1.055*v**(1/2.4)-0.055)
M = [[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]]
def sim(rgb):
    l = [lin(v) for v in rgb]
    o = [sum(M[i][k]*l[k] for k in range(3)) for i in range(3)]
    return tuple(int(round(enc(x))) for x in o)
def grey(rgb):
    r,g,b = [lin(v) for v in rgb]
    Y = 0.2126*r+0.7152*g+0.0722*b
    v = int(round(enc(Y)))
    return (v,v,v)
stops = []
for t in range(9):
    f = t/8
    stops.append(tuple(round(a+(b-a)*f) for a,b in zip((255,255,0),(0,0,255))))
W, cell, pad = 9*100, 100, 20
rows = [("colour", stops), ("grey", [grey(s) for s in stops]), ("deuteranopia sim", [sim(s) for s in stops])]
H = 3*(cell+40)+pad*2
img = Image.new("RGB", (W+2*pad, H), (255,255,255))
d = ImageDraw.Draw(img)
font = ImageFont.load_default(size=22)
small = ImageFont.load_default(size=16)
for ri,(name,cols) in enumerate(rows):
    y0 = pad + ri*(cell+40)
    d.text((pad, y0), name.upper(), fill=(0,0,0), font=small)
    for i,c in enumerate(cols):
        x0 = pad+i*100
        d.rectangle([x0, y0+24, x0+99, y0+24+cell-1], fill=c)
        d.text((x0+40, y0+24+cell//2-11), str(i+1), fill=(0,0,0) if sum(c)>380 else (255,255,255), font=font)
img.save("/work/art/vex_viewer_test.png")
for name,cols in rows:
    print(name, cols)
