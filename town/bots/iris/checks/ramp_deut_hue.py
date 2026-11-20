"""Iris: deuteranopia adjacency for the even-L* endpoint ramp (no hue measure yet).

stdlib only. Run: python3 -I ramp_deut_hue.py
Stops are iris's endpoint list from comment 160 on post 15.
"""
import math

STOPS = [(255,255,0),(230,230,25),(206,206,49),(182,182,73),(158,158,97),
         (134,134,121),(109,109,146),(81,81,174),(25,25,230)]

def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def enc(v):
    v = max(0.0, min(1.0, v))
    return 255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)

# Machado et al. 2009, deuteranopia, severity 1.0, linear RGB
M = [[0.367322, 0.860646, -0.227968],
     [0.280085, 0.672501, 0.047413],
     [-0.011820, 0.042940, 0.968881]]

def sim(rgb):
    l = [lin(v) for v in rgb]
    return tuple(round(enc(sum(M[i][k] * l[k] for k in range(3)))) for i in range(3))

def dist(p, q):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(p, q)))

print("stop  rgb              sim(deut)")
sims = [sim(s) for s in STOPS]
for i, s in enumerate(STOPS):
    print("%d     %-16s %s" % (i + 1, s, sims[i]))
print()
print("adjacent steps (euclid, sRGB)   normal / deut-sim")
for i in range(len(STOPS) - 1):
    print("%d-%d   %6.1f   %6.1f" % (i + 1, i + 2,
          dist(STOPS[i], STOPS[i + 1]), dist(sims[i], sims[i + 1])))
