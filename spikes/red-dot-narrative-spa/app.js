const VIEWBOX = { width: 1600, height: 900 };
const TOTAL_DURATION = 30_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 6_000 },
  { id: "tension", label: "tension", duration: 5_500 },
  { id: "transformation", label: "transformation", duration: 6_000 },
  { id: "resolution", label: "resolution", duration: 7_500 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
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
const searchCardRect = searchCard.querySelector("rect");
const searchCardLead = searchCard.querySelectorAll("path")[0];
const searchCardTrail = searchCard.querySelectorAll("path")[1];
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoMid = document.getElementById("search-echo-mid");
const searchEchoBottom = document.getElementById("search-echo-bottom");
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
const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  highlightRed: "#ffccd5",
  passiveGray: "#b5b5b5",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 310, y: 450 },
  searchTop: { x: 486, y: 304 },
  searchMid: { x: 594, y: 448 },
  searchBottom: { x: 330, y: 606 },
  corridorEntry: { x: 730, y: 450 },
  corridorCenter: { x: 860, y: 450 },
  corridorExit: { x: 1010, y: 450 },
  transformCenter: { x: 1070, y: 450 },
  finalCenter: { x: 820, y: 450 },
  connectorA: { x: 980, y: 300 },
  connectorB: { x: 1270, y: 392 },
  connectorC: { x: 986, y: 628 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    sceneRoot.setAttribute(
      "transform",
      "translate(0 -56) translate(800 450) scale(1.16) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
}

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

function setTrailWindow(visibleLength, opacity) {
  const clampedLength = clamp(visibleLength, 0, ACTIVE_TRAIL_LENGTH);
  activeTrail.style.strokeDasharray = `${clampedLength.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + 240).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = "0";
  setOpacity(activeTrail, opacity);
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
  setTrailWindow(0, 0);

  [
    searchCircle,
    searchSquare,
    searchCard,
    searchEchoTop,
    searchEchoMid,
    searchEchoBottom,
    searchArcTop,
    searchArcMid,
    searchArcBottom,
  ].forEach((element) => {
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
  const dotOpacity = 0.68 + clamp(progress * 0.7, 0, 0.32);
  const haloPulse = 0.18 + pulseWave(progress, 1.2) * 0.18;
  const radius = lerp(14, 20, eased);
  const haloRadius = lerp(54, 84, eased);

  applyDot(points.start, radius, haloRadius, dotOpacity, haloPulse * dotOpacity);
  setOpacity(narrativeSpine, 0.18 + clamp(progress * 0.9, 0, 0.22));
  setTrailWindow(0, 0);

  setOpacity(searchCircle, 0.2 + clamp(progress * 0.45, 0, 0.18));
  setOpacity(searchSquare, 0.16 + clamp((progress - 0.08) * 0.46, 0, 0.16));
  setOpacity(searchCard, 0.12 + clamp((progress - 0.16) * 0.42, 0, 0.14));
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

  applyDot(position, 20, 68, 1, 0.3 + pulseWave(progress, 2.2) * 0.14, stretchX, stretchY);
  setOpacity(narrativeSpine, 0.28);
  setTrailWindow(150 + progress * 210, 0.78);

  setOpacity(searchCircle, 0.72);
  setOpacity(searchSquare, 0.64);
  setOpacity(searchCard, 0.56);
  setOpacity(searchArcTop, 0.62);
  setOpacity(searchArcMid, 0.62);
  setOpacity(searchArcBottom, 0.62);

  setStrokeColor(searchCircle, progress < 0.36 ? COLORS.primaryRed : COLORS.mutedRed);
  setStrokeColor(searchSquare, progress >= 0.36 && progress < 0.68 ? COLORS.primaryRed : progress >= 0.68 ? COLORS.mutedRed : COLORS.passiveGray);
  searchCardRect.setAttribute("stroke", progress >= 0.68 ? COLORS.primaryRed : progress >= 0.5 ? COLORS.mutedRed : COLORS.passiveGray);
  searchCardLead.setAttribute("stroke", COLORS.lineGray);
  searchCardTrail.setAttribute("stroke", COLORS.lineGray);

  setStrokeColor(searchArcTop, progress < 0.36 ? COLORS.primaryRed : COLORS.mutedRed);
  setStrokeColor(searchArcMid, progress >= 0.36 && progress < 0.68 ? COLORS.primaryRed : progress >= 0.68 ? COLORS.mutedRed : COLORS.lineGray);
  setStrokeColor(searchArcBottom, progress >= 0.68 ? COLORS.primaryRed : COLORS.lineGray);

  setOpacity(searchEchoTop, progress >= 0.34 ? 0.46 : 0);
  setOpacity(searchEchoMid, progress >= 0.56 ? 0.42 : 0);
  setOpacity(searchEchoBottom, progress >= 0.82 ? 0.38 : 0);
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
  const pressurePulse = progress > 0.3 && progress < 0.72
    ? (pulseWave((progress - 0.3) / 0.42, 2.4) - 0.5) * 10
    : 0;

  const gap = lerp(208, 70, squeezeStrength) + pressurePulse;
  const topY = 450 - gap / 2 - 126;
  const bottomY = 450 + gap / 2;
  const gateWidth = lerp(148, 82, squeezeStrength) - pressurePulse * 0.5;
  const dotScaleX = lerp(1.02, 1.86, squeezeStrength);
  const dotScaleY = lerp(0.98, 0.68, squeezeStrength);

  const residueFade = 1 - easeOut(clamp((progress - 0.08) / 0.42, 0, 1));
  const trailFade = 1 - easeOut(clamp((progress - 0.16) / 0.34, 0, 1));

  applyDot(travel, 20, lerp(84, 108, squeezeStrength), 1, 0.38 + squeezeStrength * 0.14, dotScaleX, dotScaleY);
  setOpacity(narrativeSpine, 0.1 * residueFade);
  setTrailWindow(470 + progress * 80, 0.62 * trailFade);

  setOpacity(searchCircle, 0.12 * residueFade);
  setOpacity(searchSquare, 0.12 * residueFade);
  setOpacity(searchCard, 0.12 * residueFade);
  setOpacity(searchEchoTop, 0.16 * residueFade);
  setOpacity(searchEchoMid, 0.14 * residueFade);
  setOpacity(searchEchoBottom, 0.12 * residueFade);
  setOpacity(searchArcTop, 0.1 * residueFade);
  setOpacity(searchArcMid, 0.1 * residueFade);
  setOpacity(searchArcBottom, 0.1 * residueFade);

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
  const systemShift = lerp(0, -92, easeOut(clamp((progress - 0.18) / 0.72, 0, 1)));
  const ringGrow = clamp((progress - 0.12) / 0.28, 0, 1);
  const connectorGrow = clamp((progress - 0.24) / 0.48, 0, 1);
  const cardsGrow = clamp((progress - 0.42) / 0.38, 0, 1);
  const focusPosition = { x: entryMove.x + systemShift, y: entryMove.y };

  applyDot(focusPosition, lerp(20, 17, progress), lerp(92, 126, ringGrow), 1, 0.28 + pulseWave(progress, 2.4) * 0.12);
  const corridorResidue = 1 - easeOut(clamp(progress / 0.22, 0, 1));

  setOpacity(narrativeSpine, 0);
  setTrailWindow(250, 0.14 * corridorResidue);

  setOpacity(searchCircle, 0.0);
  setOpacity(searchSquare, 0.0);
  setOpacity(searchCard, 0.0);
  setOpacity(searchEchoTop, 0.0);
  setOpacity(searchEchoMid, 0.0);
  setOpacity(searchEchoBottom, 0.0);
  setOpacity(searchArcTop, 0.0);
  setOpacity(searchArcMid, 0.0);
  setOpacity(searchArcBottom, 0.0);
  setOpacity(tensionGroup, 0.1 * (1 - easeOut(clamp(progress / 0.36, 0, 1))));

  setOpacity(transformGroup, 1);
  transformRing.setAttribute("r", lerp(46, 92, easeOut(ringGrow)).toFixed(2));
  transformRingSecondary.setAttribute("r", lerp(74, 138, easeOut(ringGrow)).toFixed(2));
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
  setGroupTranslation(transformGroup, systemShift);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(-92, points.finalCenter.x - points.transformCenter.x, settle);
  const haloPulse = 0.22 + pulseWave(progress, 1.8) * 0.1;

  applyDot({ x: points.transformCenter.x + shift, y: points.finalCenter.y }, 17, lerp(112, 84, progress), 1, haloPulse);
  setOpacity(narrativeSpine, 0);
  setTrailWindow(0, 0);

  setOpacity(tensionGroup, 0);
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

  transformRing.setAttribute("r", lerp(92, 58, settle).toFixed(2));
  transformRingSecondary.setAttribute("r", lerp(138, 120, settle).toFixed(2));
  setOpacity(transformRing, 0.16 + (1 - settle) * 0.24);
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
  const rawElapsed = state.playing
    ? state.elapsedBeforePause + (now - state.startAt)
    : state.elapsedBeforePause;
  const elapsed = CAPTURE_MODE ? clamp(rawElapsed, 0, TOTAL_DURATION) : rawElapsed % TOTAL_DURATION;

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
  seek(milliseconds) {
    const nextElapsed = ((milliseconds % TOTAL_DURATION) + TOTAL_DURATION) % TOTAL_DURATION;
    state.elapsedBeforePause = nextElapsed;
    state.currentElapsed = nextElapsed;
    state.startAt = performance.now();
    render(nextElapsed);
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

applyLayout();
window.addEventListener("resize", applyLayout);
resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
