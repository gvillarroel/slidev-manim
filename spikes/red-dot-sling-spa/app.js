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
const candidateFork = document.getElementById("candidate-fork");
const candidateSling = document.getElementById("candidate-sling");
const releaseGuide = document.getElementById("release-guide");
const slingBandTop = document.getElementById("sling-band-top");
const slingBandBottom = document.getElementById("sling-band-bottom");
const anchorTop = document.getElementById("anchor-top");
const anchorBottom = document.getElementById("anchor-bottom");
const pocketBracket = document.getElementById("pocket-bracket");
const forwardSlot = document.getElementById("forward-slot");
const tensionHalo = document.getElementById("tension-halo");
const crestBase = document.getElementById("crest-base");
const crestTrace = document.getElementById("crest-trace");
const spineBase = document.getElementById("spine-base");
const spineTrace = document.getElementById("spine-trace");
const slotTop = document.getElementById("slot-top");
const slotBottom = document.getElementById("slot-bottom");
const slotTail = document.getElementById("slot-tail");
const finTop = document.getElementById("fin-top");
const finBottom = document.getElementById("fin-bottom");
const tailFin = document.getElementById("tail-fin");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const CREST_TRACE_LENGTH = crestTrace.getTotalLength();
const SPINE_TRACE_LENGTH = spineTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 564, y: 450 },
  arcCandidate: { x: 648, y: 356 },
  forkCandidate: { x: 836, y: 334 },
  slingCandidate: { x: 1012, y: 396 },
  laneEntry: { x: 934, y: 450 },
  pocket: { x: 782, y: 450 },
  center: { x: 870, y: 450 },
};

const settlement = {
  top: { x: 872, y: 394 },
  bottom: { x: 872, y: 506 },
  tail: { x: 804, y: 450 },
  topSettle: { x: 858, y: 396 },
  bottomSettle: { x: 858, y: 504 },
  tailSettle: { x: 814, y: 450 },
  anchorTop: { x: 726, y: 392 },
  anchorBottom: { x: 726, y: 508 },
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

function pointOnCrest(progress) {
  const length = clamp(progress, 0, 1) * CREST_TRACE_LENGTH;
  const point = crestTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function finState(progress, threshold) {
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
    search: 32,
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
    appearance: { x: 134, y: 142, width: 1092, height: 636 },
    search: { x: 148, y: 128, width: 1128, height: 652 },
    tension: { x: 438, y: 146, width: 902, height: 622 },
    transformation: { x: 454, y: 136, width: 928, height: 642 },
    resolution: { x: 454, y: 140, width: 922, height: 632 },
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

  setGroupTransform(candidateArc, points.arcCandidate.x, points.arcCandidate.y, 1, -4);
  setGroupTransform(candidateFork, points.forkCandidate.x, points.forkCandidate.y, 1, 0);
  setGroupTransform(candidateSling, points.slingCandidate.x, points.slingCandidate.y, 1, 4);
  [candidateArc, candidateFork, candidateSling].forEach((element) => setOpacity(element, 0));

  setOpacity(releaseGuide, 0);
  setOpacity(slingBandTop, 0);
  setOpacity(slingBandBottom, 0);
  setGroupTransform(anchorTop, settlement.anchorTop.x, settlement.anchorTop.y, 1, 0);
  setGroupTransform(anchorBottom, settlement.anchorBottom.x, settlement.anchorBottom.y, 1, 0);
  setOpacity(anchorTop, 0);
  setOpacity(anchorBottom, 0);
  setOpacity(pocketBracket, 0);
  setOpacity(forwardSlot, 0);
  setOpacity(tensionHalo, 0);

  setOpacity(crestBase, 0);
  setPathWindow(crestTrace, CREST_TRACE_LENGTH, 0, 0);
  setOpacity(spineBase, 0);
  setPathWindow(spineTrace, SPINE_TRACE_LENGTH, 0, 0);

  setGroupTransform(slotTop, settlement.top.x, settlement.top.y, 1, 0);
  setGroupTransform(slotBottom, settlement.bottom.x, settlement.bottom.y, 1, 0);
  setGroupTransform(slotTail, settlement.tail.x, settlement.tail.y, 1, 0);
  [slotTop, slotBottom, slotTail].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(finTop, settlement.top.x, settlement.top.y, 1, 0);
  setGroupTransform(finBottom, settlement.bottom.x, settlement.bottom.y, 1, 0);
  setGroupTransform(tailFin, settlement.tail.x, settlement.tail.y, 1, 0);
  [finTop, finBottom, tailFin].forEach((fin) => setOpacity(fin, 0));

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
  setOpacity(candidateArc, preview * 0.14);
  setOpacity(candidateFork, preview * 0.1);
  setOpacity(candidateSling, preview * 0.08);
  setOpacity(releaseGuide, preview * 0.1);
  setOpacity(anchorTop, preview * 0.05);
  setOpacity(anchorBottom, preview * 0.05);
  setOpacity(pocketBracket, preview * 0.08);
  setOpacity(forwardSlot, preview * 0.08);
  setOpacity(tensionHalo, preview * 0.08);
  setOpacity(crestBase, preview * 0.05);
  setOpacity(spineBase, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.arcCandidate },
    { start: 0.28, end: 0.58, from: points.arcCandidate, to: points.forkCandidate },
    { start: 0.58, end: 0.84, from: points.forkCandidate, to: points.slingCandidate },
    { start: 0.84, end: 1, from: points.slingCandidate, to: points.laneEntry },
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
  setGroupTransform(candidateFork, points.forkCandidate.x, points.forkCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateSling, points.slingCandidate.x, points.slingCandidate.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 4);
  setOpacity(candidateArc, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateFork, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateSling, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(releaseGuide, 0.14);
  setOpacity(anchorTop, 0.06);
  setOpacity(anchorBottom, 0.06);
  setOpacity(pocketBracket, 0.1);
  setOpacity(forwardSlot, 0.1);
  setOpacity(tensionHalo, 0.08);
  setOpacity(crestBase, 0.06);
  setOpacity(spineBase, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.laneEntry, points.pocket, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const anchorShift = lerp(0, 16, easeInOut(clamp(progress / 0.7, 0, 1)));
  const collapse = clamp(progress / 0.74, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.42, compression),
    lerp(1, 1.92, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const arcPosition = mixPoint(points.arcCandidate, { x: 728, y: 378 }, collapse);
  const forkPosition = mixPoint(points.forkCandidate, { x: 838, y: 352 }, collapse);
  const slingPosition = mixPoint(points.slingCandidate, { x: 924, y: 400 }, collapse);
  setGroupTransform(candidateArc, arcPosition.x, arcPosition.y, lerp(0.96, 0.72, collapse), -8);
  setGroupTransform(candidateFork, forkPosition.x, forkPosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateSling, slingPosition.x, slingPosition.y, lerp(0.95, 0.68, collapse), 10);
  setOpacity(candidateArc, lerp(0.3, 0.05, collapse));
  setOpacity(candidateFork, lerp(0.28, 0.05, collapse));
  setOpacity(candidateSling, lerp(1, 0.12, collapse));

  setOpacity(releaseGuide, clamp((progress - 0.04) * 1.7, 0, 0.78));
  setOpacity(slingBandTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(slingBandBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(anchorTop, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(anchorBottom, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(pocketBracket, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(forwardSlot, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(tensionHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(anchorTop, settlement.anchorTop.x - anchorShift, settlement.anchorTop.y, 1, 0);
  setGroupTransform(anchorBottom, settlement.anchorBottom.x - anchorShift, settlement.anchorBottom.y, 1, 0);

  setOpacity(crestBase, clamp((progress - 0.5) * 0.42, 0, 0.14));
  setOpacity(spineBase, clamp((progress - 0.56) * 0.4, 0, 0.14));
  setOpacity(slotTop, clamp((progress - 0.42) * 1.3, 0, 0.24));
  setOpacity(slotBottom, clamp((progress - 0.58) * 1.3, 0, 0.24));
  setOpacity(slotTail, clamp((progress - 0.72) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnCrest(routeProgress);
  const topReveal = finState(routeProgress, 0.2);
  const bottomReveal = finState(routeProgress, 0.58);
  const tailReveal = finState(routeProgress, 0.82);
  const spineProgress = clamp((routeProgress - 0.54) / 0.34, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(crestBase, lerp(0.24, 0.98, routeProgress));
  setPathWindow(crestTrace, CREST_TRACE_LENGTH, CREST_TRACE_LENGTH * routeProgress, 1);
  setOpacity(spineBase, clamp((progress - 0.36) * 1.2, 0, 0.22));
  setPathWindow(spineTrace, SPINE_TRACE_LENGTH, SPINE_TRACE_LENGTH * spineProgress, 0.74 * spineProgress);

  setOpacity(releaseGuide, lerp(0.78, 0.08, progress));
  setOpacity(slingBandTop, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(slingBandBottom, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(anchorTop, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(anchorBottom, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pocketBracket, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(forwardSlot, clamp(0.92 - progress * 1.05, 0, 1));
  setOpacity(tensionHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(anchorTop, settlement.anchorTop.x - lerp(16, 0, progress), settlement.anchorTop.y, 1, 0);
  setGroupTransform(anchorBottom, settlement.anchorBottom.x - lerp(16, 0, progress), settlement.anchorBottom.y, 1, 0);

  setOpacity(candidateArc, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateFork, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateSling, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotTop, slotState(routeProgress, 0.2));
  setOpacity(slotBottom, slotState(routeProgress, 0.58));
  setOpacity(slotTail, slotState(routeProgress, 0.82));

  setGroupTransform(finTop, settlement.top.x, settlement.top.y, lerp(0.88, 1, easeOut(topReveal)), -4);
  setGroupTransform(finBottom, settlement.bottom.x, settlement.bottom.y, lerp(0.88, 1, easeOut(bottomReveal)), 4);
  setGroupTransform(tailFin, settlement.tail.x, settlement.tail.y, lerp(0.88, 1, easeOut(tailReveal)), 0);
  setOpacity(finTop, topReveal);
  setOpacity(finBottom, bottomReveal);
  setOpacity(tailFin, tailReveal);

  setOpacity(anchorGrid, clamp((progress - 0.72) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(crestBase, lerp(0.98, 1, settle));
  setPathWindow(crestTrace, CREST_TRACE_LENGTH, CREST_TRACE_LENGTH, lerp(1, 0.24, settle));
  setOpacity(spineBase, lerp(0.22, 0.3, settle));
  setPathWindow(spineTrace, SPINE_TRACE_LENGTH, SPINE_TRACE_LENGTH, lerp(0.74, 0.32, settle));

  [
    releaseGuide,
    slingBandTop,
    slingBandBottom,
    anchorTop,
    anchorBottom,
    pocketBracket,
    forwardSlot,
    tensionHalo,
    candidateArc,
    candidateFork,
    candidateSling,
    slotTop,
    slotBottom,
    slotTail,
  ].forEach((element) => setOpacity(element, 0));

  setGroupTransform(
    finTop,
    lerp(settlement.top.x, settlement.topSettle.x, settle),
    lerp(settlement.top.y, settlement.topSettle.y, settle),
    0.97,
    -2,
  );
  setGroupTransform(
    finBottom,
    lerp(settlement.bottom.x, settlement.bottomSettle.x, settle),
    lerp(settlement.bottom.y, settlement.bottomSettle.y, settle),
    0.97,
    2,
  );
  setGroupTransform(
    tailFin,
    lerp(settlement.tail.x, settlement.tailSettle.x, settle),
    lerp(settlement.tail.y, settlement.tailSettle.y, settle),
    0.97,
    0,
  );
  setOpacity(finTop, 0.92);
  setOpacity(finBottom, 0.92);
  setOpacity(tailFin, 0.88);

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
