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
const candidateDiagonal = document.getElementById("candidate-diagonal");
const candidateGate = document.getElementById("candidate-gate");
const candidateFan = document.getElementById("candidate-fan");
const pinchSpine = document.getElementById("pinch-spine");
const pinchPlaneLeft = document.getElementById("pinch-plane-left");
const pinchPlaneRight = document.getElementById("pinch-plane-right");
const pinchHalo = document.getElementById("pinch-halo");
const foldBase = document.getElementById("fold-base");
const foldActive = document.getElementById("fold-active");
const slotTop = document.getElementById("slot-top");
const slotRight = document.getElementById("slot-right");
const slotBottom = document.getElementById("slot-bottom");
const slotLeft = document.getElementById("slot-left");
const facetTop = document.getElementById("facet-top");
const facetRight = document.getElementById("facet-right");
const facetBottom = document.getElementById("facet-bottom");
const facetLeft = document.getElementById("facet-left");
const memoryArc = document.getElementById("memory-arc");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const FOLD_LENGTH = foldActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 560, y: 450 },
  diagonal: { x: 646, y: 346 },
  gateCandidate: { x: 838, y: 308 },
  fan: { x: 1000, y: 418 },
  gate: { x: 820, y: 450 },
};

const system = {
  top: { x: 820, y: 308 },
  right: { x: 964, y: 450 },
  bottom: { x: 820, y: 592 },
  left: { x: 676, y: 450 },
  settleTop: { x: 820, y: 324 },
  settleRight: { x: 938, y: 450 },
  settleBottom: { x: 820, y: 576 },
  settleLeft: { x: 702, y: 450 },
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

function pointOnFold(progress) {
  const length = clamp(progress, 0, 1) * FOLD_LENGTH;
  const point = foldActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.42;
}

function facetState(progress, threshold) {
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
    appearance: 18,
    search: 52,
    tension: 14,
    transformation: 10,
    resolution: -6,
  };
  const offsetY = offsets[phaseId] ?? -6;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 126, y: 144, width: 1088, height: 630 },
    search: { x: 158, y: 140, width: 1096, height: 630 },
    tension: { x: 334, y: 154, width: 960, height: 612 },
    transformation: { x: 404, y: 162, width: 832, height: 594 },
    resolution: { x: 430, y: 170, width: 780, height: 570 },
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

  setGroupTransform(candidateDiagonal, points.diagonal.x, points.diagonal.y, 1, 0);
  setGroupTransform(candidateGate, points.gateCandidate.x, points.gateCandidate.y, 1, 0);
  setGroupTransform(candidateFan, points.fan.x, points.fan.y, 1, 0);
  [candidateDiagonal, candidateGate, candidateFan].forEach((element) => setOpacity(element, 0));

  setOpacity(pinchSpine, 0);
  setOpacity(pinchHalo, 0);
  setGroupTransform(pinchPlaneLeft, points.gate.x - 92, points.gate.y, 1, 0);
  setGroupTransform(pinchPlaneRight, points.gate.x + 92, points.gate.y, 1, 0);
  setOpacity(pinchPlaneLeft, 0);
  setOpacity(pinchPlaneRight, 0);

  setOpacity(foldBase, 0);
  setPathWindow(foldActive, FOLD_LENGTH, 0, 0);

  [slotTop, slotRight, slotBottom, slotLeft].forEach((slot) => setOpacity(slot, 0));
  setGroupTransform(slotTop, system.top.x, system.top.y, 1, 0);
  setGroupTransform(slotRight, system.right.x, system.right.y, 1, 0);
  setGroupTransform(slotBottom, system.bottom.x, system.bottom.y, 1, 0);
  setGroupTransform(slotLeft, system.left.x, system.left.y, 1, 0);

  [facetTop, facetRight, facetBottom, facetLeft].forEach((facet) => setOpacity(facet, 0));
  setGroupTransform(facetTop, system.top.x, system.top.y, 1, 0);
  setGroupTransform(facetRight, system.right.x, system.right.y, 1, 0);
  setGroupTransform(facetBottom, system.bottom.x, system.bottom.y, 1, 0);
  setGroupTransform(facetLeft, system.left.x, system.left.y, 1, 0);

  setOpacity(memoryArc, 0);
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
  setOpacity(candidateDiagonal, preview * 0.14);
  setOpacity(candidateGate, preview * 0.1);
  setOpacity(candidateFan, preview * 0.08);
  setOpacity(pinchSpine, preview * 0.12);
  setOpacity(pinchPlaneLeft, preview * 0.08);
  setOpacity(pinchPlaneRight, preview * 0.08);
  setOpacity(pinchHalo, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.diagonal },
    { start: 0.28, end: 0.58, from: points.diagonal, to: points.gateCandidate },
    { start: 0.58, end: 0.84, from: points.gateCandidate, to: points.fan },
    { start: 0.84, end: 1, from: points.fan, to: { x: 924, y: 448 } },
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

  setGroupTransform(candidateDiagonal, points.diagonal.x, points.diagonal.y, lerp(0.88, activeA ? 1.05 : 0.96, revealA), -4);
  setGroupTransform(candidateGate, points.gateCandidate.x, points.gateCandidate.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateFan, points.fan.x, points.fan.y, lerp(0.84, activeC ? 1.04 : 0.95, revealC), 6);
  setOpacity(candidateDiagonal, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateGate, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateFan, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(pinchSpine, 0.12);
  setOpacity(pinchPlaneLeft, 0.08);
  setOpacity(pinchPlaneRight, 0.08);
  setOpacity(pinchHalo, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.fan, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const planeGap = lerp(92, 34, easeInOut(clamp(progress / 0.7, 0, 1)));
  const collapse = clamp(progress / 0.74, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(86, 114, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.6, compression),
    lerp(1, 1.66, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const diagonalPosition = mixPoint(points.diagonal, { x: 744, y: 402 }, collapse);
  const gatePosition = mixPoint(points.gateCandidate, { x: 820, y: 360 }, collapse);
  const fanPosition = mixPoint(points.fan, { x: 900, y: 420 }, collapse);
  setGroupTransform(candidateDiagonal, diagonalPosition.x, diagonalPosition.y, lerp(0.96, 0.72, collapse), -10);
  setGroupTransform(candidateGate, gatePosition.x, gatePosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateFan, fanPosition.x, fanPosition.y, lerp(0.95, 0.68, collapse), 10);
  setOpacity(candidateDiagonal, lerp(0.3, 0.06, collapse));
  setOpacity(candidateGate, lerp(0.28, 0.05, collapse));
  setOpacity(candidateFan, lerp(1, 0.12, collapse));

  setOpacity(pinchSpine, clamp((progress - 0.04) * 1.7, 0, 0.74));
  setOpacity(pinchPlaneLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(pinchPlaneRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(pinchHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(pinchPlaneLeft, points.gate.x - planeGap, points.gate.y, 1, 0);
  setGroupTransform(pinchPlaneRight, points.gate.x + planeGap, points.gate.y, 1, 0);

  setOpacity(slotTop, clamp((progress - 0.42) * 1.3, 0, 0.26));
  setOpacity(slotRight, clamp((progress - 0.52) * 1.3, 0, 0.26));
  setOpacity(slotBottom, clamp((progress - 0.62) * 1.3, 0, 0.26));
  setOpacity(slotLeft, clamp((progress - 0.72) * 1.3, 0, 0.26));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnFold(routeProgress);
  const topReveal = facetState(routeProgress, 0.18);
  const rightReveal = facetState(routeProgress, 0.4);
  const bottomReveal = facetState(routeProgress, 0.62);
  const leftReveal = facetState(routeProgress, 0.82);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(foldBase, lerp(0.08, 0.28, routeProgress));
  setPathWindow(foldActive, FOLD_LENGTH, FOLD_LENGTH * routeProgress, 1);

  setOpacity(pinchSpine, lerp(0.74, 0.08, progress));
  setOpacity(pinchPlaneLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pinchPlaneRight, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pinchHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(pinchPlaneLeft, points.gate.x - lerp(34, 56, progress), points.gate.y, 1, 0);
  setGroupTransform(pinchPlaneRight, points.gate.x + lerp(34, 56, progress), points.gate.y, 1, 0);

  setOpacity(candidateDiagonal, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateGate, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateFan, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotTop, slotState(routeProgress, 0.18));
  setOpacity(slotRight, slotState(routeProgress, 0.4));
  setOpacity(slotBottom, slotState(routeProgress, 0.62));
  setOpacity(slotLeft, slotState(routeProgress, 0.82));

  setGroupTransform(facetTop, system.top.x, system.top.y, lerp(0.88, 1, easeOut(topReveal)), 0);
  setGroupTransform(facetRight, system.right.x, system.right.y, lerp(0.88, 1, easeOut(rightReveal)), 0);
  setGroupTransform(facetBottom, system.bottom.x, system.bottom.y, lerp(0.88, 1, easeOut(bottomReveal)), 0);
  setGroupTransform(facetLeft, system.left.x, system.left.y, lerp(0.88, 1, easeOut(leftReveal)), 0);
  setOpacity(facetTop, topReveal);
  setOpacity(facetRight, rightReveal);
  setOpacity(facetBottom, bottomReveal);
  setOpacity(facetLeft, leftReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.62) * 1.4, 0, 0.2));
  setOpacity(resolutionRing, clamp((progress - 0.72) * 1.5, 0, 0.24));
  setOpacity(memoryArc, clamp((progress - 0.78) * 1.5, 0, 0.12));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(foldBase, lerp(0.28, 0.46, settle));
  setPathWindow(foldActive, FOLD_LENGTH, FOLD_LENGTH, lerp(1, 0.22, settle));

  [pinchSpine, pinchPlaneLeft, pinchPlaneRight, pinchHalo, candidateDiagonal, candidateGate, candidateFan, slotTop, slotRight, slotBottom, slotLeft].forEach(
    (element) => setOpacity(element, 0),
  );

  setGroupTransform(
    facetTop,
    lerp(system.top.x, system.settleTop.x, settle),
    lerp(system.top.y, system.settleTop.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    facetRight,
    lerp(system.right.x, system.settleRight.x, settle),
    lerp(system.right.y, system.settleRight.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    facetBottom,
    lerp(system.bottom.x, system.settleBottom.x, settle),
    lerp(system.bottom.y, system.settleBottom.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    facetLeft,
    lerp(system.left.x, system.settleLeft.x, settle),
    lerp(system.left.y, system.settleLeft.y, settle),
    0.97,
    0,
  );
  setOpacity(facetTop, 0.92);
  setOpacity(facetRight, 0.92);
  setOpacity(facetBottom, 0.92);
  setOpacity(facetLeft, 0.92);

  setOpacity(resolutionHalo, lerp(0.2, 0.32, settle));
  setOpacity(resolutionRing, lerp(0.24, 0.88, settle));
  setOpacity(memoryArc, lerp(0.12, 0.36, settle));
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
