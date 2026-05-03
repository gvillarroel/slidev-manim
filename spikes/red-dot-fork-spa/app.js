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
const searchGuideD = document.getElementById("search-guide-d");
const candidateStem = document.getElementById("candidate-stem");
const candidateSplit = document.getElementById("candidate-split");
const candidateFork = document.getElementById("candidate-fork");
const forkGuide = document.getElementById("fork-guide");
const stemGuide = document.getElementById("stem-guide");
const pressureHalo = document.getElementById("pressure-halo");
const shoulderLeft = document.getElementById("shoulder-left");
const shoulderRight = document.getElementById("shoulder-right");
const crownCap = document.getElementById("crown-cap");
const forkShell = document.getElementById("fork-shell");
const forkBase = document.getElementById("fork-base");
const forkTrace = document.getElementById("fork-trace");
const slotLeftTip = document.getElementById("slot-left-tip");
const slotCenterTip = document.getElementById("slot-center-tip");
const slotRightTip = document.getElementById("slot-right-tip");
const slotStem = document.getElementById("slot-stem");
const tineLeft = document.getElementById("tine-left");
const tineCenter = document.getElementById("tine-center");
const tineRight = document.getElementById("tine-right");
const stemBlock = document.getElementById("stem-block");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const FORK_TRACE_LENGTH = forkTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 316, y: 470 },
  ingress: { x: 564, y: 470 },
  candidateStem: { x: 652, y: 420 },
  candidateSplit: { x: 822, y: 388 },
  candidateFork: { x: 998, y: 418 },
  junctionApproach: { x: 938, y: 470 },
  stemBase: { x: 820, y: 500 },
  hub: { x: 820, y: 388 },
};

const fork = {
  left: { x: 754, y: 328, rotate: -30 },
  center: { x: 820, y: 296, rotate: 0 },
  right: { x: 886, y: 328, rotate: 30 },
  stem: { x: 820, y: 474, rotate: 0 },
  squeezeLeft: { x: 786, y: 396, rotate: -18 },
  squeezeCenter: { x: 820, y: 356, rotate: 0 },
  squeezeRight: { x: 854, y: 396, rotate: 18 },
  squeezeStem: { x: 820, y: 458, rotate: 0 },
  settleLeft: { x: 750, y: 332, rotate: -28 },
  settleCenter: { x: 820, y: 300, rotate: 0 },
  settleRight: { x: 890, y: 332, rotate: 28 },
  settleStem: { x: 820, y: 478, rotate: 0 },
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

function pointOnFork(progress) {
  const length = clamp(progress, 0, 1) * FORK_TRACE_LENGTH;
  const point = forkTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function pieceReveal(progress, threshold) {
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
    appearance: 16,
    search: 24,
    tension: 8,
    transformation: 2,
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
    appearance: { x: 140, y: 146, width: 1090, height: 638 },
    search: { x: 166, y: 118, width: 1102, height: 664 },
    tension: { x: 334, y: 124, width: 972, height: 668 },
    transformation: { x: 336, y: 92, width: 968, height: 708 },
    resolution: { x: 380, y: 100, width: 900, height: 696 },
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

function resetPressure() {
  setGroupTransform(shoulderLeft, 746, 406, 1, 0);
  setGroupTransform(shoulderRight, 894, 406, 1, 0);
  setGroupTransform(crownCap, 820, 306, 1, 0);
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC, searchGuideD].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateStem, points.candidateStem.x, points.candidateStem.y, 1, -4);
  setGroupTransform(candidateSplit, points.candidateSplit.x, points.candidateSplit.y, 1, 0);
  setGroupTransform(candidateFork, points.candidateFork.x, points.candidateFork.y, 1, 4);
  [candidateStem, candidateSplit, candidateFork].forEach((element) => setOpacity(element, 0));

  setOpacity(forkGuide, 0);
  setOpacity(stemGuide, 0);
  setOpacity(pressureHalo, 0);
  resetPressure();
  setOpacity(shoulderLeft, 0);
  setOpacity(shoulderRight, 0);
  setOpacity(crownCap, 0);

  setOpacity(forkShell, 0);
  setOpacity(forkBase, 0);
  setPathWindow(forkTrace, FORK_TRACE_LENGTH, 0, 0);

  setGroupTransform(slotLeftTip, fork.left.x, fork.left.y, 1, fork.left.rotate);
  setGroupTransform(slotCenterTip, fork.center.x, fork.center.y, 1, fork.center.rotate);
  setGroupTransform(slotRightTip, fork.right.x, fork.right.y, 1, fork.right.rotate);
  setGroupTransform(slotStem, fork.stem.x, fork.stem.y, 1, fork.stem.rotate);
  [slotLeftTip, slotCenterTip, slotRightTip, slotStem].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(tineLeft, fork.left.x, fork.left.y, 1, fork.left.rotate);
  setGroupTransform(tineCenter, fork.center.x, fork.center.y, 1, fork.center.rotate);
  setGroupTransform(tineRight, fork.right.x, fork.right.y, 1, fork.right.rotate);
  setGroupTransform(stemBlock, fork.stem.x, fork.stem.y, 1, fork.stem.rotate);
  [tineLeft, tineCenter, tineRight, stemBlock].forEach((piece) => setOpacity(piece, 0));

  setOpacity(anchorGrid, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, clamp(eased * 1.02, 0, 1));

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.4) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.2);
  setOpacity(candidateStem, preview * 0.16);
  setOpacity(candidateSplit, preview * 0.1);
  setOpacity(candidateFork, preview * 0.08);
  setOpacity(forkGuide, preview * 0.12);
  setOpacity(stemGuide, preview * 0.1);
  setOpacity(shoulderLeft, preview * 0.05);
  setOpacity(shoulderRight, preview * 0.05);
  setOpacity(crownCap, preview * 0.05);
  setOpacity(forkShell, preview * 0.05);
  setOpacity(forkBase, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.candidateStem },
    { start: 0.24, end: 0.52, from: points.candidateStem, to: points.candidateSplit },
    { start: 0.52, end: 0.82, from: points.candidateSplit, to: points.candidateFork },
    { start: 0.82, end: 1, from: points.candidateFork, to: points.junctionApproach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.22, 0.06, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.04, progress));

  const revealA = clamp(progress / 0.2, 0, 1);
  const revealB = clamp((progress - 0.2) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.46) / 0.24, 0, 1);
  const revealD = clamp((progress - 0.76) / 0.18, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.24 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.24 && progress < 0.52 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.52 && progress < 0.82 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideD.setAttribute("stroke", progress >= 0.82 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.22 + revealA * 0.18);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.1 + revealC * 0.24);
  setOpacity(searchGuideD, revealD * 0.22);

  const activeStem = progress < 0.24 ? 1 : 0;
  const activeSplit = progress >= 0.24 && progress < 0.52 ? 1 : 0;
  const activeFork = progress >= 0.52 && progress < 0.82 ? 1 : 0;

  setGroupTransform(candidateStem, points.candidateStem.x, points.candidateStem.y, lerp(0.88, activeStem ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateSplit, points.candidateSplit.x, points.candidateSplit.y, lerp(0.88, activeSplit ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateFork, points.candidateFork.x, points.candidateFork.y, lerp(0.84, activeFork ? 1.05 : 0.95, revealC), 4);
  setOpacity(candidateStem, activeStem ? 1 : revealA * 0.32 + 0.14);
  setOpacity(candidateSplit, activeSplit ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateFork, activeFork ? 1 : revealC * 0.34 + 0.12);

  setOpacity(forkGuide, 0.14);
  setOpacity(stemGuide, 0.1);
  setOpacity(shoulderLeft, 0.05);
  setOpacity(shoulderRight, 0.05);
  setOpacity(crownCap, 0.05);
  setOpacity(forkShell, 0.05);
  setOpacity(forkBase, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.junctionApproach, points.hub, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.76, 0, 1);
  const shoulderGap = lerp(74, 40, easeInOut(clamp(progress / 0.72, 0, 1)));
  const crownY = lerp(306, 338, easeInOut(clamp(progress / 0.7, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.56, compression),
    lerp(1, 1.84, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC, searchGuideD].forEach((guide, index) => {
    guide.setAttribute("stroke", index >= 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 3 ? 0.22 : 0.18, 0, progress));
  });

  const stemPosition = mixPoint(points.candidateStem, { x: 744, y: 430 }, collapse);
  const splitPosition = mixPoint(points.candidateSplit, { x: 820, y: 392 }, collapse);
  const forkPosition = mixPoint(points.candidateFork, { x: 900, y: 430 }, collapse);
  setGroupTransform(candidateStem, stemPosition.x, stemPosition.y, lerp(0.96, 0.72, collapse), -8);
  setGroupTransform(candidateSplit, splitPosition.x, splitPosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateFork, forkPosition.x, forkPosition.y, lerp(0.95, 0.68, collapse), 8);
  setOpacity(candidateStem, lerp(0.28, 0.04, collapse));
  setOpacity(candidateSplit, lerp(0.32, 0.06, collapse));
  setOpacity(candidateFork, lerp(1, 0.14, collapse));

  setOpacity(forkGuide, clamp((progress - 0.04) * 1.7, 0, 0.82));
  setOpacity(stemGuide, clamp((progress - 0.06) * 1.6, 0, 0.84));
  setOpacity(shoulderLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(shoulderRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(crownCap, clamp((progress - 0.08) * 1.6, 0, 0.98));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(shoulderLeft, points.hub.x - shoulderGap, 406, 1, 0);
  setGroupTransform(shoulderRight, points.hub.x + shoulderGap, 406, 1, 0);
  setGroupTransform(crownCap, points.hub.x, crownY, 1, 0);

  const pieceEase = easeInOut(clamp(progress / 0.72, 0, 1));
  setGroupTransform(
    tineLeft,
    lerp(fork.left.x, fork.squeezeLeft.x, pieceEase),
    lerp(fork.left.y, fork.squeezeLeft.y, pieceEase),
    0.94,
    lerp(fork.left.rotate, fork.squeezeLeft.rotate, pieceEase),
  );
  setGroupTransform(
    tineCenter,
    lerp(fork.center.x, fork.squeezeCenter.x, pieceEase),
    lerp(fork.center.y, fork.squeezeCenter.y, pieceEase),
    0.94,
    0,
  );
  setGroupTransform(
    tineRight,
    lerp(fork.right.x, fork.squeezeRight.x, pieceEase),
    lerp(fork.right.y, fork.squeezeRight.y, pieceEase),
    0.94,
    lerp(fork.right.rotate, fork.squeezeRight.rotate, pieceEase),
  );
  setGroupTransform(
    stemBlock,
    lerp(fork.stem.x, fork.squeezeStem.x, pieceEase),
    lerp(fork.stem.y, fork.squeezeStem.y, pieceEase),
    0.94,
    0,
  );
  [tineLeft, tineCenter, tineRight, stemBlock].forEach((piece) =>
    setOpacity(piece, clamp((progress - 0.04) * 1.7, 0, 0.98)),
  );

  setOpacity(forkShell, clamp((progress - 0.48) * 0.42, 0, 0.16));
  setOpacity(forkBase, clamp((progress - 0.54) * 0.4, 0, 0.16));
  setOpacity(slotLeftTip, clamp((progress - 0.42) * 1.3, 0, 0.24));
  setOpacity(slotCenterTip, clamp((progress - 0.52) * 1.3, 0, 0.24));
  setOpacity(slotRightTip, clamp((progress - 0.62) * 1.3, 0, 0.24));
  setOpacity(slotStem, clamp((progress - 0.72) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnFork(routeProgress);
  const leftReveal = pieceReveal(routeProgress, 0.22);
  const centerReveal = pieceReveal(routeProgress, 0.48);
  const rightReveal = pieceReveal(routeProgress, 0.72);
  const stemReveal = pieceReveal(routeProgress, 0.08);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(forkShell, lerp(0.24, 0.98, routeProgress));
  setOpacity(forkBase, lerp(0.14, 0.3, routeProgress));
  setPathWindow(forkTrace, FORK_TRACE_LENGTH, FORK_TRACE_LENGTH * routeProgress, 1);

  setOpacity(forkGuide, lerp(0.82, 0.08, progress));
  setOpacity(stemGuide, lerp(0.84, 0.08, progress));
  setOpacity(shoulderLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(shoulderRight, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(crownCap, clamp(0.98 - progress * 1.1, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));

  setOpacity(candidateStem, clamp(0.04 - progress * 0.08, 0, 1));
  setOpacity(candidateSplit, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateFork, clamp(0.14 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC, searchGuideD].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotLeftTip, slotState(routeProgress, 0.22));
  setOpacity(slotCenterTip, slotState(routeProgress, 0.48));
  setOpacity(slotRightTip, slotState(routeProgress, 0.72));
  setOpacity(slotStem, slotState(routeProgress, 0.08));

  setGroupTransform(
    tineLeft,
    lerp(fork.squeezeLeft.x, fork.left.x, easeOut(leftReveal)),
    lerp(fork.squeezeLeft.y, fork.left.y, easeOut(leftReveal)),
    lerp(0.94, 1, easeOut(leftReveal)),
    lerp(fork.squeezeLeft.rotate, fork.left.rotate, easeOut(leftReveal)),
  );
  setGroupTransform(
    tineCenter,
    lerp(fork.squeezeCenter.x, fork.center.x, easeOut(centerReveal)),
    lerp(fork.squeezeCenter.y, fork.center.y, easeOut(centerReveal)),
    lerp(0.94, 1, easeOut(centerReveal)),
    0,
  );
  setGroupTransform(
    tineRight,
    lerp(fork.squeezeRight.x, fork.right.x, easeOut(rightReveal)),
    lerp(fork.squeezeRight.y, fork.right.y, easeOut(rightReveal)),
    lerp(0.94, 1, easeOut(rightReveal)),
    lerp(fork.squeezeRight.rotate, fork.right.rotate, easeOut(rightReveal)),
  );
  setGroupTransform(
    stemBlock,
    lerp(fork.squeezeStem.x, fork.stem.x, easeOut(stemReveal)),
    lerp(fork.squeezeStem.y, fork.stem.y, easeOut(stemReveal)),
    lerp(0.94, 1, easeOut(stemReveal)),
    0,
  );
  setOpacity(tineLeft, lerp(0.72, 1, leftReveal));
  setOpacity(tineCenter, lerp(0.72, 1, centerReveal));
  setOpacity(tineRight, lerp(0.72, 1, rightReveal));
  setOpacity(stemBlock, lerp(0.72, 1, stemReveal));

  setOpacity(anchorGrid, clamp((progress - 0.72) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.hub, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(forkShell, lerp(0.98, 0.92, settle));
  setOpacity(forkBase, lerp(0.3, 0.22, settle));
  setPathWindow(forkTrace, FORK_TRACE_LENGTH, FORK_TRACE_LENGTH, lerp(1, 0.18, settle));

  [
    forkGuide,
    stemGuide,
    pressureHalo,
    candidateStem,
    candidateSplit,
    candidateFork,
    slotLeftTip,
    slotCenterTip,
    slotRightTip,
    slotStem,
  ].forEach((element) => setOpacity(element, 0));
  setOpacity(shoulderLeft, 0);
  setOpacity(shoulderRight, 0);
  setOpacity(crownCap, 0);

  setGroupTransform(
    tineLeft,
    lerp(fork.left.x, fork.settleLeft.x, settle),
    lerp(fork.left.y, fork.settleLeft.y, settle),
    0.97,
    lerp(fork.left.rotate, fork.settleLeft.rotate, settle),
  );
  setGroupTransform(
    tineCenter,
    lerp(fork.center.x, fork.settleCenter.x, settle),
    lerp(fork.center.y, fork.settleCenter.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    tineRight,
    lerp(fork.right.x, fork.settleRight.x, settle),
    lerp(fork.right.y, fork.settleRight.y, settle),
    0.97,
    lerp(fork.right.rotate, fork.settleRight.rotate, settle),
  );
  setGroupTransform(
    stemBlock,
    lerp(fork.stem.x, fork.settleStem.x, settle),
    lerp(fork.stem.y, fork.settleStem.y, settle),
    0.97,
    0,
  );
  setOpacity(tineLeft, 0.92);
  setOpacity(tineCenter, 0.92);
  setOpacity(tineRight, 0.92);
  setOpacity(stemBlock, 0.9);

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
