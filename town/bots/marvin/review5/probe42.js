const C = require('./codec_guard.js');
const { N } = C;
const mk = (cells) => { const g = new Uint8Array(N); for (const [x,y] of cells) g[y*120+x]=1; return g; };
const out = [];
const check = (name, got, want) => out.push(`${got === want ? 'ok  ' : 'FAIL'} ${name}: ${got} ${got===want?'':'(want '+want+')'}`);
check('empty', C.encodeBoard(new Uint8Array(N)), 'v1r');
check('(60,40)', C.encodeBoard(mk([[60,40]])), 'v1r4860.1');
check('glider', C.encodeBoard(mk([[1,0],[2,1],[0,2],[1,2],[2,2]])), 'v1r1.1.120.1.117.3');
const top = []; for (let x=0;x<120;x++) top.push([x,0]);
check('top row', C.encodeBoard(mk(top)), 'v1r0.120');
check('corners', C.encodeBoard(mk([[0,0],[119,0],[0,79],[119,79]])), 'v1r0.1.118.1.9360.1.118.1');
const refuse = ['v1r1.0','v1r1.2.3','v1r9600.1','v1x','v2r','v1r00.1','v1r0.01','v1r+1.1','v1r1.1.','v1r0','v1r0.1.0.1','v1r0.2.0.2','v1r3.1.0.1','v1r1.1.0.1','v1r9599.2','v1r-1.1','v1r1e3.1'];
for (const h of refuse) { const r = C.decodeBoard(h); out.push(`${r===null?'refuse':'ACCEPT'} ${JSON.stringify(h)} (want refuse)`); }
const accept = {'v1r0.2.1.2': [0,1,3,4], 'v1r0.1.1.1': [0,2]};
for (const [h, cells] of Object.entries(accept)) { const r = C.decodeBoard(h); const got = r ? [...r.keys()].filter(i=>r[i]).join(',') : 'null'; out.push(`${got===cells.join(',')?'ok  ':'FAIL'} ${h} -> ${got}`); }
let rt = 0;
for (let t=0;t<300;t++){ const g=new Uint8Array(N); const p=[0.02,0.3,0.5][t%3]; for(let i=0;i<N;i++) g[i]= Math.random()<p?1:0;
  const h=C.encodeBoard(g); const d=C.decodeBoard(h); if(!d||d.some((v,i)=>v!==g[i])) rt++; }
out.push(`random roundtrip failures: ${rt}/300`);
// encoder never emits a zero skip after the first pair
let zs=0; for (let t=0;t<300;t++){ const g=new Uint8Array(N); for(let i=0;i<N;i++) g[i]=Math.random()<0.02?1:0; const h=C.encodeBoard(g); if (h.startsWith('v1r')) { const v=h.slice(3).split('.'); for (let i=2;i<v.length;i+=2) if (v[i]==='0') zs++; } }
out.push(`encoder zero-skip-after-first emitted: ${zs}`);
console.log(out.join('\n'));
