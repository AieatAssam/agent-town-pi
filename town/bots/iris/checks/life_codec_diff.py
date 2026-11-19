"""Differential check: Ada's v1 codec (run in node) against my stdlib encoder and validator.

Boards: seeded random (deterministic), plus fixed edge cases. For each board:
  - Ada's encodeBoard hash must be 'v1r...' or 'v1b...'.
  - My encode_runs must equal her run body exactly when she picks runs.
  - My bitmap encoder must equal her bitmap body exactly when she picks bits.
  - Her decode must return the same cells (round trip, checked in node).
  - My validator (rle_refusals.validate) must accept her hash.
Length ties: she picks bits (r.length < a.length ? r : a). Counted, not assumed.
Stdlib only. Run: python3 -I life_codec_diff.py /work/review-life-5/codec.js
"""
import base64
import json
import os
import random
import subprocess
import sys

sys.path.insert(0, '/work/checks')
from rle_vectors import encode_runs  # noqa: E402
from rle_refusals import validate  # noqa: E402

W, H = 120, 80
N = W * H
WORK = '/work/review-life-5'


def bitmap_body(cells):
    b = bytearray(N // 8)
    for i in cells:
        b[i >> 3] |= 0x80 >> (i & 7)
    return base64.urlsafe_b64encode(bytes(b)).decode().rstrip('=')


def boards():
    out = []
    out.append(('empty', []))
    out.append(('one', [0]))
    out.append(('last', [N - 1]))
    out.append(('top-row', list(range(W))))
    out.append(('full', list(range(N))))
    out.append(('checker', [i for i in range(N) if ((i % W) + (i // W)) % 2 == 0]))
    rng = random.Random(20261119)
    for k in range(400):
        p = [0.0, 0.01, 0.05, 0.2, 0.5, 0.9][k % 6]
        out.append((f'rand{k}', [i for i in range(N) if rng.random() < p]))
    return out


def main():
    codec = sys.argv[1]
    cases = boards()
    tmp_in = os.path.join(WORK, 'boards.json')
    tmp_out = os.path.join(WORK, 'ada_out.json')
    with open(tmp_in, 'w') as f:
        json.dump([{'id': k, 'cells': c} for k, (_, c) in enumerate(cases)], f)
    subprocess.run(['node', '/work/checks/life_codec_run.js', codec, tmp_in, tmp_out], check=True)
    with open(tmp_out) as f:
        res = json.load(f)

    stats = {'runs': 0, 'bits': 0, 'tie': 0, 'mismatch': 0, 'roundtrip_fail': 0, 'validator_refuses': 0}
    problems = []
    for r, (name, cells) in zip(res, cases):
        h = r['hash']
        mine_runs = 'v1r' + encode_runs([(i % W, i // W) for i in cells])[3:]
        mine_bits = 'v1b' + bitmap_body(cells)
        if not r['roundtrip']:
            stats['roundtrip_fail'] += 1
            problems.append((name, 'roundtrip'))
        if len(mine_runs) == len(mine_bits):
            stats['tie'] += 1
        if h.startswith('v1r'):
            stats['runs'] += 1
            if h != mine_runs:
                stats['mismatch'] += 1
                problems.append((name, 'runs differ', h[:40], mine_runs[:40]))
        elif h.startswith('v1b'):
            stats['bits'] += 1
            if h != mine_bits:
                stats['mismatch'] += 1
                problems.append((name, 'bits differ'))
        else:
            stats['mismatch'] += 1
            problems.append((name, 'unknown prefix', h[:10]))
        try:
            ok, _ = validate(h)  # returns (bool, info); the tuple itself is always truthy
        except Exception as e:  # validator should not raise
            ok = False
            problems.append((name, 'validator raised', repr(e)))
        if not ok:
            stats['validator_refuses'] += 1
            problems.append((name, 'my validator refuses Ada hash'))
    # Negative control: the validator must refuse a hash it should refuse, or the loop above proves nothing.
    control, _ = validate('v1r0.1.0.1')
    print('control v1r0.1.0.1 accepted by my validator:', control, '(expected False)')
    print(json.dumps(stats))
    for p in problems[:20]:
        print('PROBLEM', p)
    print('cases', len(cases), 'problems', len(problems))


if __name__ == '__main__':
    main()
