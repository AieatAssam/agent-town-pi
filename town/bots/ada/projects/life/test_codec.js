// Round-trip and rejection tests for the hash codec in index.html.
// Run: node test_codec.js
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/index.html', 'utf8');
const block = src.slice(src.indexOf('// --- codec start'), src.indexOf('// --- codec end'));
const W = 120, H = 80;
const { encodeBoard, decodeBoard, encodeBits, encodeRuns } = new Function(
  'W', 'H', block + '; return { encodeBoard, decodeBoard, encodeBits, encodeRuns };')(W, H);
const N = W * H;
let fail = 0;
const check = (name, ok) => { if (!ok) { fail++; console.log('FAIL', name); } };
const same = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);

function rnd(p) { const g = new Uint8Array(N); for (let i = 0; i < N; i++) g[i] = Math.random() < p ? 1 : 0; return g; }
const boards = {
  empty: new Uint8Array(N),
  full: new Uint8Array(N).fill(1),
  one: (() => { const g = new Uint8Array(N); g[N - 1] = 1; return g; })(),
  first: (() => { const g = new Uint8Array(N); g[0] = 1; return g; })(),
  rowWrap: (() => { const g = new Uint8Array(N); g.fill(1, 119, 121); return g; })(),
  r2: rnd(0.02), r30: rnd(0.3), r50: rnd(0.5), r100: rnd(1),
};
for (const [name, g] of Object.entries(boards)) {
  const h = encodeBoard(g);
  const back = decodeBoard(h);
  check('roundtrip ' + name, back && same(back, g));
  console.log(name.padEnd(8), String(h.length).padStart(5), 'chars', h.slice(0, 3));
}
// Encoder picks the shorter form.
check('sparse uses runs', encodeBoard(boards.r2).startsWith('v1r'));
check('dense uses bits', encodeBoard(boards.r50).startsWith('v1b'));
check('empty is runs', encodeBoard(boards.empty) === 'v1r');

// Hashes that must be refused.
const bad = [
  '', 'v2r', 'v1x', 'v1r0.0', 'v1r0.', 'v1r.5', 'v1r9600.1', 'v1r0.9601', 'v1r5.5000.4000.700',
  'v1r01.2', 'v1r1.-2', 'v1r1.2.', 'v1r 1.2', 'v1b', 'v1b' + 'A'.repeat(1599), 'v1b' + 'A'.repeat(1601),
  'v1b' + 'A'.repeat(1599) + '+', 'v1b' + 'A'.repeat(1599) + '=', 'v1r' + '1.1.'.repeat(5000) + '1.1',
];
for (const h of bad) check('reject ' + JSON.stringify(h.slice(0, 20)), decodeBoard(h) === null);

// Adjacent runs have a second spelling (skip 0 after the first pair). The encoder never emits it, so refuse it.
for (const h of ['v1r0.2.0.2', 'v1r0.1.0.1', 'v1r3.1.0.1', 'v1r0.1.1.1.0.1']) check('reject adjacent ' + h, decodeBoard(h) === null);
// Gaps of 1 or more between runs are fine, and the encoder's own output must still decode.
const gapped = decodeBoard('v1r0.2.1.2');
check('gapped runs fill 0-1 and 3-4', gapped && same(Array.from(gapped.slice(0, 6)), [1,1,0,1,1,0]));
check('encoder never emits a zero skip after the first pair', [boards.r2, boards.r30, boards.r100, boards.rowWrap].every(g => {
  const parts = encodeRuns(g).slice(3).split('.').map(Number);
  return parts.every((x, i) => i % 2 === 1 || i === 0 || x > 0);
}));

console.log(fail ? fail + ' FAILED' : 'all codec tests passed');
process.exit(fail ? 1 : 0);
