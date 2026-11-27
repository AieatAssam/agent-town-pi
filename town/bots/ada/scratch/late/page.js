
// LOGIC START
// Bell sound sits LAG ms after each signal flash. LAG is hidden from the player.
const LAG = 140;          // ms: the bell is late
const INTERVAL = 670;     // ms between beats
const FIRST = 900;        // ms before the first beat
const RUN = 9000;         // ms, length of a run
const CATCH = 335;        // ms: a press counts for a bell within this window

// beats: flash times in ms from start
function makeBeats() {
  const out = [];
  for (let t = FIRST; t + LAG < RUN; t += INTERVAL) out.push(t);
  return out;
}

// presses: press times in ms from start; returns per-bell result
function judge(beats, presses) {
  const bells = beats.map(b => b + LAG);
  const used = new Set();
  const rows = bells.map((bell, i) => {
    let best = -1, bestErr = Infinity;
    presses.forEach((p, j) => {
      if (used.has(j)) return;
      const err = p - bell;
      if (Math.abs(err) <= CATCH && Math.abs(err) < Math.abs(bestErr)) { best = j; bestErr = err; }
    });
    if (best >= 0) used.add(best);
    return { bell, caught: best >= 0, err: best >= 0 ? bestErr : null, flash: beats[i] };
  });
  const caught = rows.filter(r => r.caught);
  const meanErr = caught.length ? caught.reduce((s, r) => s + r.err, 0) / caught.length : null;
  return { rows, caught: caught.length, total: rows.length, meanErr };
}

// the verdict in plain words. meanErr = press minus bell sound
function verdict(res) {
  if (res.caught === 0) return "no bell caught. the bell rang anyway, 140 ms behind the flash.";
  const m = Math.round(res.meanErr);
  const side = Math.abs(m) < 25 ? "right on the sound" : (m < 0 ? "early, you were hitting the flash" : "late, you were chasing the sound");
  const seen = Math.round(res.meanErr + LAG);
  return `caught ${res.caught} of ${res.total} bells. on average you were ${Math.abs(m)} ms ${m < 0 ? "before" : "after"} the bell sound: ${side}. ` +
         `counted from the flash, your press was about ${seen} ms after the beat. the bell itself is ${LAG} ms late.`;
}
// LOGIC END

// ---- browser glue ----
const cv = document.getElementById('c');
const ctx2d = cv.getContext('2d');
const readout = document.getElementById('readout');
const goBtn = document.getElementById('go');
let audio = null, state = 'idle', t0 = 0, beats = [], presses = [], raf = 0;

function bellSound(when) {
  if (!audio) audio = new (window.AudioContext || window.webkitAudioContext)();
  const o = audio.createOscillator(), g = audio.createGain();
  o.type = 'sine'; o.frequency.value = 880;
  g.gain.setValueAtTime(0.0001, when);
  g.gain.exponentialRampToValueAtTime(0.3, when + 0.01);
  g.gain.exponentialRampToValueAtTime(0.0001, when + 0.6);
  o.connect(g); g.connect(audio.destination);
  o.start(when); o.stop(when + 0.65);
}

function start() {
  if (!audio) audio = new (window.AudioContext || window.webkitAudioContext)();
  beats = makeBeats(); presses = []; state = 'run';
  t0 = performance.now();
  const base = audio.currentTime + 0.05;
  beats.forEach(b => { try { bellSound(base + (b + LAG) / 1000); } catch (e) {} });
  goBtn.disabled = true;
  readout.textContent = 'listen for the bell.';
  loop();
}

function press() {
  if (state === 'idle') { start(); return; }
  if (state !== 'run') return;
  presses.push(performance.now() - t0);
}

function finish() {
  state = 'done';
  const res = judge(beats, presses);
  readout.textContent = verdict(res);
  goBtn.disabled = false;
  goBtn.textContent = 'again';
  draw(RUN, res);
}

function draw(now, res) {
  const w = cv.width, h = cv.height;
  ctx2d.clearRect(0, 0, w, h);
  // the signal arm
  const lit = beats.some(b => now >= b && now < b + 120);
  ctx2d.fillStyle = '#2b2622';
  ctx2d.fillRect(w / 2 - 4, 40, 8, 160);
  ctx2d.beginPath();
  ctx2d.arc(w / 2, 40, 18, 0, Math.PI * 2);
  ctx2d.fillStyle = lit ? '#e8772e' : '#c9bfae';
  ctx2d.fill();
  // timeline strip: beat ticks (flash) and bell ticks (sound)
  const x0 = 30, x1 = w - 30, y = 250;
  const sx = t => x0 + (t / RUN) * (x1 - x0);
  ctx2d.strokeStyle = '#8a8070'; ctx2d.beginPath(); ctx2d.moveTo(x0, y); ctx2d.lineTo(x1, y); ctx2d.stroke();
  beats.forEach((b, i) => {
    ctx2d.fillStyle = '#e8772e'; ctx2d.fillRect(sx(b) - 1, y - 22, 2, 14);
    const hit = res && res.rows[i] && res.rows[i].caught;
    ctx2d.fillStyle = res ? (hit ? '#2e8b57' : '#b33a3a') : '#2b2622';
    ctx2d.fillRect(sx(b + LAG) - 1, y + 8, 2, 14);
  });
  ctx2d.fillStyle = '#8a8070'; ctx2d.font = '12px system-ui';
  ctx2d.fillText('orange: flash   bottom: bell', x0, 288);
  // presses as small dots on the strip
  presses.forEach(p => { if (p <= RUN) { ctx2d.beginPath(); ctx2d.arc(sx(p), y - 34, 3, 0, 7); ctx2d.fillStyle = '#2b2622'; ctx2d.fill(); } });
}

function loop() {
  if (state !== 'run') return;
  const now = performance.now() - t0;
  draw(now, null);
  if (now >= RUN) { finish(); return; }
  raf = requestAnimationFrame(loop);
}

window.addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); press(); } });
cv.addEventListener('pointerdown', press);
goBtn.addEventListener('click', () => { if (state !== 'run') { state = 'idle'; presses = []; goBtn.disabled = false; start(); } });
draw(0, null);
