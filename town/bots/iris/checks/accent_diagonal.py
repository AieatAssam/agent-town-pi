#!/usr/bin/env python3
"""Check: do accent tiles in truchet.py line up on diagonals more than chance?

Counts pairs of accent tiles that are diagonal neighbours (offset (1,1) or (1,-1)),
for the current interleaved accent stream, and compares the mean over many seeds
with independent flags at p = 1/ACCENT_ODDS. This measures a count of diagonal
neighbour pairs only. It does not judge how the picture looks.

Stdlib only. Run: python3 -I accent_diagonal.py [NSEEDS]
"""
import sys
sys.path.insert(0, "/work/checks")
import accent_adjacency as aa  # noqa: E402
import truchet as t  # noqa: E402


def diagonal_pairs(grid):
    n = 0
    for j in range(t.GRID):
        for i in range(t.GRID):
            if not grid[j][i]:
                continue
            if j + 1 < t.GRID and i + 1 < t.GRID and grid[j + 1][i + 1]:
                n += 1
            if j + 1 < t.GRID and i - 1 >= 0 and grid[j + 1][i - 1]:
                n += 1
    return n


def main(argv):
    nseeds = int(argv[1]) if len(argv) > 1 else 2000
    diag_edges = 2 * (t.GRID - 1) * (t.GRID - 1)
    p = 1.0 / t.ACCENT_ODDS
    expected = diag_edges * p * p
    counts = [diagonal_pairs(aa.flags_interleaved(s)) for s in range(1, nseeds + 1)]
    mean = sum(counts) / len(counts)
    var = sum((c - mean) ** 2 for c in counts) / len(counts)
    print(f"interleaved  seeds={nseeds} mean_diagonal_accent_pairs={mean:.3f} "
          f"sd={var ** 0.5:.3f} max={max(counts)}")
    print(f"independent expectation: {expected:.3f} pairs per grid "
          f"(diagonal edges={diag_edges}, p={p:.4f})")
    # The shipped seed, for the record.
    shipped = aa.flags_interleaved(2026)
    print(f"seed 2026: diagonal_accent_pairs={diagonal_pairs(shipped)} "
          f"accent_tiles={sum(sum(r) for r in shipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
