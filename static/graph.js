/* Force-directed pattern relationship graph — vanilla JS + Canvas */
(function () {
  "use strict";

  var canvas = document.getElementById("graph-canvas");
  if (!canvas) return;
  var ctx = canvas.getContext("2d");
  var container = canvas.parentElement;

  /* ---- configuration ---- */
  var NODE_RADIUS = 18;
  var LABEL_FONT = "12px sans-serif";
  var REPULSION = 8000;
  var SPRING_LENGTH = 140;
  var SPRING_K = 0.005;
  var GRAVITY = 0.02;
  var DAMPING = 0.85;
  var TOTAL_FRAMES = 350;
  var ARROW_SIZE = 8;
  var MAX_LABEL_LEN = 22;

  /* ---- state ---- */
  var nodes = [];
  var edges = [];
  var scaleIds = [];
  var scaleColors = [];
  var frame = 0;
  var animId = null;
  var dragging = null;
  var dpr = window.devicePixelRatio || 1;
  var W, H;

  /* ---- read CSS custom properties ---- */
  function readColors() {
    var style = getComputedStyle(document.documentElement);
    scaleColors = [];
    for (var i = 0; i < 5; i++) {
      var c = style.getPropertyValue("--color-scale-" + i).trim();
      scaleColors.push(c || "#888");
    }
  }

  /* ---- resize ---- */
  function resize() {
    var rect = container.getBoundingClientRect();
    W = rect.width;
    H = Math.max(500, window.innerHeight - rect.top - 60);
    canvas.style.height = H + "px";
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  /* ---- data loading ---- */
  function load() {
    fetch(window.PATTERNS_JSON_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        scaleIds = data.scales.map(function (s) { return s.id; });
        readColors();
        resize();
        buildGraph(data);
        frame = 0;
        tick();
      });
  }

  function buildGraph(data) {
    var byNumber = {};
    var totalScales = scaleIds.length || 1;

    data.patterns.forEach(function (p) {
      var scaleIdx = scaleIds.indexOf(p.scale);
      if (scaleIdx < 0) scaleIdx = 0;
      /* initial position: spread by scale band vertically, random x */
      var bandH = H / totalScales;
      var node = {
        number: p.number,
        name: p.name,
        scale: p.scale,
        scaleIdx: scaleIdx,
        x: W * 0.2 + Math.random() * W * 0.6,
        y: bandH * scaleIdx + bandH * 0.2 + Math.random() * bandH * 0.6,
        vx: 0,
        vy: 0,
        contains: p.contains || [],
      };
      nodes.push(node);
      byNumber[p.number] = node;
    });

    /* edges from contains relationships (parent → child) */
    nodes.forEach(function (n) {
      n.contains.forEach(function (cNum) {
        if (byNumber[cNum]) {
          edges.push({ source: n, target: byNumber[cNum] });
        }
      });
    });
  }

  /* ---- physics ---- */
  function applyForces() {
    var temperature = Math.max(0.05, 1 - frame / TOTAL_FRAMES);
    var i, j, dx, dy, dist, force, n1, n2, edge;

    /* repulsion (all pairs) */
    for (i = 0; i < nodes.length; i++) {
      for (j = i + 1; j < nodes.length; j++) {
        n1 = nodes[i];
        n2 = nodes[j];
        dx = n1.x - n2.x;
        dy = n1.y - n2.y;
        dist = Math.sqrt(dx * dx + dy * dy) || 1;
        force = REPULSION / (dist * dist);
        var fx = (dx / dist) * force * temperature;
        var fy = (dy / dist) * force * temperature;
        n1.vx += fx;
        n1.vy += fy;
        n2.vx -= fx;
        n2.vy -= fy;
      }
    }

    /* spring attraction along edges */
    for (i = 0; i < edges.length; i++) {
      edge = edges[i];
      dx = edge.target.x - edge.source.x;
      dy = edge.target.y - edge.source.y;
      dist = Math.sqrt(dx * dx + dy * dy) || 1;
      force = (dist - SPRING_LENGTH) * SPRING_K * temperature;
      var sfx = (dx / dist) * force;
      var sfy = (dy / dist) * force;
      edge.source.vx += sfx;
      edge.source.vy += sfy;
      edge.target.vx -= sfx;
      edge.target.vy -= sfy;
    }

    /* gravity toward center */
    var cx = W / 2, cy = H / 2;
    for (i = 0; i < nodes.length; i++) {
      n1 = nodes[i];
      n1.vx += (cx - n1.x) * GRAVITY * temperature;
      n1.vy += (cy - n1.y) * GRAVITY * temperature;
    }

    /* integrate + damp */
    for (i = 0; i < nodes.length; i++) {
      n1 = nodes[i];
      if (n1 === dragging) {
        n1.vx = 0;
        n1.vy = 0;
        continue;
      }
      n1.vx *= DAMPING;
      n1.vy *= DAMPING;
      n1.x += n1.vx;
      n1.y += n1.vy;
      /* keep in bounds */
      n1.x = Math.max(NODE_RADIUS, Math.min(W - NODE_RADIUS, n1.x));
      n1.y = Math.max(NODE_RADIUS, Math.min(H - NODE_RADIUS, n1.y));
    }
  }

  /* ---- drawing ---- */
  function draw() {
    ctx.clearRect(0, 0, W, H);

    /* edges */
    ctx.lineWidth = 1.5;
    edges.forEach(function (e) {
      var dx = e.target.x - e.source.x;
      var dy = e.target.y - e.source.y;
      var dist = Math.sqrt(dx * dx + dy * dy) || 1;
      var ux = dx / dist, uy = dy / dist;

      /* line from source edge to target edge */
      var x1 = e.source.x + ux * NODE_RADIUS;
      var y1 = e.source.y + uy * NODE_RADIUS;
      var x2 = e.target.x - ux * NODE_RADIUS;
      var y2 = e.target.y - uy * NODE_RADIUS;

      ctx.strokeStyle = "#999";
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      /* arrowhead at target */
      var angle = Math.atan2(y2 - y1, x2 - x1);
      ctx.fillStyle = "#999";
      ctx.beginPath();
      ctx.moveTo(x2, y2);
      ctx.lineTo(
        x2 - ARROW_SIZE * Math.cos(angle - Math.PI / 6),
        y2 - ARROW_SIZE * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        x2 - ARROW_SIZE * Math.cos(angle + Math.PI / 6),
        y2 - ARROW_SIZE * Math.sin(angle + Math.PI / 6)
      );
      ctx.closePath();
      ctx.fill();
    });

    /* nodes */
    nodes.forEach(function (n) {
      ctx.fillStyle = scaleColors[n.scaleIdx] || "#888";
      ctx.beginPath();
      ctx.arc(n.x, n.y, NODE_RADIUS, 0, Math.PI * 2);
      ctx.fill();

      /* number inside circle */
      ctx.fillStyle = "#fff";
      ctx.font = "bold 11px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(n.number, n.x, n.y);

      /* label below */
      var label = n.name;
      if (label.length > MAX_LABEL_LEN) label = label.slice(0, MAX_LABEL_LEN - 1) + "\u2026";
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--color-text").trim() || "#2c2c2c";
      ctx.font = LABEL_FONT;
      ctx.fillText(label, n.x, n.y + NODE_RADIUS + 14);
    });
  }

  /* ---- animation loop ---- */
  function tick() {
    applyForces();
    draw();
    frame++;
    if (frame < TOTAL_FRAMES || dragging) {
      animId = requestAnimationFrame(tick);
    }
  }

  function restartIfSettled() {
    if (frame >= TOTAL_FRAMES && !animId) {
      /* just redraw without restarting physics */
      draw();
    }
  }

  /* ---- interaction ---- */
  function nodeAt(mx, my) {
    for (var i = nodes.length - 1; i >= 0; i--) {
      var n = nodes[i];
      var dx = mx - n.x, dy = my - n.y;
      if (dx * dx + dy * dy <= NODE_RADIUS * NODE_RADIUS) return n;
    }
    return null;
  }

  function canvasXY(e) {
    var rect = canvas.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  var dragStartPos = null;

  canvas.addEventListener("mousedown", function (e) {
    var pos = canvasXY(e);
    var hit = nodeAt(pos.x, pos.y);
    if (hit) {
      dragging = hit;
      dragStartPos = { x: pos.x, y: pos.y };
      /* restart animation if settled */
      if (frame >= TOTAL_FRAMES) {
        frame = TOTAL_FRAMES - 50;
        animId = requestAnimationFrame(tick);
      }
    }
  });

  canvas.addEventListener("mousemove", function (e) {
    var pos = canvasXY(e);
    if (dragging) {
      dragging.x = pos.x;
      dragging.y = pos.y;
      draw();
    }
    canvas.style.cursor = nodeAt(pos.x, pos.y) ? "pointer" : "default";
  });

  canvas.addEventListener("mouseup", function (e) {
    if (dragging && dragStartPos) {
      var pos = canvasXY(e);
      var dx = pos.x - dragStartPos.x, dy = pos.y - dragStartPos.y;
      /* if barely moved, treat as click → navigate */
      if (dx * dx + dy * dy < 9) {
        window.location.href = (window.ROOT_PREFIX || "") + "pattern/" + dragging.number + ".html";
      }
    }
    dragging = null;
    dragStartPos = null;
  });

  canvas.addEventListener("mouseleave", function () {
    dragging = null;
    dragStartPos = null;
  });

  window.addEventListener("resize", function () {
    resize();
    draw();
  });

  /* ---- init ---- */
  load();
})();
