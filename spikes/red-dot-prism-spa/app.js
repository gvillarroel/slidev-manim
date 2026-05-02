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
const candidateRidge = document.getElementById("candidate-ridge");
const candidateSplit = document.getElementById("candidate-split");
const candidateChannel = document.getElementById("candidate-channel");
const throatGuide = document.getElementById("throat-guide");
const clampLeft = document.getElementById("clamp-left");
const clampRight = document.getElementById("clamp-right");
const braceTop = document.getElementById("brace-top");
const braceBottom = document.getElementById("brace-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const prismShell = document.getElementById("prism-shell");
const prismBase = document.getElementById("prism-base");
const prismTrace = document.getElementById("prism-trace");
const prismAxisBase = document.getElementById("prism-axis-base");
const prismAxisTrace = document.getElementById("prism-axis-trace");
const slotUpperLeft = document.getElementById("slot-upper-left");
const slotUpperRight = document.getElementById("slot-upper-right");
const slotLowerRight = document.getElementById("slot-lower-right");
const slotLowerLeft = document.getElementById("slot-lower-left");
const facetUpperLeft = document.getElementById("facet-upper-left");
const facetUpperRight = document.getElementById("facet-upper-right");
const facetLowerRight = document.getElementById("facet-lower-right");
const facetLowerLeft = document.getElementById("facet-lower-left");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const PRISM_TRACE_LENGTH = prismTrace.getTotalLength();
const PRISM_AXIS_LENGTH = prismAxisTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 564, y: 450 },
  ridgeCandidate: { x: 642, y: 356 },
  splitCandidate: { x: 836, y: 324 },
  channelCandidate: { x: 1002, y: 394 },
  apertureApproach: { x: 930, y: 450 },
  aperture: { x: 820, y: 450 },
};

const prism = {
  center: { x: 820, y: 450 },
  left: { x: 742, y: 450 },
  upperLeft: { x: 742, y: 368 },
  upperRight: { x: 892, y: 368 },
  right: { x: 978, y: 450 },
  lowerRight: { x: 892, y: 532 },
  lowerLeft: { x: 742, y: 532 },
  settleUpperLeft: { x: 756, y: 380 },
  settleUpperRight: { x: 878, y: 380 },
  settleLowerRight: { x: 878, y: 520 },
  settleLowerLeft: { x: 756, y: 520 },
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

function pointOnPrism(progress) {
  const length = clamp(progress, 0, 1) * PRISM_TRACE_LENGTH;
  const point = prismTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function facetState(progress, threshold) {
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
    search: 34,
    tension: 12,
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
    appearance: { x: 128, y: 142, width: 1088, height: 636 },
    search: { x: 148, y: 128, width: 1116, height: 650 },
    tension: { x: 334, y: 148, width: 972, height: 624 },
    transformation: { x: 352, y: 132, width: 940, height: 646 },
    resolution: { x: 392, y: 138, width: 888, height: 632 },
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

  setGroupTransform(candidateRidge, points.ridgeCandidate.x, points.ridgeCandidate.y, 1, -4);
  setGroupTransform(candidateSplit, points.splitCandidate.x, points.splitCandidate.y, 1, 2);
  setGroupTransform(candidateChannel, points.channelCandidate.x, points.channelCandidate.y, 1, 6);
  [candidateRidge, candidateSplit, candidateChannel].forEach((element) => setOpacity(element, 0));

  setOpacity(throatGuide, 0);
  setGroupTransform(clampLeft, points.aperture.x - 176, points.aperture.y, 1, 0);
  setGroupTransform(clampRight, points.aperture.x + 176, points.aperture.y, 1, 0);
  setOpacity(clampLeft, 0);
  setOpacity(clampRight, 0);
  setOpacity(braceTop, 0);
  setOpacity(braceBottom, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(prismShell, 0);
  setOpacity(prismBase, 0);
  setPathWindow(prismTrace, PRISM_TRACE_LENGTH, 0, 0);
  setOpacity(prismAxisBase, 0);
  setPathWindow(prismAxisTrace, PRISM_AXIS_LENGTH, 0, 0);

  setGroupTransform(slotUpperLeft, prism.upperLeft.x, prism.upperLeft.y, 1, 0);
  setGroupTransform(slotUpperRight, prism.upperRight.x, prism.upperRight.y, 1, 0);
  setGroupTransform(slotLowerRight, prism.lowerRight.x, prism.lowerRight.y, 1, 0);
  setGroupTransform(slotLowerLeft, prism.lowerLeft.x, prism.lowerLeft.y, 1, 0);
  [slotUpperLeft, slotUpperRight, slotLowerRight, slotLowerLeft].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(facetUpperLeft, prism.upperLeft.x, prism.upperLeft.y, 1, 0);
  setGroupTransform(facetUpperRight, prism.upperRight.x, prism.upperRight.y, 1, 0);
  setGroupTransform(facetLowerRight, prism.lowerRight.x, prism.lowerRight.y, 1, 0);
  setGroupTransform(facetLowerLeft, prism.lowerLeft.x, prism.lowerLeft.y, 1, 0);
  [facetUpperLeft, facetUpperRight, facetLowerRight, facetLowerLeft].forEach((facet) => setOpacity(facet, 0));

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
  setOpacity(candidateRidge, preview * 0.14);
  setOpacity(candidateSplit, preview * 0.1);
  setOpacity(candidateChannel, preview * 0.08);
  setOpacity(throatGuide, preview * 0.1);
  setOpacity(clampLeft, preview * 0.05);
  setOpacity(clampRight, preview * 0.05);
  setOpacity(braceTop, preview * 0.08);
  setOpacity(braceBottom, preview * 0.08);
  setOpacity(pressureHalo, preview * 0.08);
  setOpacity(prismShell, preview * 0.05);
  setOpacity(prismBase, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.ridgeCandidate },
    { start: 0.28, end: 0.58, from: points.ridgeCandidate, to: points.splitCandidate },
    { start: 0.58, end: 0.84, from: points.splitCandidate, to: points.channelCandidate },
    { start: 0.84, end: 1, from: points.channelCandidate, to: points.apertureApproach },
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

  setGroupTransform(candidateRidge, points.ridgeCandidate.x, points.ridgeCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateSplit, points.splitCandidate.x, points.splitCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 2);
  setGroupTransform(candidateChannel, points.channelCandidate.x, points.channelCandidate.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 6);
  setOpacity(candidateRidge, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateSplit, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateChannel, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(throatGuide, 0.14);
  setOpacity(clampLeft, 0.06);
  setOpacity(clampRight, 0.06);
  setOpacity(braceTop, 0.1);
  setOpacity(braceBottom, 0.1);
  setOpacity(pressureHalo, 0.08);
  setOpacity(prismShell, 0.06);
  setOpacity(prismBase, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.apertureApproach, points.aperture, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const clampGap = lerp(176, 74, easeInOut(clamp(progress / 0.7, 0, 1)));
  const collapse = clamp(progress / 0.74, 0, 1);

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

  const ridgePosition = mixPoint(points.ridgeCandidate, { x: 734, y: 386 }, collapse);
  const splitPosition = mixPoint(points.splitCandidate, { x: 822, y: 348 }, collapse);
  const channelPosition = mixPoint(points.channelCandidate, { x: 904, y: 392 }, collapse);
  setGroupTransform(candidateRidge, ridgePosition.x, ridgePosition.y, lerp(0.96, 0.72, collapse), -8);
  setGroupTransform(candidateSplit, splitPosition.x, splitPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateChannel, channelPosition.x, channelPosition.y, lerp(0.95, 0.68, collapse), 8);
  setOpacity(candidateRidge, lerp(0.3, 0.05, collapse));
  setOpacity(candidateSplit, lerp(0.28, 0.05, collapse));
  setOpacity(candidateChannel, lerp(1, 0.12, collapse));

  setOpacity(throatGuide, clamp((progress - 0.04) * 1.7, 0, 0.78));
  setOpacity(clampLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(clampRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(braceTop, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(braceBottom, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(clampLeft, points.aperture.x - clampGap, points.aperture.y, 1, 0);
  setGroupTransform(clampRight, points.aperture.x + clampGap, points.aperture.y, 1, 0);

  setOpacity(prismShell, clamp((progress - 0.5) * 0.42, 0, 0.14));
  setOpacity(prismBase, clamp((progress - 0.56) * 0.4, 0, 0.14));
  setOpacity(prismAxisBase, clamp((progress - 0.62) * 0.42, 0, 0.12));
  setOpacity(slotUpperLeft, clamp((progress - 0.42) * 1.3, 0, 0.24));
  setOpacity(slotUpperRight, clamp((progress - 0.52) * 1.3, 0, 0.24));
  setOpacity(slotLowerRight, clamp((progress - 0.62) * 1.3, 0, 0.24));
  setOpacity(slotLowerLeft, clamp((progress - 0.72) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnPrism(routeProgress);
  const upperLeftReveal = facetState(routeProgress, 0.18);
  const upperRightReveal = facetState(routeProgress, 0.42);
  const lowerRightReveal = facetState(routeProgress, 0.66);
  const lowerLeftReveal = facetState(routeProgress, 0.84);
  const axisProgress = clamp((routeProgress - 0.62) / 0.32, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(prismShell, lerp(0.24, 0.98, routeProgress));
  setOpacity(prismBase, lerp(0.14, 0.32, routeProgress));
  setPathWindow(prismTrace, PRISM_TRACE_LENGTH, PRISM_TRACE_LENGTH * routeProgress, 1);
  setOpacity(prismAxisBase, clamp((progress - 0.36) * 1.2, 0, 0.22));
  setPathWindow(prismAxisTrace, PRISM_AXIS_LENGTH, PRISM_AXIS_LENGTH * axisProgress, 0.74 * axisProgress);

  setOpacity(throatGuide, lerp(0.78, 0.08, progress));
  setOpacity(clampLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(clampRight, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(braceTop, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(braceBottom, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(clampLeft, points.aperture.x - lerp(74, 94, progress), points.aperture.y, 1, 0);
  setGroupTransform(clampRight, points.aperture.x + lerp(74, 94, progress), points.aperture.y, 1, 0);

  setOpacity(candidateRidge, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateSplit, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateChannel, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotUpperLeft, slotState(routeProgress, 0.18));
  setOpacity(slotUpperRight, slotState(routeProgress, 0.42));
  setOpacity(slotLowerRight, slotState(routeProgress, 0.66));
  setOpacity(slotLowerLeft, slotState(routeProgress, 0.84));

  setGroupTransform(facetUpperLeft, prism.upperLeft.x, prism.upperLeft.y, lerp(0.88, 1, easeOut(upperLeftReveal)), 0);
  setGroupTransform(facetUpperRight, prism.upperRight.x, prism.upperRight.y, lerp(0.88, 1, easeOut(upperRightReveal)), 0);
  setGroupTransform(facetLowerRight, prism.lowerRight.x, prism.lowerRight.y, lerp(0.88, 1, easeOut(lowerRightReveal)), 0);
  setGroupTransform(facetLowerLeft, prism.lowerLeft.x, prism.lowerLeft.y, lerp(0.88, 1, easeOut(lowerLeftReveal)), 0);
  setOpacity(facetUpperLeft, upperLeftReveal);
  setOpacity(facetUpperRight, upperRightReveal);
  setOpacity(facetLowerRight, lowerRightReveal);
  setOpacity(facetLowerLeft, lowerLeftReveal);

  setOpacity(anchorGrid, clamp((progress - 0.72) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(prism.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(prismShell, lerp(0.98, 1, settle));
  setOpacity(prismBase, lerp(0.32, 0.42, settle));
  setPathWindow(prismTrace, PRISM_TRACE_LENGTH, PRISM_TRACE_LENGTH, lerp(1, 0.24, settle));
  setOpacity(prismAxisBase, lerp(0.22, 0.26, settle));
  setPathWindow(prismAxisTrace, PRISM_AXIS_LENGTH, PRISM_AXIS_LENGTH, lerp(0.74, 0.32, settle));

  [
    throatGuide,
    clampLeft,
    clampRight,
    braceTop,
    braceBottom,
    pressureHalo,
    candidateRidge,
    candidateSplit,
    candidateChannel,
    slotUpperLeft,
    slotUpperRight,
    slotLowerRight,
    slotLowerLeft,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(
    facetUpperLeft,
    lerp(prism.upperLeft.x, prism.settleUpperLeft.x, settle),
    lerp(prism.upperLeft.y, prism.settleUpperLeft.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    facetUpperRight,
    lerp(prism.upperRight.x, prism.settleUpperRight.x, settle),
    lerp(prism.upperRight.y, prism.settleUpperRight.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    facetLowerRight,
    lerp(prism.lowerRight.x, prism.settleLowerRight.x, settle),
    lerp(prism.lowerRight.y, prism.settleLowerRight.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    facetLowerLeft,
    lerp(prism.lowerLeft.x, prism.settleLowerLeft.x, settle),
    lerp(prism.lowerLeft.y, prism.settleLowerLeft.y, settle),
    0.97,
    0,
  );
  setOpacity(facetUpperLeft, 0.92);
  setOpacity(facetUpperRight, 0.92);
  setOpacity(facetLowerRight, 0.9);
  setOpacity(facetLowerLeft, 0.9);

  setOpacity(anchorGrid, lerp(0.12, 0.18, settle));
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
