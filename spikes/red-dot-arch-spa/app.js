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
const candidateLintel = document.getElementById("candidate-lintel");
const candidateGable = document.getElementById("candidate-gable");
const candidateArch = document.getElementById("candidate-arch");
const thresholdGuide = document.getElementById("threshold-guide");
const sillGuide = document.getElementById("sill-guide");
const pressureHalo = document.getElementById("pressure-halo");
const jambLeft = document.getElementById("jamb-left");
const jambRight = document.getElementById("jamb-right");
const crownBlock = document.getElementById("crown-block");
const archShell = document.getElementById("arch-shell");
const archBase = document.getElementById("arch-base");
const archTrace = document.getElementById("arch-trace");
const doorwayBase = document.getElementById("doorway-base");
const doorwayTrace = document.getElementById("doorway-trace");
const slotLeftPier = document.getElementById("slot-left-pier");
const slotCrownLeft = document.getElementById("slot-crown-left");
const slotCrownRight = document.getElementById("slot-crown-right");
const slotRightPier = document.getElementById("slot-right-pier");
const pierLeft = document.getElementById("pier-left");
const crownLeft = document.getElementById("crown-left");
const crownRight = document.getElementById("crown-right");
const pierRight = document.getElementById("pier-right");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ARCH_TRACE_LENGTH = archTrace.getTotalLength();
const DOORWAY_TRACE_LENGTH = doorwayTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 564, y: 450 },
  lintelCandidate: { x: 646, y: 386 },
  gableCandidate: { x: 832, y: 340 },
  archCandidate: { x: 1002, y: 390 },
  thresholdApproach: { x: 934, y: 450 },
  threshold: { x: 820, y: 450 },
};

const arch = {
  center: { x: 820, y: 450 },
  leftPier: { x: 744, y: 470 },
  crownLeft: { x: 772, y: 356 },
  crownRight: { x: 868, y: 356 },
  rightPier: { x: 896, y: 470 },
  squeezeLeftPier: { x: 786, y: 460 },
  squeezeCrownLeft: { x: 800, y: 390 },
  squeezeCrownRight: { x: 840, y: 390 },
  squeezeRightPier: { x: 854, y: 460 },
  settleLeftPier: { x: 736, y: 472 },
  settleCrownLeft: { x: 770, y: 352 },
  settleCrownRight: { x: 870, y: 352 },
  settleRightPier: { x: 904, y: 472 },
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

function pointOnArch(progress) {
  const length = clamp(progress, 0, 1) * ARCH_TRACE_LENGTH;
  const point = archTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function stoneReveal(progress, threshold) {
  return clamp((progress - threshold) / 0.16, 0, 1);
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
    tension: 10,
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
    appearance: { x: 128, y: 142, width: 1088, height: 636 },
    search: { x: 152, y: 124, width: 1110, height: 658 },
    tension: { x: 344, y: 138, width: 952, height: 642 },
    transformation: { x: 336, y: 116, width: 968, height: 668 },
    resolution: { x: 388, y: 132, width: 892, height: 646 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -16) translate(800 450) scale(1.04) translate(-800 -450)",
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

function resetThreshold() {
  setGroupTransform(jambLeft, points.threshold.x - 156, points.threshold.y, 1, 0);
  setGroupTransform(jambRight, points.threshold.x + 156, points.threshold.y, 1, 0);
  setGroupTransform(crownBlock, points.threshold.x, 352, 1, 0);
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateLintel, points.lintelCandidate.x, points.lintelCandidate.y, 1, -4);
  setGroupTransform(candidateGable, points.gableCandidate.x, points.gableCandidate.y, 1, 0);
  setGroupTransform(candidateArch, points.archCandidate.x, points.archCandidate.y, 1, 4);
  [candidateLintel, candidateGable, candidateArch].forEach((element) => setOpacity(element, 0));

  setOpacity(thresholdGuide, 0);
  setOpacity(sillGuide, 0);
  setOpacity(pressureHalo, 0);
  resetThreshold();
  setOpacity(jambLeft, 0);
  setOpacity(jambRight, 0);
  setOpacity(crownBlock, 0);

  setOpacity(archShell, 0);
  setOpacity(archBase, 0);
  setPathWindow(archTrace, ARCH_TRACE_LENGTH, 0, 0);
  setOpacity(doorwayBase, 0);
  setPathWindow(doorwayTrace, DOORWAY_TRACE_LENGTH, 0, 0);

  setGroupTransform(slotLeftPier, arch.leftPier.x, arch.leftPier.y, 1, 0);
  setGroupTransform(slotCrownLeft, arch.crownLeft.x, arch.crownLeft.y, 1, 0);
  setGroupTransform(slotCrownRight, arch.crownRight.x, arch.crownRight.y, 1, 0);
  setGroupTransform(slotRightPier, arch.rightPier.x, arch.rightPier.y, 1, 0);
  [slotLeftPier, slotCrownLeft, slotCrownRight, slotRightPier].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(pierLeft, arch.leftPier.x, arch.leftPier.y, 1, 0);
  setGroupTransform(crownLeft, arch.crownLeft.x, arch.crownLeft.y, 1, 0);
  setGroupTransform(crownRight, arch.crownRight.x, arch.crownRight.y, 1, 0);
  setGroupTransform(pierRight, arch.rightPier.x, arch.rightPier.y, 1, 0);
  [pierLeft, crownLeft, crownRight, pierRight].forEach((stone) => setOpacity(stone, 0));

  setOpacity(anchorGrid, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
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
  setOpacity(candidateLintel, preview * 0.14);
  setOpacity(candidateGable, preview * 0.1);
  setOpacity(candidateArch, preview * 0.08);
  setOpacity(thresholdGuide, preview * 0.08);
  setOpacity(sillGuide, preview * 0.08);
  setOpacity(jambLeft, preview * 0.05);
  setOpacity(jambRight, preview * 0.05);
  setOpacity(crownBlock, preview * 0.05);
  setOpacity(archShell, preview * 0.05);
  setOpacity(archBase, preview * 0.06);
  setOpacity(doorwayBase, preview * 0.05);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.lintelCandidate },
    { start: 0.28, end: 0.58, from: points.lintelCandidate, to: points.gableCandidate },
    { start: 0.58, end: 0.84, from: points.gableCandidate, to: points.archCandidate },
    { start: 0.84, end: 1, from: points.archCandidate, to: points.thresholdApproach },
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

  setGroupTransform(candidateLintel, points.lintelCandidate.x, points.lintelCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateGable, points.gableCandidate.x, points.gableCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateArch, points.archCandidate.x, points.archCandidate.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 4);
  setOpacity(candidateLintel, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateGable, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateArch, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(thresholdGuide, 0.14);
  setOpacity(sillGuide, 0.1);
  setOpacity(jambLeft, 0.06);
  setOpacity(jambRight, 0.06);
  setOpacity(crownBlock, 0.06);
  setOpacity(archShell, 0.05);
  setOpacity(archBase, 0.08);
  setOpacity(doorwayBase, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.thresholdApproach, points.threshold, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.76, 0, 1);
  const gap = lerp(156, 82, easeInOut(clamp(progress / 0.72, 0, 1)));
  const crownY = lerp(352, 378, easeInOut(clamp(progress / 0.7, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.52, compression),
    lerp(1, 1.82, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const lintelPosition = mixPoint(points.lintelCandidate, { x: 730, y: 396 }, collapse);
  const gablePosition = mixPoint(points.gableCandidate, { x: 816, y: 360 }, collapse);
  const archPosition = mixPoint(points.archCandidate, { x: 904, y: 398 }, collapse);
  setGroupTransform(candidateLintel, lintelPosition.x, lintelPosition.y, lerp(0.96, 0.72, collapse), -6);
  setGroupTransform(candidateGable, gablePosition.x, gablePosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateArch, archPosition.x, archPosition.y, lerp(0.95, 0.68, collapse), 6);
  setOpacity(candidateLintel, lerp(0.3, 0.05, collapse));
  setOpacity(candidateGable, lerp(0.28, 0.05, collapse));
  setOpacity(candidateArch, lerp(1, 0.12, collapse));

  setOpacity(thresholdGuide, clamp((progress - 0.04) * 1.7, 0, 0.82));
  setOpacity(sillGuide, clamp((progress - 0.06) * 1.6, 0, 0.84));
  setOpacity(jambLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(jambRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(crownBlock, clamp((progress - 0.08) * 1.6, 0, 0.98));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(jambLeft, points.threshold.x - gap, points.threshold.y, 1, 0);
  setGroupTransform(jambRight, points.threshold.x + gap, points.threshold.y, 1, 0);
  setGroupTransform(crownBlock, points.threshold.x, crownY, 1, 0);

  const stoneEase = easeInOut(clamp(progress / 0.72, 0, 1));
  setGroupTransform(
    pierLeft,
    lerp(arch.leftPier.x, arch.squeezeLeftPier.x, stoneEase),
    lerp(arch.leftPier.y, arch.squeezeLeftPier.y, stoneEase),
    0.96,
    0,
  );
  setGroupTransform(
    crownLeft,
    lerp(arch.crownLeft.x, arch.squeezeCrownLeft.x, stoneEase),
    lerp(arch.crownLeft.y, arch.squeezeCrownLeft.y, stoneEase),
    0.96,
    0,
  );
  setGroupTransform(
    crownRight,
    lerp(arch.crownRight.x, arch.squeezeCrownRight.x, stoneEase),
    lerp(arch.crownRight.y, arch.squeezeCrownRight.y, stoneEase),
    0.96,
    0,
  );
  setGroupTransform(
    pierRight,
    lerp(arch.rightPier.x, arch.squeezeRightPier.x, stoneEase),
    lerp(arch.rightPier.y, arch.squeezeRightPier.y, stoneEase),
    0.96,
    0,
  );
  [pierLeft, crownLeft, crownRight, pierRight].forEach((stone) =>
    setOpacity(stone, clamp((progress - 0.04) * 1.7, 0, 0.98)),
  );

  setOpacity(archShell, clamp((progress - 0.48) * 0.42, 0, 0.16));
  setOpacity(archBase, clamp((progress - 0.54) * 0.4, 0, 0.16));
  setOpacity(doorwayBase, clamp((progress - 0.58) * 0.42, 0, 0.12));
  setOpacity(slotLeftPier, clamp((progress - 0.42) * 1.3, 0, 0.24));
  setOpacity(slotCrownLeft, clamp((progress - 0.52) * 1.3, 0, 0.24));
  setOpacity(slotCrownRight, clamp((progress - 0.62) * 1.3, 0, 0.24));
  setOpacity(slotRightPier, clamp((progress - 0.72) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnArch(routeProgress);
  const leftPierReveal = stoneReveal(routeProgress, 0.18);
  const crownLeftReveal = stoneReveal(routeProgress, 0.42);
  const crownRightReveal = stoneReveal(routeProgress, 0.64);
  const rightPierReveal = stoneReveal(routeProgress, 0.82);
  const doorwayProgress = clamp((routeProgress - 0.56) / 0.32, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(archShell, lerp(0.24, 0.98, routeProgress));
  setOpacity(archBase, lerp(0.14, 0.32, routeProgress));
  setPathWindow(archTrace, ARCH_TRACE_LENGTH, ARCH_TRACE_LENGTH * routeProgress, 1);
  setOpacity(doorwayBase, clamp((progress - 0.34) * 1.2, 0, 0.24));
  setPathWindow(doorwayTrace, DOORWAY_TRACE_LENGTH, DOORWAY_TRACE_LENGTH * doorwayProgress, 0.74 * doorwayProgress);

  setOpacity(thresholdGuide, lerp(0.82, 0.08, progress));
  setOpacity(sillGuide, lerp(0.84, 0.08, progress));
  setOpacity(jambLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(jambRight, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(crownBlock, clamp(0.98 - progress * 1.1, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));

  setOpacity(candidateLintel, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateGable, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateArch, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotLeftPier, slotState(routeProgress, 0.18));
  setOpacity(slotCrownLeft, slotState(routeProgress, 0.42));
  setOpacity(slotCrownRight, slotState(routeProgress, 0.64));
  setOpacity(slotRightPier, slotState(routeProgress, 0.82));

  setGroupTransform(
    pierLeft,
    lerp(arch.squeezeLeftPier.x, arch.leftPier.x, easeOut(leftPierReveal)),
    lerp(arch.squeezeLeftPier.y, arch.leftPier.y, easeOut(leftPierReveal)),
    lerp(0.94, 1, easeOut(leftPierReveal)),
    0,
  );
  setGroupTransform(
    crownLeft,
    lerp(arch.squeezeCrownLeft.x, arch.crownLeft.x, easeOut(crownLeftReveal)),
    lerp(arch.squeezeCrownLeft.y, arch.crownLeft.y, easeOut(crownLeftReveal)),
    lerp(0.94, 1, easeOut(crownLeftReveal)),
    0,
  );
  setGroupTransform(
    crownRight,
    lerp(arch.squeezeCrownRight.x, arch.crownRight.x, easeOut(crownRightReveal)),
    lerp(arch.squeezeCrownRight.y, arch.crownRight.y, easeOut(crownRightReveal)),
    lerp(0.94, 1, easeOut(crownRightReveal)),
    0,
  );
  setGroupTransform(
    pierRight,
    lerp(arch.squeezeRightPier.x, arch.rightPier.x, easeOut(rightPierReveal)),
    lerp(arch.squeezeRightPier.y, arch.rightPier.y, easeOut(rightPierReveal)),
    lerp(0.94, 1, easeOut(rightPierReveal)),
    0,
  );
  setOpacity(pierLeft, lerp(0.72, 1, leftPierReveal));
  setOpacity(crownLeft, lerp(0.72, 1, crownLeftReveal));
  setOpacity(crownRight, lerp(0.72, 1, crownRightReveal));
  setOpacity(pierRight, lerp(0.72, 1, rightPierReveal));

  setOpacity(anchorGrid, clamp((progress - 0.72) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(arch.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(archShell, lerp(0.98, 0.92, settle));
  setOpacity(archBase, lerp(0.32, 0.26, settle));
  setPathWindow(archTrace, ARCH_TRACE_LENGTH, ARCH_TRACE_LENGTH, lerp(1, 0.16, settle));
  setOpacity(doorwayBase, lerp(0.24, 0.3, settle));
  setPathWindow(doorwayTrace, DOORWAY_TRACE_LENGTH, DOORWAY_TRACE_LENGTH, lerp(0.74, 0.22, settle));

  [
    thresholdGuide,
    sillGuide,
    pressureHalo,
    candidateLintel,
    candidateGable,
    candidateArch,
    slotLeftPier,
    slotCrownLeft,
    slotCrownRight,
    slotRightPier,
  ].forEach((element) => setOpacity(element, 0));
  setOpacity(jambLeft, 0);
  setOpacity(jambRight, 0);
  setOpacity(crownBlock, 0);

  setGroupTransform(
    pierLeft,
    lerp(arch.leftPier.x, arch.settleLeftPier.x, settle),
    lerp(arch.leftPier.y, arch.settleLeftPier.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    crownLeft,
    lerp(arch.crownLeft.x, arch.settleCrownLeft.x, settle),
    lerp(arch.crownLeft.y, arch.settleCrownLeft.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    crownRight,
    lerp(arch.crownRight.x, arch.settleCrownRight.x, settle),
    lerp(arch.crownRight.y, arch.settleCrownRight.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    pierRight,
    lerp(arch.rightPier.x, arch.settleRightPier.x, settle),
    lerp(arch.rightPier.y, arch.settleRightPier.y, settle),
    0.97,
    0,
  );
  setOpacity(pierLeft, 0.92);
  setOpacity(crownLeft, 0.92);
  setOpacity(crownRight, 0.92);
  setOpacity(pierRight, 0.9);

  setOpacity(anchorGrid, lerp(0.12, 0.16, settle));
  setOpacity(resolutionHalo, lerp(0.16, 0.26, settle));
  setOpacity(resolutionFrame, lerp(0.24, 0.68, settle));
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
