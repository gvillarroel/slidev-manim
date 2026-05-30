const TOTAL_DURATION = 36_200;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_200 },
  { id: "tension", label: "tension", duration: 6_200 },
  { id: "transformation", label: "transformation", duration: 7_400 },
  { id: "resolution", label: "resolution", duration: 10_400 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const entryLane = document.getElementById("entry-lane");
const activeTrail = document.getElementById("active-trail");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const previewBeam = document.getElementById("preview-beam");
const previewLeftLeg = document.getElementById("preview-left-leg");
const previewRightLeg = document.getElementById("preview-right-leg");
const previewLowerRail = document.getElementById("preview-lower-rail");
const previewCenterStem = document.getElementById("preview-center-stem");

const candidateWide = document.getElementById("candidate-wide");
const candidateOffset = document.getElementById("candidate-offset");
const candidateNested = document.getElementById("candidate-nested");

const pressureLeft = document.getElementById("pressure-left");
const pressureRight = document.getElementById("pressure-right");
const pressureTop = document.getElementById("pressure-top");
const pressureBottom = document.getElementById("pressure-bottom");

const caliperLeft = document.getElementById("caliper-left");
const caliperRight = document.getElementById("caliper-right");
const caliperBeam = document.getElementById("caliper-beam");
const caliperLowerRail = document.getElementById("caliper-lower-rail");
const caliperCenterStem = document.getElementById("caliper-center-stem");
const traceFrame = document.getElementById("trace-frame");
const traceCenter = document.getElementById("trace-center");

const slotTopLeft = document.getElementById("slot-top-left");
const slotTopRight = document.getElementById("slot-top-right");
const slotBottom = document.getElementById("slot-bottom");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TRACE_FRAME_LENGTH = traceFrame.getTotalLength();
const TRACE_CENTER_LENGTH = traceCenter.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 320, y: 452 },
  ingress: { x: 562, y: 448 },
  candidateA: { x: 676, y: 372 },
  candidateB: { x: 820, y: 332 },
  candidateC: { x: 968, y: 386 },
  approach: { x: 900, y: 452 },
  throat: { x: 820, y: 452 },
  bottom: { x: 820, y: 566 },
  hold: { x: 820, y: 452 },
};

const caliperAnchors = {
  left: { x: 748, y: 430 },
  right: { x: 892, y: 430 },
  beam: { x: 820, y: 296 },
  lower: { x: 820, y: 566 },
  stem: { x: 820, y: 566 },
};

const compressedAnchors = {
  left: { x: 792, y: 430 },
  right: { x: 848, y: 430 },
};

const slotPoints = {
  topLeft: { x: 748, y: 296 },
  topRight: { x: 892, y: 296 },
  bottom: { x: 820, y: 566 },
};

const candidateStyles = {
  active: { color: "#4f4f4f", opacity: 0.98 },
  visited: { color: "#b5b5b5", opacity: 0.42 },
  faint: { color: "#cfcfcf", opacity: 0.28 },
  hidden: { color: "#cfcfcf", opacity: 0 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
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

function setTransform(element, x, y, scaleX = 1, scaleY = scaleX, rotate = 0) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)})`,
  );
}

function setAbsoluteScale(element, origin, scaleX = 1, scaleY = scaleX) {
  element.setAttribute(
    "transform",
    `translate(${origin.x.toFixed(2)} ${origin.y.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-origin.x.toFixed(2)} ${-origin.y.toFixed(2)})`,
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

function pointOnTrace(path, progress, totalLength) {
  const point = path.getPointAtLength(clamp(progress, 0, 1) * totalLength);
  return { x: point.x, y: point.y };
}

function setCandidateState(element, mode) {
  const style = candidateStyles[mode];
  element.setAttribute("stroke", style.color);
  setOpacity(element, style.opacity);
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

function applyLayout(phaseId) {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.88) {
    layoutRoot.setAttribute(
      "transform",
      "translate(800 450) scale(1.038) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
    const frames = {
      appearance: { x: 124, y: 154, width: 1060, height: 648 },
      search: { x: 156, y: 136, width: 1054, height: 664 },
      tension: { x: 390, y: 156, width: 874, height: 628 },
      transformation: { x: 384, y: 122, width: 884, height: 688 },
      resolution: { x: 404, y: 108, width: 842, height: 706 },
    };
    const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
    svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
  } else {
    layoutRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svg.setAttribute("viewBox", FULL_VIEWBOX);
  }
}

function setCaliperPose(progress, opacity) {
  const leftX = lerp(compressedAnchors.left.x, caliperAnchors.left.x, progress);
  const rightX = lerp(compressedAnchors.right.x, caliperAnchors.right.x, progress);
  const legScaleY = lerp(0.88, 1, progress);
  const beamScaleX = lerp(0.44, 1, progress);
  const lowerScaleX = lerp(0.52, 1, progress);
  const stemScaleY = lerp(0.88, 1, progress);

  setTransform(caliperLeft, leftX, caliperAnchors.left.y, 1, legScaleY, 0);
  setTransform(caliperRight, rightX, caliperAnchors.right.y, 1, legScaleY, 0);
  setAbsoluteScale(caliperBeam, caliperAnchors.beam, beamScaleX, 1);
  setAbsoluteScale(caliperLowerRail, caliperAnchors.lower, lowerScaleX, 1);
  setAbsoluteScale(caliperCenterStem, caliperAnchors.stem, 1, stemScaleY);
  [caliperLeft, caliperRight, caliperBeam, caliperLowerRail, caliperCenterStem].forEach((element) => setOpacity(element, opacity));
}

function slotOpacity(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.34;
  }
  return clamp(1 - (progress - threshold) / 0.2, 0, 1) * 0.34;
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(entryLane, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [
    searchGuideA,
    searchGuideB,
    searchGuideC,
    previewBeam,
    previewLeftLeg,
    previewRightLeg,
    previewLowerRail,
    previewCenterStem,
  ].forEach((element) => setOpacity(element, 0));

  setTransform(candidateWide, points.candidateA.x, points.candidateA.y, 1, 1, -6);
  setTransform(candidateOffset, points.candidateB.x, points.candidateB.y, 1, 1, 0);
  setTransform(candidateNested, points.candidateC.x, points.candidateC.y, 1, 1, 6);
  [candidateWide, candidateOffset, candidateNested].forEach((element) => setCandidateState(element, "hidden"));

  setTransform(pressureLeft, 782, points.throat.y, 1, 1, 0);
  setTransform(pressureRight, 858, points.throat.y, 1, 1, 0);
  setTransform(pressureTop, points.throat.x, 392, 1, 1, 0);
  setTransform(pressureBottom, points.throat.x, 512, 1, 1, 0);
  [pressureLeft, pressureRight, pressureTop, pressureBottom].forEach((element) => setOpacity(element, 0));

  setCaliperPose(1, 0);
  setPathWindow(traceFrame, TRACE_FRAME_LENGTH, 0, 0);
  setPathWindow(traceCenter, TRACE_CENTER_LENGTH, 0, 0);

  setTransform(slotTopLeft, slotPoints.topLeft.x, slotPoints.topLeft.y, 1, 1, 0);
  setTransform(slotTopRight, slotPoints.topRight.x, slotPoints.topRight.y, 1, 1, 0);
  setTransform(slotBottom, slotPoints.bottom.x, slotPoints.bottom.y, 1, 1, 0);
  [slotTopLeft, slotTopRight, slotBottom].forEach((element) => setOpacity(element, 0));

  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);
  const preview = clamp((progress - 0.24) * 1.7, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 82, eased),
    clamp(progress * 1.9, 0, 1),
    0.22 + pulseWave(progress, 1.1) * 0.16,
  );

  setOpacity(entryLane, clamp((progress - 0.08) * 1.5, 0, 0.3));
  setOpacity(previewBeam, preview * 0.34);
  setOpacity(previewLeftLeg, preview * 0.24);
  setOpacity(previewRightLeg, preview * 0.24);
  setOpacity(previewLowerRail, preview * 0.28);
  setOpacity(previewCenterStem, preview * 0.22);
  setOpacity(searchGuideA, preview * 0.16);
  setOpacity(searchGuideB, preview * 0.12);
  setOpacity(searchGuideC, preview * 0.1);
  setOpacity(pressureLeft, preview * 0.08);
  setOpacity(pressureRight, preview * 0.08);
  setOpacity(pressureTop, preview * 0.06);
  setOpacity(pressureBottom, preview * 0.06);
  setCandidateState(candidateWide, progress > 0.52 ? "faint" : "hidden");
  setCandidateState(candidateOffset, progress > 0.62 ? "faint" : "hidden");
  setCandidateState(candidateNested, progress > 0.72 ? "faint" : "hidden");
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.26, from: points.ingress, to: points.candidateA },
    { start: 0.26, end: 0.56, from: points.candidateA, to: points.candidateB },
    { start: 0.56, end: 0.84, from: points.candidateB, to: points.candidateC },
    { start: 0.84, end: 1, from: points.candidateC, to: points.approach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(entryLane, lerp(0.24, 0.08, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * lerp(0.24, 1, progress), lerp(0.16, 0.05, progress));

  setOpacity(previewBeam, lerp(0.28, 0.1, progress));
  setOpacity(previewLeftLeg, lerp(0.2, 0.08, progress));
  setOpacity(previewRightLeg, lerp(0.2, 0.08, progress));
  setOpacity(previewLowerRail, lerp(0.22, 0.08, progress));
  setOpacity(previewCenterStem, lerp(0.18, 0.07, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  setOpacity(searchGuideA, 0.18 + revealA * 0.18);
  setOpacity(searchGuideB, 0.1 + revealB * 0.2);
  setOpacity(searchGuideC, 0.08 + revealC * 0.22);

  setTransform(candidateWide, points.candidateA.x, points.candidateA.y, lerp(0.9, progress < 0.28 ? 1.06 : 0.98, revealA), lerp(0.9, progress < 0.28 ? 1.06 : 0.98, revealA), -6);
  setTransform(candidateOffset, points.candidateB.x, points.candidateB.y, lerp(0.9, progress >= 0.28 && progress < 0.62 ? 1.05 : 0.98, revealB), lerp(0.9, progress >= 0.28 && progress < 0.62 ? 1.05 : 0.98, revealB), 0);
  setTransform(candidateNested, points.candidateC.x, points.candidateC.y, lerp(0.88, progress >= 0.62 ? 1.05 : 0.98, revealC), lerp(0.88, progress >= 0.62 ? 1.05 : 0.98, revealC), 6);
  setCandidateState(candidateWide, progress < 0.28 ? "active" : revealA > 0 ? "visited" : "hidden");
  setCandidateState(candidateOffset, progress < 0.28 ? "faint" : progress < 0.62 ? "active" : revealB > 0 ? "visited" : "hidden");
  setCandidateState(candidateNested, progress < 0.62 ? "faint" : progress < 0.94 ? "active" : revealC > 0 ? "visited" : "hidden");

  setOpacity(pressureLeft, 0.14);
  setOpacity(pressureRight, 0.14);
  setOpacity(pressureTop, 0.1);
  setOpacity(pressureBottom, 0.1);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.34, 0, 1);
  const position = mixPoint(points.approach, points.throat, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.78, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 118, progress),
    1,
    0.24 + pulseWave(progress, 2) * 0.08,
    lerp(1, 0.44, compression),
    lerp(1, 1.84, compression),
  );

  setOpacity(entryLane, lerp(0.08, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.06, 0, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, lerp(0.2, 0, progress)));
  [previewBeam, previewLeftLeg, previewRightLeg, previewLowerRail, previewCenterStem].forEach((preview) => setOpacity(preview, lerp(0.08, 0, progress)));

  setTransform(candidateWide, lerp(points.candidateA.x, 738, collapse), lerp(points.candidateA.y, 390, collapse), lerp(0.98, 0.72, collapse), lerp(0.98, 0.72, collapse), -8);
  setTransform(candidateOffset, lerp(points.candidateB.x, 818, collapse), lerp(points.candidateB.y, 352, collapse), lerp(1, 0.74, collapse), lerp(1, 0.74, collapse), -2);
  setTransform(candidateNested, lerp(points.candidateC.x, 902, collapse), lerp(points.candidateC.y, 390, collapse), lerp(1, 0.74, collapse), lerp(1, 0.74, collapse), 4);
  setCandidateState(candidateWide, "visited");
  setCandidateState(candidateOffset, "visited");
  setCandidateState(candidateNested, "visited");
  setOpacity(candidateWide, lerp(0.24, 0.04, collapse));
  setOpacity(candidateOffset, lerp(0.3, 0.06, collapse));
  setOpacity(candidateNested, lerp(0.94, 0.08, collapse));

  setCaliperPose(clamp((progress - 0.04) * 1.5, 0, 1) * 0.12, clamp((progress - 0.04) * 1.55, 0, 0.98));

  setTransform(pressureLeft, lerp(790, 780, easeInOut(collapse)), points.throat.y, 1, 1, 0);
  setTransform(pressureRight, lerp(850, 860, easeInOut(collapse)), points.throat.y, 1, 1, 0);
  setTransform(pressureTop, points.throat.x, lerp(402, 390, easeInOut(collapse)), 1, 1, 0);
  setTransform(pressureBottom, points.throat.x, lerp(502, 514, easeInOut(collapse)), 1, 1, 0);
  setOpacity(pressureLeft, clamp((progress - 0.08) * 1.6, 0, 0.9));
  setOpacity(pressureRight, clamp((progress - 0.08) * 1.6, 0, 0.9));
  setOpacity(pressureTop, clamp((progress - 0.06) * 1.6, 0, 0.78));
  setOpacity(pressureBottom, clamp((progress - 0.06) * 1.6, 0, 0.78));
}

function renderTransformation(progress) {
  const phaseProgress = easeInOut(clamp(progress / 0.92, 0, 1));
  const caliperOpen = phaseProgress;
  const frameProgress = clamp(phaseProgress / 0.76, 0, 1);
  const centerProgress = clamp((phaseProgress - 0.76) / 0.24, 0, 1);

  const position = phaseProgress < 0.76
    ? pointOnTrace(traceFrame, frameProgress, TRACE_FRAME_LENGTH)
    : pointOnTrace(traceCenter, centerProgress, TRACE_CENTER_LENGTH);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2) * 0.08);
  setOpacity(entryLane, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [candidateWide, candidateOffset, candidateNested, searchGuideA, searchGuideB, searchGuideC, previewBeam, previewLeftLeg, previewRightLeg, previewLowerRail, previewCenterStem].forEach((element) =>
    setOpacity(element, 0),
  );

  setCaliperPose(caliperOpen, 0.98);
  setPathWindow(traceFrame, TRACE_FRAME_LENGTH, TRACE_FRAME_LENGTH * frameProgress, 1);
  setPathWindow(traceCenter, TRACE_CENTER_LENGTH, TRACE_CENTER_LENGTH * centerProgress, centerProgress > 0 ? 1 : 0);

  setOpacity(pressureLeft, lerp(0.9, 0.02, progress));
  setOpacity(pressureRight, lerp(0.9, 0.02, progress));
  setOpacity(pressureTop, lerp(0.78, 0.02, progress));
  setOpacity(pressureBottom, lerp(0.78, 0.02, progress));

  setOpacity(slotTopLeft, slotOpacity(phaseProgress, 0.12));
  setOpacity(slotTopRight, slotOpacity(phaseProgress, 0.46));
  setOpacity(slotBottom, slotOpacity(phaseProgress, 0.82));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.45, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.82) * 1.5, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.hold, 16, 92, 1, holdPulse);
  setOpacity(entryLane, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);
  setCaliperPose(1, 0.92);
  setPathWindow(traceFrame, TRACE_FRAME_LENGTH, TRACE_FRAME_LENGTH, lerp(1, 0.16, settle));
  setPathWindow(traceCenter, TRACE_CENTER_LENGTH, TRACE_CENTER_LENGTH, lerp(1, 0.22, settle));

  [
    pressureLeft,
    pressureRight,
    pressureTop,
    pressureBottom,
    candidateWide,
    candidateOffset,
    candidateNested,
    searchGuideA,
    searchGuideB,
    searchGuideC,
    previewBeam,
    previewLeftLeg,
    previewRightLeg,
    previewLowerRail,
    previewCenterStem,
    slotTopLeft,
    slotTopRight,
    slotBottom,
  ].forEach((element) => setOpacity(element, 0));

  setOpacity(resolutionHalo, lerp(0.16, 0.24, settle));
  setOpacity(resolutionFrame, lerp(0.22, 0.64, settle));
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);

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
  applyLayout(info.phase.id);
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
  const rawElapsed = state.playing
    ? state.elapsedBeforePause + (now - state.startAt)
    : state.elapsedBeforePause;

  const elapsed = CAPTURE_MODE ? clamp(rawElapsed, 0, TOTAL_DURATION - 1) : rawElapsed % TOTAL_DURATION;
  if (state.playing) {
    state.currentElapsed = elapsed;
  }

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
  getState() {
    const info = phaseForElapsed(state.currentElapsed);
    return {
      currentElapsed: state.currentElapsed,
      totalDuration: TOTAL_DURATION,
      phase: info.phase.id,
      totalProgress: info.totalProgress,
      localProgress: info.localProgress,
      playing: state.playing,
    };
  },
};

resetScene();
render(0);
window.addEventListener("resize", () => {
  const info = phaseForElapsed(state.currentElapsed);
  applyLayout(info.phase.id);
});
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
