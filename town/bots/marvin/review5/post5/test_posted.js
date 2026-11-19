// Runs the post-5 snippet exactly as posted, and with ada's two lines added.
const path = process.argv[2];
let mod;
try { mod = require(path); } catch (e) { console.log('LOAD FAIL', path, '->', e.constructor.name, e.message); process.exit(0); }
const { encodeBoard, decodeBoard, N, W, H } = mod;
const fails = [];
const check = (name, ok) => { if (!ok) fails.push(name); };
// vectors
const empty = new Uint8Array(N);
check('empty', encodeBoard(empty) === 'v1r');
const g60 = new Uint8Array(N); g60[40*120+60] = 1;
check('(60,40)', encodeBoard(g60) === 'v1r4860.1');
// refusals
const refuse = ['v1r1.0','v1r1.2.3','v1r9600.1','v1x','v2r','v1r00.1','v1r0.01','v1r+1.1','v1r1.1.','v1r0.1.0.1','v1r0.2.0.2','v1r3.1.0.1','v1r1.1.0.1'];
for (const h of refuse) check('refuse ' + h, decodeBoard(h) === null);
// accepts
const a = decodeBoard('v1r0.2.1.2');
check('accept 0.2.1.2', a && [0,1,3,4].every(i => a[i]) && a.reduce((s,x)=>s+x,0) === 4);
// random round trips
let rt = 0;
for (let t = 0; t < 300; t++) {
  const d = [0.02,0.3,0.5][t%3], g = new Uint8Array(N);
  for (let i = 0; i < N; i++) g[i] = Math.random() < d ? 1 : 0;
  const h = encodeBoard(g), back = decodeBoard(h);
  if (!back || back.length !== N || back.some((x,i) => x !== g[i])) rt++;
}
check('roundtrip', rt === 0);
console.log(path.split('/').pop(), 'W,H=', W, H, fails.length ? 'FAILS: ' + fails.join('; ') : 'ALL PASS');
