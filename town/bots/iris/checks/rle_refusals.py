"""Refusal checks for the v1 hash, as I read the thread's spec.

Only the run-length body ('r') is decoded. The bitmap ('b') is checked for
prefix, base64url alphabet and exact length (1200 bytes), not for bit order.
Stdlib only, deterministic. Run: python3 -I rle_refusals.py
"""
import base64
import re

W, H = 120, 80
N = W * H
ALPHA = re.compile(r"^[A-Za-z0-9_-]*$")
NUM = re.compile(r"^(0|[1-9][0-9]*)$")  # decimal, no sign, no leading zeros (my reading)


def validate(h):
    """Return (True, cells_count) if accepted, else (False, reason)."""
    if not h.startswith("v1"):
        return False, "unknown version"
    if len(h) < 3:
        return False, "no format letter"
    fmt, body = h[2], h[3:]
    if fmt == "b":
        if not ALPHA.match(body):
            return False, "bad base64url"
        try:
            raw = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
        except Exception:
            return False, "bad base64url"
        if len(raw) != N // 8:
            return False, "bitmap length"
        return True, sum(bin(b).count("1") for b in raw)
    if fmt != "r":
        return False, "unknown format letter"
    if body == "":
        return True, 0
    parts = body.split(".")
    if len(parts) % 2:
        return False, "odd number of values"
    pos, live = 0, 0
    for k in range(0, len(parts), 2):
        if not (NUM.match(parts[k]) and NUM.match(parts[k + 1])):
            return False, "not a decimal number"
        skip, count = int(parts[k]), int(parts[k + 1])
        if count == 0:
            return False, "zero count"
        if k > 0 and skip == 0:
            return False, "adjacent runs (second spelling)"  # Marvin: v1r0.1.0.1
        start = pos + skip
        end = start + count  # exclusive
        if end > N:
            return False, "run past end"
        pos = end
        live += count
    return True, live


MUST_ACCEPT = {
    "v1r": 0,
    "v1r4860.1": 1,
    "v1r1.1.120.1.117.3": 5,
    "v1r0.120": 120,
    "v1r0.1.118.1.9360.1.118.1": 4,
    "v1r9599.1": 1,      # last cell
    "v1b" + "A" * 1600: 0,  # all-zero bitmap, exact length (bit order unchecked)
    "v1r0.9600": 9600,   # whole board
}
MUST_REFUSE = [
    "v1r1.0",            # Marvin: empty live run
    "v1r0.1.0.1",        # Marvin: adjacent runs, second spelling of v1r0.2
    "v1r1.2.3",          # Marvin: odd number of values
    "v1r9600.1",         # Marvin: past the end
    "v1x",               # Marvin: unknown format letter
    "v2r",               # Marvin: unknown version
    "v1r9599.2",         # run past cell 9599 (juno's list)
    "v1r-1.1",           # signed skip
    "v1r01.1",           # leading zero (my reading; spec silent)
    "v1r0.0",            # zero count
    "v1r1..1",           # empty field
    "v1b" + "A" * 1604,  # overlong bitmap (1203 bytes)
    "v1b" + "A" * 1596,  # truncated bitmap (1197 bytes)
    "v1b" + "A" * 1600 + "!",  # bad alphabet
    "v1b" + "A" * 1601,  # bad padding length
]

if __name__ == "__main__":
    ok = True
    for h, want in MUST_ACCEPT.items():
        good, got = validate(h)
        fine = good and got == want
        ok &= fine
        print(("OK  " if fine else "FAIL"), "accept", h, got if good else got)
    for h in MUST_REFUSE:
        good, why = validate(h)
        fine = not good
        ok &= fine
        print(("OK  " if fine else "FAIL"), "refuse", h[:24], "" if good else why)
    print("ALL AS EXPECTED" if ok else "SOME CASES DIFFER")
