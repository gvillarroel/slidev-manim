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
const candidateCurl = document.getElementById("candidate-curl");
const candidateSway = document.getElementById("candidate-sway");
const candidateCoil = document.getElementById("candidate-coil");
const throatGuide = document.getElementById("throat-guide");
const braceLeft = document.getElementById("brace-left");
const braceRight = document.getElementById("brace-right");
const clampTop = document.getElementById("clamp-top");
const clampBottom = document.getElementById("clamp-bottom");
const railTop = document.getElementById("rail-top");
const railBottom = document.getElementById("rail-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const coilShell = document.getElementById("coil-shell");
const coilBase = document.getElementById("coil-base");
const coilTrace = document.getElementById("coil-trace");
const coreRing = document.getElementById("core-ring");
const slotNorth = document.getElementById("slot-north");
const slotEast = document.getElementById("slot-east");
const slotSouth = document.getElementById("slot-south");
const slotWest = document.getElementById("slot-west");
const stabilityFrame = document.getElementById("stability-frame");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const COIL_TRACE_LENGTH = coilTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 560, y: 450 },
  curlCandidate: { x: 648, y: 368 },
  swayCandidate: { x: 836, y: 332 },
  coilCandidate: { x: 1002, y: 392 },
  throatApproach: { x: 934, y: 430 },
  center: { x: 820, y: 450 },
};

const coil = {
  center: { x: 820, y: 450 },
  north: { x: 820, y: 318 },
  east: { x: 948, y: 450 },
  south: { x: 820, y: 582 },
  west: { x: 692, y: 450 },
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

function pointOnCoil(progress) {
  const length = clamp(progress, 0, 1) * COIL_TRACE_LENGTH;
  const point = coilTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.2, 0, 1) * 0.42;
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
    search: 34,
    tension: 12,
    transformation: 8,
    resolution: 2,
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
    appearance: { x: 138, y: 142, width: 1080, height: 640 },
    search: { x: 152, y: 126, width: 1104, height: 654 },
    tension: { x: 344, y: 146, width: 954, height: 626 },
    transformation: { x: 334, y: 132, width: 978, height: 648 },
    resolution: { x: 382, y: 134, width: 900, height: 644 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -14) translate(800 450) scale(1.04) translate(-800 -450)",
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

  setGroupTransform(candidateCurl, points.curlCandidate.x, points.curlCandidate.y, 1, -6);
  setGroupTransform(candidateSway, points.swayCandidate.x, points.swayCandidate.y, 1, 2);
  setGroupTransform(candidateCoil, points.coilCandidate.x, points.coilCandidate.y, 1, 6);
  [candidateCurl, candidateSway, candidateCoil].forEach((element) => setOpacity(element, 0));

  setOpacity(throatGuide, 0);
  setOpacity(braceLeft, 0);
  setOpacity(braceRight, 0);
  setGroupTransform(clampTop, points.center.x, 284, 1, 0);
  setGroupTransform(clampBottom, points.center.x, 616, 1, 0);
  setOpacity(clampTop, 0);
  setOpacity(clampBottom, 0);
  setOpacity(railTop, 0);
  setOpacity(railBottom, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(coilShell, 0);
  setOpacity(coilBase, 0);
  setPathWindow(coilTrace, COIL_TRACE_LENGTH, 0, 0);
  setOpacity(coreRing, 0);

  setGroupTransform(slotNorth, coil.north.x, coil.north.y, 1, 0);
  setGroupTransform(slotEast, coil.east.x, coil.east.y, 1, 0);
  setGroupTransform(slotSouth, coil.south.x, coil.south.y, 1, 0);
  setGroupTransform(slotWest, coil.west.x, coil.west.y, 1, 0);
  [slotNorth, slotEast, slotSouth, slotWest].forEach((slot) => setOpacity(slot, 0));

  setOpacity(stabilityFrame, 0);
  setOpacity(resolutionHalo, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(candidateCurl, preview * 0.16);
  setOpacity(candidateSway, preview * 0.1);
  setOpacity(candidateCoil, preview * 0.08);
  setOpacity(throatGuide, preview * 0.1);
  setOpacity(clampTop, preview * 0.05);
  setOpacity(clampBottom, preview * 0.05);
  setOpacity(railTop, preview * 0.08);
  setOpacity(railBottom, preview * 0.08);
  setOpacity(pressureHalo, preview * 0.08);
  setOpacity(coilShell, preview * 0.04);
  setOpacity(coilBase, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.curlCandidate },
    { start: 0.28, end: 0.58, from: points.curlCandidate, to: points.swayCandidate },
    { start: 0.58, end: 0.84, from: points.swayCandidate, to: points.coilCandidate },
    { start: 0.84, end: 1, from: points.coilCandidate, to: points.throatApproach },
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

  setGroupTransform(candidateCurl, points.curlCandidate.x, points.curlCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -6);
  setGroupTransform(candidateSway, points.swayCandidate.x, points.swayCandidate.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 2);
  setGroupTransform(candidateCoil, points.coilCandidate.x, points.coilCandidate.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 6);
  setOpacity(candidateCurl, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateSway, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateCoil, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(throatGuide, 0.14);
  setOpacity(clampTop, 0.06);
  setOpacity(clampBottom, 0.06);
  setOpacity(railTop, 0.1);
  setOpacity(railBottom, 0.1);
  setOpacity(pressureHalo, 0.08);
  setOpacity(coilShell, 0.04);
  setOpacity(coilBase, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.throatApproach, points.center, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const clampGap = lerp(166, 82, easeInOut(clamp(progress / 0.7, 0, 1)));
  const collapse = clamp(progress / 0.74, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 118, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 1.82, compression),
    lerp(1, 0.5, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const curlPosition = mixPoint(points.curlCandidate, { x: 736, y: 386 }, collapse);
  const swayPosition = mixPoint(points.swayCandidate, { x: 824, y: 348 }, collapse);
  const coilPosition = mixPoint(points.coilCandidate, { x: 900, y: 392 }, collapse);
  setGroupTransform(candidateCurl, curlPosition.x, curlPosition.y, lerp(0.96, 0.72, collapse), -10);
  setGroupTransform(candidateSway, swayPosition.x, swayPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateCoil, coilPosition.x, coilPosition.y, lerp(0.95, 0.68, collapse), 10);
  setOpacity(candidateCurl, lerp(0.3, 0.05, collapse));
  setOpacity(candidateSway, lerp(0.28, 0.05, collapse));
  setOpacity(candidateCoil, lerp(1, 0.12, collapse));

  setOpacity(throatGuide, clamp((progress - 0.04) * 1.7, 0, 0.78));
  setOpacity(braceLeft, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(braceRight, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(clampTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(clampBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(railTop, clamp((progress - 0.08) * 1.5, 0, 0.8));
  setOpacity(railBottom, clamp((progress - 0.08) * 1.5, 0, 0.8));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(clampTop, points.center.x, 450 - clampGap, 1, 0);
  setGroupTransform(clampBottom, points.center.x, 450 + clampGap, 1, 0);

  setOpacity(coilShell, clamp((progress - 0.5) * 0.42, 0, 0.14));
  setOpacity(coilBase, clamp((progress - 0.56) * 0.4, 0, 0.16));
  setOpacity(coreRing, clamp((progress - 0.62) * 0.42, 0, 0.12));
  setOpacity(slotNorth, clamp((progress - 0.42) * 1.3, 0, 0.22));
  setOpacity(slotEast, clamp((progress - 0.54) * 1.3, 0, 0.22));
  setOpacity(slotSouth, clamp((progress - 0.66) * 1.3, 0, 0.22));
  setOpacity(slotWest, clamp((progress - 0.78) * 1.3, 0, 0.22));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.9, 0, 1));
  const position = pointOnCoil(routeProgress);
  const coreProgress = clamp((routeProgress - 0.02) / 0.22, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(coilShell, lerp(0.24, 0.98, routeProgress));
  setOpacity(coilBase, lerp(0.16, 0.32, routeProgress));
  setPathWindow(coilTrace, COIL_TRACE_LENGTH, COIL_TRACE_LENGTH * routeProgress, 1);
  setOpacity(coreRing, clamp((progress - 0.08) * 1.3, 0, 0.34 * coreProgress));

  setOpacity(throatGuide, lerp(0.78, 0.08, progress));
  setOpacity(braceLeft, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(braceRight, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(clampTop, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(clampBottom, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(railTop, clamp(0.8 - progress * 0.95, 0, 1));
  setOpacity(railBottom, clamp(0.8 - progress * 0.95, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(clampTop, points.center.x, lerp(368, 344, progress), 1, 0);
  setGroupTransform(clampBottom, points.center.x, lerp(532, 556, progress), 1, 0);

  setOpacity(candidateCurl, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateSway, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateCoil, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotNorth, slotState(routeProgress, 0.16));
  setOpacity(slotEast, slotState(routeProgress, 0.4));
  setOpacity(slotSouth, slotState(routeProgress, 0.66));
  setOpacity(slotWest, slotState(routeProgress, 0.84));

  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(stabilityFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;
  const returnPosition = mixPoint(pointOnCoil(1), points.center, settle);

  setDot(returnPosition, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(coilShell, lerp(0.98, 1, settle));
  setOpacity(coilBase, lerp(0.32, 0.42, settle));
  setPathWindow(coilTrace, COIL_TRACE_LENGTH, COIL_TRACE_LENGTH, lerp(1, 0.22, settle));
  setOpacity(coreRing, lerp(0.34, 0.42, settle));

  [
    throatGuide,
    braceLeft,
    braceRight,
    clampTop,
    clampBottom,
    railTop,
    railBottom,
    pressureHalo,
    candidateCurl,
    candidateSway,
    candidateCoil,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(slotNorth, coil.north.x, lerp(coil.north.y, 328, settle), 0.98, 0);
  setGroupTransform(slotEast, lerp(coil.east.x, 934, settle), coil.east.y, 0.98, 0);
  setGroupTransform(slotSouth, coil.south.x, lerp(coil.south.y, 572, settle), 0.98, 0);
  setGroupTransform(slotWest, lerp(coil.west.x, 706, settle), coil.west.y, 0.98, 0);
  setOpacity(slotNorth, 0.34);
  setOpacity(slotEast, 0.32);
  setOpacity(slotSouth, 0.34);
  setOpacity(slotWest, 0.32);

  setOpacity(resolutionHalo, lerp(0.16, 0.28, settle));
  setOpacity(stabilityFrame, lerp(0.24, 0.72, settle));
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
