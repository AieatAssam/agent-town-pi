"""Even-L* stops along the yellow->blue straight sRGB line, plus vex's grey test.

stdlib only. Run: python3 -I ramp_even_lstar.py
Exit 1 if an even-L* target cannot be reached on the line.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ramp_lightness import ramp, lstar

A, B = (255, 255, 0), (0, 0, 255)
N = 9
FINE = 20000


def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def enc(v):
    v = max(0.0, min(1.0, v))
    return 255 * (12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)


def grey_value(rgb):
    # Rec.709 luminance in linear light, sRGB encoded (vex's grey(), as I read it)
    y = 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])
    return round(enc(y))


def at(t):
    return tuple(round(a + (b - a) * t) for a, b in zip(A, B))


def lstar_at(t):
    return lstar(at(t))


# 1. the straight 9-stop ramp, with grey values and L*
pts = ramp(A, B, N)
print("straight sRGB, 9 stops")
print("  rgb  : " + " ".join("%s" % (p,) for p in pts))
print("  grey : " + " ".join("%3d" % grey_value(p) for p in pts))
print("  L*   : " + " ".join("%5.1f" % lstar(p) for p in pts))

# 2. where does L* bottom out on the line?
samples = [(i / FINE, lstar_at(i / FINE)) for i in range(FINE + 1)]
t_min, l_min = min(samples, key=lambda s: s[1])
print("  L* minimum on the line: %.1f at t=%.3f rgb=%s (pure blue L* %.1f)"
      % (l_min, t_min, at(t_min), lstar(B)))

# 3. even-L* targets, from pure yellow down to the line's own minimum
l_top = lstar(A)
targets = [l_top + (l_min - l_top) * i / (N - 1) for i in range(N)]
stops, bad = [], []
for tg in targets:
    # first t on the falling branch (0 .. t_min) where L* reaches the target
    hit = None
    for i in range(FINE + 1):
        t = i / FINE
        if t > t_min:
            break
        if lstar_at(t) <= tg:
            hit = t
            break
    if hit is None:
        bad.append(tg)
        hit = t_min
    stops.append(at(hit))

print("even-L* stops (targets %.1f .. %.1f, step %.2f), on the falling branch only"
      % (targets[0], targets[-1], (targets[-1] - targets[0]) / (N - 1)))
print("  rgb  : " + " ".join("%s" % (p,) for p in stops))
ls = [lstar(p) for p in stops]
print("  L*   : " + " ".join("%5.1f" % v for v in ls))
steps = [ls[i + 1] - ls[i] for i in range(N - 1)]
print("  dL*  : " + " ".join("%+5.1f" % v for v in steps))
print("  grey : " + " ".join("%3d" % grey_value(p) for p in stops))
print("  grey steps: " + " ".join("%+4d" % (grey_value(stops[i + 1]) - grey_value(stops[i]))
                                  for i in range(N - 1)))
if bad:
    print("UNREACHABLE targets: %s" % ["%.1f" % b for b in bad])
    sys.exit(1)
print("all %d targets reached" % N)
