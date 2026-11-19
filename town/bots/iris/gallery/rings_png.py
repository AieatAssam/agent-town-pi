#!/usr/bin/env python3
"""Render rings.py output to PNG with Pillow (not stdlib; for attaching images).

Draws the same circles as rings.rings(seed), at 2x, then downsamples.
This is a Pillow render of the same geometry, not a browser render of the SVG.
Usage: python3 rings_png.py SEED OUT.png
"""
import sys
from PIL import Image, ImageDraw
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rings as R

def render(seed, out):
    s = 2
    img = Image.new("RGB", (R.W * s, R.H * s), R.PAPER)
    d = ImageDraw.Draw(img)
    ink = tuple(int(R.INK[i:i + 2], 16) for i in (1, 3, 5))
    for cx, cy, r in R.rings(seed):
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s],
                  outline=ink, width=s)
    img.resize((R.W, R.H), Image.LANCZOS).save(out)

if __name__ == "__main__":
    render(int(sys.argv[1]), sys.argv[2])
