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
const candidateSlip = document.getElementById("candidate-slip");
const candidateRing = document.getElementById("candidate-ring");
const candidateBasin = document.getElementById("candidate-basin");
const channelLeft = document.getElementById("channel-left");
const channelRight = document.getElementById("channel-right");
const channelTop = document.getElementById("channel-top");
const channelBottom = document.getElementById("channel-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const basinShell = document.getElementById("basin-shell");
const basinBase = document.getElementById("basin-base");
const basinTrace = document.getElementById("basin-trace");
const waterline = document.getElementById("waterline");
const dockSlotLeft = document.getElementById("dock-slot-left");
const dockSlotCenter = document.getElementById("dock-slot-center");
const dockSlotRight = document.getElementById("dock-slot-right");
const dockPierLeft = document.getElementById("dock-pier-left");
const dockPierCenter = document.getElementById("dock-pier-center");
const dockPierRight = document.getElementById("dock-pier-right");
const innerRing = document.getElementById("inner-ring");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const BASIN_TRACE_LENGTH = basinTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 320, y: 450 },
  ingress: { x: 538, y: 450 },
  slipCandidate: { x: 642, y: 376 },
  ringCandidate: { x: 828, y: 352 },
  basinCandidate: { x: 1008, y: 396 },
  channelApproach: { x: 934, y: 450 },
  channelCenter: { x: 820, y: 450 },
  basinCenter: { x: 820, y: 450 },
};

const dockTargets = {
  left: { x: 760, y: 468, settleX: 768, settleY: 462 },
  center: { x: 820, y: 512, settleX: 820, settleY: 498 },
  right: { x: 880, y: 468, settleX: 872, settleY: 462 },
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
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 240).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function setLine(line, x1, y1, x2, y2) {
  line.setAttribute("x1", x1.toFixed(2));
  line.setAttribute("y1", y1.toFixed(2));
  line.setAttribute("x2", x2.toFixed(2));
  line.setAttribute("y2", y2.toFixed(2));
}

function pointOnBasin(progress) {
  const length = clamp(progress, 0, 1) * BASIN_TRACE_LENGTH;
  const point = basinTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function dockSlotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.28;
  }
  return clamp(1 - (progress - threshold) / 0.2, 0, 1) * 0.32;
}

function dockReveal(progress, threshold) {
  return easeOut(clamp((progress - threshold) / 0.18, 0, 1));
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
    search: 32,
    tension: 10,
    transformation: 4,
    resolution: -2,
  };
  const offsetY = offsets[phaseId] ?? 0;
  const portraitScales = {
    tension: 0.92,
    transformation: 0.86,
    resolution: 0.64,
  };
  const portraitScale = svg.dataset.layout === "portrait" ? (portraitScales[phaseId] ?? 1) : 1;
  const scaleTransform =
    portraitScale === 1 ? "" : ` translate(820 450) scale(${portraitScale}) translate(-820 -450)`;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})${scaleTransform}`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 128, y: 144, width: 1094, height: 632 },
    search: { x: 146, y: 130, width: 1110, height: 648 },
    tension: { x: 332, y: 150, width: 980, height: 624 },
    transformation: { x: 346, y: 126, width: 962, height: 650 },
    resolution: { x: 384, y: 132, width: 924, height: 642 },
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

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateSlip, points.slipCandidate.x, points.slipCandidate.y, 1, -3);
  setGroupTransform(candidateRing, points.ringCandidate.x, points.ringCandidate.y, 1, 0);
  setGroupTransform(candidateBasin, points.basinCandidate.x, points.basinCandidate.y, 1, 4);
  [candidateSlip, candidateRing, candidateBasin].forEach((element) => setOpacity(element, 0));

  setGroupTransform(channelLeft, 694, 450, 1, 0);
  setGroupTransform(channelRight, 946, 450, 1, 0);
  setOpacity(channelLeft, 0);
  setOpacity(channelRight, 0);
  setOpacity(channelTop, 0);
  setOpacity(channelBottom, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(basinShell, 0);
  setOpacity(basinBase, 0);
  setPathWindow(basinTrace, BASIN_TRACE_LENGTH, 0, 0);
  setOpacity(waterline, 0);

  setGroupTransform(dockSlotLeft, dockTargets.left.x, dockTargets.left.y, 1, 0);
  setGroupTransform(dockSlotCenter, dockTargets.center.x, dockTargets.center.y, 1, 0);
  setGroupTransform(dockSlotRight, dockTargets.right.x, dockTargets.right.y, 1, 0);
  [dockSlotLeft, dockSlotCenter, dockSlotRight].forEach((slot) => setOpacity(slot, 0));

  setLine(dockPierLeft, dockTargets.left.x, 338, dockTargets.left.x, 338);
  setLine(dockPierCenter, dockTargets.center.x, 338, dockTargets.center.x, 338);
  setLine(dockPierRight, dockTargets.right.x, 338, dockTargets.right.x, 338);
  setOpacity(dockPierLeft, 0);
  setOpacity(dockPierCenter, 0);
  setOpacity(dockPierRight, 0);

  setOpacity(innerRing, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);
  const preview = clamp(0.56 + progress * 0.96, 0, 1);

  setDot(
    position,
    lerp(9, 18, eased),
    lerp(36, 84, eased),
    clamp(0.34 + progress * 1.5, 0, 1),
    0.12 + pulseWave(progress, 1.2) * 0.12,
  );

  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));
  setOpacity(searchGuideA, preview * 0.22);
  setOpacity(candidateSlip, preview * 0.18);
  setOpacity(candidateRing, preview * 0.12);
  setOpacity(candidateBasin, preview * 0.1);

  setOpacity(channelLeft, preview * 0.08);
  setOpacity(channelRight, preview * 0.08);
  setOpacity(channelTop, preview * 0.1);
  setOpacity(channelBottom, preview * 0.1);
  setOpacity(pressureHalo, preview * 0.08);

  setOpacity(basinShell, preview * 0.08);
  setOpacity(basinBase, preview * 0.1);
  setOpacity(waterline, preview * 0.08);
  setOpacity(dockSlotLeft, preview * 0.12);
  setOpacity(dockSlotCenter, preview * 0.1);
  setOpacity(dockSlotRight, preview * 0.12);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.slipCandidate },
    { start: 0.28, end: 0.58, from: points.slipCandidate, to: points.ringCandidate },
    { start: 0.58, end: 0.84, from: points.ringCandidate, to: points.basinCandidate },
    { start: 0.84, end: 1, from: points.basinCandidate, to: points.channelApproach },
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
  setOpacity(searchGuideA, 0.24 + revealA * 0.18);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateSlip, points.slipCandidate.x, points.slipCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -3);
  setGroupTransform(candidateRing, points.ringCandidate.x, points.ringCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateBasin, points.basinCandidate.x, points.basinCandidate.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 4);
  setOpacity(candidateSlip, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateRing, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateBasin, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(channelLeft, 0.08);
  setOpacity(channelRight, 0.08);
  setOpacity(channelTop, 0.1);
  setOpacity(channelBottom, 0.1);
  setOpacity(pressureHalo, 0.08);
  setOpacity(basinShell, 0.06);
  setOpacity(basinBase, 0.08);
  setOpacity(waterline, 0.08);
  setOpacity(dockSlotLeft, 0.12);
  setOpacity(dockSlotCenter, 0.1);
  setOpacity(dockSlotRight, 0.12);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.channelApproach, points.channelCenter, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const gap = lerp(126, 74, easeInOut(clamp(progress / 0.72, 0, 1)));
  const collapse = clamp(progress / 0.72, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.46, compression),
    lerp(1, 1.9, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const slipPosition = mixPoint(points.slipCandidate, { x: 716, y: 392 }, collapse);
  const ringPosition = mixPoint(points.ringCandidate, { x: 808, y: 362 }, collapse);
  const basinPosition = mixPoint(points.basinCandidate, { x: 892, y: 396 }, collapse);
  setGroupTransform(candidateSlip, slipPosition.x, slipPosition.y, lerp(0.96, 0.72, collapse), -6);
  setGroupTransform(candidateRing, ringPosition.x, ringPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateBasin, basinPosition.x, basinPosition.y, lerp(0.95, 0.68, collapse), 6);
  setOpacity(candidateSlip, lerp(0.3, 0.05, collapse));
  setOpacity(candidateRing, lerp(0.28, 0.05, collapse));
  setOpacity(candidateBasin, lerp(1, 0.12, collapse));

  setGroupTransform(channelLeft, 820 - gap, 450, 1, 0);
  setGroupTransform(channelRight, 820 + gap, 450, 1, 0);
  setOpacity(channelLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(channelRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(channelTop, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(channelBottom, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));

  setOpacity(basinShell, clamp((progress - 0.46) * 0.46, 0, 0.16));
  setOpacity(basinBase, clamp((progress - 0.54) * 0.42, 0, 0.16));
  setOpacity(waterline, clamp((progress - 0.66) * 0.4, 0, 0.12));
  setOpacity(dockSlotLeft, clamp((progress - 0.44) * 1.2, 0, 0.22));
  setOpacity(dockSlotCenter, clamp((progress - 0.56) * 1.2, 0, 0.22));
  setOpacity(dockSlotRight, clamp((progress - 0.68) * 1.2, 0, 0.22));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.9, 0, 1));
  const position = pointOnBasin(routeProgress);
  const revealLeft = dockReveal(routeProgress, 0.24);
  const revealCenter = dockReveal(routeProgress, 0.52);
  const revealRight = dockReveal(routeProgress, 0.78);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(basinShell, lerp(0.24, 0.98, routeProgress));
  setOpacity(basinBase, lerp(0.16, 0.32, routeProgress));
  setPathWindow(basinTrace, BASIN_TRACE_LENGTH, BASIN_TRACE_LENGTH * routeProgress, 1);
  setOpacity(waterline, clamp((progress - 0.58) * 1.3, 0, 0.2));

  setOpacity(channelLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(channelRight, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(channelTop, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(channelBottom, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));

  setOpacity(candidateSlip, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateRing, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateBasin, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(dockSlotLeft, dockSlotState(routeProgress, 0.24));
  setOpacity(dockSlotCenter, dockSlotState(routeProgress, 0.52));
  setOpacity(dockSlotRight, dockSlotState(routeProgress, 0.78));

  setOpacity(dockPierLeft, revealLeft);
  setOpacity(dockPierCenter, revealCenter);
  setOpacity(dockPierRight, revealRight);
  setLine(dockPierLeft, dockTargets.left.x, 338, dockTargets.left.x, lerp(338, dockTargets.left.y, revealLeft));
  setLine(dockPierCenter, dockTargets.center.x, 338, dockTargets.center.x, lerp(338, dockTargets.center.y, revealCenter));
  setLine(dockPierRight, dockTargets.right.x, 338, dockTargets.right.x, lerp(338, dockTargets.right.y, revealRight));

  setOpacity(innerRing, clamp((progress - 0.7) * 1.4, 0, 0.3));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.82) * 1.6, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.basinCenter, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(basinShell, 1);
  setOpacity(basinBase, lerp(0.32, 0.28, settle));
  setPathWindow(basinTrace, BASIN_TRACE_LENGTH, BASIN_TRACE_LENGTH, lerp(1, 0.12, settle));
  setOpacity(waterline, lerp(0.2, 0.18, settle));

  [
    channelLeft,
    channelRight,
    channelTop,
    channelBottom,
    pressureHalo,
    candidateSlip,
    candidateRing,
    candidateBasin,
    dockSlotLeft,
    dockSlotCenter,
    dockSlotRight,
  ].forEach((element) => setOpacity(element, 0));

  setOpacity(dockPierLeft, 0.92);
  setOpacity(dockPierCenter, 0.94);
  setOpacity(dockPierRight, 0.92);
  setLine(
    dockPierLeft,
    lerp(dockTargets.left.x, dockTargets.left.settleX, settle),
    338,
    lerp(dockTargets.left.x, dockTargets.left.settleX, settle),
    lerp(dockTargets.left.y, dockTargets.left.settleY, settle),
  );
  setLine(
    dockPierCenter,
    dockTargets.center.x,
    338,
    dockTargets.center.x,
    lerp(dockTargets.center.y, dockTargets.center.settleY, settle),
  );
  setLine(
    dockPierRight,
    lerp(dockTargets.right.x, dockTargets.right.settleX, settle),
    338,
    lerp(dockTargets.right.x, dockTargets.right.settleX, settle),
    lerp(dockTargets.right.y, dockTargets.right.settleY, settle),
  );

  setOpacity(innerRing, lerp(0.3, 0.72, settle));
  setOpacity(resolutionHalo, lerp(0.16, 0.22, settle));
  setOpacity(resolutionFrame, lerp(0.22, 0.58, settle));
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
