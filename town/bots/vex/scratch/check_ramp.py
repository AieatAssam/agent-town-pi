# Vex: check Iris's 9-stop ramps and the full adjacent steps (stdlib, straight sRGB, Rec.709 Y, L*)
def lin(c):
    c /= 255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def Lstar(rgb):
    r,g,b = [lin(v) for v in rgb]
    Y = 0.2126*r + 0.7152*g + 0.0722*b
    return 116*(Y**(1/3)) - 16 if Y > 216/24389 else (24389/27)*Y/100*100/100 * 0 + 903.3*Y
def ramp(a,b,n):
    return [tuple(a[k] + (b[k]-a[k])*t/(n-1) for k in range(3)) for t in range(n)]
Y_=(255,255,0); B=(0,0,255); R=(255,0,0)
for name,(a,b) in {"yellow->blue":(Y_,B),"blue->red":(B,R)}.items():
    for n in (5,9):
        L=[Lstar(p) for p in ramp(a,b,n)]
        print(name,n,[round(x,1) for x in L],"steps",[round(L[i+1]-L[i],1) for i in range(n-1)])
