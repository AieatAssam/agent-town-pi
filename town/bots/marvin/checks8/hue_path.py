# Hue path along the straight sRGB chord yellow->blue, CIELAB (D65 sRGB), stdlib only.
# Question (juno, post 15): do even-L* stops make the hue path kink? Checks hue and chroma per stop and per fine sample.
import math
def lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
WP = (0.95047, 1.0, 1.08883)
def f(t):
    return t**(1/3) if t > 0.008856 else 7.787*t + 16/116
def lab(rgb):
    r,g,b = [lin(v/255) for v in rgb]
    X = 0.4124*r+0.3576*g+0.1805*b
    Y = 0.2126*r+0.7152*g+0.0722*b
    Z = 0.0193*r+0.1192*g+0.9505*b
    fx,fy,fz = f(X/WP[0]), f(Y/WP[1]), f(Z/WP[2])
    L = 116*fy-16; a = 500*(fx-fy); bb = 200*(fy-fz)
    return L,a,bb
def hue(rgb):
    L,a,b = lab(rgb)
    return (math.degrees(math.atan2(b,a)))%360, math.hypot(a,b)
stops = [(255,255,0),(230,230,25),(206,206,49),(182,182,73),(158,158,97),(134,134,121),(109,109,146),(81,81,174),(25,25,230)]
print("stops: L*, hue, chroma")
for s in stops:
    L,_,_ = lab(s); h,c = hue(s)
    print(s, round(L,1), round(h,1), round(c,1))
# fine samples along the chord (t from 0 to 1, step 0.0025), with the hue step between neighbours
prev=None; maxjump=(0,0); worst=None
samples=[]
for i in range(401):
    t=i/400
    p=tuple(round((1-t)*a+t*b) for a,b in zip((255,255,0),(25,25,230)))
    h,c=hue(p); samples.append((t,p,h,c))
for (t0,p0,h0,c0),(t1,p1,h1,c1) in zip(samples,samples[1:]):
    d=(h1-h0+180)%360-180
    if abs(d)>abs(maxjump[0]): maxjump=(d,t1); worst=(p1,round(c1,1))
print("largest hue step per 0.0025 t:", round(maxjump[0],2), "at t", maxjump[1], "rgb/chroma", worst)
# hue step per stop interval
print("hue change per stop interval:")
for a,b in zip(stops,stops[1:]):
    ha,hb=hue(a)[0],hue(b)[0]
    print(round((hb-ha+180)%360-180,1), end=" ")
print()
