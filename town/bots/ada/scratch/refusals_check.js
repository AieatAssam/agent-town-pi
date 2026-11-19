// Cross-check of the v1 hash decoder against the four refusal inputs iris listed.
// Run: node refusals_check.js
const fs = require('fs');
const src = fs.readFileSync('/work/projects/life/index.html', 'utf8');
const block = src.slice(src.indexOf('// --- codec start'), src.indexOf('// --- codec end'));
const W = 120, H = 80;
const { decodeBoard } = new Function('W', 'H', block + '; return { decodeBoard };')(W, H);

for (const h of ['v1r00.1', 'v1r0.01', 'v1r+1.1', 'v1r1']) {
  const g = decodeBoard(h);
  console.log(h.padEnd(10), g === null ? 'refused (null)' : 'ACCEPTED len=' + g.length);
}
