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
const mastPreview = document.getElementById("mast-preview");
const hubPreview = document.getElementById("hub-preview");
const candidateLean = document.getElementById("candidate-lean");
const candidateSplit = document.getElementById("candidate-split");
const candidateOpen = document.getElementById("candidate-open");
const pressureHalo = document.getElementById("pressure-halo");
const pressureLeft = document.getElementById("pressure-left");
const pressureRight = document.getElementById("pressure-right");
const signalLeft = document.getElementById("signal-left");
const signalRight = document.getElementById("signal-right");
const signalMast = document.getElementById("signal-mast");
const hubRing = document.getElementById("hub-ring");
const semaphoreTrace = document.getElementById("semaphore-trace");
const slotLeft = document.getElementById("slot-left");
const slotRight = document.getElementById("slot-right");
const slotBottom = document.getElementById("slot-bottom");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ROUTE_LENGTH = activeTrail.getTotalLength();
const TRACE_LENGTH = semaphoreTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 304, y: 452 },
  ingress: { x: 548, y: 452 },
  candidateA: { x: 642, y: 390 },
  candidateB: { x: 826, y: 344 },
  candidateC: { x: 1004, y: 394 },
  approach: { x: 930, y: 452 },
  hub: { x: 820, y: 450 },
};

const endpoints = {
  left: { x: 708, y: 368 },
  right: { x: 932, y: 368 },
  bottom: { x: 820, y: 574 },
};

const bundle = {
  left: { x: 760, y: 450 },
  right: { x: 880, y: 450 },
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
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 200).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function pointOnTrace(progress) {
  const length = clamp(progress, 0, 1) * TRACE_LENGTH;
  const point = semaphoreTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
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
    search: 26,
    tension: 8,
    transformation: 2,
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
    appearance: { x: 130, y: 150, width: 1080, height: 632 },
    search: { x: 150, y: 132, width: 1120, height: 654 },
    tension: { x: 354, y: 162, width: 940, height: 624 },
    transformation: { x: 352, y: 146, width: 948, height: 648 },
    resolution: { x: 394, y: 142, width: 876, height: 638 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -14) translate(800 450) scale(1.035) translate(-800 -450)",
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
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC, mastPreview, hubPreview].forEach((element) => setOpacity(element, 0));

  setTransform(candidateLean, points.candidateA.x, points.candidateA.y, 1, 1, -8);
  setTransform(candidateSplit, points.candidateB.x, points.candidateB.y, 1, 1, 0);
  setTransform(candidateOpen, points.candidateC.x, points.candidateC.y, 1, 1, 8);
  [candidateLean, candidateSplit, candidateOpen].forEach((element) => setOpacity(element, 0));

  setOpacity(pressureHalo, 0);
  setTransform(pressureLeft, bundle.left.x, bundle.left.y);
  setTransform(pressureRight, bundle.right.x, bundle.right.y);
  setOpacity(pressureLeft, 0);
  setOpacity(pressureRight, 0);

  setTransform(signalLeft, points.hub.x, points.hub.y, 1, 1, 0);
  setTransform(signalRight, points.hub.x, points.hub.y, 1, 1, 0);
  setTransform(signalMast, points.hub.x, points.hub.y, 1, 1, 0);
  setOpacity(signalLeft, 0);
  setOpacity(signalRight, 0);
  setOpacity(signalMast, 0);
  setOpacity(hubRing, 0);
  setPathWindow(semaphoreTrace, TRACE_LENGTH, 0, 0);

  setTransform(slotLeft, endpoints.left.x, endpoints.left.y);
  setTransform(slotRight, endpoints.right.x, endpoints.right.y);
  setTransform(slotBottom, endpoints.bottom.x, endpoints.bottom.y);
  setOpacity(slotLeft, 0);
  setOpacity(slotRight, 0);
  setOpacity(slotBottom, 0);

  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);
  const preview = clamp((progress - 0.32) * 1.6, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.4, 0, 0.34));
  setOpacity(mastPreview, preview * 0.22);
  setOpacity(hubPreview, preview * 0.18);
  setOpacity(signalMast, preview * 0.08);
  setOpacity(hubRing, preview * 0.06);
  setOpacity(slotLeft, preview * 0.04);
  setOpacity(slotRight, preview * 0.04);
  setOpacity(slotBottom, preview * 0.04);
  setOpacity(candidateLean, preview * 0.14);
  setOpacity(candidateSplit, preview * 0.12);
  setOpacity(candidateOpen, preview * 0.1);
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
  setOpacity(narrativeSpine, lerp(0.22, 0.08, progress));
  setPathWindow(activeTrail, ROUTE_LENGTH, ROUTE_LENGTH * lerp(0.26, 1, progress), lerp(0.16, 0.05, progress));
  setOpacity(mastPreview, lerp(0.2, 0.08, progress));
  setOpacity(hubPreview, lerp(0.16, 0.08, progress));
  setOpacity(signalMast, 0.05);
  setOpacity(hubRing, 0.04);

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  setOpacity(searchGuideA, 0.18 + revealA * 0.18);
  setOpacity(searchGuideB, 0.1 + revealB * 0.2);
  setOpacity(searchGuideC, 0.08 + revealC * 0.22);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setTransform(candidateLean, points.candidateA.x, points.candidateA.y, lerp(0.88, activeA ? 1.06 : 0.96, revealA), lerp(0.88, activeA ? 1.06 : 0.96, revealA), -8);
  setTransform(candidateSplit, points.candidateB.x, points.candidateB.y, lerp(0.9, activeB ? 1.05 : 0.96, revealB), lerp(0.9, activeB ? 1.05 : 0.96, revealB), 0);
  setTransform(candidateOpen, points.candidateC.x, points.candidateC.y, lerp(0.88, activeC ? 1.05 : 0.96, revealC), lerp(0.88, activeC ? 1.05 : 0.96, revealC), 8);
  setOpacity(candidateLean, activeA ? 0.98 : revealA * 0.3 + 0.14);
  setOpacity(candidateSplit, activeB ? 0.98 : revealB * 0.3 + 0.14);
  setOpacity(candidateOpen, activeC ? 1 : revealC * 0.32 + 0.12);

  setOpacity(pressureHalo, 0.06);
  setOpacity(pressureLeft, 0.08);
  setOpacity(pressureRight, 0.08);
  setOpacity(slotLeft, 0.06);
  setOpacity(slotRight, 0.06);
  setOpacity(slotBottom, 0.05);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.4, 0, 1);
  const position = mixPoint(points.approach, points.hub, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.72, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 120, progress),
    1,
    0.24 + pulseWave(progress, 2.1) * 0.1,
    lerp(1, 0.48, compression),
    lerp(1, 1.88, compression),
  );
  setOpacity(narrativeSpine, lerp(0.1, 0.02, progress));
  setPathWindow(activeTrail, ROUTE_LENGTH, ROUTE_LENGTH, lerp(0.08, 0, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, lerp(0.18, 0, progress)));
  setOpacity(mastPreview, lerp(0.08, 0.04, progress));
  setOpacity(hubPreview, lerp(0.08, 0, progress));

  const openDrift = mixPoint(points.candidateC, { x: 916, y: 404 }, collapse);
  setTransform(candidateLean, lerp(points.candidateA.x, 716, collapse), lerp(points.candidateA.y, 402, collapse), lerp(0.96, 0.72, collapse), lerp(0.96, 0.72, collapse), -12);
  setTransform(candidateSplit, lerp(points.candidateB.x, 814, collapse), lerp(points.candidateB.y, 382, collapse), lerp(0.96, 0.72, collapse), lerp(0.96, 0.72, collapse), -4);
  setTransform(candidateOpen, openDrift.x, openDrift.y, lerp(1, 0.72, collapse), lerp(1, 0.72, collapse), 2);
  setOpacity(candidateLean, lerp(0.22, 0.04, collapse));
  setOpacity(candidateSplit, lerp(0.28, 0.06, collapse));
  setOpacity(candidateOpen, lerp(0.98, 0.1, collapse));

  const leftRotation = lerp(16, 46, easeInOut(clamp(progress / 0.76, 0, 1)));
  const rightRotation = lerp(-16, -46, easeInOut(clamp(progress / 0.76, 0, 1)));
  const armScale = lerp(0.9, 0.78, easeInOut(clamp(progress / 0.76, 0, 1)));
  const mastScaleY = lerp(0.74, 0.94, easeInOut(clamp(progress / 0.68, 0, 1)));

  setTransform(signalLeft, points.hub.x, points.hub.y, armScale, armScale, leftRotation);
  setTransform(signalRight, points.hub.x, points.hub.y, armScale, armScale, rightRotation);
  setTransform(signalMast, points.hub.x, points.hub.y, 1, mastScaleY, 0);
  setOpacity(signalLeft, clamp((progress - 0.02) * 1.8, 0, 0.98));
  setOpacity(signalRight, clamp((progress - 0.02) * 1.8, 0, 0.98));
  setOpacity(signalMast, clamp((progress - 0.04) * 1.8, 0, 0.92));
  setOpacity(hubRing, clamp((progress - 0.06) * 1.8, 0, 0.94));

  setOpacity(pressureHalo, clamp((progress - 0.04) * 1.6, 0, 0.42));
  setOpacity(pressureLeft, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureRight, clamp((progress - 0.08) * 1.6, 0, 0.92));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnTrace(routeProgress);

  const leftRotation = lerp(46, 0, routeProgress);
  const rightRotation = lerp(-46, 0, routeProgress);
  const armScale = lerp(0.78, 1, routeProgress);
  const mastScaleY = lerp(0.94, 1, routeProgress);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);

  setTransform(signalLeft, points.hub.x, points.hub.y, armScale, armScale, leftRotation);
  setTransform(signalRight, points.hub.x, points.hub.y, armScale, armScale, rightRotation);
  setTransform(signalMast, points.hub.x, points.hub.y, 1, mastScaleY, 0);
  setOpacity(signalLeft, 0.98);
  setOpacity(signalRight, 0.98);
  setOpacity(signalMast, 0.94);
  setOpacity(hubRing, 0.96);
  setPathWindow(semaphoreTrace, TRACE_LENGTH, TRACE_LENGTH * routeProgress, 1);

  setOpacity(pressureHalo, lerp(0.42, 0.04, progress));
  setOpacity(pressureLeft, clamp(0.92 - progress * 1.2, 0, 1));
  setOpacity(pressureRight, clamp(0.92 - progress * 1.2, 0, 1));

  [candidateLean, candidateSplit, candidateOpen, searchGuideA, searchGuideB, searchGuideC, mastPreview, hubPreview].forEach((element) =>
    setOpacity(element, 0),
  );

  setOpacity(slotLeft, slotState(routeProgress, 0.16));
  setOpacity(slotRight, slotState(routeProgress, 0.5));
  setOpacity(slotBottom, slotState(routeProgress, 0.82));
  setOpacity(resolutionHalo, clamp((progress - 0.66) * 1.45, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.55, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.hub, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);

  setTransform(signalLeft, points.hub.x, points.hub.y, lerp(1, 0.985, settle), lerp(1, 0.985, settle), 0);
  setTransform(signalRight, points.hub.x, points.hub.y, lerp(1, 0.985, settle), lerp(1, 0.985, settle), 0);
  setTransform(signalMast, points.hub.x, points.hub.y, 1, lerp(1, 0.99, settle), 0);
  setOpacity(signalLeft, 0.92);
  setOpacity(signalRight, 0.92);
  setOpacity(signalMast, 0.9);
  setOpacity(hubRing, lerp(0.96, 0.88, settle));
  setPathWindow(semaphoreTrace, TRACE_LENGTH, TRACE_LENGTH, lerp(1, 0.16, settle));

  [
    pressureHalo,
    pressureLeft,
    pressureRight,
    candidateLean,
    candidateSplit,
    candidateOpen,
    searchGuideA,
    searchGuideB,
    searchGuideC,
    mastPreview,
    hubPreview,
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
