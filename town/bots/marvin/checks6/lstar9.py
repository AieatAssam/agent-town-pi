def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lstar(rgb):
    r, g, b = (lin(c) for c in rgb)
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 116 * (y ** (1 / 3)) - 16 if y > 0.008856 else 903.3 * y / 100 * 100 / 100 * (y) ** 0 * 1.0 if False else (116 * (y ** (1/3)) - 16)
def ramp(a, b, n=9):
    out = []
    for i in range(n):
        t = i / (n - 1)
        out.append(tuple(round(a[k] + (b[k] - a[k]) * t) for k in range(3)))
    return out
Y = (255, 255, 0); B = (0, 0, 255); R = (255, 0, 0)
for name, a, b in [("yellow->blue", Y, B), ("blue->red", B, R)]:
    pts = ramp(a, b)
    print(name, [(p, round(lstar(p), 1)) for p in pts])
    ls = [lstar(p) for p in pts]
    print("  adjacent dL*", [round(ls[i+1]-ls[i], 1) for i in range(len(ls)-1)])
