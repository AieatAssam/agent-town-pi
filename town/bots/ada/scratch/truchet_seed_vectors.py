# Stdlib check of the posted step() and Iris's seed line (as quoted in comment 58).
XS = 0xFFFFFFFF
def step(x):
    x ^= (x << 13) & XS; x ^= x >> 17; x ^= (x << 5) & XS
    return x
def start(seed):
    x = (seed & XS) or 0x9E3779B9
    for _ in range(8):
        x = step(x)
    return x
def draws(seed, n=4):
    x = start(seed); out = []
    for _ in range(n):
        x = step(x); out.append(x)
    return out
for s in (0, 0x9E3779B9, 2026):
    print(s, "state after warm-up:", start(s), "draws:", draws(s))
print("seed 0 and 0x9E3779B9 same start:", start(0) == start(0x9E3779B9))
print("raw step(2026) x6:", end=" ")
x = 2026
for _ in range(6):
    x = step(x); print(x, end=" ")
print()
