# Vex: even-L* stops on the straight sRGB yellow->blue line (stdlib, Rec.709 Y, L*)
def lin(c):
    c /= 255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def enc(v):
    v = max(0.0, min(1.0, v))
    return 255*(12.92*v if v <= 0.0031308 else 1.055*v**(1/2.4)-0.055)
def Y(rgb):
    r,g,b = [lin(v) for v in rgb]
    return 0.2126*r+0.7152*g+0.0722*b
def Lstar(rgb):
    y = Y(rgb)
    return 116*(y**(1/3)) - 16 if y > 216/24389 else 903.3*y
A=(255,255,0); B=(0,0,255)
def at(t):
    return tuple(a+(b-a)*t for a,b in zip(A,B))
# dense scan of L* along the path
N=100000
ts=[i/N for i in range(N+1)]
Ls=[Lstar(at(t)) for t in ts]
imin=min(range(N+1), key=lambda i: Ls[i])
print("L* yellow %.2f blue %.2f" % (Ls[0], Ls[-1]))
print("path minimum L* %.2f at t=%.4f" % (Ls[imin], ts[imin]))
def first_t(target):
    for i in range(N):
        if (Ls[i]-target)*(Ls[i+1]-target) <= 0:
            lo,hi=ts[i],ts[i+1]
            for _ in range(60):
                mid=(lo+hi)/2
                if (Lstar(at(lo))-target)*(Lstar(at(mid))-target) <= 0: hi=mid
                else: lo=mid
            return (lo+hi)/2
    return None
n=9
top,bot=Ls[0],Ls[-1]
targets=[top+(bot-top)*k/(n-1) for k in range(n)]
prev=None
print("stop  target_L*  t        rgb(rounded)            grey(Y-encoded)  step")
rows=[]
for k,tg in enumerate(targets):
    t=first_t(tg)
    rgb=tuple(round(v) for v in at(t))
    L=Lstar(rgb)
    g=round(enc(Y(rgb)))
    st = "" if prev is None else "%+.1f" % (L-prev)
    print("%d  %7.2f   %.4f  %-22s  %4d  %s" % (k+1,tg,t,str(rgb),g,st))
    prev=L
    rows.append(rgb)
print("rgb stops", rows)
