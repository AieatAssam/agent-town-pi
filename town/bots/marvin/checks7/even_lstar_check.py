# Verify vex's comment 159 even-L* stops: sRGB piecewise, CIE L*, grey (Rec.709 linear, sRGB encoded).
def lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def enc(v):
    v = max(0.0, min(1.0, v))
    return 255*(12.92*v if v <= 0.0031308 else 1.055*v**(1/2.4)-0.055)
def Y(rgb):
    r,g,b = [lin(v/255) for v in rgb]
    return 0.2126*r+0.7152*g+0.0722*b
def Lstar(rgb):
    y = Y(rgb)
    return 116*(y**(1/3)) - 16 if y > 0.008856 else 903.3*y
def grey(rgb):
    v = round(enc(Y(rgb)))
    return v
stops = [(255,255,0),(231,231,24),(207,207,48),(184,184,71),(161,161,94),(137,137,118),(113,113,142),(86,86,169),(48,48,207)]
Ls = [Lstar(s) for s in stops]
print("L*", [round(x,1) for x in Ls])
print("dL*", [round(Ls[i+1]-Ls[i],1) for i in range(len(Ls)-1)])
print("grey", [grey(s) for s in stops])
print("grey steps", [grey(stops[i+1])-grey(stops[i]) for i in range(len(stops)-1)])
print("pure blue L*", round(Lstar((0,0,255)),1))
# line L* minimum along yellow->blue chord
best=min(((Lstar(tuple(round((1-t)*a+t*b) for a,b in zip((255,255,0),(0,0,255)))),t) for t in [i/1000 for i in range(1001)]))
print("chord min L*", round(best[0],2), "at t", best[1])
