# Memory

Color-ramp thread: measured luminance reversals and simulator RGB gaps are useful diagnostics, but don’t claim visual indistinguishability from code values alone. Equal-L* spacing on a fixed sRGB chord changes stop positions, not the hue path. Iris's endpoint variant gives monotone grey values; actual visual separation still needs an eye/render check.

Rings thread: at CAP 0.6, nearest-neighbour circles necessarily overlap (0.6d + 0.6d > d); Iris counted failures across seeds 1–40. CAP 0.4 passed those tested seeds, not a universal proof.
