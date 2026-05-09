const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";

const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 6_000 },
  { id: "search", label: "search for form", duration: 6_500 },
  { id: "tension", label: "tension", duration: 6_500 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const travelSpine = document.getElementById("travel-spine");
const activeTrail = document.getElementById("active-trail");
const destinationGroup = document.getElementById("destination-group");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");
const searchEchoA = document.getElementById("search-echo-a");
const searchEchoB = document.getElementById("search-echo-b");
const searchEchoC = document.getElementById("search-echo-c");
const pressureHalo = document.getElementById("pressure-halo");
const pressureLeft = document.getElementById("pressure-left");
const pressureRight = document.getElementById("pressure-right");
const pressureHead = document.getElementById("pressure-head");
const compressionGuide = document.getElementById("compression-guide");
const pistonGroup = document.getElementById("piston-group");
const pistonTop = document.getElementById("piston-top");
const pistonInnerHead = document.getElementById("piston-inner-head");
const pistonLeft = document.getElementById("piston-left");
const pistonRight = document.getElementById("piston-right");
const pistonBase = document.getElementById("piston-base");
const pistonSeat = document.getElementById("piston-seat");
const pistonGuideLeft = document.getElementById("piston-guide-left");
const pistonGuideRight = document.getElementById("piston-guide-right");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionTrace = document.getElementById("resolution-trace");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const candidateStrokeSets = [
  Array.from(candidateA.querySelectorAll("[data-stroke]")),
  Array.from(candidateB.querySelectorAll("[data-stroke]")),
  Array.from(candidateC.querySelectorAll("[data-stroke]")),
];

const ROUTE_LENGTH = activeTrail.getTotalLength();
const TRACE_LENGTH = resolutionTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 292, y: 452 },
  ingress: { x: 548, y: 452 },
  appearanceHold: { x: 630, y: 430 },
  candidateA: { x: 748, y: 384 },
  candidateB: { x: 820, y: 344 },
  candidateC: { x: 924, y: 388 },
  approach: { x: 858, y: 452 },
  hub: { x: 820, y: 452 },
};

const pressure = {
  leftOpen: { x: 734, y: 452 },
  leftTight: { x: 770, y: 452 },
  rightOpen: { x: 906, y: 452 },
  rightTight: { x: 870, y: 452 },
  headOpen: { x: 820, y: 326 },
  headTight: { x: 820, y: 386 },
};

const candidateStates = {
  faint: { opacity: 0.38, scale: 0.92, stroke: "#979797" },
  active: { opacity: 0.96, scale: 1.04, stroke: "#4f4f4f" },
  visited: { opacity: 0.68, scale: 0.96, stroke: "#666666" },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
  looping: !CAPTURE_MODE,
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

function setDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = scaleX) {
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
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 240).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function setTrailingWindow(element, totalLength, endLength, visibleLength, opacity) {
  const clampedEnd = clamp(endLength, 0, totalLength);
  const segmentLength = clamp(visibleLength, 0, totalLength);
  const startLength = Math.max(0, clampedEnd - segmentLength);
  const visible = clampedEnd - startLength;
  element.style.strokeDasharray = `${visible.toFixed(2)} ${(totalLength + 240).toFixed(2)}`;
  element.style.strokeDashoffset = `${(-startLength).toFixed(2)}`;
  setOpacity(element, opacity);
}

function pointOnTrace(progress) {
  const length = clamp(progress, 0, 1) * TRACE_LENGTH;
  const point = resolutionTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function setStrokeSet(strokes, color) {
  for (const stroke of strokes) {
    stroke.setAttribute("stroke", color);
  }
}

function applyCandidate(group, strokes, point, visualState, rotate = 0, yOffset = 0) {
  setTransform(group, point.x, point.y + yOffset, visualState.scale, visualState.scale, rotate);
  setOpacity(group, visualState.opacity);
  setStrokeSet(strokes, visualState.stroke);
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
  svg.dataset.phase = info.phase.id;
}

function applySceneOffset(phaseId) {
  const offsets = {
    appearance: { x: 52, y: 18 },
    search: { x: 26, y: 24 },
    tension: { x: 0, y: 8 },
    transformation: { x: 0, y: 2 },
    resolution: { x: 0, y: -2 },
  };
  const offset = offsets[phaseId] ?? { x: 0, y: 0 };
  sceneRoot.setAttribute("transform", `translate(${offset.x} ${offset.y})`);
}

function applyLayout(phaseId) {
  const portrait = window.innerWidth / window.innerHeight < 0.9;
  if (portrait) {
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

  if (!portrait) {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 132, y: 156, width: 1080, height: 628 },
    search: { x: 142, y: 132, width: 1132, height: 656 },
    tension: { x: 332, y: 168, width: 980, height: 626 },
    transformation: { x: 346, y: 152, width: 964, height: 646 },
    resolution: { x: 392, y: 140, width: 872, height: 646 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(travelSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(searchGuideA, 0);
  setOpacity(searchGuideB, 0);
  setOpacity(searchGuideC, 0);
  applyCandidate(candidateA, candidateStrokeSets[0], points.candidateA, candidateStates.faint, -6);
  applyCandidate(candidateB, candidateStrokeSets[1], points.candidateB, candidateStates.faint, 0);
  applyCandidate(candidateC, candidateStrokeSets[2], points.candidateC, candidateStates.faint, 6);
  setOpacity(searchEchoA, 0);
  setOpacity(searchEchoB, 0);
  setOpacity(searchEchoC, 0);
  setOpacity(pressureHalo, 0);
  setTransform(pressureLeft, pressure.leftOpen.x, pressure.leftOpen.y);
  setTransform(pressureRight, pressure.rightOpen.x, pressure.rightOpen.y);
  setTransform(pressureHead, pressure.headOpen.x, pressure.headOpen.y);
  setOpacity(pressureLeft, 0);
  setOpacity(pressureRight, 0);
  setOpacity(pressureHead, 0);
  setOpacity(compressionGuide, 0);
  setOpacity(pistonGroup, 0);
  [pistonTop, pistonInnerHead, pistonLeft, pistonRight, pistonBase, pistonSeat, pistonGuideLeft, pistonGuideRight, resolutionHalo].forEach((element) =>
    setOpacity(element, 0),
  );
  setPathWindow(resolutionTrace, TRACE_LENGTH, 0, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.appearanceHold, eased);
  const preview = clamp((progress - 0.28) * 1.7, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(travelSpine, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setOpacity(destinationGroup, preview * 0.92);
  setOpacity(searchGuideA, preview * 0.42);
  setOpacity(searchGuideB, preview * 0.34);
  setOpacity(searchGuideC, preview * 0.3);
  applyCandidate(candidateA, candidateStrokeSets[0], points.candidateA, candidateStates.faint, -6, 0);
  applyCandidate(candidateB, candidateStrokeSets[1], points.candidateB, points.candidateB ? candidateStates.faint : candidateStates.faint, 0, 0);
  applyCandidate(candidateC, candidateStrokeSets[2], points.candidateC, candidateStates.faint, 6, 0);
  setOpacity(candidateA, preview * 0.46);
  setOpacity(candidateB, preview * 0.42);
  setOpacity(candidateC, preview * 0.38);
  setOpacity(pressureLeft, preview * 0.18);
  setOpacity(pressureRight, preview * 0.18);
  setOpacity(pressureHead, preview * 0.16);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.appearanceHold, to: points.candidateA },
    { start: 0.28, end: 0.58, from: points.candidateA, to: points.candidateB },
    { start: 0.58, end: 0.84, from: points.candidateB, to: points.candidateC },
    { start: 0.84, end: 1, from: points.candidateC, to: points.approach },
  ]);

  setDot(position, 18, 88, 1, 0.24 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(travelSpine, lerp(0.34, 0.14, progress));
  setTrailingWindow(
    activeTrail,
    ROUTE_LENGTH,
    ROUTE_LENGTH * lerp(0.22, 1, progress),
    lerp(180, 260, progress),
    lerp(0.2, 0.1, progress),
  );
  setOpacity(destinationGroup, lerp(0.52, 0.4, progress));
  setOpacity(searchGuideA, 0.34 + clamp(progress / 0.24, 0, 1) * 0.22);
  setOpacity(searchGuideB, 0.28 + clamp((progress - 0.22) / 0.24, 0, 1) * 0.22);
  setOpacity(searchGuideC, 0.24 + clamp((progress - 0.52) / 0.2, 0, 1) * 0.24);

  const activeA = progress < 0.32;
  const activeB = progress >= 0.32 && progress < 0.64;
  const activeC = progress >= 0.64;

  applyCandidate(
    candidateA,
    candidateStrokeSets[0],
    points.candidateA,
    activeA ? candidateStates.active : progress > 0.32 ? candidateStates.visited : candidateStates.faint,
    -6,
  );
  applyCandidate(
    candidateB,
    candidateStrokeSets[1],
    points.candidateB,
    activeB ? candidateStates.active : progress > 0.64 ? candidateStates.visited : candidateStates.faint,
    0,
  );
  applyCandidate(
    candidateC,
    candidateStrokeSets[2],
    points.candidateC,
    activeC ? candidateStates.active : candidateStates.faint,
    6,
  );

  setOpacity(searchEchoA, activeA ? 0.74 : 0);
  setOpacity(searchEchoB, activeB ? 0.74 : 0);
  setOpacity(searchEchoC, activeC ? 0.76 : 0);
  setOpacity(pressureHalo, 0.05);
  setOpacity(pressureLeft, 0.08);
  setOpacity(pressureRight, 0.08);
  setOpacity(pressureHead, 0.07);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.4, 0, 1);
  const position = mixPoint(points.approach, points.hub, easeInOut(travel));
  const collapse = easeInOut(clamp(progress / 0.74, 0, 1));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.1) * 0.1,
    lerp(1, 0.48, compression),
    lerp(1, 1.9, compression),
  );
  setOpacity(travelSpine, lerp(0.08, 0.02, progress));
  setTrailingWindow(activeTrail, ROUTE_LENGTH, ROUTE_LENGTH, lerp(180, 96, progress), lerp(0.08, 0, progress));
  setOpacity(destinationGroup, lerp(0.14, 0.06, progress));
  setOpacity(searchGuideA, lerp(0.22, 0, progress));
  setOpacity(searchGuideB, lerp(0.24, 0, progress));
  setOpacity(searchGuideC, lerp(0.26, 0, progress));

  applyCandidate(candidateA, candidateStrokeSets[0], { x: lerp(640, 718, collapse), y: lerp(392, 402, collapse) }, candidateStates.visited, -8);
  applyCandidate(candidateB, candidateStrokeSets[1], { x: lerp(820, 820, collapse), y: lerp(340, 376, collapse) }, candidateStates.visited, 0);
  applyCandidate(candidateC, candidateStrokeSets[2], { x: lerp(1000, 922, collapse), y: lerp(392, 402, collapse) }, candidateStates.visited, 8);
  setOpacity(candidateA, lerp(0.3, 0.05, collapse));
  setOpacity(candidateB, lerp(0.3, 0.06, collapse));
  setOpacity(candidateC, lerp(0.3, 0.05, collapse));
  setOpacity(searchEchoA, 0);
  setOpacity(searchEchoB, 0);
  setOpacity(searchEchoC, 0);

  const leftPoint = mixPoint(pressure.leftOpen, pressure.leftTight, collapse);
  const rightPoint = mixPoint(pressure.rightOpen, pressure.rightTight, collapse);
  const headPoint = mixPoint(pressure.headOpen, pressure.headTight, collapse);

  setTransform(pressureLeft, leftPoint.x, leftPoint.y, lerp(1, 0.92, collapse), 1);
  setTransform(pressureRight, rightPoint.x, rightPoint.y, lerp(1, 0.92, collapse), 1);
  setTransform(pressureHead, headPoint.x, headPoint.y, lerp(1, 0.9, collapse), 1);
  setOpacity(pressureHalo, clamp((progress - 0.04) * 1.6, 0, 0.42));
  setOpacity(pressureLeft, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureRight, clamp((progress - 0.08) * 1.6, 0, 0.92));
  setOpacity(pressureHead, clamp((progress - 0.04) * 1.6, 0, 0.9));
  setOpacity(compressionGuide, clamp((progress - 0.16) * 1.4, 0, 0.34));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnTrace(routeProgress);

  setDot(position, 16, 98, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(travelSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);
  setOpacity(destinationGroup, lerp(0.06, 0, progress));
  [searchGuideA, searchGuideB, searchGuideC, candidateA, candidateB, candidateC, searchEchoA, searchEchoB, searchEchoC].forEach((element) =>
    setOpacity(element, 0),
  );

  setTransform(pressureLeft, pressure.leftTight.x, pressure.leftTight.y);
  setTransform(pressureRight, pressure.rightTight.x, pressure.rightTight.y);
  setTransform(pressureHead, pressure.headTight.x, pressure.headTight.y);
  setOpacity(pressureHalo, lerp(0.42, 0.02, progress));
  setOpacity(pressureLeft, clamp(0.92 - progress * 1.3, 0, 1));
  setOpacity(pressureRight, clamp(0.92 - progress * 1.3, 0, 1));
  setOpacity(pressureHead, clamp(0.9 - progress * 1.3, 0, 1));
  setOpacity(compressionGuide, clamp(0.34 - progress * 0.6, 0, 1));

  setOpacity(pistonGroup, 1);
  setOpacity(pistonTop, clamp((routeProgress - 0.08) * 1.8, 0, 1));
  setOpacity(pistonInnerHead, clamp((routeProgress - 0.12) * 1.8, 0, 1));
  setOpacity(pistonLeft, clamp((routeProgress - 0.34) * 1.7, 0, 1));
  setOpacity(pistonBase, clamp((routeProgress - 0.58) * 1.8, 0, 1));
  setOpacity(pistonRight, clamp((routeProgress - 0.72) * 1.8, 0, 1));
  setOpacity(pistonSeat, clamp((routeProgress - 0.78) * 1.8, 0, 0.88));
  setOpacity(pistonGuideLeft, clamp((routeProgress - 0.62) * 1.5, 0, 0.82));
  setOpacity(pistonGuideRight, clamp((routeProgress - 0.8) * 1.5, 0, 0.82));
  setOpacity(resolutionHalo, clamp((progress - 0.66) * 1.5, 0, 0.16));
  setPathWindow(resolutionTrace, TRACE_LENGTH, TRACE_LENGTH * routeProgress, 1);
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.hub, 16, 98, 1, holdPulse);
  setOpacity(travelSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(pistonGroup, 1);
  setOpacity(pistonTop, 0.94);
  setOpacity(pistonInnerHead, 0.88);
  setOpacity(pistonLeft, 0.92);
  setOpacity(pistonRight, 0.92);
  setOpacity(pistonBase, 0.88);
  setOpacity(pistonSeat, lerp(0.88, 0.72, settle));
  setOpacity(pistonGuideLeft, lerp(0.82, 0.54, settle));
  setOpacity(pistonGuideRight, lerp(0.82, 0.54, settle));
  setOpacity(resolutionHalo, lerp(0.16, 0.24, settle));
  setPathWindow(resolutionTrace, TRACE_LENGTH, TRACE_LENGTH, lerp(1, 0.18, settle));

  [pressureHalo, pressureLeft, pressureRight, pressureHead, compressionGuide].forEach((element) => setOpacity(element, 0));
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

  applySceneOffset(info.phase.id);
  applyLayout(info.phase.id);
  updatePhaseLabel(info);
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
  const elapsed = state.looping ? rawElapsed % TOTAL_DURATION : clamp(rawElapsed, 0, TOTAL_DURATION);

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
    const nextElapsed = state.looping
      ? ((milliseconds % TOTAL_DURATION) + TOTAL_DURATION) % TOTAL_DURATION
      : clamp(milliseconds, 0, TOTAL_DURATION);
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
  setLooping(nextLooping) {
    state.looping = Boolean(nextLooping);
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

applyLayout("appearance");
window.addEventListener("resize", () => {
  const info = phaseForElapsed(state.currentElapsed);
  applyLayout(info.phase.id);
});
resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
