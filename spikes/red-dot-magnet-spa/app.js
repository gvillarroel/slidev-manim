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
const phaseStatus = document.getElementById("phase-status");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const guideA = document.getElementById("guide-a");
const guideB = document.getElementById("guide-b");
const guideC = document.getElementById("guide-c");
const guideD = document.getElementById("guide-d");
const candidateHorseshoe = document.getElementById("candidate-horseshoe");
const candidateBars = document.getElementById("candidate-bars");
const candidateCorner = document.getElementById("candidate-corner");

const tensionGroup = document.getElementById("tension-group");
const fieldHalo = document.getElementById("field-halo");
const leftPole = document.getElementById("left-pole");
const rightPole = document.getElementById("right-pole");
const topField = document.getElementById("top-field");
const bottomField = document.getElementById("bottom-field");
const throatGuide = document.getElementById("throat-guide");
const fieldMemory = document.getElementById("field-memory");

const transformGroup = document.getElementById("transform-group");
const arcTopBase = document.getElementById("arc-top-base");
const arcBottomBase = document.getElementById("arc-bottom-base");
const arcTopActive = document.getElementById("arc-top-active");
const arcBottomActive = document.getElementById("arc-bottom-active");
const innerField = document.getElementById("inner-field");
const finalLeftPole = document.getElementById("final-left-pole");
const finalRightPole = document.getElementById("final-right-pole");
const topCrossbar = document.getElementById("top-crossbar");
const bottomCrossbar = document.getElementById("bottom-crossbar");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionTopArc = document.getElementById("resolution-top-arc");
const resolutionBottomArc = document.getElementById("resolution-bottom-arc");
const resolutionLeftMemory = document.getElementById("resolution-left-memory");
const resolutionRightMemory = document.getElementById("resolution-right-memory");
const resolutionCoreFrame = document.getElementById("resolution-core-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ARC_TOP_LENGTH = arcTopActive.getTotalLength();
const ARC_BOTTOM_LENGTH = arcBottomActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  lineGray: "#cfcfcf",
  passiveGray: "#b5b5b5",
};

const points = {
  start: { x: 302, y: 452 },
  entry: { x: 428, y: 452 },
  searchA: { x: 532, y: 366 },
  searchB: { x: 770, y: 324 },
  searchC: { x: 624, y: 560 },
  pocket: { x: 866, y: 452 },
  topTrace: { x: 866, y: 338 },
  rightTrace: { x: 1000, y: 452 },
  bottomTrace: { x: 866, y: 566 },
  leftTrace: { x: 732, y: 452 },
  final: { x: 866, y: 452 },
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

function setGroupTransform(element, x, y, scale = 1) {
  element.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${scale.toFixed(3)})`);
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

function updatePhaseStatus(info) {
  phaseStatus.textContent = info.phase.label;
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 120, width: 1080 },
    search: { x: 180, width: 1020 },
    tension: { x: 460, width: 760 },
    transformation: { x: 360, width: 980 },
    resolution: { x: 380, width: 940 },
  };
  const frame = frames[phaseId] ?? { x: 0, width: 1600 };
  svg.setAttribute("viewBox", `${frame.x} 0 ${frame.width} 900`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -10) translate(800 450) scale(1.05) translate(-800 -450)",
    );
    sceneRoot.setAttribute("transform", "translate(0 12)");
    svg.dataset.layout = "portrait";
  } else {
    layoutRoot.setAttribute("transform", "");
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
  svg.setAttribute("viewBox", FULL_VIEWBOX);
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [guideA, guideB, guideC, guideD].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateHorseshoe, points.searchA.x, points.searchA.y, 1);
  setGroupTransform(candidateBars, points.searchB.x, points.searchB.y, 1);
  setGroupTransform(candidateCorner, points.searchC.x, points.searchC.y, 1);
  [candidateHorseshoe, candidateBars, candidateCorner].forEach((element) => setOpacity(element, 0));

  setOpacity(tensionGroup, 0);
  setOpacity(fieldHalo, 0);
  leftPole.setAttribute("x", "720");
  rightPole.setAttribute("x", "918");
  topField.setAttribute("d", "M 738 390 C 786 324, 946 324, 994 390");
  bottomField.setAttribute("d", "M 738 514 C 786 580, 946 580, 994 514");
  setOpacity(throatGuide, 0);
  setOpacity(fieldMemory, 0);

  setOpacity(transformGroup, 0);
  [arcTopBase, arcBottomBase, arcTopActive, arcBottomActive, innerField, finalLeftPole, finalRightPole, topCrossbar, bottomCrossbar].forEach(
    (element) => setOpacity(element, 0),
  );
  setPathWindow(arcTopActive, ARC_TOP_LENGTH, 0, 0);
  setPathWindow(arcBottomActive, ARC_BOTTOM_LENGTH, 0, 0);

  setOpacity(resolutionGroup, 0);
  [resolutionTopArc, resolutionBottomArc, resolutionLeftMemory, resolutionRightMemory, resolutionCoreFrame].forEach((element) =>
    setOpacity(element, 0),
  );
}

function renderAppearance(progress) {
  const eased = easeOut(clamp((progress - 0.08) / 0.92, 0, 1));
  const position = mixPoint(points.start, points.entry, eased * 0.88);

  setDot(position, lerp(6, 18, eased), lerp(20, 82, eased), clamp(progress * 1.8, 0, 1), 0.16 + pulseWave(progress, 1.1) * 0.08);
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.2, 0, 0.32));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(guideA, clamp((progress - 0.18) * 1.6, 0, 0.22));
  setOpacity(guideB, clamp((progress - 0.24) * 1.6, 0, 0.18));
  setOpacity(guideC, clamp((progress - 0.3) * 1.6, 0, 0.16));
  setOpacity(guideD, clamp((progress - 0.36) * 1.6, 0, 0.14));
  setOpacity(candidateHorseshoe, clamp((progress - 0.22) * 1.5, 0, 0.28));
  setOpacity(candidateBars, clamp((progress - 0.3) * 1.5, 0, 0.24));
  setOpacity(candidateCorner, clamp((progress - 0.38) * 1.5, 0, 0.22));

  setOpacity(tensionGroup, clamp((progress - 0.48) * 1.4, 0, 0.14));
  setOpacity(throatGuide, clamp((progress - 0.52) * 1.4, 0, 0.16));
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.entry, to: points.searchA },
    { start: 0.28, end: 0.56, from: points.searchA, to: points.searchB },
    { start: 0.56, end: 0.82, from: points.searchB, to: points.searchC },
    { start: 0.82, end: 1, from: points.searchC, to: points.pocket },
  ]);

  setDot(position, 18, 84, 1, 0.22 + pulseWave(progress, 1.9) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.14, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 230 + progress * 290, 0.78);

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  guideA.setAttribute("stroke", progress < 0.32 ? COLORS.primaryRed : COLORS.lineGray);
  guideB.setAttribute("stroke", progress >= 0.32 && progress < 0.6 ? COLORS.primaryRed : COLORS.lineGray);
  guideC.setAttribute("stroke", progress >= 0.6 && progress < 0.82 ? COLORS.primaryRed : COLORS.lineGray);
  guideD.setAttribute("stroke", progress >= 0.82 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(guideA, 0.24 + revealA * 0.18);
  setOpacity(guideB, 0.18 + revealB * 0.18);
  setOpacity(guideC, 0.18 + revealC * 0.18);
  setOpacity(guideD, clamp((progress - 0.68) * 1.4, 0, 0.28));

  setGroupTransform(candidateHorseshoe, points.searchA.x, points.searchA.y, lerp(0.9, progress < 0.32 ? 1.07 : 0.97, revealA));
  setGroupTransform(candidateBars, points.searchB.x, points.searchB.y, lerp(0.9, progress >= 0.32 && progress < 0.6 ? 1.07 : 0.97, revealB));
  setGroupTransform(candidateCorner, points.searchC.x, points.searchC.y, lerp(0.9, progress >= 0.6 ? 1.07 : 0.97, revealC));
  setOpacity(candidateHorseshoe, progress < 0.32 ? 0.94 : 0.34);
  setOpacity(candidateBars, progress >= 0.32 && progress < 0.6 ? 0.94 : 0.3);
  setOpacity(candidateCorner, progress >= 0.6 ? 0.94 : 0.28);

  const horseshoePaths = candidateHorseshoe.querySelectorAll("path");
  const barsRects = candidateBars.querySelectorAll("rect");
  const cornerPaths = candidateCorner.querySelectorAll("path");
  horseshoePaths[0].setAttribute("stroke", progress < 0.32 ? COLORS.primaryRed : COLORS.passiveGray);
  barsRects[0].setAttribute("stroke", progress >= 0.32 && progress < 0.6 ? COLORS.primaryRed : COLORS.passiveGray);
  barsRects[1].setAttribute("stroke", progress >= 0.32 && progress < 0.6 ? COLORS.primaryRed : COLORS.passiveGray);
  cornerPaths[1].setAttribute("stroke", progress >= 0.6 ? COLORS.primaryRed : COLORS.passiveGray);
  cornerPaths[2].setAttribute("stroke", progress >= 0.6 ? COLORS.primaryRed : COLORS.passiveGray);

  setOpacity(tensionGroup, 0.2);
  setOpacity(throatGuide, 0.22);
  setOpacity(fieldMemory, 0.12);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.34, 0, 1);
  const position = mixPoint(points.searchC, points.pocket, easeInOut(travel));
  const compression = progress < 0.3
    ? easeOut(progress / 0.3)
    : progress < 0.76
      ? 1
      : 1 - easeInOut((progress - 0.76) / 0.24);
  const pulse = progress > 0.28 && progress < 0.74
    ? (pulseWave((progress - 0.28) / 0.46, 2.2) - 0.5) * 10
    : 0;

  const poleGap = lerp(104, 62, compression) + pulse * 0.3;
  const arcLift = lerp(0, 26, compression) + pulse * 0.15;

  setDot(
    position,
    lerp(18, 16, compression),
    lerp(84, 112, compression),
    1,
    0.24 + compression * 0.16,
    lerp(1, 1.7, compression),
    lerp(1, 0.66, compression),
  );
  setOpacity(narrativeSpine, 0.12);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 660 + progress * 130, 0.86);

  [guideA, guideB, guideC, guideD].forEach((guide, index) => {
    setOpacity(guide, lerp(index === 3 ? 0.28 : 0.2, 0, progress));
  });

  const searchCollapse = clamp(progress / 0.64, 0, 1);
  setGroupTransform(candidateHorseshoe, lerp(points.searchA.x, 770, searchCollapse), lerp(points.searchA.y, 380, searchCollapse), lerp(0.97, 0.72, searchCollapse));
  setGroupTransform(candidateBars, lerp(points.searchB.x, 822, searchCollapse), lerp(points.searchB.y, 336, searchCollapse), lerp(0.97, 0.68, searchCollapse));
  setGroupTransform(candidateCorner, lerp(points.searchC.x, 858, searchCollapse), lerp(points.searchC.y, 530, searchCollapse), lerp(0.97, 0.74, searchCollapse));
  setOpacity(candidateHorseshoe, lerp(0.32, 0.06, searchCollapse));
  setOpacity(candidateBars, lerp(0.3, 0.08, searchCollapse));
  setOpacity(candidateCorner, lerp(0.94, 0.12, searchCollapse));

  setOpacity(tensionGroup, 1);
  setOpacity(fieldHalo, 0.16 + compression * 0.18);
  leftPole.setAttribute("x", (866 - poleGap - 94).toFixed(2));
  rightPole.setAttribute("x", (866 + poleGap).toFixed(2));
  topField.setAttribute("d", `M ${866 - poleGap - 58} ${390 - arcLift} C ${806} ${324 - arcLift}, ${926} ${324 - arcLift}, ${866 + poleGap + 58} ${390 - arcLift}`);
  bottomField.setAttribute("d", `M ${866 - poleGap - 58} ${514 + arcLift} C ${806} ${580 + arcLift}, ${926} ${580 + arcLift}, ${866 + poleGap + 58} ${514 + arcLift}`);
  setOpacity(throatGuide, 0.54);
  setOpacity(fieldMemory, 0.4);

  setOpacity(transformGroup, clamp((progress - 0.52) * 1.2, 0, 0.16));
  setOpacity(arcTopBase, clamp((progress - 0.64) * 1.5, 0, 0.12));
  setOpacity(arcBottomBase, clamp((progress - 0.64) * 1.5, 0, 0.12));
}

function renderTransformation(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.22, from: points.pocket, to: points.topTrace },
    { start: 0.22, end: 0.5, from: points.topTrace, to: points.rightTrace },
    { start: 0.5, end: 0.78, from: points.rightTrace, to: points.bottomTrace },
    { start: 0.78, end: 1, from: points.bottomTrace, to: points.final },
  ]);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0.04);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 220 + (1 - progress) * 120, 0.18);

  setOpacity(tensionGroup, lerp(1, 0.08, progress));
  setOpacity(fieldHalo, lerp(0.34, 0, progress));
  leftPole.setAttribute("x", lerp(710, 684, progress).toFixed(2));
  rightPole.setAttribute("x", lerp(928, 1002, progress).toFixed(2));
  topField.setAttribute("d", `M ${lerp(728, 748, progress).toFixed(2)} ${lerp(364, 392, progress).toFixed(2)} C 786 ${lerp(300, 336, progress).toFixed(2)}, 946 ${lerp(300, 336, progress).toFixed(2)}, ${lerp(1004, 984, progress).toFixed(2)} ${lerp(364, 392, progress).toFixed(2)}`);
  bottomField.setAttribute("d", `M ${lerp(728, 748, progress).toFixed(2)} ${lerp(540, 512, progress).toFixed(2)} C 786 ${lerp(604, 568, progress).toFixed(2)}, 946 ${lerp(604, 568, progress).toFixed(2)}, ${lerp(1004, 984, progress).toFixed(2)} ${lerp(540, 512, progress).toFixed(2)}`);
  setOpacity(throatGuide, lerp(0.54, 0, progress));
  setOpacity(fieldMemory, lerp(0.4, 0.1, progress));

  setOpacity(transformGroup, 1);
  setOpacity(arcTopBase, clamp((progress - 0.08) * 1.2, 0, 0.5));
  setOpacity(arcBottomBase, clamp((progress - 0.38) * 1.2, 0, 0.42));
  setPathWindow(arcTopActive, ARC_TOP_LENGTH, ARC_TOP_LENGTH * clamp((progress - 0.14) / 0.28, 0, 1), clamp((progress - 0.14) * 1.7, 0, 1));
  setPathWindow(arcBottomActive, ARC_BOTTOM_LENGTH, ARC_BOTTOM_LENGTH * clamp((progress - 0.46) / 0.28, 0, 1), clamp((progress - 0.46) * 1.8, 0, 1));

  const leftPoleReveal = clamp((progress - 0.12) / 0.16, 0, 1);
  const rightPoleReveal = clamp((progress - 0.28) / 0.16, 0, 1);
  const topRuleReveal = clamp((progress - 0.52) / 0.16, 0, 1);
  const bottomRuleReveal = clamp((progress - 0.68) / 0.16, 0, 1);

  setOpacity(finalLeftPole, leftPoleReveal);
  setOpacity(finalRightPole, rightPoleReveal);
  setOpacity(topCrossbar, topRuleReveal * 0.56);
  setOpacity(bottomCrossbar, bottomRuleReveal * 0.56);
  setOpacity(innerField, clamp((progress - 0.62) / 0.18, 0, 0.26));

  finalLeftPole.setAttribute(
    "transform",
    `translate(${lerp(-18, 0, easeOut(leftPoleReveal)).toFixed(2)} 0) scale(${lerp(0.94, 1, leftPoleReveal).toFixed(3)})`,
  );
  finalRightPole.setAttribute(
    "transform",
    `translate(${lerp(18, 0, easeOut(rightPoleReveal)).toFixed(2)} 0) scale(${lerp(0.94, 1, rightPoleReveal).toFixed(3)})`,
  );
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const pulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.final, 16, lerp(98, 84, progress), 1, pulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [guideA, guideB, guideC, guideD, candidateHorseshoe, candidateBars, candidateCorner, tensionGroup].forEach((element) =>
    setOpacity(element, 0),
  );

  setOpacity(transformGroup, 1);
  setOpacity(arcTopBase, lerp(0.48, 0.22, settle));
  setOpacity(arcBottomBase, lerp(0.42, 0.18, settle));
  setPathWindow(arcTopActive, ARC_TOP_LENGTH, ARC_TOP_LENGTH, lerp(1, 0.16, settle));
  setPathWindow(arcBottomActive, ARC_BOTTOM_LENGTH, ARC_BOTTOM_LENGTH, lerp(1, 0.08, settle));
  setOpacity(innerField, lerp(0.26, 0.12, settle));
  setOpacity(finalLeftPole, 0.94);
  setOpacity(finalRightPole, 0.94);
  setOpacity(topCrossbar, 0.44);
  setOpacity(bottomCrossbar, 0.4);

  finalLeftPole.setAttribute("transform", "");
  finalRightPole.setAttribute("transform", "");

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionTopArc, lerp(0.28, 0.82, settle));
  setOpacity(resolutionBottomArc, lerp(0.18, 0.62, settle));
  setOpacity(resolutionLeftMemory, lerp(0.52, 0.7, settle));
  setOpacity(resolutionRightMemory, lerp(0.52, 0.7, settle));
  setOpacity(resolutionCoreFrame, lerp(0.14, 0.46, settle));
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);
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

  svg.dataset.phase = info.phase.id;
  updatePhaseStatus(info);
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
