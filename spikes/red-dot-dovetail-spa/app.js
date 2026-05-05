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
const candidateNotch = document.getElementById("candidate-notch");
const candidateStep = document.getElementById("candidate-step");
const candidateDovetail = document.getElementById("candidate-dovetail");
const throatTop = document.getElementById("throat-top");
const throatBottom = document.getElementById("throat-bottom");
const clampTop = document.getElementById("clamp-top");
const clampBottom = document.getElementById("clamp-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const leftBody = document.getElementById("left-body");
const rightBody = document.getElementById("right-body");
const jointBase = document.getElementById("joint-base");
const jointTrace = document.getElementById("joint-trace");
const slotTopLeft = document.getElementById("slot-top-left");
const slotTopRight = document.getElementById("slot-top-right");
const slotBottomLeft = document.getElementById("slot-bottom-left");
const slotBottomRight = document.getElementById("slot-bottom-right");
const markerTop = document.getElementById("marker-top");
const markerRight = document.getElementById("marker-right");
const markerBottom = document.getElementById("marker-bottom");
const markerLeft = document.getElementById("marker-left");
const anchorTop = document.getElementById("anchor-top");
const anchorBottom = document.getElementById("anchor-bottom");
const seamTop = document.getElementById("seam-top");
const seamBottom = document.getElementById("seam-bottom");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const JOINT_TRACE_LENGTH = jointTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 348, y: 450 },
  ingress: { x: 612, y: 450 },
  notch: { x: 700, y: 392 },
  step: { x: 846, y: 450 },
  dovetail: { x: 954, y: 498 },
  throatApproach: { x: 916, y: 450 },
  throat: { x: 820, y: 450 },
};

const bodies = {
  leftStart: { x: 676, y: 450 },
  rightStart: { x: 964, y: 450 },
  leftSettle: { x: 708, y: 450 },
  rightSettle: { x: 932, y: 450 },
};

const slots = {
  topLeft: { x: 614, y: 350 },
  topRight: { x: 1026, y: 350 },
  bottomLeft: { x: 614, y: 550 },
  bottomRight: { x: 1026, y: 550 },
};

const markers = {
  top: { x: 820, y: 348 },
  right: { x: 1084, y: 450 },
  bottom: { x: 820, y: 552 },
  left: { x: 556, y: 450 },
  settleTop: { x: 820, y: 340 },
  settleRight: { x: 1070, y: 450 },
  settleBottom: { x: 820, y: 560 },
  settleLeft: { x: 570, y: 450 },
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

function pointOnJoint(progress) {
  const length = clamp(progress, 0, 1) * JOINT_TRACE_LENGTH;
  const point = jointTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
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
    appearance: 12,
    search: 24,
    tension: 12,
    transformation: 6,
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
    appearance: { x: 144, y: 154, width: 1070, height: 620 },
    search: { x: 160, y: 136, width: 1120, height: 648 },
    tension: { x: 314, y: 148, width: 986, height: 628 },
    transformation: { x: 350, y: 136, width: 938, height: 646 },
    resolution: { x: 386, y: 140, width: 892, height: 632 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -18) translate(800 450) scale(1.038) translate(-800 -450)",
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

  setGroupTransform(candidateNotch, points.notch.x, points.notch.y, 1, -4);
  setGroupTransform(candidateStep, points.step.x, points.step.y, 1, 0);
  setGroupTransform(candidateDovetail, points.dovetail.x, points.dovetail.y, 1, 6);
  [candidateNotch, candidateStep, candidateDovetail].forEach((element) => setOpacity(element, 0));

  setOpacity(throatTop, 0);
  setOpacity(throatBottom, 0);
  setGroupTransform(clampTop, points.throat.x, 360, 1, 0);
  setGroupTransform(clampBottom, points.throat.x, 540, 1, 0);
  setOpacity(clampTop, 0);
  setOpacity(clampBottom, 0);
  setOpacity(pressureHalo, 0);

  setGroupTransform(leftBody, bodies.leftStart.x, bodies.leftStart.y, 1, 0);
  setGroupTransform(rightBody, bodies.rightStart.x, bodies.rightStart.y, 1, 0);
  setOpacity(leftBody, 0);
  setOpacity(rightBody, 0);
  setOpacity(jointBase, 0);
  setPathWindow(jointTrace, JOINT_TRACE_LENGTH, 0, 0);

  [slotTopLeft, slotTopRight, slotBottomLeft, slotBottomRight].forEach((slot) => setOpacity(slot, 0));
  setGroupTransform(slotTopLeft, slots.topLeft.x, slots.topLeft.y, 1, 0);
  setGroupTransform(slotTopRight, slots.topRight.x, slots.topRight.y, 1, 0);
  setGroupTransform(slotBottomLeft, slots.bottomLeft.x, slots.bottomLeft.y, 1, 0);
  setGroupTransform(slotBottomRight, slots.bottomRight.x, slots.bottomRight.y, 1, 0);

  [markerTop, markerRight, markerBottom, markerLeft].forEach((marker) => setOpacity(marker, 0));
  setGroupTransform(markerTop, markers.top.x, markers.top.y, 1, 0);
  setGroupTransform(markerRight, markers.right.x, markers.right.y, 1, 0);
  setGroupTransform(markerBottom, markers.bottom.x, markers.bottom.y, 1, 0);
  setGroupTransform(markerLeft, markers.left.x, markers.left.y, 1, 0);

  setOpacity(anchorTop, 0);
  setOpacity(anchorBottom, 0);
  setOpacity(seamTop, 0);
  setOpacity(seamBottom, 0);
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
    0.24 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.16);
  setOpacity(candidateNotch, preview * 0.14);
  setOpacity(candidateStep, preview * 0.1);
  setOpacity(candidateDovetail, preview * 0.08);
  setOpacity(throatTop, preview * 0.1);
  setOpacity(throatBottom, preview * 0.1);
  setOpacity(clampTop, preview * 0.05);
  setOpacity(clampBottom, preview * 0.05);
  setOpacity(pressureHalo, preview * 0.06);
  setOpacity(leftBody, preview * 0.08);
  setOpacity(rightBody, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.notch },
    { start: 0.28, end: 0.58, from: points.notch, to: points.step },
    { start: 0.58, end: 0.84, from: points.step, to: points.dovetail },
    { start: 0.84, end: 1, from: points.dovetail, to: points.throatApproach },
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

  setGroupTransform(candidateNotch, points.notch.x, points.notch.y, lerp(0.88, activeA ? 1.05 : 0.96, revealA), -6);
  setGroupTransform(candidateStep, points.step.x, points.step.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateDovetail, points.dovetail.x, points.dovetail.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 8);
  setOpacity(candidateNotch, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateStep, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateDovetail, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(throatTop, 0.14);
  setOpacity(throatBottom, 0.14);
  setOpacity(clampTop, 0.06);
  setOpacity(clampBottom, 0.06);
  setOpacity(pressureHalo, 0.08);
  setOpacity(leftBody, 0.08);
  setOpacity(rightBody, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.throatApproach, points.throat, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const clampInset = lerp(0, 34, easeInOut(clamp(progress / 0.72, 0, 1)));
  const collapse = clamp(progress / 0.76, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 120, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.48, compression),
    lerp(1, 1.86, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const notchPosition = mixPoint(points.notch, { x: 734, y: 410 }, collapse);
  const stepPosition = mixPoint(points.step, { x: 820, y: 452 }, collapse);
  const dovetailPosition = mixPoint(points.dovetail, { x: 906, y: 494 }, collapse);
  setGroupTransform(candidateNotch, notchPosition.x, notchPosition.y, lerp(0.96, 0.74, collapse), -9);
  setGroupTransform(candidateStep, stepPosition.x, stepPosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateDovetail, dovetailPosition.x, dovetailPosition.y, lerp(0.95, 0.68, collapse), 9);
  setOpacity(candidateNotch, lerp(0.28, 0.05, collapse));
  setOpacity(candidateStep, lerp(0.26, 0.05, collapse));
  setOpacity(candidateDovetail, lerp(1, 0.12, collapse));

  setOpacity(throatTop, clamp((progress - 0.04) * 1.7, 0, 0.78));
  setOpacity(throatBottom, clamp((progress - 0.04) * 1.7, 0, 0.78));
  setOpacity(clampTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(clampBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(clampTop, points.throat.x, 360 + clampInset, 1, 0);
  setGroupTransform(clampBottom, points.throat.x, 540 - clampInset, 1, 0);

  setGroupTransform(leftBody, lerp(bodies.leftStart.x, bodies.leftSettle.x - 22, collapse), bodies.leftStart.y, 1, 0);
  setGroupTransform(rightBody, lerp(bodies.rightStart.x, bodies.rightSettle.x + 22, collapse), bodies.rightStart.y, 1, 0);
  setOpacity(leftBody, clamp((progress - 0.32) * 1.2, 0, 0.42));
  setOpacity(rightBody, clamp((progress - 0.42) * 1.2, 0, 0.42));
  setOpacity(jointBase, clamp((progress - 0.48) * 0.4, 0, 0.18));
  setOpacity(slotTopLeft, clamp((progress - 0.42) * 1.3, 0, 0.2));
  setOpacity(slotTopRight, clamp((progress - 0.52) * 1.3, 0, 0.2));
  setOpacity(slotBottomLeft, clamp((progress - 0.62) * 1.3, 0, 0.2));
  setOpacity(slotBottomRight, clamp((progress - 0.72) * 1.3, 0, 0.2));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnJoint(routeProgress);
  const topReveal = markerState(routeProgress, 0.18);
  const rightReveal = markerState(routeProgress, 0.48);
  const bottomReveal = markerState(routeProgress, 0.7);
  const leftReveal = markerState(routeProgress, 0.88);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setGroupTransform(leftBody, lerp(bodies.leftSettle.x - 22, bodies.leftSettle.x, routeProgress), bodies.leftSettle.y, 1, 0);
  setGroupTransform(rightBody, lerp(bodies.rightSettle.x + 22, bodies.rightSettle.x, routeProgress), bodies.rightSettle.y, 1, 0);
  setOpacity(leftBody, lerp(0.42, 0.98, routeProgress));
  setOpacity(rightBody, lerp(0.42, 0.98, routeProgress));
  setOpacity(jointBase, lerp(0.18, 0.34, routeProgress));
  setPathWindow(jointTrace, JOINT_TRACE_LENGTH, JOINT_TRACE_LENGTH * routeProgress, 1);

  setOpacity(throatTop, lerp(0.78, 0.06, progress));
  setOpacity(throatBottom, lerp(0.78, 0.06, progress));
  setOpacity(clampTop, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(clampBottom, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(clampTop, points.throat.x, lerp(394, 410, progress), 1, 0);
  setGroupTransform(clampBottom, points.throat.x, lerp(506, 490, progress), 1, 0);

  setOpacity(candidateNotch, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateStep, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateDovetail, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotTopLeft, slotState(routeProgress, 0.16));
  setOpacity(slotTopRight, slotState(routeProgress, 0.36));
  setOpacity(slotBottomRight, slotState(routeProgress, 0.64));
  setOpacity(slotBottomLeft, slotState(routeProgress, 0.82));

  setGroupTransform(markerTop, markers.top.x, markers.top.y, lerp(0.88, 1, easeOut(topReveal)), 0);
  setGroupTransform(markerRight, markers.right.x, markers.right.y, lerp(0.88, 1, easeOut(rightReveal)), 0);
  setGroupTransform(markerBottom, markers.bottom.x, markers.bottom.y, lerp(0.88, 1, easeOut(bottomReveal)), 0);
  setGroupTransform(markerLeft, markers.left.x, markers.left.y, lerp(0.88, 1, easeOut(leftReveal)), 0);
  setOpacity(markerTop, topReveal);
  setOpacity(markerRight, rightReveal);
  setOpacity(markerBottom, bottomReveal);
  setOpacity(markerLeft, leftReveal);

  setOpacity(anchorTop, clamp((progress - 0.58) * 1.5, 0, 0.14));
  setOpacity(anchorBottom, clamp((progress - 0.72) * 1.5, 0, 0.14));
  setOpacity(seamTop, clamp((progress - 0.62) * 1.5, 0, 0.2));
  setOpacity(seamBottom, clamp((progress - 0.72) * 1.5, 0, 0.2));
  setOpacity(resolutionHalo, clamp((progress - 0.66) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.78) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.throat, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setGroupTransform(leftBody, bodies.leftSettle.x, bodies.leftSettle.y, 1, 0);
  setGroupTransform(rightBody, bodies.rightSettle.x, bodies.rightSettle.y, 1, 0);
  setOpacity(leftBody, 1);
  setOpacity(rightBody, 1);
  setOpacity(jointBase, lerp(0.34, 0.26, settle));
  setPathWindow(jointTrace, JOINT_TRACE_LENGTH, JOINT_TRACE_LENGTH, lerp(1, 0.22, settle));

  [
    throatTop,
    throatBottom,
    clampTop,
    clampBottom,
    candidateNotch,
    candidateStep,
    candidateDovetail,
    slotTopLeft,
    slotTopRight,
    slotBottomLeft,
    slotBottomRight,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(markerTop, lerp(markers.top.x, markers.settleTop.x, settle), lerp(markers.top.y, markers.settleTop.y, settle), 0.97, 0);
  setGroupTransform(markerRight, lerp(markers.right.x, markers.settleRight.x, settle), lerp(markers.right.y, markers.settleRight.y, settle), 0.97, 0);
  setGroupTransform(markerBottom, lerp(markers.bottom.x, markers.settleBottom.x, settle), lerp(markers.bottom.y, markers.settleBottom.y, settle), 0.97, 0);
  setGroupTransform(markerLeft, lerp(markers.left.x, markers.settleLeft.x, settle), lerp(markers.left.y, markers.settleLeft.y, settle), 0.97, 0);
  setOpacity(markerTop, 0.92);
  setOpacity(markerRight, 0.92);
  setOpacity(markerBottom, 0.9);
  setOpacity(markerLeft, 0.92);

  setOpacity(anchorTop, lerp(0.14, 0.18, settle));
  setOpacity(anchorBottom, lerp(0.14, 0.18, settle));
  setOpacity(seamTop, lerp(0.2, 0.24, settle));
  setOpacity(seamBottom, lerp(0.2, 0.24, settle));
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
