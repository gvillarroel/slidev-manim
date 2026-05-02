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
const candidateArc = document.getElementById("candidate-arc");
const candidateCross = document.getElementById("candidate-cross");
const candidateFan = document.getElementById("candidate-fan");
const meridianSpine = document.getElementById("meridian-spine");
const horizonLeft = document.getElementById("horizon-left");
const horizonRight = document.getElementById("horizon-right");
const meridianTop = document.getElementById("meridian-top");
const meridianBottom = document.getElementById("meridian-bottom");
const tensionHalo = document.getElementById("tension-halo");
const roseBase = document.getElementById("rose-base");
const roseActive = document.getElementById("rose-active");
const slotNorth = document.getElementById("slot-north");
const slotEast = document.getElementById("slot-east");
const slotSouth = document.getElementById("slot-south");
const slotWest = document.getElementById("slot-west");
const vaneNorth = document.getElementById("vane-north");
const vaneEast = document.getElementById("vane-east");
const vaneSouth = document.getElementById("vane-south");
const vaneWest = document.getElementById("vane-west");
const memoryAxis = document.getElementById("memory-axis");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ROSE_LENGTH = roseActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 560, y: 450 },
  arc: { x: 648, y: 352 },
  cross: { x: 820, y: 320 },
  fan: { x: 1002, y: 388 },
  gate: { x: 820, y: 450 },
};

const system = {
  north: { x: 820, y: 306 },
  east: { x: 964, y: 450 },
  south: { x: 820, y: 594 },
  west: { x: 676, y: 450 },
  settleNorth: { x: 820, y: 322 },
  settleEast: { x: 928, y: 450 },
  settleSouth: { x: 820, y: 578 },
  settleWest: { x: 712, y: 450 },
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

function pointOnRose(progress) {
  const length = clamp(progress, 0, 1) * ROSE_LENGTH;
  const point = roseActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.44;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.44;
}

function vaneState(progress, threshold) {
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
    search: 54,
    tension: 24,
    transformation: 10,
    resolution: 8,
  };
  const offsetY = offsets[phaseId] ?? 8;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 120, y: 144, width: 1100, height: 620 },
    search: { x: 166, y: 138, width: 1110, height: 628 },
    tension: { x: 336, y: 148, width: 972, height: 620 },
    transformation: { x: 406, y: 160, width: 840, height: 596 },
    resolution: { x: 432, y: 170, width: 786, height: 572 },
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

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateArc, points.arc.x, points.arc.y, 1, 0);
  setGroupTransform(candidateCross, points.cross.x, points.cross.y, 1, 0);
  setGroupTransform(candidateFan, points.fan.x, points.fan.y, 1, 0);
  [candidateArc, candidateCross, candidateFan].forEach((element) => setOpacity(element, 0));

  setOpacity(meridianSpine, 0);
  setOpacity(horizonLeft, 0);
  setOpacity(horizonRight, 0);
  setGroupTransform(meridianTop, points.gate.x, points.gate.y - 92, 1, 0);
  setGroupTransform(meridianBottom, points.gate.x, points.gate.y + 92, 1, 180);
  setOpacity(meridianTop, 0);
  setOpacity(meridianBottom, 0);
  setOpacity(tensionHalo, 0);

  setOpacity(roseBase, 0);
  setPathWindow(roseActive, ROSE_LENGTH, 0, 0);

  [slotNorth, slotEast, slotSouth, slotWest].forEach((slot) => setOpacity(slot, 0));
  setGroupTransform(slotNorth, system.north.x, system.north.y, 1, 0);
  setGroupTransform(slotEast, system.east.x, system.east.y, 1, 0);
  setGroupTransform(slotSouth, system.south.x, system.south.y, 1, 0);
  setGroupTransform(slotWest, system.west.x, system.west.y, 1, 0);

  [vaneNorth, vaneEast, vaneSouth, vaneWest].forEach((vane) => setOpacity(vane, 0));
  setGroupTransform(vaneNorth, system.north.x, system.north.y, 1, 0);
  setGroupTransform(vaneEast, system.east.x, system.east.y, 1, 0);
  setGroupTransform(vaneSouth, system.south.x, system.south.y, 1, 0);
  setGroupTransform(vaneWest, system.west.x, system.west.y, 1, 0);

  setOpacity(memoryAxis, 0);
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

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.14);
  setOpacity(candidateArc, preview * 0.12);
  setOpacity(candidateCross, preview * 0.08);
  setOpacity(candidateFan, preview * 0.06);
  setOpacity(meridianSpine, preview * 0.08);
  setOpacity(horizonLeft, preview * 0.06);
  setOpacity(horizonRight, preview * 0.06);
  setOpacity(meridianTop, preview * 0.08);
  setOpacity(meridianBottom, preview * 0.08);
  setOpacity(tensionHalo, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.arc },
    { start: 0.28, end: 0.58, from: points.arc, to: points.cross },
    { start: 0.58, end: 0.84, from: points.cross, to: points.fan },
    { start: 0.84, end: 1, from: points.fan, to: { x: 924, y: 438 } },
  ]);

  setDot(position, 18, 86, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.12, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.38, 0.22, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.24 + revealA * 0.18);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateArc, points.arc.x, points.arc.y, lerp(0.88, activeA ? 1.05 : 0.96, revealA), -6);
  setGroupTransform(candidateCross, points.cross.x, points.cross.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateFan, points.fan.x, points.fan.y, lerp(0.84, activeC ? 1.04 : 0.95, revealC), 8);
  setOpacity(candidateArc, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateCross, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateFan, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(meridianSpine, 0.1);
  setOpacity(horizonLeft, 0.08);
  setOpacity(horizonRight, 0.08);
  setOpacity(meridianTop, 0.06);
  setOpacity(meridianBottom, 0.06);
  setOpacity(tensionHalo, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.fan, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const gap = lerp(92, 38, easeInOut(clamp(progress / 0.7, 0, 1)));
  const collapse = clamp(progress / 0.72, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(86, 114, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 1.54, compression),
    lerp(1, 0.62, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.14, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const arcPosition = mixPoint(points.arc, { x: 742, y: 408 }, collapse);
  const crossPosition = mixPoint(points.cross, { x: 820, y: 370 }, collapse);
  const fanPosition = mixPoint(points.fan, { x: 902, y: 428 }, collapse);
  setGroupTransform(candidateArc, arcPosition.x, arcPosition.y, lerp(0.96, 0.72, collapse), -12);
  setGroupTransform(candidateCross, crossPosition.x, crossPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateFan, fanPosition.x, fanPosition.y, lerp(0.95, 0.68, collapse), 12);
  setOpacity(candidateArc, lerp(0.3, 0.06, collapse));
  setOpacity(candidateCross, lerp(0.28, 0.05, collapse));
  setOpacity(candidateFan, lerp(1, 0.12, collapse));

  setOpacity(meridianSpine, clamp((progress - 0.04) * 1.7, 0, 0.72));
  setOpacity(horizonLeft, clamp((progress - 0.08) * 1.7, 0, 0.32));
  setOpacity(horizonRight, clamp((progress - 0.08) * 1.7, 0, 0.32));
  setGroupTransform(meridianTop, points.gate.x, points.gate.y - gap, 1, 0);
  setGroupTransform(meridianBottom, points.gate.x, points.gate.y + gap, 1, 180);
  setOpacity(meridianTop, clamp((progress - 0.04) * 1.8, 0, 1));
  setOpacity(meridianBottom, clamp((progress - 0.04) * 1.8, 0, 1));
  setOpacity(tensionHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));

  setOpacity(slotNorth, clamp((progress - 0.4) * 1.35, 0, 0.28));
  setOpacity(slotEast, clamp((progress - 0.52) * 1.35, 0, 0.28));
  setOpacity(slotSouth, clamp((progress - 0.64) * 1.35, 0, 0.28));
  setOpacity(slotWest, clamp((progress - 0.76) * 1.35, 0, 0.28));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnRose(routeProgress);
  const northReveal = vaneState(routeProgress, 0.16);
  const eastReveal = vaneState(routeProgress, 0.38);
  const southReveal = vaneState(routeProgress, 0.6);
  const westReveal = vaneState(routeProgress, 0.8);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  setOpacity(roseBase, lerp(0.08, 0.28, routeProgress));
  setPathWindow(roseActive, ROSE_LENGTH, ROSE_LENGTH * routeProgress, 1);

  setOpacity(meridianSpine, lerp(0.72, 0.1, progress));
  setOpacity(horizonLeft, lerp(0.32, 0.12, progress));
  setOpacity(horizonRight, lerp(0.32, 0.12, progress));
  setGroupTransform(meridianTop, points.gate.x, points.gate.y - lerp(38, 56, progress), 1, 0);
  setGroupTransform(meridianBottom, points.gate.x, points.gate.y + lerp(38, 56, progress), 1, 180);
  setOpacity(meridianTop, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(meridianBottom, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(tensionHalo, clamp(0.42 - progress * 0.5, 0, 1));

  setOpacity(candidateArc, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateCross, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateFan, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotNorth, slotState(routeProgress, 0.16));
  setOpacity(slotEast, slotState(routeProgress, 0.38));
  setOpacity(slotSouth, slotState(routeProgress, 0.6));
  setOpacity(slotWest, slotState(routeProgress, 0.8));

  setGroupTransform(vaneNorth, system.north.x, system.north.y, lerp(0.88, 1, easeOut(northReveal)), 0);
  setGroupTransform(vaneEast, system.east.x, system.east.y, lerp(0.88, 1, easeOut(eastReveal)), 0);
  setGroupTransform(vaneSouth, system.south.x, system.south.y, lerp(0.88, 1, easeOut(southReveal)), 0);
  setGroupTransform(vaneWest, system.west.x, system.west.y, lerp(0.88, 1, easeOut(westReveal)), 0);
  setOpacity(vaneNorth, northReveal);
  setOpacity(vaneEast, eastReveal);
  setOpacity(vaneSouth, southReveal);
  setOpacity(vaneWest, westReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.62) * 1.4, 0, 0.2));
  setOpacity(resolutionRing, clamp((progress - 0.72) * 1.5, 0, 0.26));
  setOpacity(memoryAxis, clamp((progress - 0.8) * 1.5, 0, 0.12));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  setOpacity(roseBase, lerp(0.28, 0.44, settle));
  setPathWindow(roseActive, ROSE_LENGTH, ROSE_LENGTH, lerp(1, 0.22, settle));

  [
    meridianSpine,
    horizonLeft,
    horizonRight,
    meridianTop,
    meridianBottom,
    tensionHalo,
    candidateArc,
    candidateCross,
    candidateFan,
    slotNorth,
    slotEast,
    slotSouth,
    slotWest,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(
    vaneNorth,
    lerp(system.north.x, system.settleNorth.x, settle),
    lerp(system.north.y, system.settleNorth.y, settle),
    0.98,
    0,
  );
  setGroupTransform(
    vaneEast,
    lerp(system.east.x, system.settleEast.x, settle),
    lerp(system.east.y, system.settleEast.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    vaneSouth,
    lerp(system.south.x, system.settleSouth.x, settle),
    lerp(system.south.y, system.settleSouth.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    vaneWest,
    lerp(system.west.x, system.settleWest.x, settle),
    lerp(system.west.y, system.settleWest.y, settle),
    0.97,
    0,
  );
  setOpacity(vaneNorth, 0.96);
  setOpacity(vaneEast, 0.92);
  setOpacity(vaneSouth, 0.9);
  setOpacity(vaneWest, 0.92);

  setOpacity(memoryAxis, lerp(0.12, 0.38, settle));
  setOpacity(resolutionHalo, lerp(0.2, 0.32, settle));
  setOpacity(resolutionRing, lerp(0.26, 0.88, settle));
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
