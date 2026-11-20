# Marvin's independent check of the deut-simulated hue path on the straight sRGB chord, yellow -> (25,25,230).
# stdlib only. Machado 2009 deut sev 1.0 applied in linear RGB. CIELAB D65 hue on the simulated colours.
import math
def lin(c): return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def enc(v):
    v=max(0.0,min(1.0,v)); return 255*(12.92*v if v<=0.0031308 else 1.055*v**(1/2.4)-0.055)
M=[[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]]
def sim(rgb):
    l=[lin(v/255) for v in rgb]
    return tuple(round(enc(sum(M[i][k]*l[k] for k in range(3)))) for i in range(3))
WP=(0.95047,1.0,1.08883)
def f(t): return t**(1/3) if t>0.008856 else 7.787*t+16/116
def hue_chroma(rgb):
    r,g,b=[lin(v/255) for v in rgb]
    X=0.4124*r+0.3576*g+0.1805*b; Y=0.2126*r+0.7152*g+0.0722*b; Z=0.0193*r+0.1192*g+0.9505*b
    fx,fy,fz=f(X/WP[0]),f(Y/WP[1]),f(Z/WP[2])
    a=500*(fx-fy); bb=200*(fy-fz)
    return math.degrees(math.atan2(bb,a))%360, math.hypot(a,bb)
A,B=(255,255,0),(25,25,230)
N=120
pts=[tuple(round((1-i/N)*x+(i/N)*y) for x,y in zip(A,B)) for i in range(N+1)]
for label,conv in (("normal",lambda p:p),("deut sim",sim)):
    cols=[conv(p) for p in pts]
    hc=[hue_chroma(c) for c in cols]
    # largest hue jump between neighbours where both have chroma >= 4
    best=(0,None)
    for i in range(N):
        (h0,c0),(h1,c1)=hc[i],hc[i+1]
        if c0>=4 and c1>=4:
            d=(h1-h0+180)%360-180
            if abs(d)>abs(best[0]): best=(d,i+1)
    # neighbour distance in sRGB code values
    dist=[math.dist(cols[i],cols[i+1]) for i in range(N)]
    # where chroma first drops below 4 and the grey crossing
    low=[i for i,(h,c) in enumerate(hc) if c<4]
    print(label, "min chroma sample idx:", min(range(len(hc)),key=lambda i:hc[i][1]), "min chroma", round(min(c for h,c in hc),1))
    print("  largest hue jump (chroma>=4 both ends):", round(best[0],1), "at sample", best[1])
    print("  neighbour distance min/max:", round(min(dist),1), round(max(dist),1), "max at", dist.index(max(dist)))
    print("  hue at stop-like samples 0,30,60,90,120:", [round(hc[i][0]) for i in (0,30,60,90,120)])
