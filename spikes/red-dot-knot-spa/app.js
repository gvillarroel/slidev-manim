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
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");
const crossingTop = document.getElementById("crossing-top");
const crossingBottom = document.getElementById("crossing-bottom");
const gateLeft = document.getElementById("gate-left");
const gateRight = document.getElementById("gate-right");
const gateHalo = document.getElementById("gate-halo");
const knotBase = document.getElementById("knot-base");
const knotActive = document.getElementById("knot-active");
const slotLeft = document.getElementById("slot-left");
const slotRight = document.getElementById("slot-right");
const slotBottom = document.getElementById("slot-bottom");
const anchorLeft = document.getElementById("anchor-left");
const anchorRight = document.getElementById("anchor-right");
const anchorBottom = document.getElementById("anchor-bottom");
const memoryArc = document.getElementById("memory-arc");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const KNOT_LENGTH = knotActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 560, y: 450 },
  candidateA: { x: 640, y: 334 },
  candidateB: { x: 1020, y: 338 },
  candidateC: { x: 760, y: 636 },
  gate: { x: 820, y: 450 },
};

const system = {
  left: { x: 650, y: 360 },
  right: { x: 1012, y: 352 },
  bottom: { x: 742, y: 620 },
  settleLeft: { x: 670, y: 376 },
  settleRight: { x: 990, y: 372 },
  settleBottom: { x: 760, y: 596 },
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

function pointOnKnot(progress) {
  const length = clamp(progress, 0, 1) * KNOT_LENGTH;
  const point = knotActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function anchorState(progress, threshold) {
  return clamp((progress - threshold) / 0.14, 0, 1);
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
    appearance: 18,
    search: 24,
    tension: 16,
    transformation: 12,
    resolution: -8,
  };
  const offsetY = offsets[phaseId] ?? -8;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 132, y: 150, width: 1080, height: 620 },
    search: { x: 158, y: 170, width: 1120, height: 600 },
    tension: { x: 360, y: 156, width: 900, height: 620 },
    transformation: { x: 408, y: 154, width: 840, height: 620 },
    resolution: { x: 448, y: 164, width: 780, height: 600 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -24) translate(800 450) scale(1.03) translate(-800 -450)",
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

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, 1, 0);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, 1, 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, 1, 0);
  [candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  [crossingTop, crossingBottom, gateLeft, gateRight, gateHalo].forEach((element) => setOpacity(element, 0));
  setGroupTransform(gateLeft, points.gate.x - 72, points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + 72, points.gate.y, 1, 0);

  [slotLeft, slotRight, slotBottom].forEach((element) => setOpacity(element, 0));
  setGroupTransform(slotLeft, system.left.x, system.left.y, 1, 0);
  setGroupTransform(slotRight, system.right.x, system.right.y, 1, 0);
  setGroupTransform(slotBottom, system.bottom.x, system.bottom.y, 1, 0);

  [anchorLeft, anchorRight, anchorBottom].forEach((element) => setOpacity(element, 0));
  setGroupTransform(anchorLeft, system.left.x, system.left.y, 1, 0);
  setGroupTransform(anchorRight, system.right.x, system.right.y, 1, 0);
  setGroupTransform(anchorBottom, system.bottom.x, system.bottom.y, 1, 0);

  setOpacity(knotBase, 0);
  setPathWindow(knotActive, KNOT_LENGTH, 0, 0);
  setOpacity(memoryArc, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRing, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  const preview = clamp((progress - 0.46) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.16);
  setOpacity(candidateA, preview * 0.12);
  setOpacity(candidateB, preview * 0.08);
  setOpacity(candidateC, preview * 0.06);
  setOpacity(crossingTop, preview * 0.1);
  setOpacity(crossingBottom, preview * 0.1);
  setOpacity(gateLeft, preview * 0.12);
  setOpacity(gateRight, preview * 0.12);
  setOpacity(gateHalo, preview * 0.12);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.candidateA },
    { start: 0.28, end: 0.58, from: points.candidateA, to: points.candidateB },
    { start: 0.58, end: 0.84, from: points.candidateB, to: points.candidateC },
    { start: 0.84, end: 1, from: points.candidateC, to: { x: 864, y: 518 } },
  ]);

  setDot(position, 18, 86, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.12, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.24) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.52) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.24 + revealA * 0.2);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.26);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, lerp(0.88, activeA ? 1.05 : 0.96, revealA), 0);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, lerp(0.84, activeC ? 1.04 : 0.95, revealC), 0);
  setOpacity(candidateA, activeA ? 1 : revealA * 0.34 + 0.16);
  setOpacity(candidateB, activeB ? 1 : revealB * 0.34 + 0.16);
  setOpacity(candidateC, activeC ? 1 : revealC * 0.34 + 0.14);

  setOpacity(crossingTop, 0.1);
  setOpacity(crossingBottom, 0.1);
  setOpacity(gateLeft, 0.08);
  setOpacity(gateRight, 0.08);
  setOpacity(gateHalo, 0.1);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.candidateC, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const gateGap = lerp(72, 26, easeInOut(clamp(progress / 0.68, 0, 1)));
  const collapse = clamp(progress / 0.72, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(86, 112, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.66, compression),
    lerp(1, 1.6, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const candidateAPosition = mixPoint(points.candidateA, { x: 734, y: 388 }, collapse);
  const candidateBPosition = mixPoint(points.candidateB, { x: 908, y: 392 }, collapse);
  const candidateCPosition = mixPoint(points.candidateC, { x: 824, y: 560 }, collapse);
  setGroupTransform(candidateA, candidateAPosition.x, candidateAPosition.y, lerp(0.96, 0.72, collapse), lerp(0, -8, collapse));
  setGroupTransform(candidateB, candidateBPosition.x, candidateBPosition.y, lerp(0.96, 0.72, collapse), lerp(0, 6, collapse));
  setGroupTransform(candidateC, candidateCPosition.x, candidateCPosition.y, lerp(0.95, 0.66, collapse), 0);
  setOpacity(candidateA, lerp(0.34, 0.06, collapse));
  setOpacity(candidateB, lerp(0.34, 0.06, collapse));
  setOpacity(candidateC, lerp(1, 0.14, collapse));

  setOpacity(crossingTop, clamp((progress - 0.04) * 1.6, 0, 0.86));
  setOpacity(crossingBottom, clamp((progress - 0.04) * 1.6, 0, 0.86));
  setOpacity(gateLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(gateRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(gateHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(gateLeft, points.gate.x - gateGap, points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + gateGap, points.gate.y, 1, 0);

  setOpacity(slotLeft, clamp((progress - 0.42) * 1.3, 0, 0.26));
  setOpacity(slotRight, clamp((progress - 0.52) * 1.3, 0, 0.26));
  setOpacity(slotBottom, clamp((progress - 0.62) * 1.3, 0, 0.26));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.86, 0, 1));
  const position = pointOnKnot(routeProgress);
  const leftReveal = anchorState(routeProgress, 0.16);
  const rightReveal = anchorState(routeProgress, 0.46);
  const bottomReveal = anchorState(routeProgress, 0.74);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(knotBase, lerp(0.08, 0.24, routeProgress));
  setPathWindow(knotActive, KNOT_LENGTH, KNOT_LENGTH * routeProgress, 1);

  setOpacity(crossingTop, lerp(0.86, 0.08, progress));
  setOpacity(crossingBottom, lerp(0.86, 0.08, progress));
  setOpacity(gateLeft, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(gateRight, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(gateHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(gateLeft, points.gate.x - lerp(26, 44, progress), points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + lerp(26, 44, progress), points.gate.y, 1, 0);

  setOpacity(candidateA, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateB, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateC, clamp(0.14 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotLeft, slotState(routeProgress, 0.16));
  setOpacity(slotRight, slotState(routeProgress, 0.46));
  setOpacity(slotBottom, slotState(routeProgress, 0.74));

  setGroupTransform(anchorLeft, system.left.x, system.left.y, lerp(0.88, 1, easeOut(leftReveal)), 0);
  setGroupTransform(anchorRight, system.right.x, system.right.y, lerp(0.88, 1, easeOut(rightReveal)), 0);
  setGroupTransform(anchorBottom, system.bottom.x, system.bottom.y, lerp(0.88, 1, easeOut(bottomReveal)), 0);
  setOpacity(anchorLeft, leftReveal);
  setOpacity(anchorRight, rightReveal);
  setOpacity(anchorBottom, bottomReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.64) * 1.4, 0, 0.18));
  setOpacity(resolutionRing, clamp((progress - 0.72) * 1.6, 0, 0.22));
  setOpacity(memoryArc, clamp((progress - 0.78) * 1.4, 0, 0.1));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(knotBase, lerp(0.24, 0.46, settle));
  setPathWindow(knotActive, KNOT_LENGTH, KNOT_LENGTH, lerp(1, 0.28, settle));

  [crossingTop, crossingBottom, gateLeft, gateRight, gateHalo, candidateA, candidateB, candidateC, slotLeft, slotRight, slotBottom].forEach(
    (element) => setOpacity(element, 0),
  );

  setGroupTransform(
    anchorLeft,
    lerp(system.left.x, system.settleLeft.x, settle),
    lerp(system.left.y, system.settleLeft.y, settle),
    0.96,
    0,
  );
  setGroupTransform(
    anchorRight,
    lerp(system.right.x, system.settleRight.x, settle),
    lerp(system.right.y, system.settleRight.y, settle),
    0.96,
    0,
  );
  setGroupTransform(
    anchorBottom,
    lerp(system.bottom.x, system.settleBottom.x, settle),
    lerp(system.bottom.y, system.settleBottom.y, settle),
    0.97,
    0,
  );
  setOpacity(anchorLeft, 0.92);
  setOpacity(anchorRight, 0.92);
  setOpacity(anchorBottom, 0.92);

  setOpacity(resolutionHalo, lerp(0.18, 0.3, settle));
  setOpacity(resolutionRing, lerp(0.22, 0.88, settle));
  setOpacity(memoryArc, lerp(0.1, 0.2, settle));
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
