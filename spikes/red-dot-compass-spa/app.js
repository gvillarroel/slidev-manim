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
const candidateDiagonal = document.getElementById("candidate-diagonal");
const candidateOrbit = document.getElementById("candidate-orbit");
const candidateAxis = document.getElementById("candidate-axis");
const hingeSpine = document.getElementById("hinge-spine");
const hingeTop = document.getElementById("hinge-top");
const hingeBottom = document.getElementById("hinge-bottom");
const hingeHalo = document.getElementById("hinge-halo");
const compassBase = document.getElementById("compass-base");
const compassActive = document.getElementById("compass-active");
const slotNorth = document.getElementById("slot-north");
const slotEast = document.getElementById("slot-east");
const slotSouth = document.getElementById("slot-south");
const slotWest = document.getElementById("slot-west");
const markerNorth = document.getElementById("marker-north");
const markerEast = document.getElementById("marker-east");
const markerSouth = document.getElementById("marker-south");
const markerWest = document.getElementById("marker-west");
const memoryArc = document.getElementById("memory-arc");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const COMPASS_LENGTH = compassActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 560, y: 450 },
  diagonal: { x: 646, y: 328 },
  orbit: { x: 998, y: 344 },
  axis: { x: 820, y: 620 },
  gate: { x: 820, y: 450 },
};

const system = {
  north: { x: 820, y: 318 },
  east: { x: 990, y: 450 },
  south: { x: 820, y: 582 },
  west: { x: 650, y: 450 },
  settleNorth: { x: 820, y: 334 },
  settleEast: { x: 970, y: 450 },
  settleSouth: { x: 820, y: 566 },
  settleWest: { x: 670, y: 450 },
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

function pointOnCompass(progress) {
  const length = clamp(progress, 0, 1) * COMPASS_LENGTH;
  const point = compassActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.44;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.44;
}

function markerState(progress, threshold) {
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
    search: 30,
    tension: 18,
    transformation: 8,
    resolution: -4,
  };
  const offsetY = offsets[phaseId] ?? -4;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 136, y: 148, width: 1088, height: 628 },
    search: { x: 120, y: 132, width: 1188, height: 670 },
    tension: { x: 334, y: 154, width: 972, height: 620 },
    transformation: { x: 404, y: 150, width: 846, height: 624 },
    resolution: { x: 448, y: 166, width: 780, height: 584 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -16) translate(800 450) scale(1.032) translate(-800 -450)",
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

  setGroupTransform(candidateDiagonal, points.diagonal.x, points.diagonal.y, 1, -8);
  setGroupTransform(candidateOrbit, points.orbit.x, points.orbit.y, 1, 0);
  setGroupTransform(candidateAxis, points.axis.x, points.axis.y, 1, 0);
  [candidateDiagonal, candidateOrbit, candidateAxis].forEach((element) => setOpacity(element, 0));

  setOpacity(hingeSpine, 0);
  setGroupTransform(hingeTop, points.gate.x, points.gate.y - 74, 1, 0);
  setGroupTransform(hingeBottom, points.gate.x, points.gate.y + 74, 1, 0);
  setOpacity(hingeTop, 0);
  setOpacity(hingeBottom, 0);
  setOpacity(hingeHalo, 0);

  setOpacity(compassBase, 0);
  setPathWindow(compassActive, COMPASS_LENGTH, 0, 0);

  setGroupTransform(slotNorth, system.north.x, system.north.y, 1, 0);
  setGroupTransform(slotEast, system.east.x, system.east.y, 1, 0);
  setGroupTransform(slotSouth, system.south.x, system.south.y, 1, 0);
  setGroupTransform(slotWest, system.west.x, system.west.y, 1, 0);
  [slotNorth, slotEast, slotSouth, slotWest].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(markerNorth, system.north.x, system.north.y, 1, 0);
  setGroupTransform(markerEast, system.east.x, system.east.y, 1, 0);
  setGroupTransform(markerSouth, system.south.x, system.south.y, 1, 0);
  setGroupTransform(markerWest, system.west.x, system.west.y, 1, 0);
  [markerNorth, markerEast, markerSouth, markerWest].forEach((marker) => setOpacity(marker, 0));

  setOpacity(memoryArc, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRing, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.94);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.38) * 1.95, 0, 1);
  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(candidateDiagonal, preview * 0.16);
  setOpacity(candidateOrbit, preview * 0.12);
  setOpacity(candidateAxis, preview * 0.1);
  setOpacity(hingeSpine, preview * 0.1);
  setOpacity(hingeTop, preview * 0.1);
  setOpacity(hingeBottom, preview * 0.1);
  setOpacity(hingeHalo, preview * 0.1);
  setOpacity(slotNorth, preview * 0.07);
  setOpacity(slotEast, preview * 0.07);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.diagonal },
    { start: 0.28, end: 0.58, from: points.diagonal, to: points.orbit },
    { start: 0.58, end: 0.84, from: points.orbit, to: points.axis },
    { start: 0.84, end: 1, from: points.axis, to: { x: 844, y: 532 } },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.12, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.26, 0.14, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.24) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.54) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.24 + revealA * 0.2);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateDiagonal, points.diagonal.x, points.diagonal.y, lerp(0.88, activeA ? 1.06 : 0.96, revealA), -8);
  setGroupTransform(candidateOrbit, points.orbit.x, points.orbit.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateAxis, points.axis.x, points.axis.y, lerp(0.84, activeC ? 1.04 : 0.95, revealC), 0);
  setOpacity(candidateDiagonal, activeA ? 1 : revealA * 0.34 + 0.16);
  setOpacity(candidateOrbit, activeB ? 1 : revealB * 0.34 + 0.16);
  setOpacity(candidateAxis, activeC ? 1 : revealC * 0.34 + 0.14);

  setOpacity(hingeSpine, 0.08);
  setOpacity(hingeTop, 0.06);
  setOpacity(hingeBottom, 0.06);
  setOpacity(hingeHalo, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.axis, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const hingeGap = lerp(74, 26, easeInOut(clamp(progress / 0.72, 0, 1)));
  const collapse = clamp(progress / 0.74, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 116, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 1.58, compression),
    lerp(1, 0.58, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const diagonalPosition = mixPoint(points.diagonal, { x: 738, y: 382 }, collapse);
  const orbitPosition = mixPoint(points.orbit, { x: 900, y: 378 }, collapse);
  const axisPosition = mixPoint(points.axis, { x: 820, y: 548 }, collapse);
  setGroupTransform(candidateDiagonal, diagonalPosition.x, diagonalPosition.y, lerp(0.96, 0.72, collapse), -12);
  setGroupTransform(candidateOrbit, orbitPosition.x, orbitPosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateAxis, axisPosition.x, axisPosition.y, lerp(0.95, 0.68, collapse), 0);
  setOpacity(candidateDiagonal, lerp(0.32, 0.06, collapse));
  setOpacity(candidateOrbit, lerp(0.32, 0.06, collapse));
  setOpacity(candidateAxis, lerp(1, 0.14, collapse));

  setOpacity(hingeSpine, clamp((progress - 0.04) * 1.6, 0, 0.76));
  setOpacity(hingeTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(hingeBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(hingeHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(hingeTop, points.gate.x, points.gate.y - hingeGap, 1, 0);
  setGroupTransform(hingeBottom, points.gate.x, points.gate.y + hingeGap, 1, 0);

  setOpacity(slotNorth, clamp((progress - 0.42) * 1.3, 0, 0.24));
  setOpacity(slotEast, clamp((progress - 0.54) * 1.3, 0, 0.24));
  setOpacity(slotSouth, clamp((progress - 0.66) * 1.3, 0, 0.24));
  setOpacity(slotWest, clamp((progress - 0.76) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.9, 0, 1));
  const position = pointOnCompass(routeProgress);
  const northReveal = markerState(routeProgress, 0.13);
  const eastReveal = markerState(routeProgress, 0.36);
  const southReveal = markerState(routeProgress, 0.61);
  const westReveal = markerState(routeProgress, 0.84);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(compassBase, lerp(0.08, 0.28, routeProgress));
  setPathWindow(compassActive, COMPASS_LENGTH, COMPASS_LENGTH * routeProgress, 1);

  setOpacity(hingeSpine, lerp(0.76, 0.08, progress));
  setOpacity(hingeTop, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(hingeBottom, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(hingeHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(hingeTop, points.gate.x, points.gate.y - lerp(26, 46, progress), 1, 0);
  setGroupTransform(hingeBottom, points.gate.x, points.gate.y + lerp(26, 46, progress), 1, 0);

  setOpacity(candidateDiagonal, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateOrbit, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateAxis, clamp(0.14 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotNorth, slotState(routeProgress, 0.12));
  setOpacity(slotEast, slotState(routeProgress, 0.36));
  setOpacity(slotSouth, slotState(routeProgress, 0.61));
  setOpacity(slotWest, slotState(routeProgress, 0.84));

  setGroupTransform(markerNorth, system.north.x, system.north.y, lerp(0.88, 1, easeOut(northReveal)), 0);
  setGroupTransform(markerEast, system.east.x, system.east.y, lerp(0.88, 1, easeOut(eastReveal)), 0);
  setGroupTransform(markerSouth, system.south.x, system.south.y, lerp(0.88, 1, easeOut(southReveal)), 0);
  setGroupTransform(markerWest, system.west.x, system.west.y, lerp(0.88, 1, easeOut(westReveal)), 0);
  setOpacity(markerNorth, northReveal);
  setOpacity(markerEast, eastReveal);
  setOpacity(markerSouth, southReveal);
  setOpacity(markerWest, westReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.62) * 1.4, 0, 0.18));
  setOpacity(resolutionRing, clamp((progress - 0.72) * 1.5, 0, 0.22));
  setOpacity(memoryArc, clamp((progress - 0.78) * 1.4, 0, 0.12));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 98, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(compassBase, lerp(0.28, 0.5, settle));
  setPathWindow(compassActive, COMPASS_LENGTH, COMPASS_LENGTH, lerp(1, 0.24, settle));

  [hingeSpine, hingeTop, hingeBottom, hingeHalo, candidateDiagonal, candidateOrbit, candidateAxis, slotNorth, slotEast, slotSouth, slotWest].forEach(
    (element) => setOpacity(element, 0),
  );

  setGroupTransform(
    markerNorth,
    lerp(system.north.x, system.settleNorth.x, settle),
    lerp(system.north.y, system.settleNorth.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    markerEast,
    lerp(system.east.x, system.settleEast.x, settle),
    lerp(system.east.y, system.settleEast.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    markerSouth,
    lerp(system.south.x, system.settleSouth.x, settle),
    lerp(system.south.y, system.settleSouth.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    markerWest,
    lerp(system.west.x, system.settleWest.x, settle),
    lerp(system.west.y, system.settleWest.y, settle),
    0.97,
    0,
  );
  setOpacity(markerNorth, 0.92);
  setOpacity(markerEast, 0.92);
  setOpacity(markerSouth, 0.92);
  setOpacity(markerWest, 0.92);

  setOpacity(resolutionHalo, lerp(0.18, 0.3, settle));
  setOpacity(resolutionRing, lerp(0.22, 0.9, settle));
  setOpacity(memoryArc, lerp(0.12, 0.24, settle));
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
