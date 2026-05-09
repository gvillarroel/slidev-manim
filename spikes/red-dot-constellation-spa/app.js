const TOTAL_DURATION = 30_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 4_000 },
  { id: "search", label: "search for form", duration: 6_500 },
  { id: "tension", label: "tension", duration: 5_500 },
  { id: "transformation", label: "transformation", duration: 6_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");
const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const searchRing = document.getElementById("search-ring");
const searchDiamond = document.getElementById("search-diamond");
const searchPanel = document.getElementById("search-panel");
const searchPanelRect = document.getElementById("search-panel-rect");
const searchPanelAccent = document.getElementById("search-panel-accent");
const searchPanelDetail = document.getElementById("search-panel-detail");
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoMid = document.getElementById("search-echo-mid");
const searchEchoBottom = document.getElementById("search-echo-bottom");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const tensionGroup = document.getElementById("tension-group");
const shutterTop = document.getElementById("shutter-top");
const shutterBottom = document.getElementById("shutter-bottom");
const gateFrame = document.getElementById("gate-frame");
const pressureRing = document.getElementById("pressure-ring");

const transformRig = document.getElementById("transform-rig");
const futureGroup = document.getElementById("future-group");
const futureHub = document.getElementById("future-hub");
const transformGroup = document.getElementById("transform-group");
const transformRing = document.getElementById("transform-ring");
const transformRingSecondary = document.getElementById("transform-ring-secondary");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionAura = document.getElementById("resolution-aura");
const resolutionCoreRing = document.getElementById("resolution-core-ring");

const cards = [
  {
    slot: document.getElementById("slot-a"),
    connector: document.getElementById("connector-a"),
    card: document.getElementById("card-a"),
    accent: document.getElementById("card-a-accent"),
    detail: document.getElementById("card-a-detail"),
    center: { x: 1060, y: 290 },
  },
  {
    slot: document.getElementById("slot-b"),
    connector: document.getElementById("connector-b"),
    card: document.getElementById("card-b"),
    accent: document.getElementById("card-b-accent"),
    detail: document.getElementById("card-b-detail"),
    center: { x: 1220, y: 428 },
  },
  {
    slot: document.getElementById("slot-c"),
    connector: document.getElementById("connector-c"),
    card: document.getElementById("card-c"),
    accent: document.getElementById("card-c-accent"),
    detail: document.getElementById("card-c-detail"),
    center: { x: 1060, y: 622 },
  },
];

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  highlightRed: "#ffccd5",
  passiveGray: "#b5b5b5",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 430, y: 450 },
  searchTop: { x: 520, y: 300 },
  searchMid: { x: 660, y: 420 },
  searchBottom: { x: 560, y: 612 },
  gateEntry: { x: 760, y: 470 },
  gateCenter: { x: 860, y: 470 },
  gateExit: { x: 960, y: 470 },
  hubCenter: { x: 1060, y: 450 },
  finalCenter: { x: 760, y: 450 },
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

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 1.05) {
    const intensity = clamp((1.05 - viewportRatio) / 0.58, 0, 1);
    const scale = lerp(1.06, 1.32, intensity);
    const shiftY = lerp(-18, -72, intensity);
    sceneRoot.setAttribute(
      "transform",
      `translate(800 450) scale(${scale.toFixed(3)}) translate(-800 -450) translate(0 ${shiftY.toFixed(2)})`,
    );
    svg.dataset.layout = "portrait";
  } else {
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
}

function setOpacity(element, value) {
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
}

function setTransform(element, { x, y }, scaleX = 1, scaleY = 1) {
  element.setAttribute(
    "transform",
    `translate(${x} ${y}) scale(${scaleX} ${scaleY}) translate(${-x} ${-y})`,
  );
}

function setCircleCenter(element, { x, y }) {
  element.setAttribute("cx", x.toFixed(2));
  element.setAttribute("cy", y.toFixed(2));
}

function setRectY(element, y, height) {
  element.setAttribute("y", y.toFixed(2));
  element.setAttribute("height", height.toFixed(2));
}

function setRectX(element, x, width) {
  element.setAttribute("x", x.toFixed(2));
  element.setAttribute("width", width.toFixed(2));
}

function setStrokeColor(element, color) {
  element.setAttribute("stroke", color);
}

function setTrailProgress(fraction, opacity) {
  setTrailSegment(0, fraction, opacity);
}

function setTrailSegment(startFraction, endFraction, opacity) {
  const start = clamp(startFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const end = clamp(endFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const visible = Math.max(0, end - start);
  activeTrail.style.strokeDasharray = `${visible.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + visible + 120).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = `${(-start).toFixed(2)}`;
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

function updateStatus(info) {
  phaseLabel.textContent = info.phase.label;
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
  const clamped = clamp(amount, 0, 1);
  element.style.strokeDasharray = `${length.toFixed(2)}`;
  element.style.strokeDashoffset = `${((1 - clamped) * length).toFixed(2)}`;
}

function setGroupTranslation(group, xOffset) {
  group.setAttribute("transform", `translate(${xOffset.toFixed(2)} 0)`);
}

function setSearchPalette(activeIndex) {
  setStrokeColor(
    searchRing,
    activeIndex === 0 ? COLORS.primaryRed : activeIndex > 0 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  setStrokeColor(
    searchDiamond,
    activeIndex === 1 ? COLORS.primaryRed : activeIndex > 1 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  searchPanelRect.setAttribute(
    "stroke",
    activeIndex === 2 ? COLORS.primaryRed : activeIndex > 2 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  searchPanelAccent.setAttribute("stroke", activeIndex >= 2 ? COLORS.primaryRed : COLORS.lineGray);

  setStrokeColor(
    searchArcTop,
    activeIndex === 0 ? COLORS.primaryRed : activeIndex > 0 ? COLORS.mutedRed : COLORS.lineGray,
  );
  setStrokeColor(
    searchArcMid,
    activeIndex === 1 ? COLORS.primaryRed : activeIndex > 1 ? COLORS.mutedRed : COLORS.lineGray,
  );
  setStrokeColor(searchArcBottom, activeIndex >= 2 ? COLORS.primaryRed : COLORS.lineGray);
}

function resetScene() {
  applyDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setTrailProgress(0, 0);

  [
    searchRing,
    searchDiamond,
    searchPanel,
    searchEchoTop,
    searchEchoMid,
    searchEchoBottom,
    searchArcTop,
    searchArcMid,
    searchArcBottom,
    tensionGroup,
    futureGroup,
    transformGroup,
    resolutionGroup,
  ].forEach((element) => setOpacity(element, 0));

  setStrokeColor(searchRing, COLORS.passiveGray);
  setStrokeColor(searchDiamond, COLORS.passiveGray);
  searchPanelRect.setAttribute("stroke", COLORS.passiveGray);
  searchPanelAccent.setAttribute("stroke", COLORS.lineGray);
  searchPanelDetail.setAttribute("stroke", COLORS.lineGray);
  setStrokeColor(searchArcTop, COLORS.lineGray);
  setStrokeColor(searchArcMid, COLORS.lineGray);
  setStrokeColor(searchArcBottom, COLORS.lineGray);

  setRectY(shutterTop, 216, 156);
  setRectY(shutterBottom, 568, 156);
  shutterTop.setAttribute("opacity", "0.16");
  shutterBottom.setAttribute("opacity", "0.16");
  setRectX(gateFrame, 804, 108);
  pressureRing.setAttribute("r", "32");
  setOpacity(pressureRing, 0.22);

  futureHub.setAttribute("stroke", COLORS.passiveGray);
  setGroupTranslation(transformRig, 0);
  setOpacity(transformRing, 0);
  setOpacity(transformRingSecondary, 0);

  cards.forEach(({ slot, connector, card, accent, detail, center }) => {
    setOpacity(slot, 0);
    setOpacity(connector, 0);
    setOpacity(card, 0);
    accent.setAttribute("stroke", COLORS.primaryRed);
    detail.setAttribute("stroke", COLORS.lineGray);
    setTransform(card, center, 0.9, 0.9);
    applyConnectorGrowth(connector, 0);
  });

  setOpacity(resolutionAura, 0);
  setOpacity(resolutionCoreRing, 0);
  resolutionAura.setAttribute("r", "150");
  resolutionCoreRing.setAttribute("r", "74");
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const dotOpacity = 1;
  const haloPulse = 0.22 + pulseWave(progress, 1.3) * 0.18;

  applyDot(points.start, lerp(15, 19, eased), lerp(52, 82, eased), dotOpacity, haloPulse * 0.8);
  setOpacity(narrativeSpine, 0.12 + clamp(progress * 0.32, 0, 0.1));
  setTrailProgress(0, 0);

  setOpacity(searchRing, 0.18 + clamp(progress * 0.16, 0, 0.12));
  setOpacity(searchDiamond, 0.16 + clamp(progress * 0.14, 0, 0.1));
  setOpacity(searchPanel, 0.14 + clamp(progress * 0.12, 0, 0.08));
  setOpacity(searchArcTop, 0.14 + clamp(progress * 0.12, 0, 0.08));
  setOpacity(searchArcMid, 0.11 + clamp(progress * 0.1, 0, 0.07));
  setOpacity(searchArcBottom, 0.09 + clamp(progress * 0.08, 0, 0.05));

  setOpacity(tensionGroup, 0.12 + clamp(progress * 0.12, 0, 0.08));
  setOpacity(futureGroup, 0.2 + clamp(progress * 0.12, 0, 0.1));
  cards.forEach(({ slot }, index) => {
    setOpacity(slot, 0.18 + progress * 0.05 - index * 0.006);
  });
}

function renderSearch(progress) {
  let position = points.searchTop;
  let stretchX = 1;
  let stretchY = 1;
  let activeIndex = 0;

  if (progress < 0.28) {
    const t = easeInOut(progress / 0.28);
    position = mixPoint(points.start, points.searchTop, t);
    stretchX = lerp(1, 0.9, t);
    stretchY = lerp(1, 1.1, t);
    activeIndex = 0;
  } else if (progress < 0.58) {
    const t = easeInOut((progress - 0.28) / 0.30);
    position = mixPoint(points.searchTop, points.searchMid, t);
    stretchX = lerp(0.9, 1.08, t);
    stretchY = lerp(1.08, 0.92, t);
    activeIndex = 1;
  } else if (progress < 0.84) {
    const t = easeInOut((progress - 0.58) / 0.26);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    stretchX = lerp(1.08, 0.94, t);
    stretchY = lerp(0.92, 1.12, t);
    activeIndex = 2;
  } else {
    const t = easeInOut((progress - 0.84) / 0.16);
    position = mixPoint(points.searchBottom, points.gateEntry, t);
    stretchX = lerp(0.94, 1.08, t);
    stretchY = lerp(1.12, 0.92, t);
    activeIndex = 3;
  }

  applyDot(position, 19, 84, 1, 0.34 + pulseWave(progress, 2.2) * 0.16, stretchX, stretchY);
  setOpacity(narrativeSpine, 0.26);
  setTrailProgress(0.54 * progress, 0.82);

  setOpacity(searchRing, 0.7);
  setOpacity(searchDiamond, 0.62);
  setOpacity(searchPanel, 0.56);
  setOpacity(searchArcTop, 0.58);
  setOpacity(searchArcMid, 0.58);
  setOpacity(searchArcBottom, 0.58);
  setSearchPalette(activeIndex);

  setOpacity(searchEchoTop, progress >= 0.24 ? 0.42 : 0);
  setOpacity(searchEchoMid, progress >= 0.52 ? 0.38 : 0);
  setOpacity(searchEchoBottom, progress >= 0.80 ? 0.34 : 0);

  setOpacity(futureGroup, 0.1);
  cards.forEach(({ slot }) => {
    setOpacity(slot, 0.1);
  });
}

function renderTension(progress) {
  const travel = progress < 0.26
    ? mixPoint(points.gateEntry, points.gateCenter, easeInOut(progress / 0.26))
    : progress < 0.74
      ? points.gateCenter
      : mixPoint(points.gateCenter, points.gateExit, easeInOut((progress - 0.74) / 0.26));

  const squeezeStrength = progress < 0.32
    ? easeOut(progress / 0.32)
    : progress < 0.72
      ? 1
      : 1 - easeInOut((progress - 0.72) / 0.28);
  const pressurePulse = progress > 0.3 && progress < 0.72
    ? (pulseWave((progress - 0.3) / 0.42, 2.6) - 0.5) * 12
    : 0;

  const gap = lerp(236, 78, squeezeStrength) + pressurePulse;
  const topY = 470 - gap / 2 - 156;
  const bottomY = 470 + gap / 2;
  const gateWidth = lerp(120, 74, squeezeStrength) - pressurePulse * 0.32;

  applyDot(
    travel,
    19,
    lerp(86, 108, squeezeStrength),
    1,
    0.38 + squeezeStrength * 0.1,
    lerp(1.02, 1.82, squeezeStrength),
    lerp(0.98, 0.64, squeezeStrength),
  );
  setOpacity(narrativeSpine, 0.18);
  setTrailSegment(0.36, lerp(0.54, 0.75, progress), 0.8);

  setOpacity(searchRing, 0.14);
  setOpacity(searchDiamond, 0.14);
  setOpacity(searchPanel, 0.12);
  setOpacity(searchEchoTop, 0.14);
  setOpacity(searchEchoMid, 0.12);
  setOpacity(searchEchoBottom, 0.1);
  setOpacity(searchArcTop, 0.1);
  setOpacity(searchArcMid, 0.1);
  setOpacity(searchArcBottom, 0.1);

  setOpacity(tensionGroup, 1);
  setRectY(shutterTop, topY, 156);
  setRectY(shutterBottom, bottomY, 156);
  setRectX(gateFrame, 858 - gateWidth / 2, gateWidth);
  shutterTop.setAttribute("opacity", (0.18 + squeezeStrength * 0.16).toFixed(3));
  shutterBottom.setAttribute("opacity", (0.18 + squeezeStrength * 0.16).toFixed(3));
  pressureRing.setAttribute("r", lerp(30, 42, squeezeStrength).toFixed(2));
  setOpacity(pressureRing, 0.2 + squeezeStrength * 0.22);

  setOpacity(futureGroup, 0.12);
  cards.forEach(({ slot }) => setOpacity(slot, 0.12));
}

function renderTransformation(progress) {
  const entryMove = progress < 0.22
    ? mixPoint(points.gateExit, points.hubCenter, easeOut(progress / 0.22))
    : points.hubCenter;
  const systemShift = lerp(0, -190, easeOut(clamp((progress - 0.18) / 0.72, 0, 1)));
  const slotReveal = clamp((progress - 0.04) / 0.28, 0, 1);
  const ringGrow = clamp((progress - 0.12) / 0.26, 0, 1);
  const connectorGrow = clamp((progress - 0.24) / 0.42, 0, 1);
  const cardsGrow = clamp((progress - 0.42) / 0.38, 0, 1);
  const focusPosition = { x: entryMove.x + systemShift, y: entryMove.y };

  applyDot(
    focusPosition,
    lerp(19, 16.5, progress),
    lerp(96, 124, ringGrow),
    1,
    0.28 + pulseWave(progress, 2.3) * 0.12,
  );
  setOpacity(narrativeSpine, 0.06);
  setTrailSegment(0.52, lerp(0.75, 0.9, progress), 0.22 + (1 - connectorGrow) * 0.08);

  setOpacity(searchRing, 0);
  setOpacity(searchDiamond, 0);
  setOpacity(searchPanel, 0);
  setOpacity(searchEchoTop, 0);
  setOpacity(searchEchoMid, 0);
  setOpacity(searchEchoBottom, 0);
  setOpacity(searchArcTop, 0);
  setOpacity(searchArcMid, 0);
  setOpacity(searchArcBottom, 0);
  setOpacity(tensionGroup, 0.16 + (1 - progress) * 0.08);

  setGroupTranslation(transformRig, systemShift);
  setOpacity(futureGroup, 0.14 + slotReveal * 0.34);
  setOpacity(transformGroup, 1);
  transformRing.setAttribute("r", lerp(42, 88, easeOut(ringGrow)).toFixed(2));
  transformRingSecondary.setAttribute("r", lerp(72, 132, easeOut(ringGrow)).toFixed(2));
  setOpacity(transformRing, ringGrow * 0.9);
  setOpacity(transformRingSecondary, ringGrow * 0.46);

  cards.forEach(({ slot, connector, card, center }, index) => {
    const cardProgress = clamp(cardsGrow - index * 0.12, 0, 1);
    setOpacity(slot, clamp(0.12 + slotReveal * 0.3 - cardProgress * 0.16, 0, 0.38));
    setOpacity(connector, connectorGrow * 0.92);
    applyConnectorGrowth(connector, connectorGrow);
    setOpacity(card, cardProgress);
    setTransform(
      card,
      center,
      lerp(0.9, 1, easeOut(cardProgress)),
      lerp(0.9, 1, easeOut(cardProgress)),
    );
  });
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(-190, points.finalCenter.x - points.hubCenter.x, settle);
  const haloPulse = 0.2 + pulseWave(progress, 1.7) * 0.08;

  applyDot(
    { x: points.hubCenter.x + shift, y: points.finalCenter.y },
    16.5,
    lerp(116, 86, progress),
    1,
    haloPulse,
  );
  setOpacity(narrativeSpine, 0);
  setTrailProgress(0, 0);

  setOpacity(tensionGroup, clamp(0.14 - easeOut(progress) * 0.2, 0, 1));
  setGroupTranslation(transformRig, shift);
  setOpacity(futureGroup, 0.18 - progress * 0.18);
  setOpacity(transformGroup, 1);

  cards.forEach(({ slot, connector, card, center }) => {
    setOpacity(slot, clamp(0.12 - progress * 0.14, 0, 1));
    setOpacity(connector, 0.72);
    applyConnectorGrowth(connector, 1);
    setOpacity(card, 1);
    setTransform(card, { x: center.x + shift, y: center.y }, 1, 1);
  });

  transformRing.setAttribute("r", lerp(88, 60, settle).toFixed(2));
  transformRingSecondary.setAttribute("r", lerp(132, 118, settle).toFixed(2));
  setOpacity(transformRing, 0.16 + (1 - settle) * 0.2);
  setOpacity(transformRingSecondary, 0.1 + pulseWave(progress, 1.3) * 0.06);

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionAura, 0.28);
  setOpacity(resolutionCoreRing, 0.18);
  const center = { x: points.hubCenter.x + shift, y: points.finalCenter.y };
  setCircleCenter(resolutionAura, center);
  setCircleCenter(resolutionCoreRing, center);
  resolutionAura.setAttribute("r", lerp(156, 140, progress).toFixed(2));
  resolutionCoreRing.setAttribute("r", lerp(88, 70, progress).toFixed(2));
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
  updateStatus(info);
  state.currentElapsed = elapsed;
}

function setPlaying(nextPlaying) {
  if (state.playing === nextPlaying) {
    return;
  }
  if (nextPlaying) {
    state.startAt = performance.now();
  } else {
    state.elapsedBeforePause = state.currentElapsed;
  }
  state.playing = nextPlaying;
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

window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    if (state.playing) {
      state.elapsedBeforePause = state.currentElapsed;
      setPlaying(false);
    } else {
      state.startAt = performance.now();
      setPlaying(true);
    }
  } else if (event.key.toLowerCase() === "r") {
    resetTimeline();
    if (!state.playing) {
      setPlaying(true);
    }
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
