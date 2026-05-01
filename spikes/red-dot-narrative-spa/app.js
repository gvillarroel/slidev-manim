const VIEWBOX = { width: 1600, height: 900 };
const TOTAL_DURATION = 30_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 6_000 },
  { id: "tension", label: "tension", duration: 5_500 },
  { id: "transformation", label: "transformation", duration: 6_000 },
  { id: "resolution", label: "resolution", duration: 7_500 },
];

const svg = document.getElementById("stage");
const phaseLabel = document.getElementById("phase-label");
const timelineFill = document.getElementById("timeline-fill");
const toggleButton = document.getElementById("toggle-button");
const replayButton = document.getElementById("replay-button");
const phaseDots = Array.from(document.querySelectorAll("[data-phase-dot]"));

const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");
const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const searchCircle = document.getElementById("search-circle");
const searchSquare = document.getElementById("search-square");
const searchCard = document.getElementById("search-card");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const tensionGroup = document.getElementById("tension-group");
const clampTop = document.getElementById("clamp-top");
const clampBottom = document.getElementById("clamp-bottom");
const clampGate = document.getElementById("clamp-gate");

const transformGroup = document.getElementById("transform-group");
const transformRing = document.getElementById("transform-ring");
const transformRingSecondary = document.getElementById("transform-ring-secondary");
const connectorA = document.getElementById("connector-a");
const connectorB = document.getElementById("connector-b");
const connectorC = document.getElementById("connector-c");
const cardA = document.getElementById("card-a");
const cardB = document.getElementById("card-b");
const cardC = document.getElementById("card-c");
const resolutionGroup = document.getElementById("resolution-group");
const resolutionAura = document.getElementById("resolution-aura");

const points = {
  start: { x: 220, y: 450 },
  searchTop: { x: 394, y: 308 },
  searchMid: { x: 462, y: 442 },
  searchBottom: { x: 452, y: 604 },
  corridorEntry: { x: 620, y: 470 },
  corridorCenter: { x: 780, y: 450 },
  corridorExit: { x: 980, y: 450 },
  transformCenter: { x: 1080, y: 450 },
  finalCenter: { x: 820, y: 450 },
  connectorA: { x: 964, y: 306 },
  connectorB: { x: 1258, y: 392 },
  connectorC: { x: 978, y: 620 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

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

function easeInOut(value) {
  return value < 0.5
    ? 4 * value * value * value
    : 1 - Math.pow(-2 * value + 2, 3) / 2;
}

function easeOut(value) {
  return 1 - Math.pow(1 - value, 3);
}

function pulseWave(progress, cycles = 1) {
  return (Math.sin(progress * Math.PI * 2 * cycles - Math.PI / 2) + 1) / 2;
}

function setOpacity(element, value) {
  element.setAttribute("opacity", value.toFixed(3));
}

function setTransform(element, { x, y }, scaleX = 1, scaleY = 1) {
  element.setAttribute("transform", `translate(${x} ${y}) scale(${scaleX} ${scaleY}) translate(${-x} ${-y})`);
}

function setCircleCenter(element, { x, y }) {
  element.setAttribute("cx", x.toFixed(2));
  element.setAttribute("cy", y.toFixed(2));
}

function setRectY(element, y, height) {
  element.setAttribute("y", y.toFixed(2));
  element.setAttribute("height", height.toFixed(2));
}

function setStrokeColor(element, color) {
  element.setAttribute("stroke", color);
}

function phaseForElapsed(elapsed) {
  let cursor = 0;
  for (let index = 0; index < PHASES.length; index += 1) {
    const phase = PHASES[index];
    const end = cursor + phase.duration;
    if (elapsed <= end) {
      return {
        phase,
        index,
        localElapsed: elapsed - cursor,
        localProgress: clamp((elapsed - cursor) / phase.duration, 0, 1),
        totalProgress: clamp(elapsed / TOTAL_DURATION, 0, 1),
      };
    }
    cursor = end;
  }

  const last = PHASES[PHASES.length - 1];
  return {
    phase: last,
    index: PHASES.length - 1,
    localElapsed: last.duration,
    localProgress: 1,
    totalProgress: 1,
  };
}

function updateHud(info) {
  phaseLabel.textContent = info.phase.label;
  timelineFill.style.width = `${(info.totalProgress * 100).toFixed(2)}%`;
  phaseDots.forEach((dot, index) => {
    dot.classList.toggle("is-active", index === info.index);
    dot.classList.toggle("is-complete", index < info.index);
  });
}

function applyDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1) {
  setCircleCenter(dotCore, position);
  setCircleCenter(dotHalo, position);
  dotCore.setAttribute("r", radius.toFixed(2));
  dotHalo.setAttribute("r", haloRadius.toFixed(2));
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  setTransform(dotCore, position, scaleX, scaleY);
  setTransform(dotHalo, position, scaleX, scaleY);
}

function applyConnectorGrowth(element, amount) {
  const length = element.getTotalLength();
  element.style.strokeDasharray = `${length}`;
  element.style.strokeDashoffset = `${(1 - clamp(amount, 0, 1)) * length}`;
}

function setGroupTranslation(group, xOffset) {
  group.setAttribute("transform", `translate(${xOffset.toFixed(2)} 0)`);
}

function resetScene() {
  applyDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setOpacity(activeTrail, 0);
  activeTrail.style.strokeDasharray = "0 1400";

  [searchCircle, searchSquare, searchCard, searchArcTop, searchArcMid, searchArcBottom].forEach((element) => {
    setOpacity(element, 0);
  });

  setOpacity(tensionGroup, 0);
  setRectY(clampTop, 248, 126);
  setRectY(clampBottom, 526, 126);
  clampGate.setAttribute("x", "730");
  clampGate.setAttribute("width", "120");

  setOpacity(transformGroup, 0);
  setOpacity(transformRing, 0);
  setOpacity(transformRingSecondary, 0);
  setOpacity(connectorA, 0);
  setOpacity(connectorB, 0);
  setOpacity(connectorC, 0);
  setOpacity(cardA, 0);
  setOpacity(cardB, 0);
  setOpacity(cardC, 0);
  setGroupTranslation(transformGroup, 0);

  setOpacity(resolutionGroup, 0);
  setOpacity(resolutionAura, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const dotOpacity = clamp(progress * 1.8, 0, 1);
  const haloPulse = 0.28 + pulseWave(progress, 1.2) * 0.22;
  const radius = lerp(4, 18, eased);
  const haloRadius = lerp(16, 78, eased);

  applyDot(points.start, radius, haloRadius, dotOpacity, haloPulse * dotOpacity);
  setOpacity(narrativeSpine, clamp((progress - 0.2) * 1.2, 0, 0.34));
  setOpacity(activeTrail, 0.0);

  setOpacity(searchCircle, clamp((progress - 0.42) * 1.6, 0, 0.4));
  setOpacity(searchSquare, clamp((progress - 0.5) * 1.6, 0, 0.32));
  setOpacity(searchCard, clamp((progress - 0.58) * 1.6, 0, 0.24));
}

function renderSearch(progress) {
  const segment = progress;
  let position = points.searchTop;
  let stretchX = 1;
  let stretchY = 1;

  if (segment < 0.3) {
    const t = easeInOut(segment / 0.3);
    position = mixPoint(points.start, points.searchTop, t);
    stretchX = lerp(1, 0.92, t);
    stretchY = lerp(1, 1.08, t);
  } else if (segment < 0.6) {
    const t = easeInOut((segment - 0.3) / 0.3);
    position = mixPoint(points.searchTop, points.searchMid, t);
    stretchX = lerp(0.9, 1.08, t);
    stretchY = lerp(1.1, 0.92, t);
  } else if (segment < 0.86) {
    const t = easeInOut((segment - 0.6) / 0.26);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    stretchX = lerp(1.08, 0.96, t);
    stretchY = lerp(0.9, 1.12, t);
  } else {
    const t = easeInOut((segment - 0.86) / 0.14);
    position = mixPoint(points.searchBottom, points.corridorEntry, t);
    stretchX = lerp(0.96, 1.08, t);
    stretchY = lerp(1.12, 0.92, t);
  }

  applyDot(position, 18, 74, 1, 0.34 + pulseWave(progress, 2.2) * 0.18, stretchX, stretchY);
  setOpacity(narrativeSpine, 0.28);
  setOpacity(activeTrail, 0.85);
  activeTrail.style.strokeDasharray = `${160 + progress * 280} 1400`;

  setOpacity(searchCircle, 0.66);
  setOpacity(searchSquare, 0.58);
  setOpacity(searchCard, 0.52);
  setOpacity(searchArcTop, 0.56);
  setOpacity(searchArcMid, 0.56);
  setOpacity(searchArcBottom, 0.56);

  const activeRed = "#9e1b32";
  const passiveGray = "#b5b5b5";
  setStrokeColor(searchCircle, progress < 0.36 ? activeRed : passiveGray);
  setStrokeColor(searchSquare, progress >= 0.36 && progress < 0.68 ? activeRed : passiveGray);
  searchCard.querySelector("rect").setAttribute("stroke", progress >= 0.68 ? activeRed : passiveGray);
}

function renderTension(progress) {
  const travel = progress < 0.28
    ? mixPoint(points.corridorEntry, points.corridorCenter, easeInOut(progress / 0.28))
    : progress < 0.76
      ? mixPoint(points.corridorCenter, points.corridorCenter, 1)
      : mixPoint(points.corridorCenter, points.corridorExit, easeInOut((progress - 0.76) / 0.24));

  const squeezeStrength = progress < 0.3
    ? easeOut(progress / 0.3)
    : progress < 0.72
      ? 1
      : 1 - easeInOut((progress - 0.72) / 0.28);

  const gap = lerp(186, 78, squeezeStrength);
  const topY = 450 - gap / 2 - 126;
  const bottomY = 450 + gap / 2;
  const gateWidth = lerp(160, 94, squeezeStrength);
  const dotScaleX = lerp(1.02, 1.7, squeezeStrength);
  const dotScaleY = lerp(0.98, 0.72, squeezeStrength);

  applyDot(travel, 18, lerp(76, 96, squeezeStrength), 1, 0.36 + squeezeStrength * 0.14, dotScaleX, dotScaleY);
  setOpacity(narrativeSpine, 0.16);
  setOpacity(activeTrail, 0.92);
  activeTrail.style.strokeDasharray = `${500 + progress * 260} 1400`;

  setOpacity(searchCircle, 0.12);
  setOpacity(searchSquare, 0.12);
  setOpacity(searchCard, 0.12);
  setOpacity(searchArcTop, 0.1);
  setOpacity(searchArcMid, 0.1);
  setOpacity(searchArcBottom, 0.1);

  setOpacity(tensionGroup, 1);
  setRectY(clampTop, topY, 126);
  setRectY(clampBottom, bottomY, 126);
  clampGate.setAttribute("x", (790 - gateWidth / 2).toFixed(2));
  clampGate.setAttribute("width", gateWidth.toFixed(2));
}

function renderTransformation(progress) {
  const entryMove = progress < 0.2
    ? mixPoint(points.corridorExit, points.transformCenter, easeOut(progress / 0.2))
    : points.transformCenter;
  const ringGrow = clamp((progress - 0.12) / 0.28, 0, 1);
  const connectorGrow = clamp((progress - 0.24) / 0.48, 0, 1);
  const cardsGrow = clamp((progress - 0.42) / 0.38, 0, 1);
  const trailAmount = 780 + connectorGrow * 240;

  applyDot(entryMove, lerp(18, 16, progress), lerp(86, 120, ringGrow), 1, 0.26 + pulseWave(progress, 2.4) * 0.12);
  setOpacity(narrativeSpine, 0.08);
  setOpacity(activeTrail, 0.42);
  activeTrail.style.strokeDasharray = `${trailAmount} 1400`;

  setOpacity(searchCircle, 0.0);
  setOpacity(searchSquare, 0.0);
  setOpacity(searchCard, 0.0);
  setOpacity(searchArcTop, 0.0);
  setOpacity(searchArcMid, 0.0);
  setOpacity(searchArcBottom, 0.0);
  setOpacity(tensionGroup, 0.24);

  setOpacity(transformGroup, 1);
  transformRing.setAttribute("r", lerp(40, 88, easeOut(ringGrow)).toFixed(2));
  transformRingSecondary.setAttribute("r", lerp(62, 132, easeOut(ringGrow)).toFixed(2));
  setOpacity(transformRing, ringGrow * 0.92);
  setOpacity(transformRingSecondary, ringGrow * 0.48);

  [connectorA, connectorB, connectorC].forEach((connector) => {
    setOpacity(connector, connectorGrow * 0.95);
    applyConnectorGrowth(connector, connectorGrow);
  });

  [cardA, cardB, cardC].forEach((card, index) => {
    const cardProgress = clamp(cardsGrow - index * 0.12, 0, 1);
    setOpacity(card, cardProgress);
    const center = index === 0 ? points.connectorA : index === 1 ? points.connectorB : points.connectorC;
    setTransform(card, center, lerp(0.92, 1, easeOut(cardProgress)), lerp(0.92, 1, easeOut(cardProgress)));
  });
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, points.finalCenter.x - points.transformCenter.x, settle);
  const haloPulse = 0.22 + pulseWave(progress, 1.8) * 0.1;

  applyDot({ x: points.transformCenter.x + shift, y: points.finalCenter.y }, 16, lerp(104, 82, progress), 1, haloPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(activeTrail, 0);

  setOpacity(tensionGroup, 1 - easeOut(progress) * 0.96);
  setOpacity(transformGroup, 1);
  setGroupTranslation(transformGroup, shift);

  [connectorA, connectorB, connectorC].forEach((connector) => {
    setOpacity(connector, 0.72);
    applyConnectorGrowth(connector, 1);
  });

  [cardA, cardB, cardC].forEach((card) => {
    setOpacity(card, 1);
    const baseCenter = card === cardA
      ? points.connectorA
      : card === cardB
        ? points.connectorB
        : points.connectorC;
    setTransform(card, { x: baseCenter.x + shift, y: baseCenter.y }, 1, 1);
  });

  transformRing.setAttribute("r", lerp(88, 56, settle).toFixed(2));
  transformRingSecondary.setAttribute("r", lerp(132, 118, settle).toFixed(2));
  setOpacity(transformRing, 0.18 + (1 - settle) * 0.22);
  setOpacity(transformRingSecondary, 0.1 + pulseWave(progress, 1.4) * 0.08);

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionAura, 0.34);
  setCircleCenter(resolutionAura, { x: points.transformCenter.x + shift, y: points.finalCenter.y });
  resolutionAura.setAttribute("r", lerp(158, 142, progress).toFixed(2));
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);

  if (info.phase.id === "appearance") {
    renderAppearance(info.localProgress);
  } else if (info.phase.id === "search") {
    renderSearch(info.localProgress);
  } else if (info.phase.id === "tension") {
    renderTension(info.localProgress);
  } else if (info.phase.id === "transformation") {
    renderTransformation(info.localProgress);
  } else {
    renderResolution(info.localProgress);
  }

  svg.dataset.phase = info.phase.id;
  updateHud(info);
  state.currentElapsed = elapsed;
}

function setPlaying(nextPlaying) {
  if (state.playing === nextPlaying) return;
  if (nextPlaying) {
    state.startAt = performance.now();
  } else {
    state.elapsedBeforePause = state.currentElapsed;
  }
  state.playing = nextPlaying;
  toggleButton.textContent = nextPlaying ? "pause" : "play";
  toggleButton.setAttribute("aria-label", nextPlaying ? "Pause narrative" : "Play narrative");
}

function resetTimeline() {
  state.elapsedBeforePause = 0;
  state.currentElapsed = 0;
  state.startAt = performance.now();
  render(0);
}

function tick(now) {
  const elapsed = state.playing
    ? (state.elapsedBeforePause + (now - state.startAt)) % TOTAL_DURATION
    : state.elapsedBeforePause;

  if (state.playing) {
    state.currentElapsed = elapsed;
  }

  render(elapsed);
  requestAnimationFrame(tick);
}

toggleButton.addEventListener("click", () => {
  if (state.playing) {
    state.elapsedBeforePause = state.currentElapsed;
    setPlaying(false);
  } else {
    state.startAt = performance.now();
    setPlaying(true);
  }
});

replayButton.addEventListener("click", () => {
  resetTimeline();
  if (!state.playing) {
    setPlaying(true);
  }
});

window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    toggleButton.click();
  } else if (event.key.toLowerCase() === "r") {
    replayButton.click();
  }
});

window.__RED_DOT_APP = {
  phases: PHASES,
  duration: TOTAL_DURATION,
  reset() {
    resetTimeline();
  },
  pause() {
    state.elapsedBeforePause = state.currentElapsed;
    setPlaying(false);
  },
  play() {
    state.startAt = performance.now();
    setPlaying(true);
  },
  getState() {
    const info = phaseForElapsed(state.currentElapsed);
    return {
      currentElapsed: state.currentElapsed,
      totalDuration: TOTAL_DURATION,
      phase: info.phase.id,
      totalProgress: info.totalProgress,
      localProgress: info.localProgress,
      playing: state.playing,
    };
  },
};

resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
