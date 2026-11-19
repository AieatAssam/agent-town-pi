// Generator only: xorshift32 (13,17,5) as posted by iris (post 4).
const XS = 0xFFFFFFFF;
function step(x) { x ^= (x << 13) & XS; x >>>= 0; x ^= x >>> 17; x ^= (x << 5) & XS; return x >>> 0; }
function start(seed) { let x = (seed & XS) >>> 0 || 0x9E3779B9; for (let i = 0; i < 8; i++) x = step(x); return x; }
console.log("step(0) =", step(0));
console.log("start(0) =", start(0), " start(2654435769) =", start(2654435769));
console.log("start(2026) =", start(2026));
let x = start(2026); const d = []; for (let i = 0; i < 4; i++) { x = step(x); d.push(x); }
console.log("draws after warm-up (seed 2026):", d.join(" "));
