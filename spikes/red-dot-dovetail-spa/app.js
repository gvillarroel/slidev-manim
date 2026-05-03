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
const candidateSlot = document.getElementById("candidate-slot");
const candidateStep = document.getElementById("candidate-step");
const candidateDovetail = document.getElementById("candidate-dovetail");
const joinGuide = document.getElementById("join-guide");
const seamGuide = document.getElementById("seam-guide");
const pressureHalo = document.getElementById("pressure-halo");
const leftJaw = document.getElementById("left-jaw");
const rightJaw = document.getElementById("right-jaw");
const joinShell = document.getElementById("join-shell");
const joinBase = document.getElementById("join-base");
const joinTrace = document.getElementById("join-trace");
const seamBase = document.getElementById("seam-base");
const seamTrace = document.getElementById("seam-trace");
const slotLeft = document.getElementById("slot-left");
const slotRight = document.getElementById("slot-right");
const leftPiece = document.getElementById("left-piece");
const rightPiece = document.getElementById("right-piece");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const JOIN_TRACE_LENGTH = joinTrace.getTotalLength();
const SEAM_TRACE_LENGTH = seamTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 308, y: 450 },
  ingress: { x: 566, y: 450 },
  slotCandidate: { x: 652, y: 392 },
  stepCandidate: { x: 834, y: 342 },
  dovetailCandidate: { x: 1006, y: 390 },
  thresholdApproach: { x: 950, y: 450 },
  threshold: { x: 820, y: 450 },
};

const join = {
  center: { x: 820, y: 450 },
  compressedShift: 6,
  settleShift: 2,
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

function setPieceShift(element, shiftX, scale = 1) {
  setGroupTransform(element, join.center.x + shiftX, join.center.y, scale, 0);
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

function pointOnJoin(progress) {
  const length = clamp(progress, 0, 1) * JOIN_TRACE_LENGTH;
  const point = joinTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function seamLength(progress) {
  return clamp(progress, 0, 1) * SEAM_TRACE_LENGTH;
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.4;
  }
  return clamp(1 - (progress - threshold) / 0.2, 0, 1) * 0.4;
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
    search: 28,
    tension: 10,
    transformation: 6,
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
    appearance: { x: 126, y: 146, width: 1088, height: 636 },
    search: { x: 146, y: 118, width: 1120, height: 668 },
    tension: { x: 314, y: 140, width: 974, height: 636 },
    transformation: { x: 296, y: 118, width: 1010, height: 664 },
    resolution: { x: 346, y: 132, width: 934, height: 642 },
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

  setGroupTransform(candidateSlot, points.slotCandidate.x, points.slotCandidate.y, 1, -4);
  setGroupTransform(candidateStep, points.stepCandidate.x, points.stepCandidate.y, 1, 0);
  setGroupTransform(candidateDovetail, points.dovetailCandidate.x, points.dovetailCandidate.y, 1, 4);
  [candidateSlot, candidateStep, candidateDovetail].forEach((element) => setOpacity(element, 0));

  setOpacity(joinGuide, 0);
  setOpacity(seamGuide, 0);
  setOpacity(pressureHalo, 0);
  setPieceShift(leftJaw, -28, 1);
  setPieceShift(rightJaw, 28, 1);
  setOpacity(leftJaw, 0);
  setOpacity(rightJaw, 0);

  setOpacity(joinShell, 0);
  setOpacity(joinBase, 0);
  setPathWindow(joinTrace, JOIN_TRACE_LENGTH, 0, 0);
  setOpacity(seamBase, 0);
  setPathWindow(seamTrace, SEAM_TRACE_LENGTH, 0, 0);

  setPieceShift(slotLeft, 0, 1);
  setPieceShift(slotRight, 0, 1);
  setOpacity(slotLeft, 0);
  setOpacity(slotRight, 0);

  setPieceShift(leftPiece, 0, 1);
  setPieceShift(rightPiece, 0, 1);
  setOpacity(leftPiece, 0);
  setOpacity(rightPiece, 0);

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
  setOpacity(candidateSlot, preview * 0.14);
  setOpacity(candidateStep, preview * 0.1);
  setOpacity(candidateDovetail, preview * 0.08);
  setOpacity(joinGuide, preview * 0.08);
  setOpacity(seamGuide, preview * 0.08);
  setOpacity(leftJaw, preview * 0.05);
  setOpacity(rightJaw, preview * 0.05);
  setOpacity(joinShell, preview * 0.05);
  setOpacity(joinBase, preview * 0.06);
  setOpacity(seamBase, preview * 0.05);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.slotCandidate },
    { start: 0.28, end: 0.58, from: points.slotCandidate, to: points.stepCandidate },
    { start: 0.58, end: 0.84, from: points.stepCandidate, to: points.dovetailCandidate },
    { start: 0.84, end: 1, from: points.dovetailCandidate, to: points.thresholdApproach },
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

  setGroupTransform(candidateSlot, points.slotCandidate.x, points.slotCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateStep, points.stepCandidate.x, points.stepCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(
    candidateDovetail,
    points.dovetailCandidate.x,
    points.dovetailCandidate.y,
    lerp(0.84, activeC ? 1.05 : 0.95, revealC),
    4,
  );
  setOpacity(candidateSlot, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateStep, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateDovetail, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(joinGuide, 0.14);
  setOpacity(seamGuide, 0.12);
  setOpacity(leftJaw, 0.06);
  setOpacity(rightJaw, 0.06);
  setOpacity(joinShell, 0.05);
  setOpacity(joinBase, 0.08);
  setOpacity(seamBase, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.thresholdApproach, points.threshold, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.76, 0, 1);
  const jawShift = lerp(28, join.compressedShift, easeInOut(clamp(progress / 0.72, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 124, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.44, compression),
    lerp(1, 1.92, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const slotPosition = mixPoint(points.slotCandidate, { x: 716, y: 402 }, collapse);
  const stepPosition = mixPoint(points.stepCandidate, { x: 826, y: 362 }, collapse);
  const dovetailPosition = mixPoint(points.dovetailCandidate, { x: 924, y: 398 }, collapse);
  setGroupTransform(candidateSlot, slotPosition.x, slotPosition.y, lerp(0.96, 0.72, collapse), -6);
  setGroupTransform(candidateStep, stepPosition.x, stepPosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateDovetail, dovetailPosition.x, dovetailPosition.y, lerp(0.95, 0.68, collapse), 6);
  setOpacity(candidateSlot, lerp(0.3, 0.05, collapse));
  setOpacity(candidateStep, lerp(0.28, 0.05, collapse));
  setOpacity(candidateDovetail, lerp(1, 0.12, collapse));

  setOpacity(joinGuide, clamp((progress - 0.04) * 1.7, 0, 0.82));
  setOpacity(seamGuide, clamp((progress - 0.06) * 1.6, 0, 0.84));
  setOpacity(leftJaw, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(rightJaw, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setPieceShift(leftJaw, -jawShift, 0.98);
  setPieceShift(rightJaw, jawShift, 0.98);

  setPieceShift(leftPiece, lerp(-20, -jawShift, collapse), 0.96);
  setPieceShift(rightPiece, lerp(20, jawShift, collapse), 0.96);
  setOpacity(leftPiece, clamp((progress - 0.08) * 1.5, 0, 0.72));
  setOpacity(rightPiece, clamp((progress - 0.08) * 1.5, 0, 0.72));

  setOpacity(joinShell, clamp((progress - 0.48) * 0.42, 0, 0.18));
  setOpacity(joinBase, clamp((progress - 0.54) * 0.4, 0, 0.18));
  setOpacity(seamBase, clamp((progress - 0.58) * 0.42, 0, 0.16));
  setOpacity(slotLeft, clamp((progress - 0.42) * 1.3, 0, 0.24));
  setOpacity(slotRight, clamp((progress - 0.62) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnJoin(routeProgress);
  const leftReveal = clamp((routeProgress - 0.18) / 0.22, 0, 1);
  const rightReveal = clamp((routeProgress - 0.56) / 0.22, 0, 1);
  const seamReveal = clamp((routeProgress - 0.72) / 0.18, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(joinShell, lerp(0.24, 0.98, routeProgress));
  setOpacity(joinBase, lerp(0.14, 0.3, routeProgress));
  setPathWindow(joinTrace, JOIN_TRACE_LENGTH, JOIN_TRACE_LENGTH * routeProgress, 1);
  setOpacity(seamBase, clamp((progress - 0.34) * 1.2, 0, 0.24));
  setPathWindow(seamTrace, SEAM_TRACE_LENGTH, seamLength(seamReveal), 0.72 * seamReveal);

  setOpacity(joinGuide, lerp(0.82, 0.08, progress));
  setOpacity(seamGuide, lerp(0.84, 0.08, progress));
  setOpacity(leftJaw, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(rightJaw, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));

  setOpacity(candidateSlot, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateStep, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateDovetail, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotLeft, slotState(routeProgress, 0.22));
  setOpacity(slotRight, slotState(routeProgress, 0.64));

  setPieceShift(leftPiece, lerp(-join.compressedShift, 0, easeOut(leftReveal)), lerp(0.95, 1, easeOut(leftReveal)));
  setPieceShift(rightPiece, lerp(join.compressedShift, 0, easeOut(rightReveal)), lerp(0.95, 1, easeOut(rightReveal)));
  setOpacity(leftPiece, lerp(0.72, 1, leftReveal));
  setOpacity(rightPiece, lerp(0.72, 1, rightReveal));

  setOpacity(anchorGrid, clamp((progress - 0.72) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(join.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  setOpacity(joinShell, lerp(0.98, 0.92, settle));
  setOpacity(joinBase, lerp(0.3, 0.26, settle));
  setPathWindow(joinTrace, JOIN_TRACE_LENGTH, JOIN_TRACE_LENGTH, lerp(1, 0.14, settle));
  setOpacity(seamBase, lerp(0.24, 0.28, settle));
  setPathWindow(seamTrace, SEAM_TRACE_LENGTH, SEAM_TRACE_LENGTH, lerp(0.72, 0.22, settle));

  [
    joinGuide,
    seamGuide,
    pressureHalo,
    candidateSlot,
    candidateStep,
    candidateDovetail,
    slotLeft,
    slotRight,
  ].forEach((element) => setOpacity(element, 0));
  setOpacity(leftJaw, 0);
  setOpacity(rightJaw, 0);

  setPieceShift(leftPiece, lerp(0, -join.settleShift, settle), 0.98);
  setPieceShift(rightPiece, lerp(0, join.settleShift, settle), 0.98);
  setOpacity(leftPiece, 0.92);
  setOpacity(rightPiece, 0.92);

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
