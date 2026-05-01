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
const candidateSkew = document.getElementById("candidate-skew");
const candidateRails = document.getElementById("candidate-rails");
const candidateCross = document.getElementById("candidate-cross");
const tensionAxis = document.getElementById("tension-axis");
const tensionPanelTop = document.getElementById("tension-panel-top");
const tensionPanelRight = document.getElementById("tension-panel-right");
const tensionPanelBottom = document.getElementById("tension-panel-bottom");
const tensionPanelLeft = document.getElementById("tension-panel-left");
const tensionHalo = document.getElementById("tension-halo");
const alignmentBase = document.getElementById("alignment-base");
const alignmentActive = document.getElementById("alignment-active");
const slotTop = document.getElementById("slot-top");
const slotRight = document.getElementById("slot-right");
const slotBottom = document.getElementById("slot-bottom");
const slotLeft = document.getElementById("slot-left");
const beamTop = document.getElementById("beam-top");
const beamRight = document.getElementById("beam-right");
const beamBottom = document.getElementById("beam-bottom");
const beamLeft = document.getElementById("beam-left");
const memoryArc = document.getElementById("memory-arc");
const resolutionFrame = document.getElementById("resolution-frame");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ALIGNMENT_LENGTH = alignmentActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 562, y: 450 },
  skew: { x: 648, y: 344 },
  rails: { x: 840, y: 304 },
  cross: { x: 1014, y: 410 },
  gate: { x: 820, y: 450 },
};

const system = {
  top: { x: 820, y: 318 },
  right: { x: 980, y: 450 },
  bottom: { x: 820, y: 582 },
  left: { x: 660, y: 450 },
  settleTop: { x: 820, y: 340 },
  settleRight: { x: 958, y: 450 },
  settleBottom: { x: 820, y: 560 },
  settleLeft: { x: 682, y: 450 },
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
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 220).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function pointOnAlignment(progress) {
  const length = clamp(progress, 0, 1) * ALIGNMENT_LENGTH;
  const point = alignmentActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function beamState(progress, threshold) {
  return clamp((progress - threshold) / 0.12, 0, 1);
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
    search: 44,
    tension: 14,
    transformation: 6,
    resolution: -4,
  };
  sceneRoot.setAttribute("transform", `translate(0 ${(offsets[phaseId] ?? 0).toFixed(2)})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 132, y: 142, width: 1080, height: 636 },
    search: { x: 176, y: 138, width: 1088, height: 632 },
    tension: { x: 334, y: 154, width: 968, height: 612 },
    transformation: { x: 402, y: 166, width: 852, height: 590 },
    resolution: { x: 432, y: 174, width: 780, height: 566 },
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

  setGroupTransform(candidateSkew, points.skew.x, points.skew.y, 1, -6);
  setGroupTransform(candidateRails, points.rails.x, points.rails.y, 1, 0);
  setGroupTransform(candidateCross, points.cross.x, points.cross.y, 1, 6);
  [candidateSkew, candidateRails, candidateCross].forEach((element) => setOpacity(element, 0));

  setOpacity(tensionAxis, 0);
  setOpacity(tensionHalo, 0);
  setGroupTransform(tensionPanelTop, points.gate.x, points.gate.y - 108, 1, -8);
  setGroupTransform(tensionPanelRight, points.gate.x + 106, points.gate.y, 1, 4);
  setGroupTransform(tensionPanelBottom, points.gate.x, points.gate.y + 108, 1, 8);
  setGroupTransform(tensionPanelLeft, points.gate.x - 106, points.gate.y, 1, -4);
  [tensionPanelTop, tensionPanelRight, tensionPanelBottom, tensionPanelLeft].forEach((element) => setOpacity(element, 0));

  setOpacity(alignmentBase, 0);
  setPathWindow(alignmentActive, ALIGNMENT_LENGTH, 0, 0);

  [slotTop, slotRight, slotBottom, slotLeft].forEach((slot) => setOpacity(slot, 0));
  setGroupTransform(slotTop, system.top.x, system.top.y, 1, 0);
  setGroupTransform(slotRight, system.right.x, system.right.y, 1, 0);
  setGroupTransform(slotBottom, system.bottom.x, system.bottom.y, 1, 0);
  setGroupTransform(slotLeft, system.left.x, system.left.y, 1, 0);

  [beamTop, beamRight, beamBottom, beamLeft].forEach((beam) => setOpacity(beam, 0));
  setGroupTransform(beamTop, system.top.x, system.top.y, 1, 0);
  setGroupTransform(beamRight, system.right.x, system.right.y, 1, 0);
  setGroupTransform(beamBottom, system.bottom.x, system.bottom.y, 1, 0);
  setGroupTransform(beamLeft, system.left.x, system.left.y, 1, 0);

  setOpacity(memoryArc, 0);
  setOpacity(resolutionFrame, 0);
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

  const preview = clamp((progress - 0.44) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.16);
  setOpacity(candidateSkew, preview * 0.12);
  setOpacity(candidateRails, preview * 0.08);
  setOpacity(candidateCross, preview * 0.06);
  setOpacity(tensionAxis, preview * 0.1);
  setOpacity(tensionPanelTop, preview * 0.06);
  setOpacity(tensionPanelRight, preview * 0.05);
  setOpacity(tensionPanelBottom, preview * 0.05);
  setOpacity(tensionPanelLeft, preview * 0.05);
  setOpacity(tensionHalo, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.skew },
    { start: 0.28, end: 0.58, from: points.skew, to: points.rails },
    { start: 0.58, end: 0.84, from: points.rails, to: points.cross },
    { start: 0.84, end: 1, from: points.cross, to: { x: 928, y: 444 } },
  ]);

  setDot(position, 18, 86, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.12, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.28, 0.16, progress));

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

  setGroupTransform(candidateSkew, points.skew.x, points.skew.y, lerp(0.88, activeA ? 1.05 : 0.96, revealA), -8);
  setGroupTransform(candidateRails, points.rails.x, points.rails.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateCross, points.cross.x, points.cross.y, lerp(0.86, activeC ? 1.04 : 0.95, revealC), 6);
  setOpacity(candidateSkew, activeA ? 1 : revealA * 0.32 + 0.14);
  setOpacity(candidateRails, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateCross, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(tensionAxis, 0.12);
  setOpacity(tensionPanelTop, 0.05);
  setOpacity(tensionPanelRight, 0.04);
  setOpacity(tensionPanelBottom, 0.04);
  setOpacity(tensionPanelLeft, 0.04);
  setOpacity(tensionHalo, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.cross, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.72, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(86, 114, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.58, compression),
    lerp(1, 1.68, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.16, 0, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const skewPosition = mixPoint(points.skew, { x: 736, y: 400 }, collapse);
  const railsPosition = mixPoint(points.rails, { x: 820, y: 350 }, collapse);
  const crossPosition = mixPoint(points.cross, { x: 908, y: 414 }, collapse);
  setGroupTransform(candidateSkew, skewPosition.x, skewPosition.y, lerp(0.96, 0.72, collapse), -16);
  setGroupTransform(candidateRails, railsPosition.x, railsPosition.y, lerp(0.96, 0.68, collapse), 0);
  setGroupTransform(candidateCross, crossPosition.x, crossPosition.y, lerp(0.95, 0.68, collapse), 12);
  setOpacity(candidateSkew, lerp(0.3, 0.06, collapse));
  setOpacity(candidateRails, lerp(0.28, 0.05, collapse));
  setOpacity(candidateCross, lerp(1, 0.12, collapse));

  const panelPull = easeInOut(clamp(progress / 0.68, 0, 1));
  setOpacity(tensionAxis, clamp((progress - 0.04) * 1.7, 0, 0.78));
  setOpacity(tensionHalo, clamp((progress - 0.08) * 1.6, 0, 0.44));
  setOpacity(tensionPanelTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(tensionPanelRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(tensionPanelBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(tensionPanelLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setGroupTransform(
    tensionPanelTop,
    points.gate.x + lerp(-20, 0, panelPull),
    points.gate.y - lerp(108, 54, panelPull),
    1,
    lerp(-8, -4, panelPull),
  );
  setGroupTransform(
    tensionPanelRight,
    points.gate.x + lerp(106, 54, panelPull),
    points.gate.y + lerp(-16, 0, panelPull),
    1,
    lerp(4, 2, panelPull),
  );
  setGroupTransform(
    tensionPanelBottom,
    points.gate.x + lerp(20, 0, panelPull),
    points.gate.y + lerp(108, 54, panelPull),
    1,
    lerp(8, 4, panelPull),
  );
  setGroupTransform(
    tensionPanelLeft,
    points.gate.x - lerp(106, 54, panelPull),
    points.gate.y + lerp(16, 0, panelPull),
    1,
    lerp(-4, -2, panelPull),
  );

  setOpacity(slotTop, clamp((progress - 0.44) * 1.3, 0, 0.24));
  setOpacity(slotRight, clamp((progress - 0.54) * 1.3, 0, 0.24));
  setOpacity(slotBottom, clamp((progress - 0.64) * 1.3, 0, 0.24));
  setOpacity(slotLeft, clamp((progress - 0.74) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnAlignment(routeProgress);
  const topReveal = beamState(routeProgress, 0.1);
  const rightReveal = beamState(routeProgress, 0.34);
  const bottomReveal = beamState(routeProgress, 0.56);
  const leftReveal = beamState(routeProgress, 0.78);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(alignmentBase, lerp(0.08, 0.28, routeProgress));
  setPathWindow(alignmentActive, ALIGNMENT_LENGTH, ALIGNMENT_LENGTH * routeProgress, 1);

  setOpacity(tensionAxis, lerp(0.78, 0.08, progress));
  setOpacity(tensionHalo, clamp(0.44 - progress * 0.5, 0, 1));
  [tensionPanelTop, tensionPanelRight, tensionPanelBottom, tensionPanelLeft].forEach((element) =>
    setOpacity(element, clamp(1 - progress * 1.1, 0, 1)),
  );
  setGroupTransform(tensionPanelTop, points.gate.x, points.gate.y - lerp(54, 82, progress), 1, -2);
  setGroupTransform(tensionPanelRight, points.gate.x + lerp(54, 88, progress), points.gate.y, 1, 2);
  setGroupTransform(tensionPanelBottom, points.gate.x, points.gate.y + lerp(54, 82, progress), 1, 2);
  setGroupTransform(tensionPanelLeft, points.gate.x - lerp(54, 88, progress), points.gate.y, 1, -2);

  [candidateSkew, candidateRails, candidateCross].forEach((element, index) =>
    setOpacity(element, clamp((index === 2 ? 0.12 : 0.06) - progress * 0.16, 0, 1)),
  );
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotTop, slotState(routeProgress, 0.1));
  setOpacity(slotRight, slotState(routeProgress, 0.34));
  setOpacity(slotBottom, slotState(routeProgress, 0.56));
  setOpacity(slotLeft, slotState(routeProgress, 0.78));

  setGroupTransform(beamTop, system.top.x, system.top.y, lerp(0.88, 1, easeOut(topReveal)), 0);
  setGroupTransform(beamRight, system.right.x, system.right.y, lerp(0.88, 1, easeOut(rightReveal)), 0);
  setGroupTransform(beamBottom, system.bottom.x, system.bottom.y, lerp(0.88, 1, easeOut(bottomReveal)), 0);
  setGroupTransform(beamLeft, system.left.x, system.left.y, lerp(0.88, 1, easeOut(leftReveal)), 0);
  setOpacity(beamTop, topReveal);
  setOpacity(beamRight, rightReveal);
  setOpacity(beamBottom, bottomReveal);
  setOpacity(beamLeft, leftReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.64) * 1.4, 0, 0.18));
  setOpacity(resolutionRing, clamp((progress - 0.72) * 1.5, 0, 0.22));
  setOpacity(memoryArc, clamp((progress - 0.78) * 1.6, 0, 0.12));
  setOpacity(resolutionFrame, clamp((progress - 0.76) * 1.6, 0, 0.12));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(alignmentBase, lerp(0.28, 0.18, settle));
  setPathWindow(alignmentActive, ALIGNMENT_LENGTH, ALIGNMENT_LENGTH, lerp(1, 0.2, settle));

  [
    tensionAxis,
    tensionPanelTop,
    tensionPanelRight,
    tensionPanelBottom,
    tensionPanelLeft,
    tensionHalo,
    candidateSkew,
    candidateRails,
    candidateCross,
    slotTop,
    slotRight,
    slotBottom,
    slotLeft,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(
    beamTop,
    lerp(system.top.x, system.settleTop.x, settle),
    lerp(system.top.y, system.settleTop.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    beamRight,
    lerp(system.right.x, system.settleRight.x, settle),
    lerp(system.right.y, system.settleRight.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    beamBottom,
    lerp(system.bottom.x, system.settleBottom.x, settle),
    lerp(system.bottom.y, system.settleBottom.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    beamLeft,
    lerp(system.left.x, system.settleLeft.x, settle),
    lerp(system.left.y, system.settleLeft.y, settle),
    0.97,
    0,
  );
  setOpacity(beamTop, 0.92);
  setOpacity(beamRight, 0.92);
  setOpacity(beamBottom, 0.92);
  setOpacity(beamLeft, 0.92);

  setOpacity(resolutionHalo, lerp(0.18, 0.3, settle));
  setOpacity(resolutionRing, lerp(0.22, 0.88, settle));
  setOpacity(memoryArc, lerp(0.12, 0.34, settle));
  setOpacity(resolutionFrame, lerp(0.12, 0.4, settle));
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
