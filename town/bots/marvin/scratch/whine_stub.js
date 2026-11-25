// Minimal DOM/Audio stubs to exercise whine62's script without a browser.
const fs = require('fs');
const html = fs.readFileSync('/work/projects/whine62/index.html', 'utf8');
const script = html.split('<script>')[1].split('</script>')[0];
const mk = (id) => ({ id, value: id === 'pitch' ? '5200' : (id === 'temp-in' ? '62' : ''), textContent: '', dataset: {},
  listeners: {}, addEventListener(e, f) { (this.listeners[e] = this.listeners[e] || []).push(f); },
  setAttribute(k, v) { this[k] = v; }, getContext() { return { fillRect(){}, beginPath(){}, moveTo(){}, lineTo(){}, stroke(){} }; },
  width: 440, height: 90 });
const els = {};
['temp','temp-in','pitch','play','reset','hz','log','scope'].forEach(id => els[id] = mk(id));
els['temp-in'].type = 'range'; els['pitch'].type = 'range';
global.document = { getElementById: id => els[id] };
const param = () => ({ value: 0, setTargetAtTime(v){ this.value = v; } });
global.window = {};
let made = 0;
global.window.AudioContext = function () { made++; this.state = 'running'; this.currentTime = 0; this.destination = {};
  this.createOscillator = () => ({ type: '', frequency: param(), connect(){}, start(){} });
  this.createGain = () => ({ gain: param(), connect(){} });
  this.createAnalyser = () => ({ fftSize: 0, connect(){}, getByteTimeDomainData(b){ b.fill(128); } }); };
global.requestAnimationFrame = () => {};
eval(script);
const fire = (el, ev) => els[el].listeners[ev].forEach(f => f({}));
const errs = [];
try {
  fire('temp-in', 'input');            // set temp via slider (no pitch touch)
  els['temp-in'].value = '70'; fire('temp-in', 'input');
  console.log('pitch after temp 70 (untouched):', els['pitch'].value, els['hz'].textContent);
  els['pitch'].value = '5600'; fire('pitch', 'input');
  console.log('log after pitch 5600 at 70C:', els['log'].textContent);
  fire('play', 'click'); console.log('play pressed:', els['play'].textContent, 'ctx made:', made);
  fire('play', 'click'); console.log('play released:', els['play'].textContent);
  fire('reset', 'click'); console.log('reset:', els['temp'].textContent, els['log'].textContent);
} catch (e) { errs.push(e); }
console.log('errors:', errs.map(String));
