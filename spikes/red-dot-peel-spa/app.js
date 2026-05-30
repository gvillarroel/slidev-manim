const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateTab = document.getElementById("candidate-tab");
const candidateSlot = document.getElementById("candidate-slot");
const candidateCorner = document.getElementById("candidate-corner");
const panelShell = document.getElementById("panel-shell");
const windowBase = document.getElementById("window-base");
const windowTrace = document.getElementById("window-trace");
const revealTrack = document.getElementById("reveal-track");
const seamGuide = document.getElementById("seam-guide");
const creaseLine = document.getElementById("crease-line");
const flapSlot = document.getElementById("flap-slot");
const flapShadow = document.getElementById("flap-shadow");
const flapFront = document.getElementById("flap-front");
const pressureHalo = document.getElementById("pressure-halo");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const WINDOW_TRACE_LENGTH = windowTrace.getTotalLength();
const REVEAL_TRACK_LENGTH = revealTrack.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 556, y: 450 },
  candidateTab: { x: 650, y: 392 },
  candidateSlot: { x: 828, y: 350 },
  candidateCorner: { x: 1000, y: 390 },
  seamApproach: { x: 946, y: 394 },
  seam: { x: 896, y: 374 },
  center: { x: 820, y: 450 },
};

const panel = {
  baseTop: { x: 862, y: 322 },
  baseRight: { x: 936, y: 396 },
  closedTip: { x: 936, y: 322 },
  tensionTip: { x: 914, y: 306 },
  openTip: { x: 814, y: 290 },
  settleTip: { x: 844, y: 308 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
  looping: true,
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

function segmentedPoint(progress, segments) {
  for (const segment of segments) {
    if (progress <= segment.end) {
      const local = clamp((progress - segment.start) / (segment.end - segment.start), 0, 1);
      return mixPoint(segment.from, segment.to, easeInOut(local));
    }
  }
  return segments[segments.length - 1].to;
}

function setOpacity(element, value) {
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
}

function setCircleCenter(element, point) {
  element.setAttribute("cx", point.x.toFixed(2));
  element.setAttribute("cy", point.y.toFixed(2));
}

function setGroupTransform(element, x, y, scale = 1, rotate = 0) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scale.toFixed(3)})`,
  );
}

function setDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1) {
  setCircleCenter(dotCore, position);
  setCircleCenter(dotHalo, position);
  dotCore.setAttribute("r", radius.toFixed(2));
  dotHalo.setAttribute("r", haloRadius.toFixed(2));
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  dotCore.setAttribute(
    "transform",
    `translate(${position.x} ${position.y}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-position.x} ${-position.y})`,
  );
  dotHalo.setAttribute(
    "transform",
    `translate(${position.x} ${position.y}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-position.x} ${-position.y})`,
  );
}

function setPathWindow(element, totalLength, visibleLength, opacity) {
  const clamped = clamp(visibleLength, 0, totalLength);
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 200).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function pointOnRevealTrack(progress) {
  const length = clamp(progress, 0, 1) * REVEAL_TRACK_LENGTH;
  const point = revealTrack.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function setFlap(tip, opacity, shadowOpacity) {
  const shadowTip = { x: tip.x + 14, y: tip.y + 16 };
  flapFront.setAttribute(
    "points",
    `${panel.baseTop.x},${panel.baseTop.y} ${panel.baseRight.x},${panel.baseRight.y} ${tip.x.toFixed(2)},${tip.y.toFixed(2)}`,
  );
  flapShadow.setAttribute(
    "points",
    `${panel.baseTop.x},${panel.baseTop.y} ${panel.baseRight.x},${panel.baseRight.y} ${shadowTip.x.toFixed(2)},${shadowTip.y.toFixed(2)}`,
  );
  setOpacity(flapFront, opacity);
  setOpacity(flapShadow, shadowOpacity);
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

function updatePhaseLabel(info) {
  phaseLabel.textContent = info.phase.label;
}

function applySceneOffset(phaseId) {
  const offsets = {
    appearance: 14,
    search: 24,
    tension: 10,
    transformation: 0,
    resolution: 0,
  };
  const offsetY = offsets[phaseId] ?? 0;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 156, y: 120, width: 760, height: 720 },
    search: { x: 500, y: 110, width: 620, height: 720 },
    tension: { x: 624, y: 124, width: 452, height: 720 },
    transformation: { x: 592, y: 54, width: 524, height: 780 },
    resolution: { x: 602, y: 92, width: 496, height: 780 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -10) translate(800 450) scale(1) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
  } else {
    layoutRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  }
  svg.setAttribute("viewBox", FULL_VIEWBOX);
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateTab, points.candidateTab.x, points.candidateTab.y, 1, -3);
  setGroupTransform(candidateSlot, points.candidateSlot.x, points.candidateSlot.y, 1, 0);
  setGroupTransform(candidateCorner, points.candidateCorner.x, points.candidateCorner.y, 1, 4);
  [candidateTab, candidateSlot, candidateCorner].forEach((element) => setOpacity(element, 0));

  setOpacity(panelShell, 0);
  setOpacity(windowBase, 0);
  setPathWindow(windowTrace, WINDOW_TRACE_LENGTH, 0, 0);
  setOpacity(seamGuide, 0);
  setOpacity(creaseLine, 0);
  setOpacity(flapSlot, 0);
  setFlap(panel.closedTip, 0, 0);
  setOpacity(pressureHalo, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);
  const preview = clamp((progress - 0.42) * 1.7, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));

  setOpacity(panelShell, 0.05 + preview * 0.06);
  setOpacity(windowBase, 0.04 + preview * 0.06);
  setOpacity(seamGuide, 0.04 + preview * 0.05);
  setOpacity(flapSlot, preview * 0.08);
  setOpacity(candidateTab, preview * 0.1);
  setOpacity(candidateSlot, preview * 0.08);
  setOpacity(candidateCorner, preview * 0.08);
  setFlap(panel.closedTip, preview * 0.12, preview * 0.04);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.candidateTab },
    { start: 0.28, end: 0.56, from: points.candidateTab, to: points.candidateSlot },
    { start: 0.56, end: 0.84, from: points.candidateSlot, to: points.candidateCorner },
    { start: 0.84, end: 1, from: points.candidateCorner, to: points.seamApproach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.22, 0.06, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.04, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.24 + revealA * 0.2);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateTab, points.candidateTab.x, points.candidateTab.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateSlot, points.candidateSlot.x, points.candidateSlot.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateCorner, points.candidateCorner.x, points.candidateCorner.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 4);
  setOpacity(candidateTab, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateSlot, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateCorner, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(panelShell, 0.08 + progress * 0.08);
  setOpacity(windowBase, 0.06 + progress * 0.08);
  setOpacity(seamGuide, 0.08 + progress * 0.1);
  setOpacity(flapSlot, 0.1 + progress * 0.08);
  setFlap(panel.closedTip, 0.08, 0.02);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.seamApproach, points.seam, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.76, 0, 1);
  const flapEase = easeInOut(clamp(progress / 0.72, 0, 1));
  const flapTip = mixPoint(panel.closedTip, panel.tensionTip, flapEase);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.56, compression),
    lerp(1, 1.74, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const tabPosition = mixPoint(points.candidateTab, { x: 760, y: 390 }, collapse);
  const slotPosition = mixPoint(points.candidateSlot, { x: 838, y: 356 }, collapse);
  const cornerPosition = mixPoint(points.candidateCorner, { x: 910, y: 350 }, collapse);
  setGroupTransform(candidateTab, tabPosition.x, tabPosition.y, lerp(0.96, 0.74, collapse), -6);
  setGroupTransform(candidateSlot, slotPosition.x, slotPosition.y, lerp(0.96, 0.76, collapse), 0);
  setGroupTransform(candidateCorner, cornerPosition.x, cornerPosition.y, lerp(0.95, 0.72, collapse), 8);
  setOpacity(candidateTab, lerp(0.3, 0.04, collapse));
  setOpacity(candidateSlot, lerp(0.34, 0.06, collapse));
  setOpacity(candidateCorner, lerp(1, 0.16, collapse));

  setOpacity(panelShell, 0.94);
  setOpacity(windowBase, 0.16 + progress * 0.08);
  setPathWindow(windowTrace, WINDOW_TRACE_LENGTH, 0, 0);
  setOpacity(seamGuide, clamp((progress - 0.04) * 1.7, 0, 0.9));
  setOpacity(creaseLine, clamp((progress - 0.08) * 1.5, 0, 0.34));
  setOpacity(flapSlot, clamp((progress - 0.08) * 1.5, 0, 0.28));
  setFlap(flapTip, clamp((progress - 0.06) * 1.6, 0, 1), clamp((progress - 0.1) * 1.5, 0, 0.18));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp((progress - 0.08) / 0.84, 0, 1));
  const position = pointOnRevealTrack(routeProgress);
  const flapOpen = easeInOut(clamp(progress / 0.82, 0, 1));
  const flapTip = mixPoint(panel.tensionTip, panel.openTip, flapOpen);
  const traceProgress = clamp((progress - 0.2) / 0.56, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(panelShell, 0.98);
  setOpacity(windowBase, lerp(0.18, 0.3, routeProgress));
  setPathWindow(windowTrace, WINDOW_TRACE_LENGTH, WINDOW_TRACE_LENGTH * traceProgress, 0.92 * traceProgress);
  setOpacity(seamGuide, lerp(0.72, 0.06, progress));
  setOpacity(creaseLine, lerp(0.34, 0.42, progress));
  setOpacity(flapSlot, clamp(0.28 - progress * 0.42, 0, 1));
  setFlap(flapTip, 1, lerp(0.18, 0.34, progress));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.36, 0, 1));

  setOpacity(candidateTab, 0);
  setOpacity(candidateSlot, 0);
  setOpacity(candidateCorner, clamp(0.12 - progress * 0.18, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(resolutionHalo, clamp((progress - 0.62) * 1.5, 0, 0.18));
  setOpacity(resolutionFrame, clamp((progress - 0.78) * 1.6, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;
  const flapTip = mixPoint(panel.openTip, panel.settleTip, settle);

  setDot(points.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(panelShell, lerp(0.98, 0.92, settle));
  setOpacity(windowBase, lerp(0.3, 0.22, settle));
  setPathWindow(windowTrace, WINDOW_TRACE_LENGTH, WINDOW_TRACE_LENGTH, lerp(0.92, 0.2, settle));
  setOpacity(seamGuide, 0);
  setOpacity(creaseLine, lerp(0.42, 0.3, settle));
  setOpacity(flapSlot, 0);
  setFlap(flapTip, lerp(1, 0.86, settle), lerp(0.34, 0.18, settle));
  setOpacity(pressureHalo, 0);

  [candidateTab, candidateSlot, candidateCorner].forEach((element) => setOpacity(element, 0));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(resolutionHalo, lerp(0.18, 0.28, settle));
  setOpacity(resolutionFrame, lerp(0.24, 0.66, settle));
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);
  applySceneOffset(info.phase.id);
  applyFraming(info.phase.id);

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

  updatePhaseLabel(info);
  svg.dataset.phase = info.phase.id;
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
  let elapsed = state.elapsedBeforePause;
  if (state.playing) {
    const rawElapsed = state.elapsedBeforePause + (now - state.startAt);
    if (state.looping) {
      elapsed = rawElapsed % TOTAL_DURATION;
    } else {
      elapsed = Math.min(rawElapsed, TOTAL_DURATION - 1);
      if (rawElapsed >= TOTAL_DURATION) {
        state.playing = false;
        state.elapsedBeforePause = elapsed;
      }
    }
  }

  state.currentElapsed = elapsed;
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
  setLooping(looping) {
    state.looping = Boolean(looping);
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
      looping: state.looping,
    };
  },
};

applyLayout();
window.addEventListener("resize", applyLayout);
resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
