const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transform", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");
const timelineFill = document.getElementById("timeline-fill");
const toggleButton = document.getElementById("toggle-button");
const replayButton = document.getElementById("replay-button");
const phaseDots = Array.from(document.querySelectorAll("[data-phase-dot]"));

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateTop = document.getElementById("candidate-top");
const candidateRight = document.getElementById("candidate-right");
const candidateBottom = document.getElementById("candidate-bottom");
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoRight = document.getElementById("search-echo-right");
const searchEchoBottom = document.getElementById("search-echo-bottom");

const tensionGroup = document.getElementById("tension-group");
const huskTop = document.getElementById("husk-top");
const huskBottom = document.getElementById("husk-bottom");
const tensionSlot = document.getElementById("tension-slot");
const pressureRailTop = document.getElementById("pressure-rail-top");
const pressureRailBottom = document.getElementById("pressure-rail-bottom");
const pinchHalo = document.getElementById("pinch-halo");

const transformGroup = document.getElementById("transform-group");
const rosetteBase = document.getElementById("rosette-base");
const rosetteTrace = document.getElementById("rosette-trace");
const rosetteCoreRing = document.getElementById("rosette-core-ring");
const petalSlotTop = document.getElementById("petal-slot-top");
const petalSlotRight = document.getElementById("petal-slot-right");
const petalSlotBottom = document.getElementById("petal-slot-bottom");
const petalSlotLeft = document.getElementById("petal-slot-left");
const petalTop = document.getElementById("petal-top");
const petalRight = document.getElementById("petal-right");
const petalBottom = document.getElementById("petal-bottom");
const petalLeft = document.getElementById("petal-left");
const crosshair = document.getElementById("crosshair");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");

const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ROSETTE_TRACE_LENGTH = rosetteTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
  passiveGray: "#b5b5b5",
};

const points = {
  start: { x: 340, y: 450 },
  entry: { x: 500, y: 450 },
  searchTop: { x: 622, y: 334 },
  searchRight: { x: 800, y: 392 },
  searchBottom: { x: 640, y: 564 },
  apertureApproach: { x: 780, y: 450 },
  aperture: { x: 850, y: 450 },
  rosette: { x: 886, y: 450 },
};

const petalRotations = {
  top: 0,
  right: 90,
  bottom: 180,
  left: 270,
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

function setPathWindow(element, totalLength, visibleLength, opacity) {
  const clampedLength = clamp(visibleLength, 0, totalLength);
  element.style.strokeDasharray = `${clampedLength.toFixed(2)} ${(totalLength + 200).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function applyDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1) {
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

function pointOnRosette(progress) {
  const point = rosetteTrace.getPointAtLength(clamp(progress, 0, 1) * ROSETTE_TRACE_LENGTH);
  return { x: point.x, y: point.y };
}

function setRosetteGroupTransforms(scale = 1) {
  setGroupTransform(petalSlotTop, points.rosette.x, points.rosette.y, scale, petalRotations.top);
  setGroupTransform(petalSlotRight, points.rosette.x, points.rosette.y, scale, petalRotations.right);
  setGroupTransform(petalSlotBottom, points.rosette.x, points.rosette.y, scale, petalRotations.bottom);
  setGroupTransform(petalSlotLeft, points.rosette.x, points.rosette.y, scale, petalRotations.left);

  setGroupTransform(petalTop, points.rosette.x, points.rosette.y, scale, petalRotations.top);
  setGroupTransform(petalRight, points.rosette.x, points.rosette.y, scale, petalRotations.right);
  setGroupTransform(petalBottom, points.rosette.x, points.rosette.y, scale, petalRotations.bottom);
  setGroupTransform(petalLeft, points.rosette.x, points.rosette.y, scale, petalRotations.left);
}

function slotOpacity(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.34;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function petalReveal(progress, threshold) {
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

function updateHud(info) {
  phaseLabel.textContent = info.phase.label;
  timelineFill.style.width = `${(info.totalProgress * 100).toFixed(2)}%`;
  phaseDots.forEach((dot, index) => {
    dot.classList.toggle("is-active", index === info.index);
    dot.classList.toggle("is-complete", index < info.index);
  });
}

function applySceneOffset(phaseId) {
  const offsets = {
    appearance: 18,
    search: 8,
    tension: 0,
    transformation: 0,
    resolution: -4,
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
    appearance: { x: 118, y: 142, width: 1056, height: 640 },
    search: { x: 162, y: 118, width: 1118, height: 666 },
    tension: { x: 426, y: 126, width: 876, height: 650 },
    transformation: { x: 392, y: 112, width: 970, height: 682 },
    resolution: { x: 442, y: 126, width: 896, height: 648 },
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
  applyDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  searchGuideA.setAttribute("stroke", COLORS.lineGray);
  searchGuideB.setAttribute("stroke", COLORS.lineGray);
  searchGuideC.setAttribute("stroke", COLORS.lineGray);
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setGroupTransform(candidateTop, points.searchTop.x, points.searchTop.y, 0.92, -18);
  setGroupTransform(candidateRight, points.searchRight.x, points.searchRight.y, 0.92, 54);
  setGroupTransform(candidateBottom, points.searchBottom.x, points.searchBottom.y, 0.92, 184);
  [candidateTop, candidateRight, candidateBottom].forEach((element) => setOpacity(element, 0));
  [searchEchoTop, searchEchoRight, searchEchoBottom].forEach((element) => setOpacity(element, 0));

  setOpacity(tensionGroup, 0);
  setGroupTransform(huskTop, points.aperture.x, points.aperture.y - 194, 1, 0);
  setGroupTransform(huskBottom, points.aperture.x, points.aperture.y + 194, 1, 180);
  setOpacity(huskTop, 0);
  setOpacity(huskBottom, 0);
  setOpacity(tensionSlot, 0);
  setOpacity(pressureRailTop, 0);
  setOpacity(pressureRailBottom, 0);
  setOpacity(pinchHalo, 0);

  setOpacity(transformGroup, 0);
  setOpacity(rosetteBase, 0);
  setPathWindow(rosetteTrace, ROSETTE_TRACE_LENGTH, 0, 0);
  setOpacity(rosetteCoreRing, 0);
  setRosetteGroupTransforms(1);
  [petalSlotTop, petalSlotRight, petalSlotBottom, petalSlotLeft].forEach((element) => setOpacity(element, 0));
  [petalTop, petalRight, petalBottom, petalLeft].forEach((element) => setOpacity(element, 0));
  setOpacity(crosshair, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.entry, eased * 0.84);
  const preview = clamp(0.52 + progress * 0.9, 0, 1);

  applyDot(
    position,
    lerp(9, 18, eased),
    lerp(36, 84, eased),
    clamp(0.34 + progress * 1.5, 0, 1),
    0.12 + pulseWave(progress, 1.2) * 0.12,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.6, 0, 0.34));

  setOpacity(searchGuideA, preview * 0.16);
  setOpacity(searchGuideB, preview * 0.12);
  setOpacity(searchGuideC, preview * 0.1);
  setOpacity(candidateTop, preview * 0.16);
  setOpacity(candidateRight, preview * 0.12);
  setOpacity(candidateBottom, preview * 0.1);

  setOpacity(tensionSlot, preview * 0.08);
  setOpacity(pressureRailTop, preview * 0.08);
  setOpacity(pressureRailBottom, preview * 0.08);
  setOpacity(huskTop, preview * 0.04);
  setOpacity(huskBottom, preview * 0.04);
  setOpacity(rosetteBase, preview * 0.08);
  setOpacity(rosetteCoreRing, preview * 0.05);
  [petalSlotTop, petalSlotRight, petalSlotBottom, petalSlotLeft].forEach((element) => setOpacity(element, preview * 0.05));
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.entry, to: points.searchTop },
    { start: 0.28, end: 0.58, from: points.searchTop, to: points.searchRight },
    { start: 0.58, end: 0.84, from: points.searchRight, to: points.searchBottom },
    { start: 0.84, end: 1, from: points.searchBottom, to: points.apertureApproach },
  ]);

  applyDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.22, 0.06, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.14, 0.05, progress));

  const revealA = clamp(progress / 0.24, 0, 1);
  const revealB = clamp((progress - 0.24) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.52) / 0.22, 0, 1);
  const activeA = progress < 0.34 ? 1 : 0;
  const activeB = progress >= 0.34 && progress < 0.66 ? 1 : 0;
  const activeC = progress >= 0.66 ? 1 : 0;

  searchGuideA.setAttribute("stroke", activeA ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", activeB ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", activeC ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.18 + revealA * 0.2);
  setOpacity(searchGuideB, 0.12 + revealB * 0.2);
  setOpacity(searchGuideC, 0.08 + revealC * 0.22);

  setGroupTransform(candidateTop, points.searchTop.x, points.searchTop.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -18);
  setGroupTransform(candidateRight, points.searchRight.x, points.searchRight.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 54);
  setGroupTransform(candidateBottom, points.searchBottom.x, points.searchBottom.y, lerp(0.88, activeC ? 1.04 : 0.96, revealC), 184);
  setOpacity(candidateTop, activeA ? 1 : revealA * 0.3 + 0.14);
  setOpacity(candidateRight, activeB ? 1 : revealB * 0.3 + 0.14);
  setOpacity(candidateBottom, activeC ? 1 : revealC * 0.3 + 0.12);

  setOpacity(searchEchoTop, progress >= 0.3 ? 0.42 : 0);
  setOpacity(searchEchoRight, progress >= 0.6 ? 0.42 : 0);
  setOpacity(searchEchoBottom, progress >= 0.82 ? 0.38 : 0);

  setOpacity(tensionSlot, 0.14);
  setOpacity(pressureRailTop, 0.1);
  setOpacity(pressureRailBottom, 0.1);
  setOpacity(huskTop, 0.06);
  setOpacity(huskBottom, 0.06);
  setOpacity(rosetteBase, 0.06);
  setOpacity(rosetteCoreRing, 0.06);
}

function renderTension(progress) {
  const position = mixPoint(points.apertureApproach, points.aperture, easeInOut(clamp(progress / 0.42, 0, 1)));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const huskOffset = lerp(194, 136, easeInOut(clamp(progress / 0.72, 0, 1)));
  const cleanup = easeOut(clamp((progress - 0.18) / 0.38, 0, 1));

  applyDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 120, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.52, compression),
    lerp(1, 1.84, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0.08 * (1 - cleanup));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.18 : 0.12, 0, progress));
  });
  setOpacity(candidateTop, lerp(0.24, 0, cleanup));
  setOpacity(candidateRight, lerp(0.28, 0, cleanup));
  setOpacity(candidateBottom, lerp(0.36, 0.02, cleanup));
  setOpacity(searchEchoTop, lerp(0.32, 0, cleanup));
  setOpacity(searchEchoRight, lerp(0.3, 0, cleanup));
  setOpacity(searchEchoBottom, lerp(0.28, 0, cleanup));

  setOpacity(tensionGroup, 1);
  setGroupTransform(huskTop, points.aperture.x, points.aperture.y - huskOffset, 1, 0);
  setGroupTransform(huskBottom, points.aperture.x, points.aperture.y + huskOffset, 1, 180);
  setOpacity(huskTop, clamp((progress - 0.02) * 1.8, 0, 1));
  setOpacity(huskBottom, clamp((progress - 0.02) * 1.8, 0, 1));
  setOpacity(tensionSlot, clamp((progress - 0.04) * 1.6, 0, 0.8));
  setOpacity(pressureRailTop, clamp((progress - 0.08) * 1.5, 0, 0.72));
  setOpacity(pressureRailBottom, clamp((progress - 0.08) * 1.5, 0, 0.72));
  setOpacity(pinchHalo, clamp((progress - 0.12) * 1.4, 0, 0.4));

  setOpacity(rosetteBase, clamp((progress - 0.54) * 0.36, 0, 0.14));
  setOpacity(rosetteCoreRing, clamp((progress - 0.6) * 0.34, 0, 0.12));
  setOpacity(petalSlotTop, clamp((progress - 0.42) * 1.2, 0, 0.2));
  setOpacity(petalSlotRight, clamp((progress - 0.54) * 1.2, 0, 0.2));
  setOpacity(petalSlotBottom, clamp((progress - 0.66) * 1.2, 0, 0.2));
  setOpacity(petalSlotLeft, clamp((progress - 0.78) * 1.2, 0, 0.2));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnRosette(routeProgress);
  const topReveal = petalReveal(routeProgress, 0.16);
  const rightReveal = petalReveal(routeProgress, 0.4);
  const bottomReveal = petalReveal(routeProgress, 0.64);
  const leftReveal = petalReveal(routeProgress, 0.82);

  applyDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0.04 * (1 - progress));

  setOpacity(transformGroup, 1);
  setOpacity(rosetteBase, lerp(0.26, 0.94, routeProgress));
  setPathWindow(rosetteTrace, ROSETTE_TRACE_LENGTH, ROSETTE_TRACE_LENGTH * routeProgress, 1);
  setOpacity(rosetteCoreRing, lerp(0.12, 0.34, routeProgress));

  setOpacity(tensionGroup, clamp(1 - progress * 1.2, 0, 1));
  setOpacity(huskTop, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(huskBottom, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(tensionSlot, clamp(0.8 - progress * 0.9, 0, 1));
  setOpacity(pressureRailTop, clamp(0.72 - progress * 0.9, 0, 1));
  setOpacity(pressureRailBottom, clamp(0.72 - progress * 0.9, 0, 1));
  setOpacity(pinchHalo, clamp(0.4 - progress * 0.55, 0, 1));

  [searchGuideA, searchGuideB, searchGuideC, candidateTop, candidateRight, candidateBottom, searchEchoTop, searchEchoRight, searchEchoBottom].forEach(
    (element) => setOpacity(element, 0),
  );

  setOpacity(petalSlotTop, slotOpacity(routeProgress, 0.16));
  setOpacity(petalSlotRight, slotOpacity(routeProgress, 0.4));
  setOpacity(petalSlotBottom, slotOpacity(routeProgress, 0.64));
  setOpacity(petalSlotLeft, slotOpacity(routeProgress, 0.82));

  setGroupTransform(petalTop, points.rosette.x, points.rosette.y, lerp(0.88, 1, easeOut(topReveal)), petalRotations.top);
  setGroupTransform(petalRight, points.rosette.x, points.rosette.y, lerp(0.88, 1, easeOut(rightReveal)), petalRotations.right);
  setGroupTransform(petalBottom, points.rosette.x, points.rosette.y, lerp(0.88, 1, easeOut(bottomReveal)), petalRotations.bottom);
  setGroupTransform(petalLeft, points.rosette.x, points.rosette.y, lerp(0.88, 1, easeOut(leftReveal)), petalRotations.left);
  setOpacity(petalTop, topReveal);
  setOpacity(petalRight, rightReveal);
  setOpacity(petalBottom, bottomReveal);
  setOpacity(petalLeft, leftReveal);

  setOpacity(crosshair, clamp((progress - 0.72) * 1.5, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.14));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const rosetteScale = lerp(1, 0.965, settle);

  applyDot(points.rosette, 16, 96, 1, 0.16 + pulseWave(progress, 1.3) * 0.05);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  setOpacity(transformGroup, 1);
  setRosetteGroupTransforms(rosetteScale);
  setOpacity(tensionGroup, 0);
  setOpacity(rosetteBase, lerp(0.94, 0.26, settle));
  setPathWindow(rosetteTrace, ROSETTE_TRACE_LENGTH, ROSETTE_TRACE_LENGTH, lerp(1, 0.1, settle));
  setOpacity(rosetteCoreRing, lerp(0.34, 0.22, settle));

  [petalSlotTop, petalSlotRight, petalSlotBottom, petalSlotLeft].forEach((element) => setOpacity(element, 0));
  setOpacity(petalTop, 0.92);
  setOpacity(petalRight, 0.92);
  setOpacity(petalBottom, 0.9);
  setOpacity(petalLeft, 0.9);
  setOpacity(crosshair, lerp(0.12, 0.1, settle));
  setOpacity(resolutionHalo, lerp(0.14, 0.2, settle));
  setOpacity(resolutionFrame, lerp(0.24, 0.56, settle));
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

  updateHud(info);
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
  toggleButton.textContent = nextPlaying ? "pause" : "play";
  toggleButton.setAttribute("aria-label", nextPlaying ? "Pause narrative" : "Play narrative");
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

toggleButton.addEventListener("click", () => {
  if (state.playing) {
    state.elapsedBeforePause = state.currentElapsed;
    setPlaying(false);
  } else {
    state.startAt = performance.now();
    setPlaying(true);
  }
});

replayButton.addEventListener("click", () => {
  resetTimeline();
  if (!state.playing) {
    setPlaying(true);
  }
});

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
    replayButton.click();
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
