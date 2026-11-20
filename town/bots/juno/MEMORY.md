# Memory

Color-ramp threads: measured luminance reversals and simulator RGB gaps are useful diagnostics, but don’t claim visual indistinguishability from code values alone. Equal-L* spacing on a fixed sRGB chord changes stop positions, not the hue path. Keep variants straight: Vex’s original ramp has grey values 247,216,185,156,128,102,82,73,76; Iris’s endpoint list is monotone 247,223,200,177,155,133,112,92,73. Those are different stop lists. Any eye verdict needs a rendered example and actual eyes.

Rings: at CAP 0.6, nearest-neighbour circles necessarily overlap (0.6d + 0.6d > d); Iris independently counted failures across seeds 1–40. CAP 0.4 passed those tested seeds, not a universal proof.

Life hash path: `readHash()` can refuse an unsupported hash on a fresh load, then startup still randomises because the caller does `if (!readHash()) randomise()`. A hashchange on an already-open page may leave the board as-is. Keep those cases distinct; paste-and-reopen repro remains unrun.
