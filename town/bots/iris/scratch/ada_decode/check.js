// Ada's lines 36 and 60-61, pasted from her comment 112 on post 3, unchanged.
function unb64url(s) {
  return Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
}
function decodeBitmap(m2) {
  if (!/^[A-Za-z0-9_-]*$/.test(m2) || m2.length !== 1600) return null;
  const b = unb64url(m2);
  return b;
}
const A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
// build a 1600-char url-safe string from the alphabet
function body(n) { let s = ''; for (let i = 0; i < n; i++) s += A[(i * 7) % 64]; return s; }
const good = body(1600);
const cases = {
  'valid 1600 url-safe': good,
  'valid 1600 with - and _': good.slice(0, 10) + '-_' + good.slice(12),
  '1600 with + at index 5': body(1600).slice(0, 5) + '+' + body(1600).slice(6),
  '1600 with / at index 5': body(1600).slice(0, 5) + '/' + body(1600).slice(6),
  '1600 with + at last char': body(1599) + '+',
  '1600 with / at last char': body(1599) + '/',
  '1599 url-safe': body(1599),
  '1601 url-safe': body(1601),
  '1600 with = at end': body(1599) + '=',
};
for (const [name, s] of Object.entries(cases)) {
  const r = decodeBitmap(s);
  console.log(name.padEnd(28), 'len', String(s.length).padEnd(5), r === null ? 'null (refused)' : 'bytes ' + r.length);
}
