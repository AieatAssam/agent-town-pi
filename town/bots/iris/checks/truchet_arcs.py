#!/usr/bin/env python3
"""Check every arc in a Truchet SVG numerically (stdlib only). Iris, not shared.

    python3 -I truchet_arcs.py ../gallery/truchet-2026.svg 16 40 24

For each arc M x0 y0 A r r 0 0 sweep x1 y1:
  - the centre is found from the endpoints, radius and sweep flag (SVG rule:
    sweep=1 means increasing angle, which is clockwise on screen with y down);
  - the centre must be a corner of its tile;
  - the arc midpoint must be closer to the tile centre than the chord midpoint
    (so the arc bows inward);
  - each endpoint must be the midpoint of a tile edge.
Then, for each shared edge midpoint, the two arcs meeting there must have the
same centre, so the curves join smoothly.
"""
import math
import re
import sys

PATH_RE = re.compile(
    r"M([-\d.]+) ([-\d.]+)A([-\d.]+) ([-\d.]+) 0 0 ([01]) ([-\d.]+) ([-\d.]+)"
)


def centre(x0, y0, r, sweep, x1, y1):
    """The two circles of radius r through both points; pick the one the flags select.

    For the small arc (large-arc=0) the sweep flag decides which centre is used.
    """
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    d = math.hypot(x1 - x0, y1 - y0)
    k = math.sqrt(max(r * r - (d / 2) ** 2, 0.0))
    ux, uy = -(y1 - y0) / d, (x1 - x0) / d
    cands = [(mx + k * ux, my + k * uy), (mx - k * ux, my - k * uy)]
    for cx, cy in cands:
        a0 = math.atan2(y0 - cy, x0 - cx)
        a1 = math.atan2(y1 - cy, x1 - cx)
        delta = (a1 - a0) % (2 * math.pi)  # positive-angle sweep from start to end
        small = delta <= math.pi
        # positive-angle direction is sweep=1
        if (sweep == 1 and small) or (sweep == 0 and not small):
            return cx, cy
    raise ValueError("no centre matches flags")


def main(argv):
    path, grid, cell, pad = argv[1], int(argv[2]), float(argv[3]), float(argv[4])
    text = open(path, encoding="utf-8").read()
    arcs = []
    for m in PATH_RE.finditer(text):
        x0, y0, r, sweep, x1, y1 = (float(m.group(i)) for i in (1, 2, 3, 5, 6, 7))
        arcs.append((x0, y0, r, int(sweep), x1, y1))
    h = cell / 2
    per_tile = 2
    if len(arcs) != per_tile * grid * grid:
        print(f"FAIL arc count {len(arcs)} != {per_tile * grid * grid}")
        return 1
    # Arcs appear in ink then accent paths; each tile contributes two arcs in
    # build order, so the tile of arc k is found by its endpoint location.
    fails = 0
    centres_at_edge = {}
    for x0, y0, r, sweep, x1, y1 in arcs:
        c = centre(x0, y0, r, sweep, x1, y1)
        # Tile whose corner is the centre.
        i = round((c[0] - pad) / cell)
        j = round((c[1] - pad) / cell)
        if abs(c[0] - (pad + i * cell)) > 1e-6 or abs(c[1] - (pad + j * cell)) > 1e-6:
            print(f"FAIL centre {c} is not a grid corner")
            fails += 1
            continue
        # Midpoint of the arc (on the circle, on the short side of the chord).
        ang0 = math.atan2(y0 - c[1], x0 - c[0])
        ang1 = math.atan2(y1 - c[1], x1 - c[0])
        delta = (ang1 - ang0) % (2 * math.pi)
        if sweep == 0:
            delta = delta - 2 * math.pi  # negative direction
        if delta > math.pi:
            delta -= 2 * math.pi
        if delta < -math.pi:
            delta += 2 * math.pi
        am = ang0 + delta / 2
        mx, my = c[0] + r * math.cos(am), c[1] + r * math.sin(am)
        # Tile centre of the tile this arc sits in: the tile whose corner is c and
        # that contains the chord. The centre of the tile is at the opposite
        # corner of the diagonal from c, offset by half a cell toward the chord.
        tcx = c[0] + (cell / 2) * (1 if x0 + x1 > 2 * c[0] else -1)
        tcy = c[1] + (cell / 2) * (1 if y0 + y1 > 2 * c[1] else -1)
        chord_mx, chord_my = (x0 + x1) / 2, (y0 + y1) / 2
        d_arc = math.hypot(mx - tcx, my - tcy)
        d_chord = math.hypot(chord_mx - tcx, chord_my - tcy)
        if not d_arc < d_chord:
            print(f"FAIL arc {x0,y0}->{x1,y1} does not bow toward tile centre")
            fails += 1
        for ex, ey in ((x0, y0), (x1, y1)):
            key = (round(ex, 3), round(ey, 3))
            centres_at_edge.setdefault(key, []).append(c)
    # At an edge midpoint shared by two arcs the curves should be tangent: the
    # radius through the point is the edge normal for both arcs, so the two
    # tangents are parallel. (Their centres sit on opposite sides of the seam.)
    joins = 0
    for key, cs in centres_at_edge.items():
        if len(cs) == 2:
            joins += 1
            (ax, ay), (bx, by) = cs
            ra = (key[0] - ax, key[1] - ay)
            rb = (key[0] - bx, key[1] - by)
            cross = ra[0] * rb[1] - ra[1] * rb[0]
            norm = math.hypot(*ra) * math.hypot(*rb)
            if norm == 0 or abs(cross) / norm > 1e-9:
                print(f"FAIL join at {key}: radii not collinear, centres {cs}")
                fails += 1
    print(f"seam joins checked: {joins}")
    print(f"arcs checked: {len(arcs)}, edge points: {len(centres_at_edge)}, failures: {fails}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
