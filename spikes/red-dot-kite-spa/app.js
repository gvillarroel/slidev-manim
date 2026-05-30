const TOTAL_DURATION = 35_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
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
const destinationGuide = document.getElementById("destination-guide");

const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const searchGuideReturn = document.getElementById("search-guide-return");
const candidateLozenge = document.getElementById("candidate-lozenge");
const candidateSpar = document.getElementById("candidate-spar");
const candidateKite = document.getElementById("candidate-kite");

const anchorGroup = document.getElementById("anchor-group");
const tensionLines = document.getElementById("tension-lines");
const pressureDiamond = document.getElementById("pressure-diamond");
const pressureSpar = document.getElementById("pressure-spar");
const pressureHalo = document.getElementById("pressure-halo");

const kiteUnderlay = document.getElementById("kite-underlay");
const kiteShell = document.getElementById("kite-shell");
const kiteTrace = document.getElementById("kite-trace");
const kiteSpine = document.getElementById("kite-spine");
const spineTrace = document.getElementById("spine-trace");
const wingBraceLeft = document.getElementById("wing-brace-left");
const wingBraceRight = document.getElementById("wing-brace-right");
const tailLink = document.getElementById("tail-link");
const tailTrace = document.getElementById("tail-trace");
const tailNodeTop = document.getElementById("tail-node-top");
const tailNodeBottom = document.getElementById("tail-node-bottom");

const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const KITE_TRACE_LENGTH = kiteTrace.getTotalLength();
const SPINE_TRACE_LENGTH = spineTrace.getTotalLength();
const TAIL_TRACE_LENGTH = tailTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
  dark: "#4f4f4f",
  mutedRed: "#c97a89",
};

const points = {
  start: { x: 340, y: 450 },
  approach: { x: 600, y: 450 },
  candidateA: { x: 700, y: 360 },
  candidateB: { x: 820, y: 312 },
  candidateC: { x: 920, y: 372 },
  preTension: { x: 892, y: 420 },
  center: { x: 820, y: 430 },
};

const candidateBase = {
  lozenge: { x: 700, y: 360, rotation: -6 },
  spar: { x: 820, y: 312, rotation: 0 },
  kite: { x: 920, y: 372, rotation: 6 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "180 96 430 840",
  search: "500 88 380 824",
  tension: "646 104 362 784",
  transformation: "652 86 364 808",
  resolution: "648 52 372 848",
};

const PORTRAIT_LAYOUT = {
  appearance: { x: 440, y: 452, scale: 1.02 },
  search: { x: 824, y: 430, scale: 1.08 },
  tension: { x: 820, y: 432, scale: 1.12 },
  transformation: { x: 820, y: 430, scale: 1.1 },
  resolution: { x: 820, y: 430, scale: 1.04 },
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

function pointOnKite(progress) {
  const length = clamp(progress, 0, 1) * KITE_TRACE_LENGTH;
  const point = kiteTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function setCandidateState(element, base, mode) {
  if (mode === "active") {
    setGroupTransform(element, base.x, base.y, 1.02, base.rotation);
    setOpacity(element, 1);
    return;
  }
  if (mode === "visited") {
    setGroupTransform(element, base.x, base.y, 0.94, base.rotation);
    setOpacity(element, 0.3);
    return;
  }
  if (mode === "faint") {
    setGroupTransform(element, base.x, base.y, 0.9, base.rotation);
    setOpacity(element, 0.14);
    return;
  }
  setGroupTransform(element, base.x, base.y, 0.86, base.rotation);
  setOpacity(element, 0);
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
    appearance: 62,
    search: 54,
    tension: 16,
    transformation: 6,
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
  svg.setAttribute("viewBox", PORTRAIT_VIEWBOXES[phaseId] ?? FULL_VIEWBOX);
}

function applyLayout(phaseId = "appearance") {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    const layout = PORTRAIT_LAYOUT[phaseId] ?? PORTRAIT_LAYOUT.appearance;
    layoutRoot.setAttribute(
      "transform",
      `translate(${layout.x} ${layout.y}) scale(${layout.scale}) translate(${-layout.x} ${-layout.y})`,
    );
    svg.dataset.layout = "portrait";
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
  } else {
    layoutRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  }
  applyFraming(phaseId);
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);
  setOpacity(destinationGuide, 0);

  [searchGuideA, searchGuideB, searchGuideC, searchGuideReturn].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setCandidateState(candidateLozenge, candidateBase.lozenge, "hidden");
  setCandidateState(candidateSpar, candidateBase.spar, "hidden");
  setCandidateState(candidateKite, candidateBase.kite, "hidden");

  setOpacity(anchorGroup, 0);
  setOpacity(tensionLines, 0);
  pressureDiamond.setAttribute(
    "transform",
    `translate(${points.center.x} ${points.center.y}) scale(1) translate(${-points.center.x} ${-points.center.y})`,
  );
  pressureSpar.setAttribute(
    "transform",
    `translate(${points.center.x} ${points.center.y}) scale(1) translate(${-points.center.x} ${-points.center.y})`,
  );
  setOpacity(pressureDiamond, 0);
  setOpacity(pressureSpar, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(kiteUnderlay, 0);
  setOpacity(kiteShell, 0);
  setPathWindow(kiteTrace, KITE_TRACE_LENGTH, 0, 0);
  setOpacity(kiteSpine, 0);
  setPathWindow(spineTrace, SPINE_TRACE_LENGTH, 0, 0);
  setOpacity(wingBraceLeft, 0);
  setOpacity(wingBraceRight, 0);
  setOpacity(tailLink, 0);
  setPathWindow(tailTrace, TAIL_TRACE_LENGTH, 0, 0);
  setOpacity(tailNodeTop, 0);
  setOpacity(tailNodeBottom, 0);

  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.approach, eased * 0.9);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.15) * 0.16,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.18) * 1.24, 0, 0.22));
  setOpacity(destinationGuide, clamp((progress - 0.18) * 1.28, 0, 0.22));

  const preview = clamp((progress - 0.46) * 1.5, 0, 1);
  setCandidateState(candidateLozenge, candidateBase.lozenge, preview > 0 ? "faint" : "hidden");
  setCandidateState(candidateSpar, candidateBase.spar, preview > 0.22 ? "faint" : "hidden");
  setCandidateState(candidateKite, candidateBase.kite, preview > 0.42 ? "faint" : "hidden");
  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(searchGuideB, clamp((preview - 0.14) * 1.3, 0, 0.18));
  setOpacity(searchGuideC, clamp((preview - 0.3) * 1.4, 0, 0.16));
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.26, from: points.approach, to: points.candidateA },
    { start: 0.26, end: 0.54, from: points.candidateA, to: points.candidateB },
    { start: 0.54, end: 0.8, from: points.candidateB, to: points.candidateC },
    { start: 0.8, end: 1, from: points.candidateC, to: points.preTension },
  ]);

  setDot(position, 18, 86, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.18, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, lerp(180, 72, progress), lerp(0.08, 0.02, progress));
  setOpacity(destinationGuide, 0.16);

  searchGuideA.setAttribute("stroke", progress < 0.28 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.28 && progress < 0.58 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.58 && progress < 0.84 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideReturn.setAttribute("stroke", progress >= 0.84 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.34);
  setOpacity(searchGuideB, 0.3);
  setOpacity(searchGuideC, 0.28);
  setOpacity(searchGuideReturn, 0.24);

  const lozengeMode = progress < 0.28 ? "active" : "visited";
  const sparMode = progress < 0.28 ? "faint" : progress < 0.58 ? "active" : "visited";
  const kiteMode = progress < 0.58 ? "faint" : progress < 0.86 ? "active" : "visited";
  setCandidateState(candidateLozenge, candidateBase.lozenge, lozengeMode);
  setCandidateState(candidateSpar, candidateBase.spar, sparMode);
  setCandidateState(candidateKite, candidateBase.kite, kiteMode);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const collapse = easeInOut(clamp(progress / 0.78, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.3, 0, 1));
  const position = mixPoint(points.preTension, points.center, easeInOut(travel));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(86, 120, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.46, collapse),
    lerp(1, 1.84, collapse),
  );
  setOpacity(narrativeSpine, lerp(0.1, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0.05 * residue);
  setOpacity(destinationGuide, lerp(0.16, 0.06, progress));

  [searchGuideA, searchGuideB, searchGuideC, searchGuideReturn].forEach((guide) => setOpacity(guide, 0.18 * residue));
  setCandidateState(candidateLozenge, candidateBase.lozenge, "visited");
  setCandidateState(candidateSpar, candidateBase.spar, "visited");
  setCandidateState(candidateKite, candidateBase.kite, "visited");
  setOpacity(candidateLozenge, 0.14 * residue);
  setOpacity(candidateSpar, 0.14 * residue);
  setOpacity(candidateKite, 0.16 * residue);

  setOpacity(anchorGroup, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(tensionLines, clamp((progress - 0.04) * 1.7, 0, 0.96));
  const diamondScale = lerp(1.04, 0.56, collapse);
  pressureDiamond.setAttribute(
    "transform",
    `translate(${points.center.x} ${points.center.y}) scale(${diamondScale.toFixed(3)}) translate(${-points.center.x} ${-points.center.y})`,
  );
  pressureSpar.setAttribute(
    "transform",
    `translate(${points.center.x} ${points.center.y}) scale(${diamondScale.toFixed(3)}) translate(${-points.center.x} ${-points.center.y})`,
  );
  setOpacity(pressureDiamond, clamp((progress - 0.06) * 1.8, 0, 0.82));
  setOpacity(pressureSpar, clamp((progress - 0.1) * 1.8, 0, 0.74));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.7, 0, 0.4));
  setOpacity(kiteUnderlay, clamp((progress - 0.56) * 0.5, 0, 0.14));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.82, 0, 1));
  const position = pointOnKite(routeProgress);
  const spineProgress = clamp((progress - 0.28) / 0.3, 0, 1);
  const braceProgress = clamp((progress - 0.44) / 0.22, 0, 1);
  const tailProgress = clamp((progress - 0.54) / 0.28, 0, 1);
  const tensionFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);
  setOpacity(destinationGuide, lerp(0.14, 0.02, progress));

  setOpacity(anchorGroup, 0.84 * tensionFade);
  setOpacity(tensionLines, 0.92 * tensionFade);
  setOpacity(pressureDiamond, 0.8 * tensionFade);
  setOpacity(pressureSpar, 0.72 * tensionFade);
  setOpacity(pressureHalo, 0.34 * tensionFade);
  setOpacity(kiteUnderlay, lerp(0.18, 0.08, progress));

  setOpacity(kiteShell, lerp(0.22, 1, routeProgress));
  setPathWindow(kiteTrace, KITE_TRACE_LENGTH, KITE_TRACE_LENGTH * routeProgress, 1);
  setOpacity(kiteSpine, clamp((progress - 0.2) * 1.5, 0, 0.9));
  setPathWindow(spineTrace, SPINE_TRACE_LENGTH, SPINE_TRACE_LENGTH * spineProgress, 0.84 * spineProgress);
  setOpacity(wingBraceLeft, braceProgress * 0.9);
  setOpacity(wingBraceRight, braceProgress * 0.9);
  setOpacity(tailLink, tailProgress * 0.88);
  setPathWindow(tailTrace, TAIL_TRACE_LENGTH, TAIL_TRACE_LENGTH * tailProgress, 0.78 * tailProgress);
  setOpacity(tailNodeTop, clamp((tailProgress - 0.14) * 1.3, 0, 0.82));
  setOpacity(tailNodeBottom, clamp((tailProgress - 0.3) * 1.3, 0, 0.76));
  setOpacity(resolutionHalo, clamp((progress - 0.7) * 1.4, 0, 0.12));
  setOpacity(resolutionFrame, clamp((progress - 0.78) * 1.4, 0, 0.18));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const traceFade = lerp(0.24, 0.12, settle);
  const haloPulse = 0.18 + pulseWave(progress, 1.4) * 0.06;

  setDot(points.center, 16, 88, 1, haloPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);
  setOpacity(destinationGuide, 0);
  setOpacity(anchorGroup, 0);
  setOpacity(tensionLines, 0);
  setOpacity(pressureDiamond, 0);
  setOpacity(pressureSpar, 0);
  setOpacity(pressureHalo, 0);
  setOpacity(kiteUnderlay, 0);

  setOpacity(kiteShell, 0.94);
  setPathWindow(kiteTrace, KITE_TRACE_LENGTH, KITE_TRACE_LENGTH, traceFade);
  setOpacity(kiteSpine, 0.84);
  setPathWindow(spineTrace, SPINE_TRACE_LENGTH, SPINE_TRACE_LENGTH, 0.18);
  setOpacity(wingBraceLeft, 0.82);
  setOpacity(wingBraceRight, 0.82);
  setOpacity(tailLink, 0.74);
  setPathWindow(tailTrace, TAIL_TRACE_LENGTH, TAIL_TRACE_LENGTH, 0.14);
  setOpacity(tailNodeTop, 0.62);
  setOpacity(tailNodeBottom, 0.54);
  setOpacity(resolutionHalo, lerp(0.12, 0.22, settle));
  setOpacity(resolutionFrame, lerp(0.18, 0.64, settle));
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);
  applyLayout(info.phase.id);
  applySceneOffset(info.phase.id);

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

applyLayout("appearance");
window.addEventListener("resize", () => {
  const info = phaseForElapsed(state.currentElapsed);
  applyLayout(info.phase.id);
});
resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
