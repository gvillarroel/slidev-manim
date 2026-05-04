const TOTAL_DURATION = 36_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 9_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");
const clampPreview = document.getElementById("clamp-preview");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");
const topRail = document.getElementById("top-rail");
const bottomRail = document.getElementById("bottom-rail");
const jawLeft = document.getElementById("jaw-left");
const jawRight = document.getElementById("jaw-right");
const pressureHalo = document.getElementById("pressure-halo");
const axisBase = document.getElementById("axis-base");
const axisActive = document.getElementById("axis-active");
const tickTop = document.getElementById("tick-top");
const tickBottom = document.getElementById("tick-bottom");
const memorySeamLeft = document.getElementById("memory-seam-left");
const memorySeamRight = document.getElementById("memory-seam-right");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const AXIS_LENGTH = axisActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 584, y: 450 },
  candidateA: { x: 648, y: 350 },
  candidateB: { x: 820, y: 322 },
  candidateC: { x: 972, y: 396 },
  clampApproach: { x: 934, y: 450 },
  gate: { x: 820, y: 450 },
  axisLeft: { x: 742, y: 450 },
  axisRight: { x: 898, y: 450 },
};

const clamp = {
  leftOpen: { x: 676, y: 450 },
  leftClosed: { x: 760, y: 450 },
  leftSettle: { x: 724, y: 450 },
  rightOpen: { x: 964, y: 450 },
  rightClosed: { x: 880, y: 450 },
  rightSettle: { x: 916, y: 450 },
  topOpen: { x: 820, y: 352 },
  topClosed: { x: 820, y: 392 },
  topSettle: { x: 820, y: 390 },
  bottomOpen: { x: 820, y: 548 },
  bottomClosed: { x: 820, y: 508 },
  bottomSettle: { x: 820, y: 510 },
  tickTop: { x: 820, y: 352 },
  tickBottom: { x: 820, y: 548 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
  looping: true,
};

function clampValue(value, min, max) {
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
      const local = clampValue((progress - segment.start) / (segment.end - segment.start), 0, 1);
      return mixPoint(segment.from, segment.to, easeInOut(local));
    }
  }
  return segments[segments.length - 1].to;
}

function setOpacity(element, value) {
  element.setAttribute("opacity", clampValue(value, 0, 1).toFixed(3));
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
  const clamped = clampValue(visibleLength, 0, totalLength);
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 200).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
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
        localProgress: clampValue((elapsed - cursor) / phase.duration, 0, 1),
        totalProgress: clampValue(elapsed / TOTAL_DURATION, 0, 1),
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
    appearance: 10,
    search: 28,
    tension: 8,
    transformation: 4,
    resolution: -2,
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
    appearance: { x: 108, y: 150, width: 1120, height: 632 },
    search: { x: 154, y: 146, width: 1112, height: 632 },
    tension: { x: 338, y: 164, width: 948, height: 598 },
    transformation: { x: 358, y: 150, width: 944, height: 624 },
    resolution: { x: 360, y: 136, width: 940, height: 648 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -18) translate(800 450) scale(1.035) translate(-800 -450)",
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
  setOpacity(clampPreview, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, 1, -2);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, 1, 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, 1, 2);
  [candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  setGroupTransform(topRail, clamp.topOpen.x, clamp.topOpen.y, 1, 0);
  setGroupTransform(bottomRail, clamp.bottomOpen.x, clamp.bottomOpen.y, 1, 0);
  setGroupTransform(jawLeft, clamp.leftOpen.x, clamp.leftOpen.y, 1, 0);
  setGroupTransform(jawRight, clamp.rightOpen.x, clamp.rightOpen.y, 1, 0);
  setOpacity(topRail, 0);
  setOpacity(bottomRail, 0);
  setOpacity(jawLeft, 0);
  setOpacity(jawRight, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(axisBase, 0);
  setPathWindow(axisActive, AXIS_LENGTH, 0, 0);

  setGroupTransform(tickTop, clamp.tickTop.x, clamp.tickTop.y, 1, 0);
  setGroupTransform(tickBottom, clamp.tickBottom.x, clamp.tickBottom.y, 1, 0);
  setOpacity(tickTop, 0);
  setOpacity(tickBottom, 0);
  setOpacity(memorySeamLeft, 0);
  setOpacity(memorySeamRight, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, clampValue(eased * 0.98, 0, 1));
  const preview = clampValue((progress - 0.44) * 1.8, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 80, eased),
    clampValue(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clampValue((progress - 0.1) * 1.5, 0, 0.34));
  setOpacity(clampPreview, preview * 0.3);

  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(candidateA, preview * 0.14);
  setOpacity(candidateB, preview * 0.1);
  setOpacity(candidateC, preview * 0.1);

  setGroupTransform(topRail, clamp.topOpen.x, clamp.topOpen.y, 1, 0);
  setGroupTransform(bottomRail, clamp.bottomOpen.x, clamp.bottomOpen.y, 1, 0);
  setGroupTransform(jawLeft, clamp.leftOpen.x, clamp.leftOpen.y, 1, 0);
  setGroupTransform(jawRight, clamp.rightOpen.x, clamp.rightOpen.y, 1, 0);
  setOpacity(topRail, preview * 0.1);
  setOpacity(bottomRail, preview * 0.1);
  setOpacity(jawLeft, preview * 0.08);
  setOpacity(jawRight, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.candidateA },
    { start: 0.24, end: 0.54, from: points.candidateA, to: points.candidateB },
    { start: 0.54, end: 0.82, from: points.candidateB, to: points.candidateC },
    { start: 0.82, end: 1, from: points.candidateC, to: points.clampApproach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.24, 0.08, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.04, progress));
  setOpacity(clampPreview, 0.2);

  const revealA = clampValue(progress / 0.22, 0, 1);
  const revealB = clampValue((progress - 0.22) / 0.24, 0, 1);
  const revealC = clampValue((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.28 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.28 && progress < 0.58 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.58 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.22 + revealA * 0.22);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.12 + revealC * 0.24);

  const activeA = progress < 0.28 ? 1 : 0;
  const activeB = progress >= 0.28 && progress < 0.58 ? 1 : 0;
  const activeC = progress >= 0.58 ? 1 : 0;

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, lerp(0.88, activeC ? 1.04 : 0.96, revealC), 4);
  setOpacity(candidateA, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateB, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateC, activeC ? 1 : revealC * 0.34 + 0.12);

  setGroupTransform(topRail, clamp.topOpen.x, clamp.topOpen.y, 1, 0);
  setGroupTransform(bottomRail, clamp.bottomOpen.x, clamp.bottomOpen.y, 1, 0);
  setGroupTransform(jawLeft, clamp.leftOpen.x, clamp.leftOpen.y, 1, 0);
  setGroupTransform(jawRight, clamp.rightOpen.x, clamp.rightOpen.y, 1, 0);
  setOpacity(topRail, 0.1);
  setOpacity(bottomRail, 0.1);
  setOpacity(jawLeft, 0.12);
  setOpacity(jawRight, 0.12);
}

function renderTension(progress) {
  const travel = clampValue(progress / 0.36, 0, 1);
  const position = mixPoint(points.clampApproach, points.gate, easeInOut(travel));
  const compression = Math.sin(clampValue(progress / 0.8, 0, 1) * Math.PI);
  const supportProgress = easeInOut(clampValue(progress / 0.7, 0, 1));
  const candidateFade = clampValue(progress / 0.48, 0, 1);

  setDot(
    position,
    lerp(18, 17, progress),
    lerp(88, 124, progress),
    1,
    0.22 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 1.72, compression),
    lerp(1, 0.56, compression),
  );
  setOpacity(narrativeSpine, lerp(0.1, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.04, 0, progress));
  setOpacity(clampPreview, lerp(0.2, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, candidateFade));
  });

  setGroupTransform(candidateA, lerp(points.candidateA.x, 716, candidateFade), lerp(points.candidateA.y, 378, candidateFade), lerp(0.96, 0.74, candidateFade), -4);
  setGroupTransform(candidateB, lerp(points.candidateB.x, 820, candidateFade), lerp(points.candidateB.y, 346, candidateFade), lerp(0.96, 0.68, candidateFade), 0);
  setGroupTransform(candidateC, lerp(points.candidateC.x, 924, candidateFade), lerp(points.candidateC.y, 392, candidateFade), lerp(0.96, 0.74, candidateFade), 4);
  setOpacity(candidateA, lerp(0.3, 0.08, candidateFade));
  setOpacity(candidateB, lerp(0.3, 0.06, candidateFade));
  setOpacity(candidateC, lerp(1, 0.1, candidateFade));

  setGroupTransform(
    topRail,
    lerp(clamp.topOpen.x, clamp.topClosed.x, supportProgress),
    lerp(clamp.topOpen.y, clamp.topClosed.y, supportProgress),
    1,
    0,
  );
  setGroupTransform(
    bottomRail,
    lerp(clamp.bottomOpen.x, clamp.bottomClosed.x, supportProgress),
    lerp(clamp.bottomOpen.y, clamp.bottomClosed.y, supportProgress),
    1,
    0,
  );
  setGroupTransform(
    jawLeft,
    lerp(clamp.leftOpen.x, clamp.leftClosed.x, supportProgress),
    lerp(clamp.leftOpen.y, clamp.leftClosed.y, supportProgress),
    1,
    0,
  );
  setGroupTransform(
    jawRight,
    lerp(clamp.rightOpen.x, clamp.rightClosed.x, supportProgress),
    lerp(clamp.rightOpen.y, clamp.rightClosed.y, supportProgress),
    1,
    0,
  );
  setOpacity(topRail, clampValue((progress - 0.06) * 1.6, 0, 0.88));
  setOpacity(bottomRail, clampValue((progress - 0.06) * 1.6, 0, 0.88));
  setOpacity(jawLeft, clampValue((progress - 0.02) * 1.6, 0, 1));
  setOpacity(jawRight, clampValue((progress - 0.02) * 1.6, 0, 1));
  setOpacity(pressureHalo, clampValue((progress - 0.08) * 1.5, 0, 0.44));

  setOpacity(axisBase, clampValue((progress - 0.52) * 1.2, 0, 0.16));
}

function renderTransformation(progress) {
  const hold = clampValue(progress / 0.18, 0, 1);
  const releaseProgress = clampValue((progress - 0.18) / 0.82, 0, 1);
  const sweepProgress = clampValue((progress - 0.24) / 0.54, 0, 1);
  const position = segmentedPoint(releaseProgress, [
    { start: 0, end: 0.2, from: points.gate, to: points.axisLeft },
    { start: 0.2, end: 0.74, from: points.axisLeft, to: points.axisRight },
    { start: 0.74, end: 1, from: points.axisRight, to: points.gate },
  ]);

  const settle = easeInOut(releaseProgress);
  const holdCompression = 1 + (1 - hold) * 0.72;
  const holdSquash = 1 - (1 - hold) * 0.44;

  setDot(
    position,
    lerp(17, 16, releaseProgress),
    lerp(124, 96, releaseProgress),
    1,
    0.22 + pulseWave(progress, 2.0) * 0.08,
    holdCompression,
    holdSquash,
  );

  setOpacity(narrativeSpine, 0);
  setOpacity(clampPreview, 0);
  [searchGuideA, searchGuideB, searchGuideC, candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  setGroupTransform(
    topRail,
    lerp(clamp.topClosed.x, clamp.topSettle.x, settle),
    lerp(clamp.topClosed.y, clamp.topSettle.y, settle),
    1,
    0,
  );
  setGroupTransform(
    bottomRail,
    lerp(clamp.bottomClosed.x, clamp.bottomSettle.x, settle),
    lerp(clamp.bottomClosed.y, clamp.bottomSettle.y, settle),
    1,
    0,
  );
  setGroupTransform(
    jawLeft,
    lerp(clamp.leftClosed.x, clamp.leftSettle.x, settle),
    lerp(clamp.leftClosed.y, clamp.leftSettle.y, settle),
    1,
    0,
  );
  setGroupTransform(
    jawRight,
    lerp(clamp.rightClosed.x, clamp.rightSettle.x, settle),
    lerp(clamp.rightClosed.y, clamp.rightSettle.y, settle),
    1,
    0,
  );
  setOpacity(topRail, lerp(0.88, 0.16, settle));
  setOpacity(bottomRail, lerp(0.88, 0.16, settle));
  setOpacity(jawLeft, lerp(1, 0.94, settle));
  setOpacity(jawRight, lerp(1, 0.94, settle));
  setOpacity(pressureHalo, clampValue(0.44 - settle * 0.5, 0, 1));

  setOpacity(axisBase, lerp(0.16, 0.34, sweepProgress));
  setPathWindow(axisActive, AXIS_LENGTH, AXIS_LENGTH * sweepProgress, lerp(0.4, 1, sweepProgress));

  const tickReveal = clampValue((releaseProgress - 0.36) / 0.26, 0, 1);
  setGroupTransform(tickTop, clamp.tickTop.x, clamp.tickTop.y, lerp(0.88, 1, easeOut(tickReveal)), 0);
  setGroupTransform(tickBottom, clamp.tickBottom.x, clamp.tickBottom.y, lerp(0.88, 1, easeOut(tickReveal)), 0);
  setOpacity(tickTop, tickReveal);
  setOpacity(tickBottom, tickReveal);

  setOpacity(memorySeamLeft, clampValue((releaseProgress - 0.62) * 1.2, 0, 0.18));
  setOpacity(memorySeamRight, clampValue((releaseProgress - 0.68) * 1.2, 0, 0.18));
  setOpacity(resolutionFrame, clampValue((releaseProgress - 0.76) * 1.3, 0, 0.28));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(clampPreview, 0);
  [
    searchGuideA,
    searchGuideB,
    searchGuideC,
    candidateA,
    candidateB,
    candidateC,
    topRail,
    bottomRail,
    pressureHalo,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(jawLeft, clamp.leftSettle.x, clamp.leftSettle.y, 0.98, 0);
  setGroupTransform(jawRight, clamp.rightSettle.x, clamp.rightSettle.y, 0.98, 0);
  setOpacity(jawLeft, 0.94);
  setOpacity(jawRight, 0.94);

  setOpacity(axisBase, lerp(0.34, 0.4, settle));
  setPathWindow(axisActive, AXIS_LENGTH, AXIS_LENGTH, lerp(1, 0.08, settle));

  setGroupTransform(tickTop, clamp.tickTop.x, clamp.tickTop.y, 0.98, 0);
  setGroupTransform(tickBottom, clamp.tickBottom.x, clamp.tickBottom.y, 0.98, 0);
  setOpacity(tickTop, lerp(0.92, 0.88, settle));
  setOpacity(tickBottom, lerp(0.92, 0.88, settle));
  setOpacity(memorySeamLeft, lerp(0.18, 0.2, settle));
  setOpacity(memorySeamRight, lerp(0.18, 0.2, settle));
  setOpacity(resolutionFrame, lerp(0.28, 0.84, settle));
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
