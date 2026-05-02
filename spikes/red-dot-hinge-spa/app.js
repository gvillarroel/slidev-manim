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
const candidateFlap = document.getElementById("candidate-flap");
const candidateCorner = document.getElementById("candidate-corner");
const candidateSplit = document.getElementById("candidate-split");

const tensionHalo = document.getElementById("tension-halo");
const throatGuide = document.getElementById("throat-guide");
const topPin = document.getElementById("top-pin");
const bottomSlot = document.getElementById("bottom-slot");
const leftShutter = document.getElementById("left-shutter");
const rightShutter = document.getElementById("right-shutter");
const pivotRing = document.getElementById("pivot-ring");

const wingTop = document.getElementById("wing-top");
const wingRight = document.getElementById("wing-right");
const wingBottom = document.getElementById("wing-bottom");
const wingLeft = document.getElementById("wing-left");
const activeTop = document.getElementById("active-top");
const activeRight = document.getElementById("active-right");
const activeBottom = document.getElementById("active-bottom");
const activeLeft = document.getElementById("active-left");
const activeTopPath = document.getElementById("active-top-path");
const activeRightPath = document.getElementById("active-right-path");
const activeBottomPath = document.getElementById("active-bottom-path");
const activeLeftPath = document.getElementById("active-left-path");

const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ACTIVE_TOP_LENGTH = activeTopPath.getTotalLength();
const ACTIVE_RIGHT_LENGTH = activeRightPath.getTotalLength();
const ACTIVE_BOTTOM_LENGTH = activeBottomPath.getTotalLength();
const ACTIVE_LEFT_LENGTH = activeLeftPath.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 302, y: 454 },
  entry: { x: 556, y: 454 },
  flap: { x: 676, y: 392 },
  corner: { x: 846, y: 338 },
  split: { x: 1000, y: 410 },
  mouth: { x: 934, y: 454 },
  pocket: { x: 846, y: 454 },
  pivot: { x: 846, y: 404 },
  center: { x: 846, y: 454 },
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

function rangedProgress(progress, start, end) {
  return clamp((progress - start) / (end - start), 0, 1);
}

function setOpacity(element, value) {
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
}

function setCircleCenter(element, point) {
  element.setAttribute("cx", point.x.toFixed(2));
  element.setAttribute("cy", point.y.toFixed(2));
}

function setEllipseRadius(element, rx, ry) {
  element.setAttribute("rx", rx.toFixed(2));
  element.setAttribute("ry", ry.toFixed(2));
}

function setGroupTransform(element, x, y, scale = 1, rotate = 0, scaleY = scale) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scale.toFixed(3)} ${scaleY.toFixed(3)})`,
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
    appearance: 10,
    search: 22,
    tension: 16,
    transformation: 10,
    resolution: 0,
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
    appearance: { x: 120, y: 142, width: 1120, height: 644 },
    search: { x: 166, y: 128, width: 1128, height: 662 },
    tension: { x: 548, y: 112, width: 596, height: 742 },
    transformation: { x: 548, y: 92, width: 596, height: 776 },
    resolution: { x: 620, y: 90, width: 452, height: 772 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -12) translate(800 450) scale(1.05) translate(-800 -450)",
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
  setDot(points.start, 18, 72, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateFlap, points.flap.x, points.flap.y, 1, -6);
  setGroupTransform(candidateCorner, points.corner.x, points.corner.y, 1, 0);
  setGroupTransform(candidateSplit, points.split.x, points.split.y, 1, 4);
  [candidateFlap, candidateCorner, candidateSplit].forEach((candidate) => setOpacity(candidate, 0));

  setEllipseRadius(tensionHalo, 166, 126);
  setOpacity(tensionHalo, 0);
  setOpacity(throatGuide, 0);
  setGroupTransform(topPin, points.center.x, points.center.y, 1, 0);
  setGroupTransform(bottomSlot, points.center.x, points.center.y + 110, 1, 0);
  setGroupTransform(leftShutter, points.center.x, points.center.y, 0.66, 0, 0.94);
  setGroupTransform(rightShutter, points.center.x, points.center.y, 0.66, 0, 0.94);
  setOpacity(topPin, 0);
  setOpacity(bottomSlot, 0);
  setOpacity(leftShutter, 0);
  setOpacity(rightShutter, 0);
  setOpacity(pivotRing, 0);

  setGroupTransform(wingTop, points.center.x, points.center.y, 0.82, 0);
  setGroupTransform(wingRight, points.center.x, points.center.y, 0.82, 90);
  setGroupTransform(wingBottom, points.center.x, points.center.y, 0.82, 180);
  setGroupTransform(wingLeft, points.center.x, points.center.y, 0.82, -90);
  setGroupTransform(activeTop, points.center.x, points.center.y, 0.82, 0);
  setGroupTransform(activeRight, points.center.x, points.center.y, 0.82, 90);
  setGroupTransform(activeBottom, points.center.x, points.center.y, 0.82, 180);
  setGroupTransform(activeLeft, points.center.x, points.center.y, 0.82, -90);

  [wingTop, wingRight, wingBottom, wingLeft, activeTop, activeRight, activeBottom, activeLeft].forEach((element) => setOpacity(element, 0));
  setPathWindow(activeTopPath, ACTIVE_TOP_LENGTH, 0, 0);
  setPathWindow(activeRightPath, ACTIVE_RIGHT_LENGTH, 0, 0);
  setPathWindow(activeBottomPath, ACTIVE_BOTTOM_LENGTH, 0, 0);
  setPathWindow(activeLeftPath, ACTIVE_LEFT_LENGTH, 0, 0);

  setEllipseRadius(resolutionHalo, 146, 152);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRing, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.entry, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(16, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.1) * 1.5, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.14);
  setOpacity(candidateFlap, preview * 0.12);
  setOpacity(candidateCorner, preview * 0.08);
  setOpacity(candidateSplit, preview * 0.06);
  setOpacity(throatGuide, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.entry, to: points.flap },
    { start: 0.24, end: 0.54, from: points.flap, to: points.corner },
    { start: 0.54, end: 0.82, from: points.corner, to: points.split },
    { start: 0.82, end: 1, from: points.split, to: points.mouth },
  ]);

  setDot(position, 18, 84, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.14, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.24, 0.12, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.2 + revealA * 0.22);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateFlap, points.flap.x, points.flap.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), -6);
  setGroupTransform(candidateCorner, points.corner.x, points.corner.y, lerp(0.9, activeB ? 1.05 : 0.97, revealB), 0);
  setGroupTransform(candidateSplit, points.split.x, points.split.y, lerp(0.9, activeC ? 1.05 : 0.97, revealC), 4);
  setOpacity(candidateFlap, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateCorner, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateSplit, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(topPin, 0.08);
  setOpacity(throatGuide, 0.12);
}

function renderTension(progress) {
  const ingress = easeInOut(clamp(progress / 0.28, 0, 1));
  const compression = clamp((progress - 0.32) / 0.28, 0, 1);
  const position = mixPoint(points.mouth, points.pocket, ingress);
  const shutterScale = lerp(0.66, 1, easeInOut(clamp((progress - 0.14) / 0.34, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(84, 108, progress),
    1,
    0.24 + pulseWave(progress, 2) * 0.1,
    lerp(1, 0.72, compression),
    lerp(1, 1.18, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.18 : 0.12, 0, progress));
  });

  setGroupTransform(candidateFlap, lerp(points.flap.x, 742, progress), lerp(points.flap.y, 420, progress), lerp(0.98, 0.76, progress), -12);
  setGroupTransform(candidateCorner, lerp(points.corner.x, 846, progress), lerp(points.corner.y, 382, progress), lerp(0.98, 0.72, progress), 0);
  setGroupTransform(candidateSplit, lerp(points.split.x, 952, progress), lerp(points.split.y, 430, progress), lerp(1, 0.78, progress), 10);
  setOpacity(candidateFlap, lerp(0.28, 0.04, progress));
  setOpacity(candidateCorner, lerp(0.24, 0.04, progress));
  setOpacity(candidateSplit, lerp(0.74, 0.06, progress));

  setEllipseRadius(tensionHalo, lerp(166, 176, progress), lerp(126, 134, progress));
  setOpacity(tensionHalo, clamp((progress - 0.02) * 1.6, 0, 0.24));
  setOpacity(throatGuide, lerp(0.12, 0.28, progress));
  setGroupTransform(topPin, points.center.x, points.center.y, 1, 0);
  setGroupTransform(bottomSlot, points.center.x, lerp(points.center.y + 122, points.center.y + 110, progress), 1, 0);
  setOpacity(topPin, clamp((progress - 0.06) * 1.8, 0, 0.92));
  setOpacity(bottomSlot, clamp((progress - 0.14) * 1.8, 0, 0.92));
  setGroupTransform(leftShutter, points.center.x, points.center.y, shutterScale, 0, lerp(0.92, 1.02, progress));
  setGroupTransform(rightShutter, points.center.x, points.center.y, shutterScale, 0, lerp(0.92, 1.02, progress));
  setOpacity(leftShutter, clamp((progress - 0.16) * 1.8, 0, 1));
  setOpacity(rightShutter, clamp((progress - 0.16) * 1.8, 0, 1));
  setOpacity(pivotRing, clamp((progress - 0.3) * 1.6, 0, 0.16));
}

function renderTransformation(progress) {
  const rise = rangedProgress(progress, 0, 0.34);
  const settle = rangedProgress(progress, 0.34, 1);
  const topReveal = easeInOut(rangedProgress(progress, 0.08, 0.34));
  const rightReveal = easeInOut(rangedProgress(progress, 0.24, 0.52));
  const leftReveal = easeInOut(rangedProgress(progress, 0.38, 0.68));
  const bottomReveal = easeInOut(rangedProgress(progress, 0.54, 0.86));
  const activeTopReveal = easeInOut(rangedProgress(progress, 0.1, 0.28));
  const activeRightReveal = easeInOut(rangedProgress(progress, 0.26, 0.48));
  const activeLeftReveal = easeInOut(rangedProgress(progress, 0.42, 0.66));
  const activeBottomReveal = easeInOut(rangedProgress(progress, 0.58, 0.84));
  const route =
    progress <= 0.34
      ? mixPoint(points.pocket, points.pivot, easeInOut(rise))
      : mixPoint(points.pivot, points.center, easeInOut(settle));

  setDot(
    route,
    16,
    98,
    1,
    0.22 + pulseWave(progress, 1.8) * 0.08,
    lerp(0.74, 1, settle || topReveal),
    lerp(1.18, 1, settle || topReveal),
  );
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);
  [searchGuideA, searchGuideB, searchGuideC, candidateFlap, candidateCorner, candidateSplit].forEach((element) => setOpacity(element, 0));

  setEllipseRadius(tensionHalo, lerp(176, 146, progress), lerp(134, 152, progress));
  setOpacity(tensionHalo, lerp(0.24, 0.12, progress));
  setOpacity(throatGuide, clamp(0.28 - progress * 0.34, 0, 1));
  setOpacity(topPin, lerp(0.92, 0.46, progress));
  setOpacity(bottomSlot, lerp(0.92, 0.1, progress));
  setGroupTransform(leftShutter, points.center.x, points.center.y, lerp(1, 0.76, progress), -lerp(0, 18, progress), lerp(1.02, 0.9, progress));
  setGroupTransform(rightShutter, points.center.x, points.center.y, lerp(1, 0.76, progress), lerp(0, 18, progress), lerp(1.02, 0.9, progress));
  setOpacity(leftShutter, lerp(1, 0, clamp((progress - 0.18) * 1.45, 0, 1)));
  setOpacity(rightShutter, lerp(1, 0, clamp((progress - 0.18) * 1.45, 0, 1)));
  setOpacity(pivotRing, clamp((progress - 0.18) * 1.4, 0, 0.26));

  setGroupTransform(wingTop, points.center.x, points.center.y, lerp(0.72, 1, topReveal), lerp(-8, 0, topReveal));
  setGroupTransform(wingRight, points.center.x, points.center.y, lerp(0.72, 1, rightReveal), lerp(96, 90, rightReveal));
  setGroupTransform(wingLeft, points.center.x, points.center.y, lerp(0.72, 1, leftReveal), lerp(-96, -90, leftReveal));
  setGroupTransform(wingBottom, points.center.x, points.center.y, lerp(0.72, 1, bottomReveal), lerp(172, 180, bottomReveal));
  setOpacity(wingTop, clamp(topReveal * 1.1, 0, 0.92));
  setOpacity(wingRight, clamp(rightReveal * 1.1, 0, 0.92));
  setOpacity(wingLeft, clamp(leftReveal * 1.1, 0, 0.92));
  setOpacity(wingBottom, clamp(bottomReveal * 1.1, 0, 0.92));

  setGroupTransform(activeTop, points.center.x, points.center.y, lerp(0.72, 1, topReveal), 0);
  setGroupTransform(activeRight, points.center.x, points.center.y, lerp(0.72, 1, rightReveal), 90);
  setGroupTransform(activeLeft, points.center.x, points.center.y, lerp(0.72, 1, leftReveal), -90);
  setGroupTransform(activeBottom, points.center.x, points.center.y, lerp(0.72, 1, bottomReveal), 180);
  setPathWindow(activeTopPath, ACTIVE_TOP_LENGTH, ACTIVE_TOP_LENGTH * activeTopReveal, activeTopReveal * 0.96);
  setPathWindow(activeRightPath, ACTIVE_RIGHT_LENGTH, ACTIVE_RIGHT_LENGTH * activeRightReveal, activeRightReveal * 0.94);
  setPathWindow(activeLeftPath, ACTIVE_LEFT_LENGTH, ACTIVE_LEFT_LENGTH * activeLeftReveal, activeLeftReveal * 0.92);
  setPathWindow(activeBottomPath, ACTIVE_BOTTOM_LENGTH, ACTIVE_BOTTOM_LENGTH * activeBottomReveal, activeBottomReveal * 0.94);

  setOpacity(resolutionHalo, clamp((progress - 0.42) * 1.45, 0, 0.24));
  setOpacity(resolutionRing, clamp((progress - 0.62) * 1.45, 0, 0.2));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.center, 16, 92, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(throatGuide, 0);
  setOpacity(tensionHalo, 0);
  setOpacity(topPin, 0.14);
  setOpacity(bottomSlot, 0);
  setOpacity(leftShutter, 0);
  setOpacity(rightShutter, 0);
  setOpacity(pivotRing, lerp(0.26, 0.18, settle));

  setGroupTransform(wingTop, points.center.x, points.center.y, lerp(1, 0.94, settle), 0);
  setGroupTransform(wingRight, points.center.x, points.center.y, lerp(1, 0.94, settle), 90);
  setGroupTransform(wingBottom, points.center.x, points.center.y, lerp(1, 0.94, settle), 180);
  setGroupTransform(wingLeft, points.center.x, points.center.y, lerp(1, 0.94, settle), -90);
  [wingTop, wingRight, wingBottom, wingLeft].forEach((element) => setOpacity(element, lerp(0.92, 0.84, settle)));

  setGroupTransform(activeTop, points.center.x, points.center.y, 0.94, 0);
  setGroupTransform(activeRight, points.center.x, points.center.y, 0.94, 90);
  setGroupTransform(activeBottom, points.center.x, points.center.y, 0.94, 180);
  setGroupTransform(activeLeft, points.center.x, points.center.y, 0.94, -90);
  setPathWindow(activeTopPath, ACTIVE_TOP_LENGTH, ACTIVE_TOP_LENGTH, lerp(0.14, 0.04, settle));
  setPathWindow(activeRightPath, ACTIVE_RIGHT_LENGTH, ACTIVE_RIGHT_LENGTH, lerp(0.12, 0.03, settle));
  setPathWindow(activeBottomPath, ACTIVE_BOTTOM_LENGTH, ACTIVE_BOTTOM_LENGTH, lerp(0.12, 0.03, settle));
  setPathWindow(activeLeftPath, ACTIVE_LEFT_LENGTH, ACTIVE_LEFT_LENGTH, lerp(0.12, 0.03, settle));

  setEllipseRadius(resolutionHalo, 146, 152);
  setOpacity(resolutionHalo, lerp(0.24, 0.32, settle));
  setOpacity(resolutionRing, lerp(0.2, 0.86, settle));
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
