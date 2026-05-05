const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";

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

const travelSpine = document.getElementById("travel-spine");
const activeTrail = document.getElementById("active-trail");
const destinationGroup = document.getElementById("destination-group");
const crownSlot = document.getElementById("crown-slot");
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
const pressureCap = document.getElementById("pressure-cap");
const tensionGuide = document.getElementById("tension-guide");
const crownGroup = document.getElementById("crown-group");
const crownLeft = document.getElementById("crown-left");
const crownRight = document.getElementById("crown-right");
const crownDoorLeft = document.getElementById("crown-door-left");
const crownDoorRight = document.getElementById("crown-door-right");
const crownDoorTop = document.getElementById("crown-door-top");
const crownDoorBase = document.getElementById("crown-door-base");
const crownOuterLeft = document.getElementById("crown-outer-left");
const crownOuterRight = document.getElementById("crown-outer-right");
const resolutionHalo = document.getElementById("resolution-halo");
const traceCenter = document.getElementById("trace-center");
const traceLeft = document.getElementById("trace-left");
const traceRight = document.getElementById("trace-right");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ROUTE_LENGTH = activeTrail.getTotalLength();
const TRACE_CENTER_LENGTH = traceCenter.getTotalLength();
const TRACE_LEFT_LENGTH = traceLeft.getTotalLength();
const TRACE_RIGHT_LENGTH = traceRight.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 292, y: 452 },
  ingress: { x: 548, y: 452 },
  candidateA: { x: 642, y: 394 },
  candidateB: { x: 826, y: 342 },
  candidateC: { x: 1006, y: 394 },
  gate: { x: 820, y: 378 },
  crownLeftPeak: { x: 752, y: 324 },
  crownCenterPeak: { x: 820, y: 288 },
  crownRightPeak: { x: 888, y: 324 },
  final: { x: 820, y: 452 },
};

const candidateStates = {
  faint: { opacity: 0.18, scale: 0.92, stroke: "#b5b5b5" },
  active: { opacity: 0.94, scale: 1.04, stroke: "#4f4f4f" },
  visited: { opacity: 0.34, scale: 0.96, stroke: "#7a7a7a" },
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
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 200).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function applyStrokeReveal(element, progress, totalLength) {
  const shown = clamp(progress, 0, 1) * totalLength;
  element.style.strokeDasharray = `${shown.toFixed(2)} ${(totalLength + 160).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
}

function setCandidateState(element, anchor, stateName, rotate = 0) {
  const config = candidateStates[stateName];
  element.querySelectorAll("[data-stroke]").forEach((child) => {
    child.setAttribute("stroke", config.stroke);
  });
  setTransform(element, anchor.x, anchor.y, config.scale, config.scale, rotate);
  setOpacity(element, config.opacity);
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
    localProgress: 1,
    totalProgress: 1,
  };
}

function updatePhaseLabel(info) {
  phaseLabel.textContent = info.phase.label;
}

function applySceneOffset(phaseId) {
  const offsets = {
    appearance: { x: 60, y: 18 },
    search: { x: 24, y: 24 },
    tension: { x: 0, y: 10 },
    transformation: { x: 0, y: 2 },
    resolution: { x: 0, y: -4 },
  };
  const offset = offsets[phaseId] ?? { x: 0, y: 0 };
  sceneRoot.setAttribute("transform", `translate(${offset.x} ${offset.y})`);
}

function applyLayout(phaseId) {
  const portrait = window.innerWidth / window.innerHeight < 0.9;
  svg.dataset.layout = portrait ? "portrait" : "landscape";
  svg.setAttribute("preserveAspectRatio", portrait ? "xMidYMid slice" : "xMidYMid meet");

  if (!portrait) {
    layoutRoot.setAttribute("transform", "");
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  layoutRoot.setAttribute(
    "transform",
    "translate(0 -12) translate(800 450) scale(1.035) translate(-800 -450)",
  );
  const frames = {
    appearance: { x: 132, y: 148, width: 1080, height: 638 },
    search: { x: 132, y: 122, width: 1148, height: 666 },
    tension: { x: 352, y: 136, width: 936, height: 664 },
    transformation: { x: 332, y: 118, width: 978, height: 692 },
    resolution: { x: 394, y: 122, width: 860, height: 676 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function resetScene() {
  setDot(points.start, 18, 74, 0, 0);
  setOpacity(travelSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);

  setOpacity(destinationGroup, 0);
  setOpacity(crownSlot, 0);
  [searchGuideA, searchGuideB, searchGuideC, searchEchoA, searchEchoB, searchEchoC].forEach((element) => setOpacity(element, 0));
  setCandidateState(candidateA, points.candidateA, "faint", -8);
  setCandidateState(candidateB, points.candidateB, "faint", 0);
  setCandidateState(candidateC, points.candidateC, "faint", 8);
  setOpacity(candidateA, 0);
  setOpacity(candidateB, 0);
  setOpacity(candidateC, 0);

  setOpacity(pressureHalo, 0);
  setTransform(pressureLeft, 742, 378);
  setTransform(pressureRight, 898, 378);
  setTransform(pressureCap, 820, 320, 1.12, 1.06);
  setOpacity(pressureLeft, 0);
  setOpacity(pressureRight, 0);
  setOpacity(pressureCap, 0);
  setOpacity(tensionGuide, 0);

  setOpacity(crownGroup, 0);
  [crownLeft, crownRight, crownDoorLeft, crownDoorRight, crownDoorTop, crownDoorBase, crownOuterLeft, crownOuterRight, resolutionHalo].forEach((element) => setOpacity(element, 0));
  [traceCenter, traceLeft, traceRight].forEach((element) => {
    setOpacity(element, 0);
    element.style.strokeDasharray = "0 1200";
    element.style.strokeDashoffset = "0";
  });
}

function renderAppearance(progress) {
  const moveProgress = easeOut(clamp(progress / 0.68, 0, 1));
  const position = mixPoint(points.start, points.ingress, moveProgress);
  const scaffold = 0.28 + progress * 0.2;

  setDot(position, lerp(16, 18, progress), lerp(52, 72, progress), progress < 0.08 ? progress / 0.08 : 1, 0.12 + progress * 0.1);
  setOpacity(travelSpine, 0.2);
  setPathWindow(activeTrail, ROUTE_LENGTH, lerp(26, 118, moveProgress), 0.18);

  setOpacity(destinationGroup, scaffold);
  setOpacity(crownSlot, 0.22 + progress * 0.14);

  setOpacity(searchGuideA, clamp((progress - 0.34) / 0.22, 0, 1) * 0.2);
  setOpacity(searchGuideB, clamp((progress - 0.52) / 0.2, 0, 1) * 0.12);
  setOpacity(searchGuideC, clamp((progress - 0.7) / 0.16, 0, 1) * 0.08);
  setCandidateState(candidateA, points.candidateA, "faint", -8);
  setCandidateState(candidateB, points.candidateB, "faint", 0);
  setCandidateState(candidateC, points.candidateC, "faint", 8);
  setOpacity(candidateA, clamp((progress - 0.42) / 0.24, 0, 1) * 0.14);
  setOpacity(candidateB, clamp((progress - 0.56) / 0.2, 0, 1) * 0.1);
  setOpacity(candidateC, clamp((progress - 0.72) / 0.16, 0, 1) * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.candidateA },
    { start: 0.24, end: 0.56, from: points.candidateA, to: points.candidateB },
    { start: 0.56, end: 0.84, from: points.candidateB, to: points.candidateC },
    { start: 0.84, end: 1, from: points.candidateC, to: points.gate },
  ]);

  setDot(position, 18, 72, 1, 0.2 + pulseWave(progress, 1.5) * 0.06);
  setOpacity(travelSpine, 0.16);
  setPathWindow(activeTrail, ROUTE_LENGTH, lerp(210, ROUTE_LENGTH * 0.86, progress), 0.2);
  setOpacity(destinationGroup, 0.28);
  setOpacity(crownSlot, 0.16);

  setOpacity(searchGuideA, clamp((progress - 0.02) / 0.18, 0, 1) * 0.4);
  setOpacity(searchGuideB, clamp((progress - 0.26) / 0.18, 0, 1) * 0.38);
  setOpacity(searchGuideC, clamp((progress - 0.58) / 0.18, 0, 1) * 0.36);

  setCandidateState(candidateA, points.candidateA, progress < 0.28 ? "active" : "visited", -8);
  setCandidateState(candidateB, points.candidateB, progress < 0.22 ? "faint" : progress < 0.64 ? "active" : "visited", 0);
  setCandidateState(candidateC, points.candidateC, progress < 0.56 ? "faint" : progress < 0.9 ? "active" : "visited", 8);

  setOpacity(searchEchoA, clamp((progress - 0.18) / 0.12, 0, 1) * 0.46);
  setOpacity(searchEchoB, clamp((progress - 0.48) / 0.12, 0, 1) * 0.44);
  setOpacity(searchEchoC, clamp((progress - 0.78) / 0.12, 0, 1) * 0.42);
}

function renderTension(progress) {
  const squeeze = easeInOut(clamp((progress - 0.14) / 0.62, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.24, 0, 1));
  const capDrop = easeInOut(clamp((progress - 0.08) / 0.54, 0, 1));

  setDot(
    points.gate,
    lerp(18, 19, squeeze),
    lerp(72, 58, squeeze),
    1,
    0.22 + pulseWave(progress, 1.6) * 0.08,
    lerp(1, 0.48, squeeze),
    lerp(1, 1.78, squeeze),
  );
  setOpacity(travelSpine, 0.12);
  setPathWindow(activeTrail, ROUTE_LENGTH, lerp(760, 220, progress), 0.18 * residue);
  setOpacity(destinationGroup, 0.26);
  setOpacity(crownSlot, 0.1);

  setCandidateState(candidateA, points.candidateA, "visited", -8);
  setCandidateState(candidateB, points.candidateB, "visited", 0);
  setCandidateState(candidateC, points.candidateC, "visited", 8);
  setOpacity(candidateA, 0.18 * residue);
  setOpacity(candidateB, 0.16 * residue);
  setOpacity(candidateC, 0.14 * residue);
  setOpacity(searchEchoA, 0.16 * residue);
  setOpacity(searchEchoB, 0.14 * residue);
  setOpacity(searchEchoC, 0.12 * residue);
  setOpacity(searchGuideA, 0.12 * residue);
  setOpacity(searchGuideB, 0.1 * residue);
  setOpacity(searchGuideC, 0.08 * residue);

  setOpacity(pressureHalo, 0.16 + pulseWave(progress, 1.2) * 0.08);
  setOpacity(pressureLeft, 0.82);
  setOpacity(pressureRight, 0.82);
  setOpacity(pressureCap, 0.82);
  setOpacity(tensionGuide, 0.42);
  setTransform(pressureLeft, lerp(742, 778, squeeze), 378);
  setTransform(pressureRight, lerp(898, 862, squeeze), 378);
  setTransform(pressureCap, 820, lerp(320, 298, capDrop), lerp(1.12, 0.78, squeeze), lerp(1.06, 0.82, squeeze));
}

function renderTransformation(progress) {
  const tensionFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  const groupScale = lerp(0.94, 1, easeOut(clamp((progress - 0.08) / 0.42, 0, 1)));
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.18, from: points.gate, to: points.crownCenterPeak },
    { start: 0.18, end: 0.38, from: points.crownCenterPeak, to: points.crownLeftPeak },
    { start: 0.38, end: 0.56, from: points.crownLeftPeak, to: points.crownCenterPeak },
    { start: 0.56, end: 0.76, from: points.crownCenterPeak, to: points.crownRightPeak },
    { start: 0.76, end: 1, from: points.crownRightPeak, to: points.final },
  ]);

  const centerProgress = clamp(progress / 0.2, 0, 1);
  const leftProgress = clamp((progress - 0.18) / 0.2, 0, 1);
  const rightProgress = clamp((progress - 0.56) / 0.2, 0, 1);
  const doorwayProgress = clamp((progress - 0.16) / 0.44, 0, 1);
  const outerProgress = clamp((progress - 0.34) / 0.36, 0, 1);

  setDot(position, lerp(19, 17, progress), lerp(56, 118, progress), 1, 0.24 + pulseWave(progress, 2.2) * 0.08);
  setOpacity(travelSpine, 0.08 * tensionFade);
  setPathWindow(activeTrail, ROUTE_LENGTH, 170, 0.14 * tensionFade);
  setOpacity(destinationGroup, 0.18 * (1 - doorwayProgress));
  setOpacity(crownSlot, 0.06 * (1 - doorwayProgress));

  setOpacity(pressureHalo, 0.18 * tensionFade);
  setOpacity(pressureLeft, 0.82 * tensionFade);
  setOpacity(pressureRight, 0.82 * tensionFade);
  setOpacity(pressureCap, 0.82 * tensionFade);
  setOpacity(tensionGuide, 0.4 * tensionFade);
  setTransform(pressureLeft, lerp(778, 742, doorwayProgress), 378);
  setTransform(pressureRight, lerp(862, 898, doorwayProgress), 378);
  setTransform(pressureCap, 820, lerp(298, 320, doorwayProgress), lerp(0.78, 1.04, doorwayProgress), lerp(0.82, 0.96, doorwayProgress));

  setOpacity(crownGroup, 1);
  crownGroup.setAttribute(
    "transform",
    `translate(${points.final.x} ${points.final.y}) scale(${groupScale.toFixed(3)} ${groupScale.toFixed(3)}) translate(${-points.final.x} ${-points.final.y})`,
  );

  setOpacity(crownLeft, leftProgress * 0.96);
  setOpacity(crownRight, rightProgress * 0.96);
  setOpacity(crownDoorLeft, doorwayProgress * 0.92);
  setOpacity(crownDoorRight, doorwayProgress * 0.92);
  setOpacity(crownDoorTop, doorwayProgress * 0.82);
  setOpacity(crownDoorBase, clamp((progress - 0.58) / 0.22, 0, 1) * 0.76);
  setOpacity(crownOuterLeft, outerProgress * 0.54);
  setOpacity(crownOuterRight, outerProgress * 0.54);
  setOpacity(resolutionHalo, clamp((progress - 0.7) / 0.2, 0, 1) * 0.1);

  setOpacity(traceCenter, centerProgress * 0.88);
  applyStrokeReveal(traceCenter, centerProgress, TRACE_CENTER_LENGTH);
  setOpacity(traceLeft, leftProgress * 0.88);
  applyStrokeReveal(traceLeft, leftProgress, TRACE_LEFT_LENGTH);
  setOpacity(traceRight, rightProgress * 0.88);
  applyStrokeReveal(traceRight, rightProgress, TRACE_RIGHT_LENGTH);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const haloPulse = 0.14 + pulseWave(progress, 1.5) * 0.06;
  const groupScale = lerp(1.012, 1, settle);

  setDot(points.final, 17, lerp(104, 82, progress), 1, haloPulse);
  setOpacity(travelSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(crownSlot, 0);
  [pressureHalo, pressureLeft, pressureRight, pressureCap, tensionGuide].forEach((element) => setOpacity(element, 0));

  setOpacity(crownGroup, 1);
  crownGroup.setAttribute(
    "transform",
    `translate(${points.final.x} ${points.final.y}) scale(${groupScale.toFixed(3)} ${groupScale.toFixed(3)}) translate(${-points.final.x} ${-points.final.y})`,
  );
  [crownLeft, crownRight, crownDoorLeft, crownDoorRight].forEach((element) => setOpacity(element, 0.96));
  setOpacity(crownDoorTop, 0.84);
  setOpacity(crownDoorBase, 0.76);
  setOpacity(crownOuterLeft, 0.42);
  setOpacity(crownOuterRight, 0.42);
  setOpacity(resolutionHalo, 0.08);

  setOpacity(traceCenter, lerp(0.34, 0.12, settle));
  applyStrokeReveal(traceCenter, 1, TRACE_CENTER_LENGTH);
  setOpacity(traceLeft, lerp(0.28, 0.08, settle));
  applyStrokeReveal(traceLeft, 1, TRACE_LEFT_LENGTH);
  setOpacity(traceRight, lerp(0.28, 0.08, settle));
  applyStrokeReveal(traceRight, 1, TRACE_RIGHT_LENGTH);
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
  if (state.playing === nextPlaying) return;
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
