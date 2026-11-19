const C = require('./codec.js');
const { N } = C;
const mk = (cells) => { const g = new Uint8Array(N); for (const [x,y] of cells) g[y*120+x]=1; return g; };
const out = [];
const check = (name, got, want) => out.push(`${got === want ? 'ok  ' : 'FAIL'} ${name}: ${got} ${got===want?'':'(want '+want+')'}`);
// vectors
check('empty', C.encodeBoard(new Uint8Array(N)), 'v1r');
check('(60,40)', C.encodeBoard(mk([[60,40]])), 'v1r4860.1');
check('glider', C.encodeBoard(mk([[1,0],[2,1],[0,2],[1,2],[2,2]])), 'v1r1.1.120.1.117.3');
const top = []; for (let x=0;x<120;x++) top.push([x,0]);
check('top row', C.encodeBoard(mk(top)), 'v1r0.120');
check('corners', C.encodeBoard(mk([[0,0],[119,0],[0,79],[119,79]])), 'v1r0.1.118.1.9360.1.118.1');
// refusals
const bad = ['v1r1.0','v1r1.2.3','v1r9600.1','v1x','v2r','v1r00.1','v1r0.01','v1r+1.1','v1r1.1.','v1r0','v1r 1.1','v1r1.1 ','v1r9599.2','v1r-1.1','v1r1.-1','v1r1e3.1','v1r١.1','v1b','v1r0.1.0.1'];
for (const h of bad) { const r = C.decodeBoard(h); out.push(`${r===null?'refuse':'ACCEPT'} ${JSON.stringify(h)}`); }
// bitmap refusals
const bmp = 'A'.repeat(1600);
const cases = {
  'b truncated 1599': 'v1b' + 'A'.repeat(1599),
  'b overlong 1601': 'v1b' + 'A'.repeat(1601),
  'b with +': 'v1b' + 'A'.repeat(1599) + '+',
  'b with /': 'v1b' + 'A'.repeat(1599) + '/',
  'b with =': 'v1b' + 'A'.repeat(1599) + '=',
  'b with space': 'v1b' + ' ' + 'A'.repeat(1599),
  'b with newline': 'v1b' + 'A'.repeat(1599) + '\n',
  'b with -': 'v1b' + 'A'.repeat(1599) + '-',
  'b with _': 'v1b' + 'A'.repeat(1599) + '_',
};
for (const [k,h] of Object.entries(cases)) { const r = C.decodeBoard(h); out.push(`${r===null?'refuse':'ACCEPT'} ${k}`); }
// round trip random
let rt = 0;
for (let t=0;t<200;t++){ const g=new Uint8Array(N); const p=[0.02,0.3,0.5][t%3]; for(let i=0;i<N;i++) g[i]= Math.random()<p?1:0;
  const h=C.encodeBoard(g); const d=C.decodeBoard(h); if(!d||d.some((v,i)=>v!==g[i])) rt++; }
out.push(`random roundtrip failures: ${rt}/200`);
// whole-board bitmap encode -> decode
console.log(out.join('\n'));
