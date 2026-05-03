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
const candidateCorner = document.getElementById("candidate-corner");
const candidatePocket = document.getElementById("candidate-pocket");
const candidateStep = document.getElementById("candidate-step");
const chamberGuide = document.getElementById("chamber-guide");
const laneTop = document.getElementById("lane-top");
const laneBottom = document.getElementById("lane-bottom");
const deadendCap = document.getElementById("deadend-cap");
const pressureTop = document.getElementById("pressure-top");
const pressureBottom = document.getElementById("pressure-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const mazeBase = document.getElementById("maze-base");
const mazeShell = document.getElementById("maze-shell");
const mazeTrace = document.getElementById("maze-trace");
const slotOuterRight = document.getElementById("slot-outer-right");
const slotBottomLeft = document.getElementById("slot-bottom-left");
const slotInnerTurn = document.getElementById("slot-inner-turn");
const wallNorth = document.getElementById("wall-north");
const wallWest = document.getElementById("wall-west");
const wallSouth = document.getElementById("wall-south");
const mazeGrid = document.getElementById("maze-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const MAZE_TRACE_LENGTH = mazeTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcac8",
};

const points = {
  start: { x: 360, y: 450 },
  ingress: { x: 600, y: 450 },
  cornerCandidate: { x: 682, y: 350 },
  pocketCandidate: { x: 850, y: 338 },
  stepCandidate: { x: 1004, y: 440 },
  throatApproach: { x: 930, y: 450 },
  throat: { x: 888, y: 450 },
  final: { x: 812, y: 450 },
};

const slots = {
  outerRight: { x: 980, y: 332 },
  bottomLeft: { x: 654, y: 576 },
  innerTurn: { x: 734, y: 412 },
};

const walls = {
  north: { x: 820, y: 332 },
  west: { x: 654, y: 450 },
  south: { x: 812, y: 576 },
  settleNorth: { x: 820, y: 348 },
  settleWest: { x: 672, y: 450 },
  settleSouth: { x: 816, y: 560 },
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

function pointOnMaze(progress) {
  const length = clamp(progress, 0, 1) * MAZE_TRACE_LENGTH;
  const point = mazeTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function wallState(progress, threshold) {
  return clamp((progress - threshold) / 0.18, 0, 1);
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
    search: 42,
    tension: 16,
    transformation: 6,
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
    appearance: { x: 122, y: 148, width: 1090, height: 628 },
    search: { x: 148, y: 136, width: 1116, height: 640 },
    tension: { x: 338, y: 156, width: 942, height: 610 },
    transformation: { x: 312, y: 132, width: 1032, height: 640 },
    resolution: { x: 350, y: 140, width: 980, height: 636 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -16) translate(800 450) scale(1.038) translate(-800 -450)",
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

  setGroupTransform(candidateCorner, points.cornerCandidate.x, points.cornerCandidate.y, 1, -4);
  setGroupTransform(candidatePocket, points.pocketCandidate.x, points.pocketCandidate.y, 1, 4);
  setGroupTransform(candidateStep, points.stepCandidate.x, points.stepCandidate.y, 1, 0);
  [candidateCorner, candidatePocket, candidateStep].forEach((element) => setOpacity(element, 0));

  setOpacity(chamberGuide, 0);
  setOpacity(laneTop, 0);
  setOpacity(laneBottom, 0);
  setOpacity(deadendCap, 0);
  setOpacity(pressureTop, 0);
  setOpacity(pressureBottom, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(mazeBase, 0);
  setOpacity(mazeShell, 0);
  setPathWindow(mazeTrace, MAZE_TRACE_LENGTH, 0, 0);

  setGroupTransform(slotOuterRight, slots.outerRight.x, slots.outerRight.y, 1, 0);
  setGroupTransform(slotBottomLeft, slots.bottomLeft.x, slots.bottomLeft.y, 1, 0);
  setGroupTransform(slotInnerTurn, slots.innerTurn.x, slots.innerTurn.y, 1, 0);
  [slotOuterRight, slotBottomLeft, slotInnerTurn].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(wallNorth, walls.north.x, walls.north.y, 1, 0);
  setGroupTransform(wallWest, walls.west.x, walls.west.y, 1, 0);
  setGroupTransform(wallSouth, walls.south.x, walls.south.y, 1, 0);
  [wallNorth, wallWest, wallSouth].forEach((wall) => setOpacity(wall, 0));

  setOpacity(mazeGrid, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.84);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.12);
  setOpacity(candidateCorner, preview * 0.08);
  setOpacity(candidatePocket, preview * 0.06);
  setOpacity(candidateStep, preview * 0.03);
  setOpacity(chamberGuide, preview * 0.08);
  setOpacity(laneTop, preview * 0.04);
  setOpacity(laneBottom, preview * 0.04);
  setOpacity(deadendCap, preview * 0.04);
  setOpacity(pressureTop, preview * 0.05);
  setOpacity(pressureBottom, preview * 0.05);
  setOpacity(pressureHalo, preview * 0.06);
  setOpacity(mazeShell, preview * 0.08);
  setOpacity(mazeBase, preview * 0.02);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.cornerCandidate },
    { start: 0.28, end: 0.58, from: points.cornerCandidate, to: points.pocketCandidate },
    { start: 0.58, end: 0.84, from: points.pocketCandidate, to: points.stepCandidate },
    { start: 0.84, end: 1, from: points.stepCandidate, to: points.throatApproach },
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
  setOpacity(searchGuideA, 0.22 + revealA * 0.16);
  setOpacity(searchGuideB, 0.1 + revealB * 0.18);
  setOpacity(searchGuideC, 0.08 + revealC * 0.18);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(
    candidateCorner,
    points.cornerCandidate.x,
    points.cornerCandidate.y,
    lerp(0.88, activeA ? 1.05 : 0.96, revealA),
    -4,
  );
  setGroupTransform(
    candidatePocket,
    points.pocketCandidate.x,
    points.pocketCandidate.y,
    lerp(0.88, activeB ? 1.05 : 0.96, revealB),
    4,
  );
  setGroupTransform(
    candidateStep,
    points.stepCandidate.x,
    points.stepCandidate.y,
    lerp(0.84, activeC ? 1.05 : 0.96, revealC),
    0,
  );
  setOpacity(candidateCorner, activeA ? 1 : revealA * 0.18 + 0.08);
  setOpacity(candidatePocket, activeB ? 1 : revealB * 0.18 + 0.08);
  setOpacity(candidateStep, activeC ? 1 : revealC * 0.16 + 0.08);

  setOpacity(chamberGuide, 0.12);
  setOpacity(laneTop, 0.06);
  setOpacity(laneBottom, 0.06);
  setOpacity(deadendCap, 0.06);
  setOpacity(pressureTop, 0.08);
  setOpacity(pressureBottom, 0.08);
  setOpacity(pressureHalo, 0.06);
  setOpacity(mazeShell, 0.06);
  setOpacity(mazeBase, 0.02);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.44, 0, 1);
  const position = mixPoint(points.throatApproach, points.throat, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.76, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 120, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.5, compression),
    lerp(1, 1.84, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const cornerPosition = mixPoint(points.cornerCandidate, { x: 734, y: 392 }, collapse);
  const pocketPosition = mixPoint(points.pocketCandidate, { x: 816, y: 348 }, collapse);
  const stepPosition = mixPoint(points.stepCandidate, { x: 900, y: 420 }, collapse);
  setGroupTransform(candidateCorner, cornerPosition.x, cornerPosition.y, lerp(0.96, 0.72, collapse), -8);
  setGroupTransform(candidatePocket, pocketPosition.x, pocketPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateStep, stepPosition.x, stepPosition.y, lerp(0.95, 0.68, collapse), 4);
  setOpacity(candidateCorner, lerp(0.18, 0.02, collapse));
  setOpacity(candidatePocket, lerp(0.16, 0.02, collapse));
  setOpacity(candidateStep, lerp(0.72, 0.08, collapse));

  setOpacity(chamberGuide, clamp((progress - 0.04) * 1.7, 0, 0.78));
  setOpacity(laneTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(laneBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(deadendCap, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(pressureTop, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureBottom, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));

  setOpacity(mazeShell, clamp((progress - 0.52) * 0.32, 0, 0.1));
  setOpacity(mazeBase, clamp((progress - 0.6) * 0.28, 0, 0.08));
  setOpacity(slotOuterRight, clamp((progress - 0.52) * 1.1, 0, 0.12));
  setOpacity(slotBottomLeft, clamp((progress - 0.64) * 1.1, 0, 0.12));
  setOpacity(slotInnerTurn, clamp((progress - 0.76) * 1.1, 0, 0.12));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnMaze(routeProgress);
  const northReveal = wallState(routeProgress, 0.24);
  const westReveal = wallState(routeProgress, 0.58);
  const southReveal = wallState(routeProgress, 0.84);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(mazeBase, lerp(0.16, 0.96, routeProgress));
  setOpacity(mazeShell, lerp(0.1, 0.18, routeProgress));
  setPathWindow(mazeTrace, MAZE_TRACE_LENGTH, MAZE_TRACE_LENGTH * routeProgress, 1);

  setOpacity(chamberGuide, lerp(0.78, 0.08, progress));
  setOpacity(laneTop, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(laneBottom, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(deadendCap, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(pressureTop, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(pressureBottom, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));

  setOpacity(candidateCorner, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidatePocket, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateStep, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotOuterRight, slotState(routeProgress, 0.18));
  setOpacity(slotBottomLeft, slotState(routeProgress, 0.56));
  setOpacity(slotInnerTurn, slotState(routeProgress, 0.8));

  setGroupTransform(wallNorth, walls.north.x, walls.north.y, lerp(0.88, 1, easeOut(northReveal)), 0);
  setGroupTransform(wallWest, walls.west.x, walls.west.y, lerp(0.88, 1, easeOut(westReveal)), 0);
  setGroupTransform(wallSouth, walls.south.x, walls.south.y, lerp(0.88, 1, easeOut(southReveal)), 0);
  setOpacity(wallNorth, northReveal);
  setOpacity(wallWest, westReveal);
  setOpacity(wallSouth, southReveal);

  setOpacity(mazeGrid, clamp((progress - 0.76) * 1.3, 0, 0.06));
  setOpacity(resolutionHalo, clamp((progress - 0.62) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.74) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.final, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(mazeBase, lerp(0.96, 1, settle));
  setOpacity(mazeShell, lerp(0.18, 0.04, settle));
  setPathWindow(mazeTrace, MAZE_TRACE_LENGTH, MAZE_TRACE_LENGTH, lerp(1, 0.28, settle));

  [
    chamberGuide,
    laneTop,
    laneBottom,
    deadendCap,
    pressureTop,
    pressureBottom,
    pressureHalo,
    candidateCorner,
    candidatePocket,
    candidateStep,
    slotOuterRight,
    slotBottomLeft,
    slotInnerTurn,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(
    wallNorth,
    lerp(walls.north.x, walls.settleNorth.x, settle),
    lerp(walls.north.y, walls.settleNorth.y, settle),
    0.96,
    0,
  );
  setGroupTransform(
    wallWest,
    lerp(walls.west.x, walls.settleWest.x, settle),
    lerp(walls.west.y, walls.settleWest.y, settle),
    0.96,
    0,
  );
  setGroupTransform(
    wallSouth,
    lerp(walls.south.x, walls.settleSouth.x, settle),
    lerp(walls.south.y, walls.settleSouth.y, settle),
    0.96,
    0,
  );
  setOpacity(wallNorth, 0.92);
  setOpacity(wallWest, 0.92);
  setOpacity(wallSouth, 0.92);

  setOpacity(mazeGrid, lerp(0.06, 0, settle));
  setOpacity(resolutionHalo, lerp(0.16, 0.28, settle));
  setOpacity(resolutionFrame, lerp(0.24, 0.72, settle));
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
