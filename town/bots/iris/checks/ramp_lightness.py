"""Lightness along straight RGB ramps (stdlib only).

Prints CIE L* at evenly spaced points on a straight sRGB interpolation
between two colours, so a colour ramp can be judged by lightness steps.
Usage: python3 -I ramp_lightness.py
"""

def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lstar(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    if y > 0.008856:
        return 116 * y ** (1 / 3) - 16
    return 903.3 * y

def ramp(a, b, n):
    out = []
    for i in range(n):
        t = i / (n - 1)
        out.append(tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3)))
    return out

def show(name, a, b, n=5):
    pts = ramp(a, b, n)
    print(name)
    for p in pts:
        print("  rgb%-16s L*=%6.1f" % (str(p), lstar(p)))

if __name__ == "__main__":
    show("yellow -> blue", (255, 255, 0), (0, 0, 255))
    show("blue -> red", (0, 0, 255), (255, 0, 0))
