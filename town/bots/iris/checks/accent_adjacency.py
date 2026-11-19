#!/usr/bin/env python3
"""Check: are the accent tiles in truchet.py clumped?

Compares two ways of drawing the accent flag:
  interleaved: the current generator (accent drawn from the same stream as orientation)
  separate:    a second XorShift32 stream seeded from the same seed (Rex's suggestion)

For each scheme and each seed, count 4-neighbour pairs of accent tiles, and compare
with what independent flags at p = 1/ACCENT_ODDS would give on average.
Stdlib only. Run: python3 -I accent_adjacency.py [NSEEDS]
"""
import sys
sys.path.insert(0, "/work/gallery")
import truchet as t  # noqa: E402


def flags_interleaved(seed):
    rng = t.XorShift32(seed)
    grid = [[False] * t.GRID for _ in range(t.GRID)]
    for j in range(t.GRID):
        for i in range(t.GRID):
            rng.below(2)                       # orientation
            grid[j][i] = rng.below(t.ACCENT_ODDS) == 0
    return grid


def flags_separate(seed):
    rng = t.XorShift32(seed)
    acc = t.XorShift32(seed ^ 0x5BD1E995)      # its own stream; same seed space
    grid = [[False] * t.GRID for _ in range(t.GRID)]
    for j in range(t.GRID):
        for i in range(t.GRID):
            rng.below(2)
            grid[j][i] = acc.below(t.ACCENT_ODDS) == 0
    return grid


def adjacent_pairs(grid):
    n = 0
    for j in range(t.GRID):
        for i in range(t.GRID):
            if not grid[j][i]:
                continue
            if i + 1 < t.GRID and grid[j][i + 1]:
                n += 1
            if j + 1 < t.GRID and grid[j + 1][i]:
                n += 1
    return n


def main(argv):
    nseeds = int(argv[1]) if len(argv) > 1 else 200
    edges = 2 * t.GRID * (t.GRID - 1)
    p = 1.0 / t.ACCENT_ODDS
    expected = edges * p * p
    for name, fn in (("interleaved", flags_interleaved), ("separate", flags_separate)):
        counts = [adjacent_pairs(fn(s)) for s in range(1, nseeds + 1)]
        mean = sum(counts) / len(counts)
        var = sum((c - mean) ** 2 for c in counts) / len(counts)
        print(f"{name:12s} seeds={nseeds} mean_adjacent_accent_pairs={mean:.3f} "
              f"sd={var ** 0.5:.3f} max={max(counts)} zero_pairs_seeds={sum(c == 0 for c in counts)}")
    print(f"independent expectation: {expected:.3f} pairs per grid (edges={edges}, p={p:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
