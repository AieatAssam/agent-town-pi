# Vex: deuteranopia sim (Machado 2009 sev 1.0, linear RGB) for the even-L* stops
import math
def lin(c):
    c /= 255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def enc(v):
    v = max(0.0, min(1.0, v))
    return 255*(12.92*v if v <= 0.0031308 else 1.055*v**(1/2.4)-0.055)
M = [[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]]
def sim(rgb):
    l=[lin(v) for v in rgb]
    o=[sum(M[i][k]*l[k] for k in range(3)) for i in range(3)]
    return tuple(int(round(enc(x))) for x in o)
stops=[(255,255,0),(231,231,24),(207,207,48),(184,184,71),(161,161,94),(137,137,118),(113,113,142),(86,86,169),(48,48,207)]
s=[sim(c) for c in stops]
for i,c in enumerate(s):
    d = "" if i==0 else " dE-ish(sum|diff|)=%d" % sum(abs(a-b) for a,b in zip(c,s[i-1]))
    print(i+1, c, d)
