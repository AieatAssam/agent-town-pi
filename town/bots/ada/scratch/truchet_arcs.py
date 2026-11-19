# Check which way each SVG arc in iris's Truchet tile bows (small-arc flag, given sweep).
# SVG: sweep=1 means positive-angle direction (clockwise on screen, y down).
import math

def centres(p, q, r):
    (x0, y0), (x1, y1) = p, q
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    d = math.hypot(x1 - x0, y1 - y0)
    k = math.sqrt(max(r * r - (d / 2) ** 2, 0))
    ux, uy = -(y1 - y0) / d, (x1 - x0) / d
    return (mx + k * ux, my + k * uy), (mx - k * ux, my - k * uy)

def arc_mid(p, q, r, sweep):
    # pick the centre whose small arc goes p->q in the requested sweep direction
    for c in centres(p, q, r):
        a0 = math.atan2(p[1] - c[1], p[0] - c[0])
        a1 = math.atan2(q[1] - c[1], q[0] - c[0])
        delta = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi  # in (-pi, pi]
        ok = (delta > 0) if sweep == 1 else (delta < 0)
        if ok:
            am = a0 + delta / 2
            return (c[0] + r * math.cos(am), c[1] + r * math.sin(am)), c
    raise ValueError("no centre")

def check(o, s=40, h=20):
    if o == 0:
        arcs = [((h, 0), (0, h), 1), ((s, h), (h, s), 0)]
    else:
        arcs = [((h, 0), (s, h), 0), ((0, h), (h, s), 1)]
    tc = (s / 2, s / 2)
    for p, q, sw in arcs:
        m, c = arc_mid(p, q, h, sw)
        chord = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        toward = math.dist(m, tc) < math.dist(chord, tc)
        print(f"o={o} {p}->{q} sweep={sw} centre=({c[0]:.1f},{c[1]:.1f}) "
              f"mid=({m[0]:.1f},{m[1]:.1f}) bows_to_tile_centre={toward}")

check(0); check(1)
