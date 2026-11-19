// --- codec start
// Hash format v1: "v1b" + 1600 base64url chars (1200-byte bitmap, MSB first, row-major),
// or "v1r" + runs "skip.count.skip.count..." (one flat dot-separated list of numbers, row-major;
// skip counts empty cells since the end of the previous run).
// encodeBoard picks whichever string is shorter. decodeBoard returns null for anything it cannot prove valid.
const N = W * H, BYTES = N / 8;
function b64url(bytes) {
  let s = ''; for (const x of bytes) s += String.fromCharCode(x);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
function unb64url(s) {
  return Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
}
function encodeBits(g) {
  const b = new Uint8Array(BYTES);
  for (let i = 0; i < N; i++) if (g[i]) b[i >> 3] |= 0x80 >> (i & 7);
  return 'v1b' + b64url(b);
}
function encodeRuns(g) {
  const parts = []; let pos = 0;
  for (;;) {
    let s = pos; while (s < N && !g[s]) s++;
    if (s >= N) break;
    let e = s; while (e < N && g[e]) e++;
    parts.push(s - pos, e - s);
    pos = e;
  }
  return 'v1r' + parts.join('.');
}
function encodeBoard(g) { const a = encodeBits(g), r = encodeRuns(g); return r.length < a.length ? r : a; }
function decodeBoard(h) {
  const m = /^v1([br])([\s\S]*)$/.exec(h);
  if (!m) return null;
  const g = new Uint8Array(N);
  if (m[1] === 'b') {
    if (!/^[A-Za-z0-9_-]*$/.test(m[2]) || m[2].length !== 1600) return null;
    const b = unb64url(m[2]);
    for (let i = 0; i < N; i++) g[i] = (b[i >> 3] >> (7 - (i & 7))) & 1;
    return g;
  }
  if (m[2] === '') return g;
  const v = m[2].split('.');
  if (v.length % 2) return null;
  let pos = 0;
  for (let i = 0; i < v.length; i += 2) {
    if (!/^(0|[1-9]\d*)$/.test(v[i]) || !/^[1-9]\d*$/.test(v[i + 1])) return null;
    const start = pos + Number(v[i]), count = Number(v[i + 1]);
    if (start + count > N) return null;
    g.fill(1, start, start + count);
    pos = start + count;
  }
  return g;
}
// --- codec end

module.exports = { encodeBoard, decodeBoard, N, W, H };
