// Iris post 4 step() as posted, 32-bit xorshift (13,17,5). Checks only the generator.
const XS = 0xFFFFFFFFn;
function step(x) {
  x ^= (x << 13n) & XS;
  x ^= x >> 17n;
  x ^= (x << 5n) & XS;
  return x;
}
// Seed 0 is a fixed point: every draw is 0.
console.log("step(0) =", step(0n));
// Nonzero seed: first outputs, and whether the state ever reaches 0 in 2^20 steps.
let x = 2026n, zero = false, first = [];
for (let i = 0; i < (1 << 20); i++) {
  x = step(x);
  if (i < 6) first.push(x.toString());
  if (x === 0n) { zero = true; break; }
}
console.log("seed 2026 first outputs:", first.join(" "));
console.log("reached 0 within 2^20 steps:", zero);
// Low bit as orientation draw: fraction of ones over 16*16 draws, and over the first 2^20.
let s = 2026n, ones = 0;
const N = 1 << 20;
for (let i = 0; i < N; i++) { s = step(s); ones += Number(s & 1n); }
console.log("low-bit ones fraction over 2^20 draws:", (ones / N).toFixed(4));
