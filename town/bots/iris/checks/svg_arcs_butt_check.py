#!/usr/bin/env python3
"""Check svg_arcs_png.butt_coverage against analytic areas. Run: python3 -I svg_arcs_butt_check.py"""
import math, sys
sys.path.insert(0, '/work/checks')
import svg_arcs_png as s

def area(arc, half_w, pad=30):
    cx, cy, R, _, _ = arc
    tot = 0.0
    for py in range(int(cy) - pad, int(cy) + pad):
        for px in range(int(cx) - pad, int(cx) + pad):
            tot += s.butt_coverage(px, py, arc, half_w)
    return tot

ok = True
# Quarter arc centred at (64,24), radius 20, from (44,24) to (64,44), as in the SVG path "M44 24A20 20 0 0 0 64 44".
cx, cy, a0, delta = s.arc_centre(44, 24, 20, 0, 0, 64, 44)
arc = (cx, cy, 20, a0, delta)
print('centre', round(cx, 6), round(cy, 6), 'delta(deg)', round(math.degrees(delta), 3))
for hw in (3.5, 1.0):
    got = area(arc, hw)
    exp_butt = (math.pi / 2) * 2 * 20 * hw
    exp_round = exp_butt + math.pi * hw * hw
    print(f'half_w {hw}: sum {got:.2f}  butt-analytic {exp_butt:.2f}  round-analytic {exp_round:.2f}')
    ok &= abs(got - exp_butt) < 0.02 * exp_butt
# Points just beyond the ends must be empty; points inside the sector must be covered.
far_start = (cx + 20 * math.cos(a0) - 3, cy + 20 * math.sin(a0) - 3)  # sits past the start cut
print('tile-centre side covered:', round(s.butt_coverage(44, 44, arc, 3.5), 3))
mid = a0 + delta / 2
inside = (cx + 20 * math.cos(mid), cy + 20 * math.sin(mid))
print('mid-arc pixel coverage:', round(s.butt_coverage(int(inside[0]), int(inside[1]), arc, 3.5), 3))
print('ALL AS EXPECTED' if ok else 'MISMATCH')
