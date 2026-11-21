// Hero figure: animates the same gradient-descent recurrence used in the
// actual app (src/pages/gradient-descent.py DEFAULT_CONFIG: x0=8.0, lr=0.1)
// so the landing page shows the real algorithm, not a decorative stand-in.
(function () {
  "use strict";

  var canvas = document.getElementById("hero-canvas");
  if (!canvas || !canvas.getContext) return;

  var ctx = canvas.getContext("2d");
  var dpr = window.devicePixelRatio || 1;
  var cssWidth = 460;
  var cssHeight = 300;

  canvas.width = cssWidth * dpr;
  canvas.height = cssHeight * dpr;
  canvas.style.width = "100%";
  canvas.style.height = "auto";
  ctx.scale(dpr, dpr);

  var X0 = 8.0;
  var LR = 0.1;
  var ITERATIONS = 20;

  function f(x) {
    return 0.5 * x * x;
  }

  var domainMin = -9,
    domainMax = 9;
  var padding = { top: 18, right: 18, bottom: 30, left: 18 };
  var plotW = cssWidth - padding.left - padding.right;
  var plotH = cssHeight - padding.top - padding.bottom;
  var fMax = f(domainMax);

  function toCanvasX(x) {
    return padding.left + ((x - domainMin) / (domainMax - domainMin)) * plotW;
  }
  function toCanvasY(y) {
    return padding.top + plotH - (y / fMax) * plotH;
  }

  var ruleColor, mutedColor, signalColor;

  // Read from the CSS tokens so the canvas follows the theme; called again
  // whenever the theme switch changes them.
  function readColors() {
    var cs = getComputedStyle(document.documentElement);
    ruleColor = cs.getPropertyValue("--rule").trim();
    mutedColor = cs.getPropertyValue("--muted").trim();
    signalColor = cs.getPropertyValue("--signal").trim();
  }
  readColors();

  function drawStatic() {
    ctx.clearRect(0, 0, cssWidth, cssHeight);

    // faint horizontal reference lines
    ctx.strokeStyle = ruleColor;
    ctx.lineWidth = 1;
    for (var i = 0; i <= 3; i++) {
      var gy = padding.top + (plotH / 3) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, gy);
      ctx.lineTo(cssWidth - padding.right, gy);
      ctx.stroke();
    }

    // the parabola f(x) = 0.5x^2
    ctx.beginPath();
    ctx.strokeStyle = mutedColor;
    ctx.lineWidth = 1.5;
    for (var px = 0; px <= plotW; px++) {
      var x = domainMin + (px / plotW) * (domainMax - domainMin);
      var cx = padding.left + px;
      var cy = toCanvasY(f(x));
      if (px === 0) ctx.moveTo(cx, cy);
      else ctx.lineTo(cx, cy);
    }
    ctx.stroke();
  }

  var lastX = X0;
  var lastStep = 0;

  function drawBall(x, step) {
    lastX = x;
    lastStep = step;
    var cx = toCanvasX(x);
    var cy = toCanvasY(f(x));

    ctx.beginPath();
    ctx.fillStyle = signalColor;
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fill();

    var caption = document.getElementById("hero-caption-x");
    var captionStep = document.getElementById("hero-caption-step");
    if (caption) caption.textContent = "x = " + x.toFixed(3);
    if (captionStep) captionStep.textContent = "Schritt " + step + "/" + ITERATIONS;
  }

  document.addEventListener("themechange", function () {
    readColors();
    drawStatic();
    drawBall(lastX, lastStep);
  });

  var reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  function finalX() {
    return X0 * Math.pow(1 - LR, ITERATIONS);
  }

  if (reduceMotion) {
    drawStatic();
    drawBall(finalX(), ITERATIONS);
    return;
  }

  var durationMs = 2200;
  var startTime = null;

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function frame(timestamp) {
    if (startTime === null) startTime = timestamp;
    var elapsed = timestamp - startTime;
    var t = Math.min(elapsed / durationMs, 1);
    var eased = easeOutCubic(t);

    var x = X0 * Math.pow(1 - LR, eased * ITERATIONS);
    var step = Math.round(eased * ITERATIONS);

    drawStatic();
    drawBall(x, step);

    if (t < 1) {
      requestAnimationFrame(frame);
    }
  }

  requestAnimationFrame(frame);
})();
