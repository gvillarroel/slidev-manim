const TOTAL_DURATION = 36_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 8_000 },
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
const candidateRamp = document.getElementById("candidate-ramp");
const candidatePocket = document.getElementById("candidate-pocket");
const candidateWheel = document.getElementById("candidate-wheel");
const tensionGuide = document.getElementById("tension-guide");
const pawlGuide = document.getElementById("pawl-guide");
const trackArcBack = document.getElementById("track-arc-back");
const trackArcFront = document.getElementById("track-arc-front");
const toothA = document.getElementById("tooth-a");
const toothB = document.getElementById("tooth-b");
const toothC = document.getElementById("tooth-c");
const capturePocket = document.getElementById("capture-pocket");
const pawlBody = document.getElementById("pawl-body");
const pawlAccent = document.getElementById("pawl-accent");
const pressureHalo = document.getElementById("pressure-halo");
const resolveArc = document.getElementById("resolve-arc");
const resolveToothA = document.getElementById("resolve-tooth-a");
const resolveToothB = document.getElementById("resolve-tooth-b");
const resolveToothC = document.getElementById("resolve-tooth-c");
const resolveToothD = document.getElementById("resolve-tooth-d");
const resolvePawl = document.getElementById("resolve-pawl");
const resolvePawlAccent = document.getElementById("resolve-pawl-accent");
const resolveTrace = document.getElementById("resolve-trace");
const resolveCorners = document.getElementById("resolve-corners");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TENSION_GUIDE_LENGTH = tensionGuide.getTotalLength();
const RESOLVE_TRACE_LENGTH = resolveTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 300, y: 450 },
  ingress: { x: 530, y: 450 },
  ramp: { x: 674, y: 396 },
  pocket: { x: 824, y: 522 },
  wheel: { x: 996, y: 396 },
  approach: { x: 946, y: 398 },
  capture: { x: 804, y: 490 },
  upperRight: { x: 904, y: 360 },
  center: { x: 820, y: 450 },
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

function pointOnPath(path, totalLength, progress) {
  const length = clamp(progress, 0, 1) * totalLength;
  const point = path.getPointAtLength(length);
  return { x: point.x, y: point.y };
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

function setTranslate(element, x = 0, y = 0) {
  element.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
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
    appearance: 16,
    search: 24,
    tension: 10,
    transformation: 2,
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
    appearance: { x: 92, y: 24, width: 856, height: 860 },
    search: { x: 238, y: 6, width: 790, height: 888 },
    tension: { x: 426, y: 0, width: 684, height: 900 },
    transformation: { x: 442, y: 0, width: 668, height: 900 },
    resolution: { x: 482, y: 0, width: 624, height: 900 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute("transform", "translate(0 -6)");
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

  setGroupTransform(candidateRamp, points.ramp.x, points.ramp.y, 1, -4);
  setGroupTransform(candidatePocket, points.pocket.x, points.pocket.y, 1, 0);
  setGroupTransform(candidateWheel, points.wheel.x, points.wheel.y, 1, 6);
  [candidateRamp, candidatePocket, candidateWheel].forEach((element) => setOpacity(element, 0));

  setOpacity(tensionGuide, 0);
  setOpacity(pawlGuide, 0);
  setOpacity(trackArcBack, 0);
  setOpacity(trackArcFront, 0);
  setOpacity(toothA, 0);
  setOpacity(toothB, 0);
  setOpacity(toothC, 0);
  setOpacity(capturePocket, 0);
  setOpacity(pawlBody, 0);
  setOpacity(pawlAccent, 0);
  setOpacity(pressureHalo, 0);
  [trackArcBack, trackArcFront, toothA, toothB, toothC, capturePocket].forEach((element) => setTranslate(element, 0, 0));
  setGroupTransform(pawlBody, 860, 328, 1, 0);

  setOpacity(resolveArc, 0);
  setOpacity(resolveToothA, 0);
  setOpacity(resolveToothB, 0);
  setOpacity(resolveToothC, 0);
  setOpacity(resolveToothD, 0);
  setOpacity(resolvePawl, 0);
  setOpacity(resolvePawlAccent, 0);
  setPathWindow(resolveTrace, RESOLVE_TRACE_LENGTH, 0, 0);
  setOpacity(resolveCorners, 0);
  setOpacity(resolutionHalo, 0);
  [resolveArc, resolveToothA, resolveToothB, resolveToothC, resolveToothD, resolveCorners].forEach((element) =>
    setTranslate(element, 0, 0),
  );
  setGroupTransform(resolvePawl, 878, 340, 1, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.9);
  const preview = clamp((progress - 0.44) * 1.75, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 88, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.1) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.1) * 1.4, 0, 0.34));

  setOpacity(searchGuideA, preview * 0.24);
  setOpacity(candidateRamp, preview * 0.18);
  setOpacity(candidatePocket, preview * 0.12);
  setOpacity(candidateWheel, preview * 0.1);

  setOpacity(tensionGuide, preview * 0.08);
  setOpacity(pawlGuide, preview * 0.08);
  setOpacity(trackArcBack, preview * 0.08);
  setOpacity(trackArcFront, preview * 0.06);
  setOpacity(toothA, preview * 0.08);
  setOpacity(toothB, preview * 0.06);
  setOpacity(toothC, preview * 0.04);
  setOpacity(capturePocket, preview * 0.05);
  setOpacity(pawlBody, preview * 0.06);
  setOpacity(pawlAccent, preview * 0.05);
  setOpacity(pressureHalo, preview * 0.08);

  setOpacity(resolveArc, preview * 0.06);
  setOpacity(resolveToothA, preview * 0.06);
  setOpacity(resolveToothB, preview * 0.05);
  setOpacity(resolveToothC, preview * 0.04);
  setOpacity(resolvePawl, preview * 0.05);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.ramp },
    { start: 0.24, end: 0.56, from: points.ramp, to: points.pocket },
    { start: 0.56, end: 0.84, from: points.pocket, to: points.wheel },
    { start: 0.84, end: 1, from: points.wheel, to: points.approach },
  ]);

  const revealA = clamp(progress / 0.2, 0, 1);
  const revealB = clamp((progress - 0.2) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.52) / 0.24, 0, 1);
  const activeA = progress < 0.26 ? 1 : 0;
  const activeB = progress >= 0.26 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setDot(position, 18, 92, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.22, 0.05, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.04, progress));

  searchGuideA.setAttribute("stroke", activeA ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", activeB ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", activeC ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.2 + revealA * 0.22);
  setOpacity(searchGuideB, 0.1 + revealB * 0.24);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  setGroupTransform(candidateRamp, points.ramp.x, points.ramp.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidatePocket, points.pocket.x, points.pocket.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateWheel, points.wheel.x, points.wheel.y, lerp(0.84, activeC ? 1.05 : 0.96, revealC), 6);
  setOpacity(candidateRamp, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidatePocket, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateWheel, activeC ? 1 : revealC * 0.36 + 0.12);

  setOpacity(tensionGuide, 0.12);
  setOpacity(pawlGuide, 0.1);
  setOpacity(trackArcBack, 0.08);
  setOpacity(trackArcFront, 0.07);
  setOpacity(toothA, 0.08);
  setOpacity(toothB, 0.06);
  setOpacity(toothC, 0.05);
  setOpacity(capturePocket, 0.06);
  setOpacity(pawlBody, 0.08);
  setOpacity(pawlAccent, 0.08);
  setOpacity(pressureHalo, 0.08);

  setOpacity(resolveArc, 0.06);
  setOpacity(resolveToothA, 0.06);
  setOpacity(resolveToothB, 0.05);
  setOpacity(resolveToothC, 0.04);
  setOpacity(resolvePawl, 0.04);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.44, 0, 1);
  const collapse = clamp((progress - 0.42) / 0.5, 0, 1);
  const pathPosition = pointOnPath(tensionGuide, TENSION_GUIDE_LENGTH, easeInOut(travel));
  const position = mixPoint(pathPosition, points.capture, easeInOut(collapse));
  const compression = Math.sin(clamp(progress / 0.86, 0, 1) * Math.PI);
  const pawlDrop = lerp(0, 44, easeInOut(clamp(progress / 0.7, 0, 1)));
  const arcLift = lerp(0, -14, easeInOut(clamp(progress / 0.7, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(92, 126, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.54, compression),
    lerp(1, 1.88, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.03, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.08, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const rampPosition = mixPoint(points.ramp, { x: 728, y: 404 }, collapse);
  const pocketPosition = mixPoint(points.pocket, { x: 790, y: 500 }, collapse);
  const wheelPosition = mixPoint(points.wheel, { x: 916, y: 396 }, collapse);
  setGroupTransform(candidateRamp, rampPosition.x, rampPosition.y, lerp(0.96, 0.72, collapse), -8);
  setGroupTransform(candidatePocket, pocketPosition.x, pocketPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateWheel, wheelPosition.x, wheelPosition.y, lerp(0.96, 0.76, collapse), 4);
  setOpacity(candidateRamp, lerp(0.3, 0.05, collapse));
  setOpacity(candidatePocket, lerp(0.28, 0.05, collapse));
  setOpacity(candidateWheel, lerp(1, 0.12, collapse));

  setOpacity(tensionGuide, clamp((progress - 0.02) * 1.8, 0, 0.74));
  setOpacity(pawlGuide, clamp((progress - 0.02) * 1.8, 0, 0.7));
  setOpacity(trackArcBack, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(trackArcFront, clamp((progress - 0.08) * 1.6, 0, 0.84));
  setOpacity(toothA, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(toothB, clamp((progress - 0.08) * 1.6, 0, 1));
  setOpacity(toothC, clamp((progress - 0.12) * 1.55, 0, 1));
  setOpacity(capturePocket, clamp((progress - 0.14) * 1.6, 0, 1));
  setOpacity(pawlBody, clamp((progress - 0.08) * 1.6, 0, 1));
  setOpacity(pawlAccent, clamp((progress - 0.1) * 1.6, 0, 1));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.55, 0, 0.44));

  [trackArcBack, trackArcFront, toothA, toothB, toothC, capturePocket].forEach((element) => setTranslate(element, 0, arcLift));
  setGroupTransform(pawlBody, 860, 328 + pawlDrop, 1, 0);
  setTranslate(pawlAccent, 0, pawlDrop);
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.92, 0, 1));
  const position = pointOnPath(resolveTrace, RESOLVE_TRACE_LENGTH, routeProgress);
  const open = easeOut(progress);

  setDot(position, 16, 100, 1, 0.2 + pulseWave(progress, 2.0) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [candidateRamp, candidatePocket, candidateWheel, searchGuideA, searchGuideB, searchGuideC].forEach((element) => {
    setOpacity(element, 0);
  });

  setOpacity(tensionGuide, lerp(0.74, 0.06, progress));
  setOpacity(pawlGuide, lerp(0.7, 0.02, progress));
  setOpacity(trackArcBack, clamp(1 - progress * 1.0, 0, 1));
  setOpacity(trackArcFront, clamp(0.84 - progress * 0.92, 0, 1));
  setOpacity(toothA, clamp(1 - progress * 1.05, 0, 1));
  setOpacity(toothB, clamp(1 - progress * 1.02, 0, 1));
  setOpacity(toothC, clamp(1 - progress * 0.98, 0, 1));
  setOpacity(capturePocket, clamp(1 - progress * 1.2, 0, 1));
  setOpacity(pawlBody, clamp(1 - progress * 0.96, 0, 1));
  setOpacity(pawlAccent, clamp(1 - progress * 1.02, 0, 1));
  setOpacity(pressureHalo, clamp(0.44 - progress * 0.52, 0, 1));
  [trackArcBack, trackArcFront, toothA, toothB, toothC, capturePocket].forEach((element) =>
    setTranslate(element, 0, lerp(-14, -6, progress)),
  );
  setGroupTransform(pawlBody, 860, lerp(372, 348, progress), 1, 0);
  setTranslate(pawlAccent, 0, lerp(44, 10, progress));

  setOpacity(resolveArc, clamp(progress * 1.45, 0, 0.98));
  setOpacity(resolveToothA, clamp((progress - 0.04) * 1.55, 0, 0.98));
  setOpacity(resolveToothB, clamp((progress - 0.1) * 1.55, 0, 0.98));
  setOpacity(resolveToothC, clamp((progress - 0.16) * 1.55, 0, 0.98));
  setOpacity(resolveToothD, clamp((progress - 0.24) * 1.55, 0, 0.98));
  setOpacity(resolvePawl, clamp((progress - 0.12) * 1.5, 0, 1));
  setOpacity(resolvePawlAccent, clamp((progress - 0.18) * 1.55, 0, 0.96));
  setPathWindow(resolveTrace, RESOLVE_TRACE_LENGTH, RESOLVE_TRACE_LENGTH * routeProgress, 0.9);
  setOpacity(resolveCorners, clamp((progress - 0.68) * 1.4, 0, 0.42));
  setOpacity(resolutionHalo, clamp((progress - 0.74) * 1.45, 0, 0.12));

  [resolveArc, resolveToothA, resolveToothB, resolveToothC, resolveToothD].forEach((element) =>
    setTranslate(element, 0, lerp(8, -4, open)),
  );
  setGroupTransform(resolvePawl, 878, lerp(348, 340, progress), 1, 0);
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.2) * 0.05;
  const position = mixPoint(points.upperRight, points.center, settle);

  setDot(position, 16, 100, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [tensionGuide, pawlGuide, trackArcBack, trackArcFront, toothA, toothB, toothC, capturePocket, pawlBody, pawlAccent, pressureHalo].forEach((element) => {
    setOpacity(element, 0);
  });

  setOpacity(resolveArc, 0.96);
  setOpacity(resolveToothA, 0.96);
  setOpacity(resolveToothB, 0.96);
  setOpacity(resolveToothC, 0.94);
  setOpacity(resolveToothD, 0.9);
  setOpacity(resolvePawl, lerp(1, 0.42, settle));
  setOpacity(resolvePawlAccent, lerp(0.96, 0.18, settle));
  setPathWindow(resolveTrace, RESOLVE_TRACE_LENGTH, RESOLVE_TRACE_LENGTH, lerp(0.9, 0, settle));
  setOpacity(resolveCorners, lerp(0.42, 0.92, settle));
  setOpacity(resolutionHalo, lerp(0.12, 0.22, settle));

  [resolveArc, resolveToothA, resolveToothB, resolveToothC, resolveToothD].forEach((element) =>
    setTranslate(element, 0, lerp(-4, -18, settle)),
  );
  setTranslate(resolveCorners, 0, lerp(0, -4, settle));
  setGroupTransform(resolvePawl, 878, lerp(340, 326, settle), 1, 0);
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
