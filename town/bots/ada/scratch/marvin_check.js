// Runs Marvin's valid vectors (encoder must match) and refusal list (decoder must return null)
// through the codec block in /work/projects/life/index.html. Run: node marvin_check.js
const fs = require('fs');
const src = fs.readFileSync('/work/projects/life/index.html', 'utf8');
const block = src.slice(src.indexOf('// --- codec start'), src.indexOf('// --- codec end'));
const W = 120, H = 80;
const api = new Function('W', 'H', block + '; return { encodeBoard, encodeRuns, decodeBoard, N, BYTES };')(W, H);
const { encodeBoard, encodeRuns, decodeBoard, N } = api;
const cells = (list) => { const g = new Uint8Array(N); for (const [x, y] of list) g[y * W + x] = 1; return g; };
const bitmapOf = (g) => { const { encodeBits } = new Function('W','H', block + '; return { encodeBits };')(W, H); return encodeBits(g); };

let bad = 0;
const valid = [
  ['empty', [], 'v1r'],
  ['one cell (60,40)', [[60, 40]], 'v1r4860.1'],
  ['glider', [[1,0],[2,1],[0,2],[1,2],[2,2]], 'v1r1.1.120.1.117.3'],
  ['full top row', Array.from({length: 120}, (_, x) => [x, 0]), 'v1r0.120'],
  ['four corners', [[0,0],[119,0],[0,79],[119,79]], 'v1r0.1.118.1.9360.1.118.1'],
];
for (const [name, list, want] of valid) {
  const g = cells(list);
  const got = encodeRuns(g);
  const dec = decodeBoard(want);
  const roundTrip = dec && dec.every((v, i) => v === g[i]);
  const ok = got === want && roundTrip;
  if (!ok) bad++;
  console.log((ok ? 'ok    ' : 'FAIL  ') + name.padEnd(18), 'encodeRuns=' + got, roundTrip ? 'decodes' : 'NOT-DECODED');
}

// refusals: base the bitmap ones on a real 1600-char bitmap
const full = bitmapOf(cells([])); // 'v1b' + 1600 chars
const body = full.slice(3);
const flipLast = (c) => body.slice(0, -1) + c;
const refuse = [
  ['bitmap truncated by 4', 'v1b' + body.slice(0, -4)],
  ['bitmap + AAAA', 'v1b' + body + 'AAAA'],
  ['last char +', 'v1b' + flipLast('+')],
  ['last char /', 'v1b' + flipLast('/')],
  ['= in middle', 'v1b' + body.slice(0, 800) + '=' + body.slice(801)],
  ['v1r00.1', 'v1r00.1'],
  ['v1r0.01', 'v1r0.01'],
  ['v1r+1.1', 'v1r+1.1'],
  ['v1r1.1.', 'v1r1.1.'],
  ['v1r1.0 empty run', 'v1r1.0'],
  ['v1r1.2.3 odd values', 'v1r1.2.3'],
  ['v1r9600.1 past end', 'v1r9600.1'],
  ['v1x unknown format', 'v1x'],
  ['v2r unknown version', 'v2r'],
  ['v1r1 (iris case)', 'v1r1'],
];
for (const [name, h] of refuse) {
  const g = decodeBoard(h);
  const ok = g === null;
  if (!ok) bad++;
  console.log((ok ? 'ok    ' : 'FAIL  ') + ('refuse: ' + name).padEnd(30), g === null ? 'null' : 'ACCEPTED');
}
console.log(bad === 0 ? 'ALL PASS' : bad + ' FAILED');
