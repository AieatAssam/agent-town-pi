#!/usr/bin/env python3
"""Encode/decode a Game of Life board for a URL hash.

Hash layout:  v1<format><body>
  v1   format version. Grid is fixed at 120x80. Unknown versions are refused.
  b    bitmap: row-major bits, packed MSB first, base64url without padding
  r    run-length: decimal "skip.count" pairs joined by '.', row-major order.
       Each pair means: skip <skip> dead cells, then set <count> live cells.
       Pairs must stay inside the board and must not overlap.

The encoder picks whichever body is shorter.

Usage:
  boardhash.py selftest
  boardhash.py sizes            # size table for a few board shapes
"""
import base64
import binascii
import random
import re
import sys

W, H = 120, 80
VERSION = "v1"
N = W * H


def _bits(cells):
    """cells: set of (x, y). Returns list of 0/1 in row-major order."""
    out = [0] * N
    for x, y in cells:
        if 0 <= x < W and 0 <= y < H:
            out[y * W + x] = 1
    return out


def _encode_bitmap(bits):
    packed = bytearray((len(bits) + 7) // 8)
    for i, b in enumerate(bits):
        if b:
            packed[i // 8] |= 0x80 >> (i % 8)
    return "b" + base64.urlsafe_b64encode(bytes(packed)).decode().rstrip("=")


def _encode_rle(bits):
    pairs = []
    i = 0
    while i < N:
        skip = 0
        while i < N and bits[i] == 0:
            skip += 1
            i += 1
        if i == N:
            break
        count = 0
        while i < N and bits[i] == 1:
            count += 1
            i += 1
        pairs.append((skip, count))
    return "r" + ".".join("%d.%d" % p for p in pairs)


def encode(cells):
    bits = _bits(cells)
    a = _encode_bitmap(bits)
    b = _encode_rle(bits)
    body = a if len(a) <= len(b) else b
    return VERSION + body


_B64URL = re.compile(r"[A-Za-z0-9_-]*\Z")
_DIGITS = re.compile(r"(0|[1-9][0-9]*)\Z")


def _decode_bitmap(body):
    # Check the alphabet ourselves. b64decode(altchars=...) would also accept
    # standard '+' and '/', which silently decode to a different board.
    if not _B64URL.match(body):
        raise ValueError("bitmap is not valid base64url")
    try:
        packed = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
    except binascii.Error as e:
        raise ValueError("bitmap is not valid base64url: %s" % e)
    if len(packed) != N // 8:
        raise ValueError("bitmap has the wrong length")
    return {(i % W, i // W) for i in range(N)
            if (packed[i // 8] >> (7 - i % 8)) & 1}


def _decode_rle(body):
    cells = set()
    if not body:
        return cells
    pos = 0
    parts = body.split(".")
    if len(parts) % 2:
        raise ValueError("run-length needs skip/count pairs")
    for k in range(0, len(parts), 2):
        # Canonical decimal only: ASCII digits, no leading zeros, so each
        # board has exactly one hash. isdigit() would accept e.g. '²'.
        if not (_DIGITS.match(parts[k]) and _DIGITS.match(parts[k + 1])):
            raise ValueError("run-length values must be canonical decimal")
        skip, count = int(parts[k]), int(parts[k + 1])
        if count < 1:
            raise ValueError("live run must be at least one cell")
        # After the first run the encoder always leaves at least one dead
        # cell, so skip 0 there would be a second spelling of one board.
        if k > 0 and skip < 1:
            raise ValueError("adjacent runs must be merged; skip must be >= 1")
        start = pos + skip
        end = start + count
        if end > N:
            raise ValueError("run goes past the end of the board")
        # pos only moves forward, so runs cannot overlap.
        for i in range(start, end):
            cells.add((i % W, i // W))
        pos = end
    return cells


def decode(s):
    if not s:
        raise ValueError("empty hash")
    if not s.startswith(VERSION):
        raise ValueError("unknown or missing version tag")
    kind, body = s[len(VERSION)], s[len(VERSION) + 1:]
    if kind == "b":
        return _decode_bitmap(body)
    if kind == "r":
        return _decode_rle(body)
    raise ValueError("unknown format letter %r" % kind)


def _random_board(density, rng):
    return {(x, y) for x in range(W) for y in range(H) if rng.random() < density}


def selftest():
    rng = random.Random(1)
    cases = [set(), {(0, 0)}, {(W - 1, H - 1)}, {(x, 0) for x in range(W)}]
    cases.append({(x, y) for x in range(W) for y in range(H)})
    cases.append(_random_board(0.5, rng))
    cases.append(_random_board(0.02, rng))
    for density in (0.0, 0.05, 0.3, 1.0):
        cases.append(_random_board(density, rng))
    for cells in cases:
        s = encode(cells)
        assert decode(s) == cells, "roundtrip failed"
        assert len(s) <= len(VERSION) + 1 + (N + 7) // 8 * 4 // 3 + 2, "too long"
    # Malformed input must be refused, not silently accepted.
    bad_inputs = [
        "", "b", "x123", "v2b", "v2r", "v1x", "v1b!!!",
        "v1b" + "A" * 5,                 # wrong bitmap length
        "v1r1.2.3",                      # odd number of values
        "v1r1.0",                        # zero-length live run
        "v1r0.1.0.1",                    # adjacent runs: spell as v1r0.2
        "v1r1.1.0.1",                    # adjacent runs after a gap
        "v1r-1.1", "v1r1.a",             # not decimal
        "v1r%d.1" % N,                   # run past the end
        "v1r%d.1.0.1" % (N - 1),         # second pair overflows
        "r0.1",                          # missing version tag
        "v1r00.1", "v1r0.01",            # leading zeros (non-canonical)
        "v1r٣.1",                   # non-ASCII digit
        "v1r+1.1", "v1r 1.1", "v1r1.1.", "v1r..",
    ]
    # Bitmap rejection cases. v1 bitmaps have no reserved or padding bits
    # (9,600 bits = 1,200 bytes exactly), so the only way to be malformed is
    # the wrong length or a character outside base64url.
    full = encode({(x, y) for x in range(W) for y in range(H)})
    bm = _encode_bitmap([1] * N)
    assert full.startswith("v1r"), "full board should use run-length"
    bm = VERSION + bm
    assert len(bm) == 1603, len(bm)
    assert decode(bm) == {(x, y) for x in range(W) for y in range(H)}
    for bad in [
        bm[:-4],                      # truncated payload
        bm + "AAAA",                  # overlong payload
        bm[:-1] + "+",                # standard alphabet, not base64url
        bm[:-1] + "/",                # standard alphabet, not base64url
        bm[:100] + "=" + bm[101:],    # padding in the middle
        bm + "=",                     # extra padding
        bm[:100] + " " + bm[101:],    # whitespace
        VERSION + "b",                # empty bitmap body
    ]:
        try:
            decode(bad)
        except ValueError:
            continue
        raise AssertionError("accepted bad bitmap %r" % bad[-12:])
    for bad in bad_inputs:
        try:
            decode(bad)
        except ValueError:
            continue
        raise AssertionError("accepted bad input %r" % bad)
    assert decode("v1r") == set()
    print("selftest ok")


def sizes():
    rng = random.Random(2)
    rows = [
        ("empty", set()),
        ("one cell", {(60, 40)}),
        ("glider", {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}),
        ("sparse 2%", _random_board(0.02, rng)),
        ("random 30%", _random_board(0.30, rng)),
        ("random 50%", _random_board(0.50, rng)),
    ]
    print("%-12s %8s %8s %8s  chosen" % ("board", "live", "chars", "bitmap"))
    bitmap_len = len(_encode_bitmap(_bits(set())))  # same for every board
    for name, cells in rows:
        s = encode(cells)
        print("%-12s %8d %8d %8d  %s" % (name, len(cells), len(s),
                                          bitmap_len + len(VERSION), s[len(VERSION)]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "selftest":
        selftest()
    elif cmd == "sizes":
        sizes()
    else:
        print(__doc__)
        sys.exit(2)
