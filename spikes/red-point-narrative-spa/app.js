const DURATION_SECONDS = 30;
const ACTS = [
  { label: "appearance", progress: 0.12 },
  { label: "search", progress: 0.24 },
  { label: "tension", progress: 0.58 },
  { label: "transformation", progress: 0.78 },
  { label: "resolution", progress: 0.95 },
];

const POINTS = {
  spawn: { x: 24, y: 56 },
  searchA: { x: 37, y: 35 },
  searchB: { x: 50, y: 63 },
  searchC: { x: 65, y: 36 },
  gate: { x: 52.5, y: 50 },
  emerge: { x: 60, y: 49 },
  anchor: { x: 66, y: 43 },
  nodeA: { x: 46, y: 31 },
  nodeB: { x: 60, y: 29 },
  nodeC: { x: 73, y: 34 },
  nodeD: { x: 59, y: 67 },
  nodeE: { x: 43, y: 58 },
};

const root = document.documentElement;
const actLabel = document.getElementById("act-label");
const ticks = Array.from(document.querySelectorAll(".timeline-tick"));
const trails = [
  document.querySelector(".trail-a"),
  document.querySelector(".trail-b"),
  document.querySelector(".trail-c"),
];
const probeLine = document.querySelector(".probe-line");
const nodes = {
  a: document.querySelector(".node-a"),
  b: document.querySelector(".node-b"),
  c: document.querySelector(".node-c"),
  d: document.querySelector(".node-d"),
  e: document.querySelector(".node-e"),
};
const lines = {
  a: document.querySelector(".line-a"),
  b: document.querySelector(".line-b"),
  c: document.querySelector(".line-c"),
  d: document.querySelector(".line-d"),
};

const state = {
  progress: 0,
  playing: true,
  startTime: performance.now(),
  rafId: 0,
  completionResolver: null,
  completionPromise: null,
};

state.completionPromise = new Promise((resolve) => {
  state.completionResolver = resolve;
});

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function lerp(start, end, amount) {
  return start + (end - start) * amount;
}

function mixPoint(a, b, amount) {
  return {
    x: lerp(a.x, b.x, amount),
    y: lerp(a.y, b.y, amount),
  };
}

function range(progress, start, end) {
  return clamp((progress - start) / (end - start), 0, 1);
}

function easeInOutCubic(value) {
  if (value < 0.5) {
    return 4 * value * value * value;
  }
  return 1 - Math.pow(-2 * value + 2, 3) / 2;
}

function easeOutCubic(value) {
  return 1 - Math.pow(1 - value, 3);
}

function easeInCubic(value) {
  return value * value * value;
}

function wave(progress, cycles = 1) {
  return (Math.sin(progress * Math.PI * 2 * cycles) + 1) / 2;
}

function lineBetween(from, to, opacity, draw) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const length = Math.hypot(dx, dy);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  return {
    left: `${from.x}%`,
    top: `${from.y}%`,
    width: `${length}%`,
    angle: `${angle}deg`,
    opacity,
    draw,
  };
}

function activeSearchTarget(progress) {
  if (progress < 0.34) {
    return POINTS.searchA;
  }
  if (progress < 0.68) {
    return POINTS.searchB;
  }
  return POINTS.searchC;
}

function dotStateFor(progress) {
  if (progress <= 0.22) {
    const t = easeOutCubic(range(progress, 0, 0.22));
    const position = mixPoint(
      { x: POINTS.spawn.x - 4, y: POINTS.spawn.y + 1.5 },
      POINTS.spawn,
      t,
    );
    return {
      ...position,
      scaleX: lerp(0.24, 1, t),
      scaleY: lerp(0.24, 1, t),
      opacity: lerp(0.08, 1, t),
      rotation: `${lerp(-28, 0, t)}deg`,
      haloScale: lerp(0.6, 1.1, t),
      haloOpacity: lerp(0.08, 0.28, t),
      ringScale: lerp(0.6, 1.05, t),
      ringOpacity: lerp(0.2, 0.04, t),
      pulseAOpacity: 0,
      pulseBOpacity: 0,
      pulseAScale: 0.5,
      pulseBScale: 0.5,
    };
  }

  if (progress <= 0.46) {
    const t = range(progress, 0.22, 0.46);
    let position;
    if (t < 0.34) {
      position = mixPoint(POINTS.spawn, POINTS.searchA, easeInOutCubic(t / 0.34));
    } else if (t < 0.68) {
      position = mixPoint(POINTS.searchA, POINTS.searchB, easeInOutCubic((t - 0.34) / 0.34));
    } else {
      position = mixPoint(POINTS.searchB, POINTS.searchC, easeInOutCubic((t - 0.68) / 0.32));
    }
    const wobble = wave(t, 2.4);
    return {
      ...position,
      scaleX: lerp(0.94, 1.18, wobble),
      scaleY: lerp(1.12, 0.9, wobble),
      opacity: 1,
      rotation: `${lerp(-20, 18, wobble)}deg`,
      haloScale: lerp(0.92, 1.28, wobble),
      haloOpacity: 0.22,
      ringScale: lerp(0.9, 1.25, wobble),
      ringOpacity: 0.12,
      pulseAOpacity: 0.18,
      pulseBOpacity: 0.08,
      pulseAScale: lerp(0.82, 1.18, wobble),
      pulseBScale: lerp(1.08, 1.52, wobble),
    };
  }

  if (progress <= 0.66) {
    const t = range(progress, 0.46, 0.66);
    const position = mixPoint(POINTS.searchC, POINTS.gate, easeInOutCubic(t));
    const pressure = wave(clamp(t * 1.25, 0, 1), 1.5);
    return {
      ...position,
      scaleX: lerp(1, 1.7, easeInCubic(t)),
      scaleY: lerp(1, 0.74, easeInCubic(t)),
      opacity: 1,
      rotation: `${lerp(8, 0, t)}deg`,
      haloScale: lerp(1.05, 1.32, t),
      haloOpacity: lerp(0.22, 0.3, pressure),
      ringScale: lerp(1.08, 1.34, t),
      ringOpacity: lerp(0.12, 0.18, pressure),
      pulseAOpacity: lerp(0.14, 0.24, pressure),
      pulseBOpacity: lerp(0.05, 0.14, pressure),
      pulseAScale: lerp(0.96, 1.08, t),
      pulseBScale: lerp(1.22, 1.4, t),
    };
  }

  if (progress <= 0.84) {
    const t = range(progress, 0.66, 0.84);
    const position = mixPoint(POINTS.gate, POINTS.anchor, easeOutCubic(t));
    return {
      ...position,
      scaleX: lerp(1.7, 1.02, t),
      scaleY: lerp(0.74, 1.02, t),
      opacity: 1,
      rotation: `${lerp(0, -6, t)}deg`,
      haloScale: lerp(1.32, 1.24, t),
      haloOpacity: lerp(0.34, 0.24, t),
      ringScale: lerp(1.3, 1.58, t),
      ringOpacity: lerp(0.18, 0.3, t),
      pulseAOpacity: lerp(0.26, 0.1, t),
      pulseBOpacity: lerp(0.16, 0.22, t),
      pulseAScale: lerp(1.08, 1.34, t),
      pulseBScale: lerp(1.28, 1.62, t),
    };
  }

  const t = range(progress, 0.84, 1);
  return {
    ...POINTS.anchor,
    scaleX: 1,
    scaleY: 1,
    opacity: 1,
    rotation: "0deg",
    haloScale: lerp(1.24, 1.18, t),
    haloOpacity: 0.24,
    ringScale: lerp(1.58, 1.22, t),
    ringOpacity: lerp(0.3, 0.08, t),
    pulseAOpacity: lerp(0.08, 0, t),
    pulseBOpacity: lerp(0.22, 0.04, t),
    pulseAScale: lerp(1.34, 1.6, t),
    pulseBScale: lerp(1.62, 1.92, t),
  };
}

function setStyles(entries) {
  for (const [name, value] of Object.entries(entries)) {
    root.style.setProperty(name, value);
  }
}

function updateLine(element, config) {
  element.style.left = config.left;
  element.style.top = config.top;
  element.style.width = config.width;
  element.style.opacity = String(config.opacity);
  element.style.transform = `translateY(-50%) rotate(${config.angle}) scaleX(${config.draw})`;
}

function placeNode(element, point) {
  element.style.left = `${point.x}%`;
  element.style.top = `${point.y}%`;
}

function actFor(progress) {
  if (progress < 0.22) return "appearance";
  if (progress < 0.46) return "search";
  if (progress < 0.66) return "tension";
  if (progress < 0.84) return "transformation";
  return "resolution";
}

function updateTicks(progress) {
  let activeIndex = 0;
  for (let index = 0; index < ACTS.length; index += 1) {
    if (progress >= ACTS[index].progress) {
      activeIndex = index;
    }
  }
  ticks.forEach((tick, index) => {
    tick.classList.toggle("is-active", index <= activeIndex);
  });
}

function render(progress) {
  const p = clamp(progress, 0, 1);
  const dot = dotStateFor(p);
  const search = range(p, 0.22, 0.46);
  const tension = range(p, 0.46, 0.66);
  const transform = range(p, 0.66, 0.84);
  const resolve = range(p, 0.84, 1);

  setStyles({
    "--point-x": `${dot.x}%`,
    "--point-y": `${dot.y}%`,
    "--point-scale-x": dot.scaleX.toFixed(3),
    "--point-scale-y": dot.scaleY.toFixed(3),
    "--point-opacity": dot.opacity.toFixed(3),
    "--point-rotation": dot.rotation,
    "--halo-scale": dot.haloScale.toFixed(3),
    "--halo-opacity": dot.haloOpacity.toFixed(3),
    "--ring-scale": dot.ringScale.toFixed(3),
    "--ring-opacity": dot.ringOpacity.toFixed(3),
    "--pulse-a-opacity": dot.pulseAOpacity.toFixed(3),
    "--pulse-b-opacity": dot.pulseBOpacity.toFixed(3),
    "--pulse-a-scale": dot.pulseAScale.toFixed(3),
    "--pulse-b-scale": dot.pulseBScale.toFixed(3),
    "--circle-opacity": (0.56 * clamp(1 - Math.abs(search - 0.18) / 0.28, 0, 1)).toFixed(3),
    "--square-opacity": (0.58 * clamp(1 - Math.abs(search - 0.5) / 0.3, 0, 1)).toFixed(3),
    "--arc-opacity": (0.56 * clamp(1 - Math.abs(search - 0.82) / 0.28, 0, 1)).toFixed(3),
    "--gate-opacity": (
      lerp(0, 1, easeOutCubic(tension))
      * (1 - easeInCubic(clamp(range(p, 0.7, 0.88), 0, 1)))
    ).toFixed(3),
    "--gate-gap": `${lerp(28, 7.5, easeInOutCubic(tension))}%`,
    "--lane-opacity": (
      lerp(0, 0.72, clamp(search * 0.65 + tension + transform * 0.45, 0, 1))
      * (1 - easeOutCubic(resolve))
    ).toFixed(3),
    "--constellation-opacity": lerp(0, 1, clamp(transform * 1.15 + resolve, 0, 1)).toFixed(3),
    "--line-opacity": lerp(0, 1, clamp(transform * 1.15 + resolve, 0, 1)).toFixed(3),
    "--line-scale": easeOutCubic(clamp(transform * 1.2, 0, 1)).toFixed(3),
    "--node-opacity": lerp(0, 1, clamp(transform * 1.2 + resolve, 0, 1)).toFixed(3),
    "--trail-opacity-a": (search > 0.06 ? 0.24 : 0).toFixed(3),
    "--trail-opacity-b": (search > 0.12 ? 0.17 : 0).toFixed(3),
    "--trail-opacity-c": (search > 0.18 ? 0.11 : 0).toFixed(3),
    "--background-shift": `${lerp(-18, 22, p)}%`,
  });

  actLabel.textContent = actFor(p);
  updateTicks(p);

  [0.03, 0.06, 0.09].forEach((offset, index) => {
    const trailPoint = dotStateFor(clamp(p - offset, 0, 1));
    trails[index].style.left = `${trailPoint.x}%`;
    trails[index].style.top = `${trailPoint.y}%`;
  });

  const activeTarget = activeSearchTarget(search);
  const probeOpacity = search > 0 ? 0.38 : 0;
  updateLine(probeLine, lineBetween({ x: dot.x, y: dot.y }, activeTarget, probeOpacity, clamp(search * 1.4, 0, 1)));
  probeLine.style.opacity = String(probeOpacity * (1 - clamp(tension * 1.4, 0, 1)));

  placeNode(nodes.a, POINTS.nodeA);
  placeNode(nodes.b, POINTS.nodeB);
  placeNode(nodes.c, POINTS.nodeC);
  placeNode(nodes.d, POINTS.nodeD);
  placeNode(nodes.e, POINTS.nodeE);

  const draw = easeOutCubic(clamp(transform * 1.08 + resolve, 0, 1));
  updateLine(lines.a, lineBetween(POINTS.nodeA, POINTS.nodeB, 0.7, draw));
  updateLine(lines.b, lineBetween(POINTS.nodeB, POINTS.anchor, 0.9, draw));
  updateLine(lines.c, lineBetween(POINTS.anchor, POINTS.nodeD, 0.82, draw));
  updateLine(lines.d, lineBetween(POINTS.nodeE, POINTS.anchor, 0.64, draw));
}

function tick(now) {
  if (!state.playing) {
    return;
  }

  const elapsed = (now - state.startTime) / 1000;
  state.progress = clamp(elapsed / DURATION_SECONDS, 0, 1);
  render(state.progress);

  if (state.progress >= 1) {
    state.playing = false;
    if (state.completionResolver) {
      state.completionResolver(true);
      state.completionResolver = null;
    }
    return;
  }

  state.rafId = requestAnimationFrame(tick);
}

function play(fromProgress = state.progress) {
  cancelAnimationFrame(state.rafId);
  state.progress = clamp(fromProgress, 0, 1);
  state.startTime = performance.now() - state.progress * DURATION_SECONDS * 1000;
  state.playing = true;
  state.rafId = requestAnimationFrame(tick);
}

function pause() {
  state.playing = false;
  cancelAnimationFrame(state.rafId);
}

function setProgress(progress) {
  pause();
  state.progress = clamp(progress, 0, 1);
  render(state.progress);
}

function getState() {
  return {
    progress: state.progress,
    act: actFor(state.progress),
    durationSeconds: DURATION_SECONDS,
  };
}

render(0);
play(0);

window.redPointNarrative = {
  acts: ACTS,
  durationSeconds: DURATION_SECONDS,
  getState,
  pause,
  play,
  setProgress,
  waitForComplete: () => state.completionPromise,
};
