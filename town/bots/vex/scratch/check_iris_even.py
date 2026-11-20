def lin(c):
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def enc(v):
    v = max(0.0, min(1.0, v))
    return 255*(12.92*v if v <= 0.0031308 else 1.055*v**(1/2.4)-0.055)
def Y(rgb):
    r,g,b=[lin(v/255) for v in rgb]
    return 0.2126*r+0.7152*g+0.0722*b
def Lstar(rgb):
    y=Y(rgb)
    return 116*(y**(1/3))-16 if y>0.008856 else 903.3*y
def grey(rgb):
    v=round(enc(Y(rgb))); return v
stops=[(255,255,0),(230,230,25),(206,206,49),(182,182,73),(158,158,97),(134,134,121),(109,109,146),(81,81,174),(25,25,230)]
# chord minimum of L* along yellow->blue straight sRGB line
ys=(255,255,0); yb=(25,25,230)
best=None
for i in range(0,100001):
    t=i/100000
    p=tuple(ys[k]+(yb[k]-ys[k])*t for k in range(3))
    L=Lstar(p)
    if best is None or L<best[0]: best=(L,t,p)
print("chord min", best)
L=[Lstar(s) for s in stops]
print("L*", [round(x,1) for x in L])
print("steps", [round(L[i+1]-L[i],1) for i in range(8)])
print("grey", [grey(s) for s in stops])
print("Lstar of pure blue", Lstar((0,0,255)))
print("Lstar of (48,48,207)", Lstar((48,48,207)))
