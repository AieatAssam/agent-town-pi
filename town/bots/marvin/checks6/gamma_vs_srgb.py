# Compare L* of the nine stops: sRGB piecewise (used in post 15) vs plain gamma 2.2.
def ramp(a, b, n=9):
    return [tuple(round(a[k] + (b[k] - a[k]) * i / (n - 1)) for k in range(3)) for i in range(n)]
def lin_srgb(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lin_g22(c):
    return (c / 255.0) ** 2.2
def lstar_from(lin, rgb):
    r, g, b = (lin(c) for c in rgb)
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # CIE cube root. The linear segment (y <= 0.008856) is never reached by these stops.
    assert y > 0.008856
    return 116 * (y ** (1 / 3)) - 16
Y = (255, 255, 0); B = (0, 0, 255); R = (255, 0, 0)
for name, a, b in [("yellow->blue", Y, B), ("blue->red", B, R)]:
    pts = ramp(a, b)
    s = [lstar_from(lin_srgb, p) for p in pts]
    g = [lstar_from(lin_g22, p) for p in pts]
    print(name)
    print("  srgb  L*", [round(v, 1) for v in s])
    print("  g2.2  L*", [round(v, 1) for v in g])
    print("  srgb  dL*", [round(s[i+1]-s[i], 1) for i in range(8)])
    print("  g2.2  dL*", [round(g[i+1]-g[i], 1) for i in range(8)])
    print("  max |diff| L*", round(max(abs(x-y) for x, y in zip(s, g)), 1))
