const TOTAL_DURATION = 36_800;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 9_800 },
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
const stemPreview = document.getElementById("stem-preview");
const yokePreview = document.getElementById("yoke-preview");
const prongPreviewLeft = document.getElementById("prong-preview-left");
const prongPreviewRight = document.getElementById("prong-preview-right");
const candidateLean = document.getElementById("candidate-lean");
const candidateNarrow = document.getElementById("candidate-narrow");
const candidateOpen = document.getElementById("candidate-open");
const pressureHalo = document.getElementById("pressure-halo");
const pressureLeft = document.getElementById("pressure-left");
const pressureRight = document.getElementById("pressure-right");
const forkLeft = document.getElementById("fork-left");
const forkRight = document.getElementById("fork-right");
const forkYoke = document.getElementById("fork-yoke");
const forkStem = document.getElementById("fork-stem");
const forkTraceU = document.getElementById("fork-trace-u");
const forkTraceStem = document.getElementById("fork-trace-stem");
const slotLeft = document.getElementById("slot-left");
const slotRight = document.getElementById("slot-right");
const slotBottom = document.getElementById("slot-bottom");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ROUTE_LENGTH = activeTrail.getTotalLength();
const TRACE_U_LENGTH = forkTraceU.getTotalLength();
const TRACE_STEM_LENGTH = forkTraceStem.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 320, y: 456 },
  ingress: { x: 562, y: 454 },
  candidateA: { x: 648, y: 370 },
  candidateB: { x: 834, y: 332 },
  candidateC: { x: 1010, y: 372 },
  approach: { x: 924, y: 426 },
  throat: { x: 820, y: 422 },
  hold: { x: 820, y: 422 },
};

const anchors = {
  left: { x: 792, y: 444 },
  right: { x: 848, y: 444 },
  yoke: { x: 820, y: 444 },
  stem: { x: 820, y: 556 },
};

const compressedAnchors = {
  left: { x: 806, y: 444 },
  right: { x: 834, y: 444 },
};

const slots = {
  left: { x: 792, y: 280 },
  right: { x: 848, y: 280 },
  bottom: { x: 820, y: 676 },
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

function setTransform(element, x, y, scaleX = 1, scaleY = scaleX, rotate = 0) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)})`,
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

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.34;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.34;
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
    tension: 10,
    transformation: 4,
    resolution: 0,
  };
  sceneRoot.setAttribute("transform", `translate(0 ${(offsets[phaseId] ?? 0).toFixed(2)})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 126, y: 154, width: 1098, height: 640 },
    search: { x: 150, y: 138, width: 1116, height: 652 },
    tension: { x: 346, y: 166, width: 938, height: 620 },
    transformation: { x: 356, y: 140, width: 924, height: 664 },
    resolution: { x: 388, y: 124, width: 878, height: 676 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -10) translate(800 450) scale(1.035) translate(-800 -450)",
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

function setForkPose(progress, opacity) {
  const leftX = lerp(compressedAnchors.left.x, anchors.left.x, progress);
  const rightX = lerp(compressedAnchors.right.x, anchors.right.x, progress);
  const leftAngle = lerp(-7, 0, progress);
  const rightAngle = lerp(7, 0, progress);
  const prongScaleY = lerp(0.88, 1, progress);
  const yokeScaleX = lerp(0.56, 1, progress);
  const yokeScaleY = lerp(0.9, 1, progress);
  const stemScaleY = lerp(0.9, 1, progress);

  setTransform(forkLeft, leftX, anchors.left.y, 1, prongScaleY, leftAngle);
  setTransform(forkRight, rightX, anchors.right.y, 1, prongScaleY, rightAngle);
  setTransform(forkYoke, anchors.yoke.x, anchors.yoke.y, yokeScaleX, yokeScaleY, 0);
  setTransform(forkStem, anchors.stem.x, anchors.stem.y, 1, stemScaleY, 0);
  [forkLeft, forkRight, forkYoke, forkStem].forEach((element) => setOpacity(element, opacity));
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(entryLane, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC, stemPreview, yokePreview, prongPreviewLeft, prongPreviewRight].forEach((element) =>
    setOpacity(element, 0),
  );

  setTransform(candidateLean, points.candidateA.x, points.candidateA.y, 1, 1, -7);
  setTransform(candidateNarrow, points.candidateB.x, points.candidateB.y, 1, 1, 0);
  setTransform(candidateOpen, points.candidateC.x, points.candidateC.y, 1, 1, 7);
  [candidateLean, candidateNarrow, candidateOpen].forEach((element) => setOpacity(element, 0));

  setTransform(pressureLeft, 786, points.throat.y, 1, 1, 0);
  setTransform(pressureRight, 854, points.throat.y, 1, 1, 0);
  setOpacity(pressureHalo, 0);
  setOpacity(pressureLeft, 0);
  setOpacity(pressureRight, 0);

  setForkPose(1, 0);
  setPathWindow(forkTraceU, TRACE_U_LENGTH, 0, 0);
  setPathWindow(forkTraceStem, TRACE_STEM_LENGTH, 0, 0);

  setTransform(slotLeft, slots.left.x, slots.left.y);
  setTransform(slotRight, slots.right.x, slots.right.y);
  setTransform(slotBottom, slots.bottom.x, slots.bottom.y);
  setOpacity(slotLeft, 0);
  setOpacity(slotRight, 0);
  setOpacity(slotBottom, 0);

  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);
  const preview = clamp((progress - 0.28) * 1.6, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.16,
  );

  setOpacity(entryLane, clamp((progress - 0.08) * 1.5, 0, 0.3));
  setOpacity(stemPreview, preview * 0.24);
  setOpacity(yokePreview, preview * 0.18);
  setOpacity(prongPreviewLeft, preview * 0.2);
  setOpacity(prongPreviewRight, preview * 0.2);
  setOpacity(candidateLean, preview * 0.12);
  setOpacity(candidateNarrow, preview * 0.1);
  setOpacity(candidateOpen, preview * 0.08);
  setOpacity(searchGuideA, preview * 0.12);
  setOpacity(searchGuideB, preview * 0.08);
  setOpacity(searchGuideC, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.candidateA },
    { start: 0.28, end: 0.58, from: points.candidateA, to: points.candidateB },
    { start: 0.58, end: 0.84, from: points.candidateB, to: points.candidateC },
    { start: 0.84, end: 1, from: points.candidateC, to: points.approach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(entryLane, lerp(0.24, 0.08, progress));
  setPathWindow(activeTrail, ROUTE_LENGTH, ROUTE_LENGTH * lerp(0.28, 1, progress), lerp(0.16, 0.05, progress));
  setOpacity(stemPreview, lerp(0.22, 0.08, progress));
  setOpacity(yokePreview, lerp(0.18, 0.08, progress));
  setOpacity(prongPreviewLeft, lerp(0.18, 0.06, progress));
  setOpacity(prongPreviewRight, lerp(0.18, 0.06, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  setOpacity(searchGuideA, 0.18 + revealA * 0.18);
  setOpacity(searchGuideB, 0.1 + revealB * 0.2);
  setOpacity(searchGuideC, 0.08 + revealC * 0.22);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setTransform(candidateLean, points.candidateA.x, points.candidateA.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), lerp(0.9, activeA ? 1.06 : 0.97, revealA), -7);
  setTransform(candidateNarrow, points.candidateB.x, points.candidateB.y, lerp(0.9, activeB ? 1.05 : 0.97, revealB), lerp(0.9, activeB ? 1.05 : 0.97, revealB), 0);
  setTransform(candidateOpen, points.candidateC.x, points.candidateC.y, lerp(0.88, activeC ? 1.05 : 0.97, revealC), lerp(0.88, activeC ? 1.05 : 0.97, revealC), 7);
  setOpacity(candidateLean, activeA ? 0.98 : revealA * 0.28 + 0.16);
  setOpacity(candidateNarrow, activeB ? 0.98 : revealB * 0.28 + 0.16);
  setOpacity(candidateOpen, activeC ? 1 : revealC * 0.28 + 0.14);

  setOpacity(pressureHalo, 0.04);
  setOpacity(pressureLeft, 0.06);
  setOpacity(pressureRight, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.36, 0, 1);
  const position = mixPoint(points.approach, points.throat, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.78, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 118, progress),
    1,
    0.24 + pulseWave(progress, 2.1) * 0.08,
    lerp(1, 0.46, compression),
    lerp(1, 1.84, compression),
  );

  setOpacity(entryLane, lerp(0.08, 0.02, progress));
  setPathWindow(activeTrail, ROUTE_LENGTH, ROUTE_LENGTH, lerp(0.06, 0, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, lerp(0.18, 0, progress)));
  [stemPreview, yokePreview, prongPreviewLeft, prongPreviewRight].forEach((preview) => setOpacity(preview, lerp(0.08, 0, progress)));

  setTransform(candidateLean, lerp(points.candidateA.x, 724, collapse), lerp(points.candidateA.y, 388, collapse), lerp(0.98, 0.74, collapse), lerp(0.98, 0.74, collapse), -10);
  setTransform(candidateNarrow, lerp(points.candidateB.x, 818, collapse), lerp(points.candidateB.y, 358, collapse), lerp(1, 0.76, collapse), lerp(1, 0.76, collapse), -2);
  setTransform(candidateOpen, lerp(points.candidateC.x, 908, collapse), lerp(points.candidateC.y, 390, collapse), lerp(1, 0.76, collapse), lerp(1, 0.76, collapse), 4);
  setOpacity(candidateLean, lerp(0.24, 0.04, collapse));
  setOpacity(candidateNarrow, lerp(0.28, 0.06, collapse));
  setOpacity(candidateOpen, lerp(0.96, 0.08, collapse));

  setForkPose(clamp((progress - 0.04) * 1.5, 0, 1) * 0.12, clamp((progress - 0.04) * 1.55, 0, 0.98));
  setTransform(pressureLeft, lerp(792, 780, easeInOut(collapse)), points.throat.y, 1, 1, 0);
  setTransform(pressureRight, lerp(848, 860, easeInOut(collapse)), points.throat.y, 1, 1, 0);
  setOpacity(pressureHalo, clamp((progress - 0.06) * 1.6, 0, 0.42));
  setOpacity(pressureLeft, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureRight, clamp((progress - 0.08) * 1.6, 0, 0.92));
}

function renderTransformation(progress) {
  const phaseProgress = easeInOut(clamp(progress / 0.92, 0, 1));
  const forkOpen = phaseProgress;
  const uProgress = clamp(phaseProgress / 0.74, 0, 1);
  const stemProgress = clamp((phaseProgress - 0.74) / 0.26, 0, 1);

  const position = phaseProgress < 0.74
    ? pointOnTrace(forkTraceU, uProgress, TRACE_U_LENGTH)
    : pointOnTrace(forkTraceStem, stemProgress, TRACE_STEM_LENGTH);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2) * 0.08);
  setOpacity(entryLane, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);

  [candidateLean, candidateNarrow, candidateOpen, searchGuideA, searchGuideB, searchGuideC, stemPreview, yokePreview, prongPreviewLeft, prongPreviewRight].forEach((element) =>
    setOpacity(element, 0),
  );

  setForkPose(forkOpen, 0.98);
  setPathWindow(forkTraceU, TRACE_U_LENGTH, TRACE_U_LENGTH * uProgress, 1);
  setPathWindow(forkTraceStem, TRACE_STEM_LENGTH, TRACE_STEM_LENGTH * stemProgress, stemProgress > 0 ? 1 : 0);

  setOpacity(pressureHalo, lerp(0.42, 0.04, progress));
  setOpacity(pressureLeft, clamp(0.92 - progress * 1.2, 0, 1));
  setOpacity(pressureRight, clamp(0.92 - progress * 1.2, 0, 1));

  setOpacity(slotLeft, slotState(phaseProgress, 0.12));
  setOpacity(slotRight, slotState(phaseProgress, 0.44));
  setOpacity(slotBottom, slotState(phaseProgress, 0.82));
  setOpacity(resolutionHalo, clamp((progress - 0.66) * 1.45, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.55, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.hold, 16, 94, 1, holdPulse);
  setOpacity(entryLane, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);
  setForkPose(1, 0.92);
  setPathWindow(forkTraceU, TRACE_U_LENGTH, TRACE_U_LENGTH, lerp(1, 0.18, settle));
  setPathWindow(forkTraceStem, TRACE_STEM_LENGTH, TRACE_STEM_LENGTH, lerp(1, 0.22, settle));

  [
    pressureHalo,
    pressureLeft,
    pressureRight,
    candidateLean,
    candidateNarrow,
    candidateOpen,
    searchGuideA,
    searchGuideB,
    searchGuideC,
    stemPreview,
    yokePreview,
    prongPreviewLeft,
    prongPreviewRight,
    slotLeft,
    slotRight,
    slotBottom,
  ].forEach((element) => setOpacity(element, 0));

  setOpacity(resolutionHalo, lerp(0.16, 0.24, settle));
  setOpacity(resolutionFrame, lerp(0.22, 0.64, settle));
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
