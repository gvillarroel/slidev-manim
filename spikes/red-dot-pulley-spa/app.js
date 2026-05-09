const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";

const TOTAL_DURATION = 37_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 9_000 },
  { id: "resolution", label: "resolution", duration: 9_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const travelSpine = document.getElementById("travel-spine");
const activeTrail = document.getElementById("active-trail");
const destinationGroup = document.getElementById("destination-group");
const beamSlot = document.getElementById("beam-slot");
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
const pressureTop = document.getElementById("pressure-top");
const tensionGuide = document.getElementById("tension-guide");
const pulleyGroup = document.getElementById("pulley-group");
const beamTop = document.getElementById("beam-top");
const beamLeftDrop = document.getElementById("beam-left-drop");
const beamRightDrop = document.getElementById("beam-right-drop");
const pulleyLeftOuter = document.getElementById("pulley-left-outer");
const pulleyLeftInner = document.getElementById("pulley-left-inner");
const pulleyRightOuter = document.getElementById("pulley-right-outer");
const pulleyRightInner = document.getElementById("pulley-right-inner");
const hangingCable = document.getElementById("hanging-cable");
const lowerBar = document.getElementById("lower-bar");
const lowerLeftReturn = document.getElementById("lower-left-return");
const lowerRightReturn = document.getElementById("lower-right-return");
const resolutionHalo = document.getElementById("resolution-halo");
const traceCenterUp = document.getElementById("trace-center-up");
const traceLeft = document.getElementById("trace-left");
const traceRight = document.getElementById("trace-right");
const traceDrop = document.getElementById("trace-drop");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ROUTE_LENGTH = activeTrail.getTotalLength();
const TRACE_CENTER_UP_LENGTH = traceCenterUp.getTotalLength();
const TRACE_LEFT_LENGTH = traceLeft.getTotalLength();
const TRACE_RIGHT_LENGTH = traceRight.getTotalLength();
const TRACE_DROP_LENGTH = traceDrop.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 292, y: 454 },
  ingress: { x: 552, y: 454 },
  candidateA: { x: 670, y: 392 },
  candidateB: { x: 820, y: 334 },
  candidateC: { x: 968, y: 392 },
  gate: { x: 820, y: 418 },
  tension: { x: 820, y: 438 },
  centerHub: { x: 820, y: 336 },
  leftWheel: { x: 742, y: 330 },
  rightWheel: { x: 898, y: 330 },
  final: { x: 820, y: 500 },
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
    appearance: { x: 186, y: 16 },
    search: { x: 72, y: 22 },
    tension: { x: 0, y: 56 },
    transformation: { x: 0, y: 18 },
    resolution: { x: 0, y: -6 },
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
    "translate(0 -10) translate(800 450) scale(1.035) translate(-800 -450)",
  );
  const frames = {
    appearance: { x: 128, y: 156, width: 1096, height: 628 },
    search: { x: 146, y: 118, width: 1138, height: 672 },
    tension: { x: 320, y: 152, width: 992, height: 648 },
    transformation: { x: 314, y: 110, width: 1006, height: 706 },
    resolution: { x: 380, y: 118, width: 884, height: 692 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function resetScene() {
  setDot(points.start, 18, 74, 0, 0);
  setOpacity(travelSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);

  setOpacity(destinationGroup, 0);
  setOpacity(beamSlot, 0);
  [searchGuideA, searchGuideB, searchGuideC, searchEchoA, searchEchoB, searchEchoC].forEach((element) => setOpacity(element, 0));
  setCandidateState(candidateA, points.candidateA, "faint", -10);
  setCandidateState(candidateB, points.candidateB, "faint", 0);
  setCandidateState(candidateC, points.candidateC, "faint", 10);
  setOpacity(candidateA, 0);
  setOpacity(candidateB, 0);
  setOpacity(candidateC, 0);

  setOpacity(pressureHalo, 0);
  setCircleCenter(pressureHalo, points.tension);
  pressureLeft.setAttribute("cx", "770");
  pressureLeft.setAttribute("cy", "394");
  pressureRight.setAttribute("cx", "870");
  pressureRight.setAttribute("cy", "394");
  pressureTop.setAttribute("transform", "");
  setOpacity(pressureLeft, 0);
  setOpacity(pressureRight, 0);
  setOpacity(pressureTop, 0);
  setOpacity(tensionGuide, 0);

  setOpacity(pulleyGroup, 0);
  [
    beamTop,
    beamLeftDrop,
    beamRightDrop,
    pulleyLeftOuter,
    pulleyLeftInner,
    pulleyRightOuter,
    pulleyRightInner,
    hangingCable,
    lowerBar,
    lowerLeftReturn,
    lowerRightReturn,
    resolutionHalo,
  ].forEach((element) => setOpacity(element, 0));
  [traceCenterUp, traceLeft, traceRight, traceDrop].forEach((element) => {
    setOpacity(element, 0);
    element.style.strokeDasharray = "0 1200";
    element.style.strokeDashoffset = "0";
  });
}

function renderAppearance(progress) {
  const moveProgress = easeOut(clamp(progress / 0.68, 0, 1));
  const position = mixPoint(points.start, points.ingress, moveProgress);
  const scaffold = 0.38 + progress * 0.24;

  setDot(position, lerp(16, 18, progress), lerp(52, 72, progress), progress < 0.08 ? progress / 0.08 : 1, 0.12 + progress * 0.1);
  setOpacity(travelSpine, 0.2);
  setPathWindow(activeTrail, ROUTE_LENGTH, lerp(26, 118, moveProgress), 0.18);

  setOpacity(destinationGroup, scaffold);
  setOpacity(beamSlot, 0.32 + progress * 0.16);

  setOpacity(searchGuideA, clamp((progress - 0.32) / 0.22, 0, 1) * 0.24);
  setOpacity(searchGuideB, clamp((progress - 0.5) / 0.2, 0, 1) * 0.18);
  setOpacity(searchGuideC, clamp((progress - 0.68) / 0.16, 0, 1) * 0.1);
  setCandidateState(candidateA, points.candidateA, "faint", -10);
  setCandidateState(candidateB, points.candidateB, "faint", 0);
  setCandidateState(candidateC, points.candidateC, "faint", 10);
  setOpacity(candidateA, clamp((progress - 0.42) / 0.24, 0, 1) * 0.18);
  setOpacity(candidateB, clamp((progress - 0.56) / 0.2, 0, 1) * 0.12);
  setOpacity(candidateC, clamp((progress - 0.72) / 0.16, 0, 1) * 0.08);
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
  setOpacity(destinationGroup, 0.3);
  setOpacity(beamSlot, 0.16);

  setOpacity(searchGuideA, clamp((progress - 0.02) / 0.18, 0, 1) * 0.4);
  setOpacity(searchGuideB, clamp((progress - 0.26) / 0.18, 0, 1) * 0.38);
  setOpacity(searchGuideC, clamp((progress - 0.58) / 0.18, 0, 1) * 0.36);

  setCandidateState(candidateA, points.candidateA, progress < 0.28 ? "active" : "visited", -10);
  setCandidateState(candidateB, points.candidateB, progress < 0.22 ? "faint" : progress < 0.64 ? "active" : "visited", 0);
  setCandidateState(candidateC, points.candidateC, progress < 0.56 ? "faint" : progress < 0.9 ? "active" : "visited", 10);

  setOpacity(searchEchoA, clamp((progress - 0.18) / 0.12, 0, 1) * 0.46);
  setOpacity(searchEchoB, clamp((progress - 0.48) / 0.12, 0, 1) * 0.44);
  setOpacity(searchEchoC, clamp((progress - 0.78) / 0.12, 0, 1) * 0.42);
}

function renderTension(progress) {
  const squeeze = easeInOut(clamp((progress - 0.14) / 0.62, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.24, 0, 1));
  const topDrop = easeInOut(clamp((progress - 0.08) / 0.54, 0, 1));
  const settle = easeInOut(clamp(progress / 0.28, 0, 1));
  const tensionPoint = mixPoint(points.gate, points.tension, settle);
  const wheelCenterY = lerp(394, 410, settle);

  setDot(
    tensionPoint,
    lerp(18, 19, squeeze),
    lerp(72, 58, squeeze),
    1,
    0.22 + pulseWave(progress, 1.6) * 0.08,
    lerp(1, 0.56, squeeze),
    lerp(1, 1.7, squeeze),
  );
  setOpacity(travelSpine, 0.1 * residue);
  setPathWindow(activeTrail, ROUTE_LENGTH, lerp(760, 220, progress), 0.18 * residue);
  setOpacity(destinationGroup, 0.34);
  setOpacity(beamSlot, 0.18);

  setCandidateState(candidateA, points.candidateA, "visited", -10);
  setCandidateState(candidateB, points.candidateB, "visited", 0);
  setCandidateState(candidateC, points.candidateC, "visited", 10);
  setOpacity(candidateA, 0.18 * residue);
  setOpacity(candidateB, 0.16 * residue);
  setOpacity(candidateC, 0.14 * residue);
  setOpacity(searchEchoA, 0.16 * residue);
  setOpacity(searchEchoB, 0.14 * residue);
  setOpacity(searchEchoC, 0.12 * residue);
  setOpacity(searchGuideA, 0.12 * residue);
  setOpacity(searchGuideB, 0.1 * residue);
  setOpacity(searchGuideC, 0.08 * residue);

  setCircleCenter(pressureHalo, tensionPoint);
  setOpacity(pressureHalo, 0.16 + pulseWave(progress, 1.2) * 0.08);
  setOpacity(pressureLeft, 0.82);
  setOpacity(pressureRight, 0.82);
  setOpacity(pressureTop, 0.82);
  setOpacity(tensionGuide, 0.42);
  pressureLeft.setAttribute("cx", lerp(770, 792, squeeze).toFixed(2));
  pressureLeft.setAttribute("cy", wheelCenterY.toFixed(2));
  pressureRight.setAttribute("cx", lerp(870, 848, squeeze).toFixed(2));
  pressureRight.setAttribute("cy", wheelCenterY.toFixed(2));
  pressureTop.setAttribute(
    "transform",
    `translate(820 306) translate(0 ${lerp(0, 18, topDrop).toFixed(2)}) scale(${lerp(1, 0.8, squeeze).toFixed(3)} 1) translate(-820 -306)`,
  );
}

function renderTransformation(progress) {
  const tensionFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  const groupScale = lerp(0.95, 1, easeOut(clamp((progress - 0.08) / 0.42, 0, 1)));
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.16, from: points.tension, to: points.centerHub },
    { start: 0.16, end: 0.34, from: points.centerHub, to: points.leftWheel },
    { start: 0.34, end: 0.5, from: points.leftWheel, to: points.centerHub },
    { start: 0.5, end: 0.68, from: points.centerHub, to: points.rightWheel },
    { start: 0.68, end: 0.82, from: points.rightWheel, to: points.centerHub },
    { start: 0.82, end: 1, from: points.centerHub, to: points.final },
  ]);

  const centerUpProgress = clamp(progress / 0.18, 0, 1);
  const leftProgress = clamp((progress - 0.16) / 0.18, 0, 1);
  const rightProgress = clamp((progress - 0.5) / 0.18, 0, 1);
  const dropProgress = clamp((progress - 0.78) / 0.2, 0, 1);
  const structureProgress = clamp((progress - 0.1) / 0.42, 0, 1);
  const cableProgress = clamp((progress - 0.58) / 0.26, 0, 1);
  const returnProgress = clamp((progress - 0.42) / 0.28, 0, 1);

  setDot(position, lerp(19, 17, progress), lerp(56, 116, progress), 1, 0.24 + pulseWave(progress, 2.2) * 0.08);
  setOpacity(travelSpine, 0.08 * tensionFade);
  setPathWindow(activeTrail, ROUTE_LENGTH, 170, 0.14 * tensionFade);
  setOpacity(destinationGroup, 0.16 * (1 - structureProgress));
  setOpacity(beamSlot, 0.06 * (1 - structureProgress));

  setOpacity(pressureHalo, 0.18 * tensionFade);
  setOpacity(pressureLeft, 0.82 * tensionFade);
  setOpacity(pressureRight, 0.82 * tensionFade);
  setOpacity(pressureTop, 0.82 * tensionFade);
  setOpacity(tensionGuide, 0.4 * tensionFade);
  pressureLeft.setAttribute("cx", lerp(792, 770, structureProgress).toFixed(2));
  pressureLeft.setAttribute("cy", lerp(410, 394, structureProgress).toFixed(2));
  pressureRight.setAttribute("cx", lerp(848, 870, structureProgress).toFixed(2));
  pressureRight.setAttribute("cy", lerp(410, 394, structureProgress).toFixed(2));
  pressureTop.setAttribute(
    "transform",
    `translate(820 306) translate(0 ${lerp(18, 0, structureProgress).toFixed(2)}) scale(${lerp(0.8, 1, structureProgress).toFixed(3)} 1) translate(-820 -306)`,
  );

  setOpacity(pulleyGroup, 1);
  pulleyGroup.setAttribute(
    "transform",
    `translate(${points.final.x} ${points.final.y}) scale(${groupScale.toFixed(3)} ${groupScale.toFixed(3)}) translate(${-points.final.x} ${-points.final.y})`,
  );

  setOpacity(beamTop, structureProgress * 0.96);
  setOpacity(beamLeftDrop, structureProgress * 0.92);
  setOpacity(beamRightDrop, structureProgress * 0.92);
  setOpacity(pulleyLeftOuter, leftProgress * 0.94);
  setOpacity(pulleyLeftInner, clamp((progress - 0.26) / 0.14, 0, 1) * 0.58);
  setOpacity(pulleyRightOuter, rightProgress * 0.94);
  setOpacity(pulleyRightInner, clamp((progress - 0.6) / 0.14, 0, 1) * 0.58);
  setOpacity(hangingCable, cableProgress * 0.92);
  setOpacity(lowerBar, clamp((progress - 0.72) / 0.16, 0, 1) * 0.76);
  setOpacity(lowerLeftReturn, returnProgress * 0.5);
  setOpacity(lowerRightReturn, clamp((progress - 0.56) / 0.2, 0, 1) * 0.5);
  setOpacity(resolutionHalo, clamp((progress - 0.76) / 0.18, 0, 1) * 0.1);

  setOpacity(traceCenterUp, centerUpProgress * 0.9);
  applyStrokeReveal(traceCenterUp, centerUpProgress, TRACE_CENTER_UP_LENGTH);
  setOpacity(traceLeft, leftProgress * 0.9);
  applyStrokeReveal(traceLeft, leftProgress, TRACE_LEFT_LENGTH);
  setOpacity(traceRight, rightProgress * 0.9);
  applyStrokeReveal(traceRight, rightProgress, TRACE_RIGHT_LENGTH);
  setOpacity(traceDrop, dropProgress * 0.9);
  applyStrokeReveal(traceDrop, dropProgress, TRACE_DROP_LENGTH);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const haloPulse = 0.14 + pulseWave(progress, 1.5) * 0.06;
  const groupScale = lerp(1.012, 1, settle);

  setDot(points.final, 17, lerp(102, 80, progress), 1, haloPulse);
  setOpacity(travelSpine, 0);
  setPathWindow(activeTrail, ROUTE_LENGTH, 0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(beamSlot, 0);
  [pressureHalo, pressureLeft, pressureRight, pressureTop, tensionGuide].forEach((element) => setOpacity(element, 0));

  setOpacity(pulleyGroup, 1);
  pulleyGroup.setAttribute(
    "transform",
    `translate(${points.final.x} ${points.final.y}) scale(${groupScale.toFixed(3)} ${groupScale.toFixed(3)}) translate(${-points.final.x} ${-points.final.y})`,
  );
  [beamTop, beamLeftDrop, beamRightDrop, pulleyLeftOuter, pulleyRightOuter, hangingCable].forEach((element) => setOpacity(element, 0.96));
  [pulleyLeftInner, pulleyRightInner].forEach((element) => setOpacity(element, 0.42));
  setOpacity(lowerBar, 0.74);
  setOpacity(lowerLeftReturn, 0.34);
  setOpacity(lowerRightReturn, 0.34);
  setOpacity(resolutionHalo, 0.08);

  setOpacity(traceCenterUp, lerp(0.32, 0.12, settle));
  applyStrokeReveal(traceCenterUp, 1, TRACE_CENTER_UP_LENGTH);
  setOpacity(traceLeft, lerp(0.26, 0.08, settle));
  applyStrokeReveal(traceLeft, 1, TRACE_LEFT_LENGTH);
  setOpacity(traceRight, lerp(0.26, 0.08, settle));
  applyStrokeReveal(traceRight, 1, TRACE_RIGHT_LENGTH);
  setOpacity(traceDrop, lerp(0.34, 0.12, settle));
  applyStrokeReveal(traceDrop, 1, TRACE_DROP_LENGTH);
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
