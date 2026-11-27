
(function () {
  var W = 640, H = 360;
  var cv = document.getElementById('c');
  var g = cv.getContext('2d');
  var txt = document.getElementById('txt');
  var hud = document.getElementById('hud');

  var dragging = false, lastX = 0, lastT = 0;
  var smooth = 0;          // crank speed, CSS px per second, smoothed
  var fps = 0;             // film frames per second from the crank
  var acc = 0;             // time accumulator for film frames
  var frame = 0;
  var flick = 1;           // per film frame brightness (1 = full)
  var jx = 0;              // per film frame horizontal jitter when running fast
  var scroll = 0;          // sprocket holes scroll with the film
  var irisT = 0;           // 0..1, the iris opening on a new card
  var scratches = [];
  var last = performance.now();

  function wrap(t) {
    g.font = '34px Georgia, "Times New Roman", serif';
    var words = (t || ' ').split(/\s+/), out = [], cur = '';
    for (var i = 0; i < words.length; i++) {
      var test = cur ? cur + ' ' + words[i] : words[i];
      if (g.measureText(test).width > 520 && cur) { out.push(cur); cur = words[i]; }
      else cur = test;
    }
    if (cur) out.push(cur);
    return out;
  }

  function band() {
    if (fps < 1) return 'the reel has stopped';
    if (fps < 12) return 'too slow: it flickers and dims';
    if (fps <= 24) return 'steady, about right';
    return 'too fast: everybody runs';
  }

  function tick() {
    frame++;
    scroll = (scroll + 3) % 40;
    if (fps < 1) flick = 1;
    else if (fps < 12) flick = 0.5 + 0.5 * Math.random();
    else flick = 1;
    jx = fps > 24 ? (Math.random() - 0.5) * 14 : 0;
    if (Math.random() < 0.05) scratches.push({ x: Math.random() * W, life: 3 });
    scratches = scratches.filter(function (s) { s.life--; return s.life > 0; });
  }

  function render() {
    g.setTransform(1, 0, 0, 1, 0, 0);
    g.fillStyle = '#050403';
    g.fillRect(0, 0, W, H);

    // the card, opened by the iris
    g.save();
    g.beginPath();
    g.arc(W / 2, H / 2, irisT * Math.hypot(W, H) / 2, 0, Math.PI * 2);
    g.clip();
    g.translate(jx, 0);
    g.fillStyle = '#e9dcb8';
    g.fillRect(-20, 0, W + 40, H);
    g.fillStyle = '#1d140c';
    g.font = '34px Georgia, "Times New Roman", serif';
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    var ls = wrap(txt.value);
    var lh = 44, y0 = H / 2 - (ls.length - 1) * lh / 2;
    for (var i = 0; i < ls.length; i++) g.fillText(ls[i], W / 2, y0 + i * lh);
    g.restore();

    // scratches
    g.strokeStyle = 'rgba(255,250,235,0.55)';
    g.lineWidth = 1;
    for (var s = 0; s < scratches.length; s++) {
      var x = scratches[s].x;
      g.beginPath(); g.moveTo(x, 0); g.lineTo(x + 1, H); g.stroke();
    }

    // sprocket band on both edges
    g.fillStyle = '#2b2218';
    g.fillRect(0, 0, 22, H);
    g.fillRect(W - 22, 0, 22, H);
    g.fillStyle = '#050403';
    for (var y = -40; y < H + 40; y += 40) {
      var yy = (((y + scroll) % H) + H) % H;
      g.fillRect(6, yy, 10, 18);
      g.fillRect(W - 16, yy, 10, 18);
    }

    // vignette
    var grd = g.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, W * 0.62);
    grd.addColorStop(0, 'rgba(0,0,0,0)');
    grd.addColorStop(1, 'rgba(0,0,0,0.7)');
    g.fillStyle = grd;
    g.fillRect(0, 0, W, H);

    // projector flicker
    if (flick < 1) {
      g.fillStyle = 'rgba(0,0,0,' + (1 - flick).toFixed(3) + ')';
      g.fillRect(0, 0, W, H);
    }
  }

  function loop(t) {
    var dt = Math.min(0.05, (t - last) / 1000);
    last = t;
    smooth *= Math.pow(0.08, dt);            // the crank slows down when you let go
    fps = Math.min(40, smooth / 20);
    acc += fps * dt;
    while (acc >= 1) { acc -= 1; tick(); }
    irisT = Math.min(1, irisT + dt * 0.7);
    render();
    hud.textContent = Math.round(fps) + ' fps: ' + band();
    requestAnimationFrame(loop);
  }

  cv.addEventListener('pointerdown', function (e) {
    dragging = true;
    lastX = e.clientX;
    lastT = performance.now();
    cv.setPointerCapture(e.pointerId);
  });
  cv.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    var now = performance.now();
    var dtms = Math.max(4, now - lastT);
    var dx = Math.abs(e.clientX - lastX);
    var speed = dx / dtms * 1000;              // CSS px per second
    smooth = smooth * 0.5 + speed * 0.5;
    lastX = e.clientX;
    lastT = now;
  });
  function stop() { dragging = false; }
  cv.addEventListener('pointerup', stop);
  cv.addEventListener('pointercancel', stop);

  txt.addEventListener('input', function () { irisT = 0; });

  requestAnimationFrame(loop);
})();
