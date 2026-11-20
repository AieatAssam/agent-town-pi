"""Iris: deuteranopia sim of the hue path for the nine-stop yellow-to-blue ramp.

stdlib only. Run: python3 -I ramp_deut_huepath.py
Path: 120 straight-sRGB samples from yellow (255,255,0) to (25,25,230), the same chord
as checks/ramp_hue_render.py. Each sample is simulated with Machado 2009 deut, severity 1.0,
linear RGB. Reports the CIELAB hue angle and chroma of the normal and simulated colours,
and the largest step-to-step hue jump (ignoring samples with chroma < 4, where hue is undefined).
Hue is only a rough measure; the distance columns are the more useful check.
"""
import math

YELLOW = (255, 255, 0)
BLUE = (25, 25, 230)
N = 120

def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def enc(v):
    v = max(0.0, min(1.0, v))
    return 255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)

M = [[0.367322, 0.860646, -0.227968],
     [0.280085, 0.672501, 0.047413],
     [-0.011820, 0.042940, 0.968881]]

def sim(rgb):
    l = [lin(v) for v in rgb]
    return tuple(enc(sum(M[i][k] * l[k] for k in range(3))) for i in range(3))

def lab_ab(rgb):
    r, g, b = (lin(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 500 * (fx - fy), 200 * (fy - fz)

def hue_chroma(rgb):
    a, b = lab_ab(rgb)
    return math.degrees(math.atan2(b, a)) % 360, math.hypot(a, b)

def chord(t):
    return tuple(YELLOW[i] + (BLUE[i] - YELLOW[i]) * t for i in range(3))

def rnd(p):
    return tuple(round(v) for v in p)

def hue_jump(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)

samples = [chord(i / (N - 1)) for i in range(N)]
normal = [hue_chroma(rnd(s)) for s in samples]
deut = [hue_chroma(rnd(sim(s))) for s in samples]

# where the normal chord crosses grey (chroma < 4) and what the sim does there
grey_n = [i for i, (h, c) in enumerate(normal) if c < 4]
grey_d = [i for i, (h, c) in enumerate(deut) if c < 4]
print("normal chord grey samples (chroma<4): %s" % (grey_n or "none"))
print("sim chord grey samples (chroma<4):    %s" % (grey_d or "none"))
print()

def max_jump(hs):
    best = (0.0, None)
    for i in range(len(hs) - 1):
        (h1, c1), (h2, c2) = hs[i], hs[i + 1]
        if c1 < 4 or c2 < 4:
            continue
        j = hue_jump(h1, h2)
        if j > best[0]:
            best = (j, i)
    return best

jn, in_ = max_jump(normal)
jd, id_ = max_jump(deut)
print("largest hue jump between samples, both chroma >= 4 (deg):")
print("  normal: %.1f at sample %s" % (jn, in_))
print("  deut:   %.1f at sample %s" % (jd, id_))
print()

# sample-to-sample colour distance in the sim, in sRGB code values (screen distance only)
def dist(p, q):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(p, q)))

steps_n = [dist(rnd(samples[i]), rnd(samples[i + 1])) for i in range(N - 1)]
steps_d = [dist(rnd(sim(samples[i])), rnd(sim(samples[i + 1]))) for i in range(N - 1)]
print("sample-to-sample distance, sRGB code values (screen, not perceptual):")
print("  normal: min %.2f  max %.2f" % (min(steps_n), max(steps_n)))
print("  deut:   min %.2f  max %.2f" % (min(steps_d), max(steps_d)))
print()
print("stop-level check (sim of the nine stops, hue of each):")
STOPS = [(255,255,0),(230,230,25),(206,206,49),(182,182,73),(158,158,97),
         (134,134,121),(109,109,146),(81,81,174),(25,25,230)]
for i, s in enumerate(STOPS):
    ds = rnd(sim(s))
    h, c = hue_chroma(ds)
    print("  stop %d  sim %-16s hue %6.1f chroma %5.1f" % (i + 1, ds, h, c))
