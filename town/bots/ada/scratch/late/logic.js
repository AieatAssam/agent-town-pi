
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

console.log(verdict(judge(makeBeats(), [])));
console.log(verdict(judge(makeBeats(), makeBeats().map(b=>b+140))));
