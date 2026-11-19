import sys
sys.path.insert(0, "/work/scratch/rings")
import rings
counts = {}
for seed in range(1, 41):
    counts[seed] = len(rings.points(seed))
short = {s: n for s, n in counts.items() if n < 90}
print("seeds 1-40: min", min(counts.values()), "max", max(counts.values()))
print("seeds with fewer than 90 centres:", short or "none")
print("seed 2026 centres:", len(rings.points(2026)))
