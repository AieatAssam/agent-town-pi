#!/usr/bin/env python3
"""Rasterise the Truchet SVG (M and circular A commands only) to PNG, stdlib only.

Iris, private check. Usage:
    python3 -I svg_arcs_png.py IN.svg OUT.png

Approximations, stated so nobody mistakes this for a browser render:
- Strokes are drawn as distance-to-segment bands (round caps), not butt caps.
- Anti-aliasing is one-pixel linear coverage at the stroke edge.
- Only what this SVG uses is parsed: M, A with rx == ry, and the
  <path stroke="..."> groups with stroke-width taken from the parent <g>.
"""
import math
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

NS = "{http://www.w3.org/2000/svg}"


def parse_hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def arc_points(x0, y0, r, large, sweep, x1, y1, steps=24):
    """Polyline for a circular arc from (x0,y0) to (x1,y1), SVG endpoint rules."""
    dx, dy = (x1 - x0) / 2, (y1 - y0) / 2
    d2 = dx * dx + dy * dy
    if d2 == 0:
        return [(x0, y0)]
    k = math.sqrt(max(r * r - d2, 0.0)) / math.sqrt(d2)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    cands = [(mx - k * dy, my + k * dx), (mx + k * dy, my - k * dx)]
    best = None
    for cx, cy in cands:
        v1 = (x0 - cx, y0 - cy)
        v2 = (x1 - cx, y1 - cy)
        delta = math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])
        # SVG rule: the centre is the one whose arc direction matches the sweep flag.
        # large=0 means the smaller arc, |delta| < pi.
        if (delta > 0) == bool(sweep) and (large == 0) == (abs(delta) < math.pi):
            best = (cx, cy, v1, delta)
            break
    if best is None:
        cx, cy = cands[0]
        best = (cx, cy, (x0 - cx, y0 - cy), 0.0)
    cx, cy, v1, delta = best
    a0 = math.atan2(v1[1], v1[0])
    pts = []
    for i in range(steps + 1):
        a = a0 + delta * i / steps
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def path_segments(d):
    """Turn path data (M and A only, absolute) into line segments."""
    toks = re.findall(r"[MA]|-?\d*\.?\d+(?:e-?\d+)?", d)
    segs, i, cur, start = [], 0, None, None
    while i < len(toks):
        t = toks[i]
        if t == "M":
            cur = (float(toks[i + 1]), float(toks[i + 2]))
            i += 3
            continue
        if t == "A":
            rx, ry = float(toks[i + 1]), float(toks[i + 2])
            large, sweep = int(float(toks[i + 4])), int(float(toks[i + 5]))
            x1, y1 = float(toks[i + 6]), float(toks[i + 7])
            if abs(rx - ry) > 1e-9:
                raise ValueError("elliptical arc not supported")
            pts = arc_points(cur[0], cur[1], rx, large, sweep, x1, y1)
            segs.extend(zip(pts, pts[1:]))
            cur = (x1, y1)
            i += 8
            continue
        raise ValueError(f"unexpected token {t!r}")
    return segs


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(__doc__)
        return 2
    root = ET.parse(argv[1]).getroot()
    W = int(float(root.get("width")))
    H = int(float(root.get("height")))
    paper = (244, 239, 230)
    buf = [[paper] * W for _ in range(H)]
    for g in root.iter(NS + "g"):
        sw = float(g.get("stroke-width", "1"))
        for p in g.iter(NS + "path"):
            colour = parse_hex(p.get("stroke", "#000000"))
            r = sw / 2
            for (ax, ay), (bx, by) in path_segments(p.get("d")):
                x_lo, x_hi = int(math.floor(min(ax, bx) - r - 1)), int(math.ceil(max(ax, bx) + r + 1))
                y_lo, y_hi = int(math.floor(min(ay, by) - r - 1)), int(math.ceil(max(ay, by) + r + 1))
                vx, vy = bx - ax, by - ay
                L2 = vx * vx + vy * vy or 1e-12
                for py in range(max(y_lo, 0), min(y_hi, H)):
                    for px in range(max(x_lo, 0), min(x_hi, W)):
                        qx, qy = px + 0.5 - ax, py + 0.5 - ay
                        t = max(0.0, min(1.0, (qx * vx + qy * vy) / L2))
                        dx, dy = qx - t * vx, qy - t * vy
                        dist = math.sqrt(dx * dx + dy * dy)
                        cov = max(0.0, min(1.0, r + 0.5 - dist))
                        if cov > 0:
                            bg = buf[py][px]
                            buf[py][px] = tuple(round(bg[k] * (1 - cov) + colour[k] * cov) for k in range(3))

    raw = bytearray()
    for row in buf:
        raw.append(0)
        for c in row:
            raw.extend(c)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(argv[2], "wb") as f:
        f.write(png)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
