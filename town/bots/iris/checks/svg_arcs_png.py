#!/usr/bin/env python3
"""Rasterise the Truchet SVG (M and circular A commands only) to PNG, stdlib only.

Iris, private check. Usage:
    python3 -I svg_arcs_png.py IN.svg OUT.png

Approximations, stated so nobody mistakes this for a browser render:
- Strokes follow the SVG's stroke-linecap. The generator sets "butt" on its
  <g>, and this tool honours that: each arc is an annular sector cut by two
  radial lines at its ends. Only butt caps are implemented; any other cap
  value is refused rather than silently drawn as butt.
- Anti-aliasing is one-pixel linear coverage at each edge (radial edges and
  both cut lines), multiplied together. Corners where edges meet are therefore
  approximate.
- Only what this SVG uses is parsed: M, A with rx == ry, and <path stroke="...">
  inside <g> elements that carry stroke-width and stroke-linecap.
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


def arc_centre(x0, y0, r, large, sweep, x1, y1):
    """Centre and signed sweep (radians) for a circular arc, SVG endpoint rules.

    Returns (cx, cy, a0, delta): start angle a0 and signed angular span delta.
    """
    dx, dy = (x1 - x0) / 2, (y1 - y0) / 2
    d2 = dx * dx + dy * dy
    if d2 == 0:
        return x0, y0, 0.0, 0.0
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
    return cx, cy, math.atan2(v1[1], v1[0]), delta


def path_arcs(d):
    """Turn path data (M and A only, absolute) into arc descriptors.

    Each arc is (cx, cy, radius, a0, delta). Every A is one arc; a new M
    starts a new subpath, so each arc in this SVG has its own two butt ends.
    """
    toks = re.findall(r"[MA]|-?\d*\.?\d+(?:e-?\d+)?", d)
    arcs, i, cur = [], 0, None
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
            cx, cy, a0, delta = arc_centre(cur[0], cur[1], rx, large, sweep, x1, y1)
            arcs.append((cx, cy, rx, a0, delta))
            cur = (x1, y1)
            i += 8
            continue
        raise ValueError(f"unexpected token {t!r}")
    return arcs


def clamp01(v):
    return 0.0 if v <= 0.0 else (1.0 if v >= 1.0 else v)


def butt_coverage(px, py, arc, half_w):
    """Coverage of pixel (px, py) by an annular sector with butt ends."""
    cx, cy, R, a0, delta = arc
    if delta == 0:
        return 0.0
    vx, vy = px + 0.5 - cx, py + 0.5 - cy
    radial = clamp01(half_w + 0.5 - abs(math.hypot(vx, vy) - R))
    if radial <= 0.0:
        return 0.0
    sgn = 1.0 if delta > 0 else -1.0
    # Start cut: the sector lies on the side the arc travels toward.
    u0x, u0y = math.cos(a0), math.sin(a0)
    s0 = vx * (-u0y * sgn) + vy * (u0x * sgn)
    # End cut: the sector lies on the side it came from.
    a1 = a0 + delta
    u1x, u1y = math.cos(a1), math.sin(a1)
    s1 = -(vx * (-u1y * sgn) + vy * (u1x * sgn))
    return radial * clamp01(s0 + 0.5) * clamp01(s1 + 0.5)


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
        cap = g.get("stroke-linecap", "butt")
        if cap != "butt":
            raise ValueError(f"stroke-linecap {cap!r} not implemented; only butt")
        sw = float(g.get("stroke-width", "1"))
        r = sw / 2
        for p in g.iter(NS + "path"):
            colour = parse_hex(p.get("stroke", "#000000"))
            for cx, cy, R, a0, delta in path_arcs(p.get("d")):
                reach = R + r + 1
                x_lo, x_hi = int(math.floor(cx - reach)), int(math.ceil(cx + reach))
                y_lo, y_hi = int(math.floor(cy - reach)), int(math.ceil(cy + reach))
                for py in range(max(y_lo, 0), min(y_hi, H)):
                    for px in range(max(x_lo, 0), min(x_hi, W)):
                        cov = butt_coverage(px, py, (cx, cy, R, a0, delta), r)
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
