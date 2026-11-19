"""Adjacent L* steps along straight sRGB ramps (stdlib only).

For each ramp, prints the L* at each stop and the change to the next stop.
Shows where a ramp has a flat stretch or a sharp jump, which five points can hide.
Usage: python3 -I ramp_adjacent.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ramp_lightness import ramp, lstar

RAMPS = [("yellow -> blue", (255, 255, 0), (0, 0, 255)),
         ("blue -> red", (0, 0, 255), (255, 0, 0))]

def report(name, a, b, n):
    pts = ramp(a, b, n)
    ls = [lstar(p) for p in pts]
    steps = [ls[i + 1] - ls[i] for i in range(n - 1)]
    print("%s, %d stops" % (name, n))
    print("  L*    : " + " ".join("%6.1f" % v for v in ls))
    print("  dL*   : " + " ".join("%+6.1f" % v for v in steps))
    print("  max |dL*| = %.1f, min |dL*| = %.1f" % (max(abs(s) for s in steps), min(abs(s) for s in steps)))

if __name__ == "__main__":
    for name, a, b in RAMPS:
        report(name, a, b, 5)
        report(name, a, b, 9)
