"""Check Marvin's v1 run-length vectors for the 120x80 Life hash.

Spec (from the thread): index = y*120 + x, row-major from 0.
Body 'r' is skip.count pairs; skip is measured from the end of the previous run.
Stdlib only, deterministic.
"""
W, H = 120, 80
N = W * H


def encode_runs(cells):
    """cells: iterable of (x, y). Returns the 'v1r' hash body."""
    idx = sorted(y * W + x for x, y in cells)
    parts = []
    pos = 0  # first cell not yet covered by a run
    i = 0
    while i < len(idx):
        start = idx[i]
        end = start
        while i + 1 < len(idx) and idx[i + 1] == end + 1:
            i += 1
            end = idx[i]
        count = end - start + 1
        parts.append(f"{start - pos}.{count}")
        pos = end + 1
        i += 1
    return "v1r" + ".".join(parts)


CASES = {
    "empty": [],
    "one cell (60,40)": [(60, 40)],
    "glider": [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],
    "full top row": [(x, 0) for x in range(W)],
    "four corners": [(0, 0), (119, 0), (0, 79), (119, 79)],
}

EXPECTED = {
    "empty": "v1r",
    "one cell (60,40)": "v1r4860.1",
    "glider": "v1r1.1.120.1.117.3",
    "full top row": "v1r0.120",
    "four corners": "v1r0.1.118.1.9360.1.118.1",
}

if __name__ == "__main__":
    ok = True
    for name, cells in CASES.items():
        got = encode_runs(cells)
        status = "OK  " if got == EXPECTED[name] else "DIFF"
        ok &= got == EXPECTED[name]
        print(f"{status} {name:18} {got}")
    print("ALL MATCH" if ok else "MISMATCH")
