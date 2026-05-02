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
const candidateSling = document.getElementById("candidate-sling");
const candidateBalance = document.getElementById("candidate-balance");
const captureGuide = document.getElementById("capture-guide");
const orbitBase = document.getElementById("orbit-base");
const captureFinTop = document.getElementById("capture-fin-top");
const captureFinBottom = document.getElementById("capture-fin-bottom");
const equatorBar = document.getElementById("equator-bar");
const polarBar = document.getElementById("polar-bar");
const pressureHalo = document.getElementById("pressure-halo");
const coreShell = document.getElementById("core-shell");
const coreRing = document.getElementById("core-ring");
const orbitTrace = document.getElementById("orbit-trace");
const axisTrace = document.getElementById("axis-trace");
const slotTopRight = document.getElementById("slot-top-right");
const slotBottomLeft = document.getElementById("slot-bottom-left");
const slotRight = document.getElementById("slot-right");
const satelliteTopRight = document.getElementById("satellite-top-right");
const satelliteBottomLeft = document.getElementById("satellite-bottom-left");
const satelliteRight = document.getElementById("satellite-right");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const CAPTURE_GUIDE_LENGTH = captureGuide.getTotalLength();
const ORBIT_TRACE_LENGTH = orbitTrace.getTotalLength();
const AXIS_TRACE_LENGTH = axisTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 560, y: 450 },
  arcCandidate: { x: 640, y: 356 },
  slingCandidate: { x: 838, y: 334 },
  balanceCandidate: { x: 1012, y: 404 },
  approach: { x: 940, y: 404 },
};

const orbit = {
  center: { x: 820, y: 450 },
  right: { x: 1000, y: 450 },
  topRight: { x: 930, y: 378 },
  bottomLeft: { x: 710, y: 522 },
  rightSatellite: { x: 970, y: 450 },
  settleTopRight: { x: 916, y: 388 },
  settleBottomLeft: { x: 724, y: 512 },
  settleRightSatellite: { x: 954, y: 450 },
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

function pointOnPath(path, totalLength, progress) {
  const length = clamp(progress, 0, 1) * totalLength;
  const point = path.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function satelliteState(progress, threshold) {
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
    search: 32,
    tension: 8,
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
    search: { x: 142, y: 128, width: 1120, height: 650 },
    tension: { x: 312, y: 148, width: 1012, height: 624 },
    transformation: { x: 278, y: 126, width: 1076, height: 646 },
    resolution: { x: 332, y: 138, width: 1000, height: 632 },
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

  setGroupTransform(candidateArc, points.arcCandidate.x, points.arcCandidate.y, 1, -4);
  setGroupTransform(candidateSling, points.slingCandidate.x, points.slingCandidate.y, 1, 4);
  setGroupTransform(candidateBalance, points.balanceCandidate.x, points.balanceCandidate.y, 1, 0);
  [candidateArc, candidateSling, candidateBalance].forEach((element) => setOpacity(element, 0));

  setOpacity(captureGuide, 0);
  setOpacity(orbitBase, 0);
  setOpacity(captureFinTop, 0);
  setOpacity(captureFinBottom, 0);
  setOpacity(equatorBar, 0);
  setOpacity(polarBar, 0);
  setOpacity(pressureHalo, 0);
  captureFinTop.setAttribute("transform", "");
  captureFinBottom.setAttribute("transform", "");

  setOpacity(coreShell, 0);
  setOpacity(coreRing, 0);
  setPathWindow(orbitTrace, ORBIT_TRACE_LENGTH, 0, 0);
  setPathWindow(axisTrace, AXIS_TRACE_LENGTH, 0, 0);

  setGroupTransform(slotTopRight, orbit.topRight.x, orbit.topRight.y, 1, 0);
  setGroupTransform(slotBottomLeft, orbit.bottomLeft.x, orbit.bottomLeft.y, 1, 0);
  setGroupTransform(slotRight, orbit.rightSatellite.x, orbit.rightSatellite.y, 1, 0);
  [slotTopRight, slotBottomLeft, slotRight].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(satelliteTopRight, orbit.topRight.x, orbit.topRight.y, 1, 0);
  setGroupTransform(satelliteBottomLeft, orbit.bottomLeft.x, orbit.bottomLeft.y, 1, 0);
  setGroupTransform(satelliteRight, orbit.rightSatellite.x, orbit.rightSatellite.y, 1, 0);
  [satelliteTopRight, satelliteBottomLeft, satelliteRight].forEach((satellite) => setOpacity(satellite, 0));

  setOpacity(anchorGrid, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.9);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.22);
  setOpacity(candidateArc, preview * 0.18);
  setOpacity(candidateSling, preview * 0.14);
  setOpacity(candidateBalance, preview * 0.12);
  setOpacity(captureGuide, preview * 0.12);
  setOpacity(orbitBase, preview * 0.18);
  setOpacity(coreShell, preview * 0.12);
  setOpacity(coreRing, preview * 0.08);
  setOpacity(captureFinTop, preview * 0.1);
  setOpacity(captureFinBottom, preview * 0.1);
  setOpacity(equatorBar, preview * 0.1);
  setOpacity(polarBar, preview * 0.06);
  setOpacity(pressureHalo, preview * 0.1);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.arcCandidate },
    { start: 0.28, end: 0.58, from: points.arcCandidate, to: points.slingCandidate },
    { start: 0.58, end: 0.84, from: points.slingCandidate, to: points.balanceCandidate },
    { start: 0.84, end: 1, from: points.balanceCandidate, to: points.approach },
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

  setGroupTransform(candidateArc, points.arcCandidate.x, points.arcCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateSling, points.slingCandidate.x, points.slingCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 4);
  setGroupTransform(candidateBalance, points.balanceCandidate.x, points.balanceCandidate.y, lerp(0.84, activeC ? 1.05 : 0.96, revealC), 0);
  setOpacity(candidateArc, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateSling, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateBalance, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(captureGuide, 0.16);
  setOpacity(orbitBase, 0.12);
  setOpacity(coreShell, 0.08);
  setOpacity(coreRing, 0.08);
  setOpacity(captureFinTop, 0.06);
  setOpacity(captureFinBottom, 0.06);
  setOpacity(pressureHalo, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.46, 0, 1);
  const position = pointOnPath(captureGuide, CAPTURE_GUIDE_LENGTH, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const finShift = lerp(0, 34, easeInOut(clamp(progress / 0.7, 0, 1)));
  const collapse = clamp(progress / 0.76, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.54, compression),
    lerp(1, 1.84, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const arcPosition = mixPoint(points.arcCandidate, { x: 718, y: 380 }, collapse);
  const slingPosition = mixPoint(points.slingCandidate, { x: 828, y: 338 }, collapse);
  const balancePosition = mixPoint(points.balanceCandidate, { x: 928, y: 404 }, collapse);
  setGroupTransform(candidateArc, arcPosition.x, arcPosition.y, lerp(0.96, 0.72, collapse), -8);
  setGroupTransform(candidateSling, slingPosition.x, slingPosition.y, lerp(0.96, 0.68, collapse), 0);
  setGroupTransform(candidateBalance, balancePosition.x, balancePosition.y, lerp(0.95, 0.7, collapse), 4);
  setOpacity(candidateArc, lerp(0.3, 0.05, collapse));
  setOpacity(candidateSling, lerp(0.28, 0.05, collapse));
  setOpacity(candidateBalance, lerp(1, 0.12, collapse));

  setOpacity(captureGuide, clamp((progress - 0.04) * 1.7, 0, 0.82));
  setOpacity(orbitBase, clamp((progress - 0.06) * 1.5, 0, 0.46));
  setOpacity(coreShell, clamp((progress - 0.08) * 1.5, 0, 0.94));
  setOpacity(coreRing, clamp((progress - 0.12) * 1.5, 0, 0.52));
  setOpacity(captureFinTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(captureFinBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(equatorBar, clamp((progress - 0.16) * 1.4, 0, 0.88));
  setOpacity(polarBar, clamp((progress - 0.24) * 1.4, 0, 0.44));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  captureFinTop.setAttribute("transform", `translate(0 ${finShift.toFixed(2)})`);
  captureFinBottom.setAttribute("transform", `translate(0 ${(-finShift).toFixed(2)})`);

  setOpacity(slotTopRight, clamp((progress - 0.56) * 1.4, 0, 0.18));
  setOpacity(slotBottomLeft, clamp((progress - 0.68) * 1.4, 0, 0.18));
  setOpacity(slotRight, clamp((progress - 0.46) * 1.4, 0, 0.18));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.9, 0, 1));
  const position = pointOnPath(orbitTrace, ORBIT_TRACE_LENGTH, routeProgress);
  const rightReveal = satelliteState(routeProgress, 0.12);
  const topRightReveal = satelliteState(routeProgress, 0.42);
  const bottomLeftReveal = satelliteState(routeProgress, 0.68);
  const axisProgress = clamp((routeProgress - 0.24) / 0.5, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(orbitBase, lerp(0.46, 0.22, routeProgress));
  setOpacity(coreShell, lerp(0.94, 1, routeProgress));
  setOpacity(coreRing, lerp(0.52, 0.68, routeProgress));
  setPathWindow(orbitTrace, ORBIT_TRACE_LENGTH, ORBIT_TRACE_LENGTH * routeProgress, 1);
  setPathWindow(axisTrace, AXIS_TRACE_LENGTH, AXIS_TRACE_LENGTH * axisProgress, 0.72 * axisProgress);
  setOpacity(equatorBar, lerp(0.88, 0.26, progress));
  setOpacity(polarBar, lerp(0.44, 0.18, progress));

  setOpacity(captureGuide, lerp(0.82, 0.06, progress));
  setOpacity(captureFinTop, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(captureFinBottom, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));
  captureFinTop.setAttribute("transform", `translate(0 ${lerp(34, 12, progress).toFixed(2)})`);
  captureFinBottom.setAttribute("transform", `translate(0 ${lerp(-34, -12, progress).toFixed(2)})`);

  setOpacity(candidateArc, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateSling, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateBalance, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotRight, slotState(routeProgress, 0.14));
  setOpacity(slotTopRight, slotState(routeProgress, 0.44));
  setOpacity(slotBottomLeft, slotState(routeProgress, 0.7));

  setGroupTransform(satelliteRight, orbit.rightSatellite.x, orbit.rightSatellite.y, lerp(0.82, 1, easeOut(rightReveal)), 0);
  setGroupTransform(satelliteTopRight, orbit.topRight.x, orbit.topRight.y, lerp(0.82, 1, easeOut(topRightReveal)), 0);
  setGroupTransform(satelliteBottomLeft, orbit.bottomLeft.x, orbit.bottomLeft.y, lerp(0.82, 1, easeOut(bottomLeftReveal)), 0);
  setOpacity(satelliteRight, rightReveal * 0.82);
  setOpacity(satelliteTopRight, topRightReveal * 0.94);
  setOpacity(satelliteBottomLeft, bottomLeftReveal * 0.94);

  setOpacity(anchorGrid, clamp((progress - 0.72) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;
  const position = mixPoint(orbit.right, orbit.center, settle);

  setDot(position, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(coreShell, 1);
  setOpacity(coreRing, lerp(0.68, 0.82, settle));
  setOpacity(orbitBase, lerp(0.22, 0.28, settle));
  setPathWindow(orbitTrace, ORBIT_TRACE_LENGTH, ORBIT_TRACE_LENGTH, lerp(1, 0.3, settle));
  setPathWindow(axisTrace, AXIS_TRACE_LENGTH, AXIS_TRACE_LENGTH, lerp(0.72, 0.34, settle));
  setOpacity(equatorBar, lerp(0.26, 0.22, settle));
  setOpacity(polarBar, lerp(0.18, 0.24, settle));

  [
    captureGuide,
    captureFinTop,
    captureFinBottom,
    pressureHalo,
    candidateArc,
    candidateSling,
    candidateBalance,
    slotTopRight,
    slotBottomLeft,
    slotRight,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(
    satelliteTopRight,
    lerp(orbit.topRight.x, orbit.settleTopRight.x, settle),
    lerp(orbit.topRight.y, orbit.settleTopRight.y, settle),
    0.96,
    0,
  );
  setGroupTransform(
    satelliteBottomLeft,
    lerp(orbit.bottomLeft.x, orbit.settleBottomLeft.x, settle),
    lerp(orbit.bottomLeft.y, orbit.settleBottomLeft.y, settle),
    0.96,
    0,
  );
  setGroupTransform(
    satelliteRight,
    lerp(orbit.rightSatellite.x, orbit.settleRightSatellite.x, settle),
    orbit.rightSatellite.y,
    0.92,
    0,
  );
  setOpacity(satelliteTopRight, 0.92);
  setOpacity(satelliteBottomLeft, 0.9);
  setOpacity(satelliteRight, lerp(0.46, 0.16, settle));

  setOpacity(anchorGrid, lerp(0.12, 0.18, settle));
  setOpacity(resolutionHalo, lerp(0.16, 0.28, settle));
  setOpacity(resolutionFrame, lerp(0.22, 0.72, settle));
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
