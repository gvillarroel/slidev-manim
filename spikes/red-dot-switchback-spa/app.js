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
const candidateStep = document.getElementById("candidate-step");
const candidateElbow = document.getElementById("candidate-elbow");
const candidateSwitch = document.getElementById("candidate-switch");
const corridorGuide = document.getElementById("corridor-guide");
const centerGuide = document.getElementById("center-guide");
const pressureHalo = document.getElementById("pressure-halo");
const gateLeft = document.getElementById("gate-left");
const gateTop = document.getElementById("gate-top");
const gateRight = document.getElementById("gate-right");
const gateMid = document.getElementById("gate-mid");
const switchShell = document.getElementById("switch-shell");
const switchBase = document.getElementById("switch-base");
const switchTrace = document.getElementById("switch-trace");
const innerBase = document.getElementById("inner-base");
const innerTrace = document.getElementById("inner-trace");
const turnSlotTop = document.getElementById("turn-slot-top");
const turnSlotMid = document.getElementById("turn-slot-mid");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const SWITCH_TRACE_LENGTH = switchTrace.getTotalLength();
const INNER_TRACE_LENGTH = innerTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 316, y: 450 },
  ingress: { x: 566, y: 450 },
  stepCandidate: { x: 680, y: 394 },
  elbowCandidate: { x: 852, y: 336 },
  switchCandidate: { x: 1010, y: 402 },
  pocketApproach: { x: 922, y: 430 },
  pocketCorner: { x: 842, y: 430 },
  pocketRelease: { x: 842, y: 450 },
  resolution: { x: 846, y: 450 },
};

const gates = {
  left: { x: 780, y: 430 },
  top: { x: 846, y: 326 },
  right: { x: 946, y: 390 },
  mid: { x: 852, y: 450 },
  squeezeLeft: { x: 812, y: 430 },
  squeezeTop: { x: 850, y: 352 },
  squeezeRight: { x: 914, y: 390 },
  squeezeMid: { x: 838, y: 450 },
};

const slots = {
  top: { x: 942, y: 322 },
  mid: { x: 792, y: 470 },
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

function pointOnSwitch(progress) {
  const length = clamp(progress, 0, 1) * SWITCH_TRACE_LENGTH;
  const point = switchTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
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
    appearance: { x: 16, y: 10 },
    search: { x: 0, y: 24 },
    tension: { x: 0, y: 10 },
    transformation: { x: 0, y: -2 },
    resolution: { x: 0, y: -6 },
  };
  const offset = offsets[phaseId] ?? { x: 0, y: 0 };
  sceneRoot.setAttribute("transform", `translate(${offset.x} ${offset.y})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 132, y: 142, width: 1100, height: 640 },
    search: { x: 148, y: 118, width: 1128, height: 666 },
    tension: { x: 372, y: 142, width: 918, height: 636 },
    transformation: { x: 356, y: 104, width: 934, height: 692 },
    resolution: { x: 420, y: 86, width: 864, height: 736 },
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
}

function resetScene() {
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);
  [searchGuideA, searchGuideB, searchGuideC].forEach((element) => {
    element.setAttribute("stroke", COLORS.lineGray);
    setOpacity(element, 0);
  });

  setGroupTransform(candidateStep, points.stepCandidate.x, points.stepCandidate.y, 1, -4);
  setGroupTransform(candidateElbow, points.elbowCandidate.x, points.elbowCandidate.y, 1, 0);
  setGroupTransform(candidateSwitch, points.switchCandidate.x, points.switchCandidate.y, 1, 4);
  [candidateStep, candidateElbow, candidateSwitch].forEach((element) => setOpacity(element, 0));

  setOpacity(corridorGuide, 0);
  setOpacity(centerGuide, 0);
  setOpacity(pressureHalo, 0);
  setGroupTransform(gateLeft, gates.left.x, gates.left.y, 1, 0);
  setGroupTransform(gateTop, gates.top.x, gates.top.y, 1, 0);
  setGroupTransform(gateRight, gates.right.x, gates.right.y, 1, 0);
  setGroupTransform(gateMid, gates.mid.x, gates.mid.y, 1, 0);
  [gateLeft, gateTop, gateRight, gateMid].forEach((element) => setOpacity(element, 0));

  setOpacity(switchShell, 0);
  setOpacity(switchBase, 0);
  setPathWindow(switchTrace, SWITCH_TRACE_LENGTH, 0, 0);
  setOpacity(innerBase, 0);
  setPathWindow(innerTrace, INNER_TRACE_LENGTH, 0, 0);
  setGroupTransform(turnSlotTop, slots.top.x, slots.top.y, 1, 0);
  setGroupTransform(turnSlotMid, slots.mid.x, slots.mid.y, 1, 0);
  setOpacity(turnSlotTop, 0);
  setOpacity(turnSlotMid, 0);
  setOpacity(anchorGrid, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
  setDot(points.start, 18, 76, 0, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.8);

  setDot(
    position,
    lerp(5, 18, eased),
    lerp(20, 86, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.2) * 0.16,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.1) * 1.5, 0, 0.32));

  const preview = clamp((progress - 0.34) * 1.9, 0, 1);
  setOpacity(searchGuideA, preview * 0.24);
  setOpacity(searchGuideB, preview * 0.16);
  setOpacity(searchGuideC, preview * 0.12);
  setOpacity(candidateStep, preview * 0.18);
  setOpacity(candidateElbow, preview * 0.14);
  setOpacity(candidateSwitch, preview * 0.1);
  setOpacity(corridorGuide, preview * 0.08);
  setOpacity(centerGuide, preview * 0.05);
  setOpacity(switchShell, preview * 0.05);
  setOpacity(switchBase, preview * 0.07);
  setOpacity(innerBase, preview * 0.05);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.stepCandidate },
    { start: 0.28, end: 0.58, from: points.stepCandidate, to: points.elbowCandidate },
    { start: 0.58, end: 0.84, from: points.elbowCandidate, to: points.switchCandidate },
    { start: 0.84, end: 1, from: points.switchCandidate, to: points.pocketApproach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.7) * 0.1);
  setOpacity(narrativeSpine, lerp(0.22, 0.06, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.04, progress));

  const revealA = clamp(progress / 0.24, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.24, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.24 + revealA * 0.18);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateStep, points.stepCandidate.x, points.stepCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateElbow, points.elbowCandidate.x, points.elbowCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateSwitch, points.switchCandidate.x, points.switchCandidate.y, lerp(0.84, activeC ? 1.04 : 0.94, revealC), 4);
  setOpacity(candidateStep, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateElbow, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateSwitch, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(corridorGuide, 0.12);
  setOpacity(centerGuide, 0.08);
  setOpacity(switchShell, 0.05);
  setOpacity(switchBase, 0.08);
  setOpacity(innerBase, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.38, 0, 1);
  const bend = clamp(progress / 0.78, 0, 1);
  const position = progress < 0.42
    ? mixPoint(points.pocketApproach, points.pocketCorner, easeInOut(travel))
    : mixPoint(points.pocketCorner, points.pocketRelease, easeInOut(clamp((progress - 0.42) / 0.24, 0, 1)));
  const compression = Math.sin(bend * Math.PI);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 124, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.54, compression),
    lerp(1, 1.84, compression),
  );
  setOpacity(narrativeSpine, lerp(0.1, 0.03, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.08, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  setGroupTransform(candidateStep, lerp(points.stepCandidate.x, 728, bend), lerp(points.stepCandidate.y, 404, bend), lerp(0.96, 0.72, bend), -6);
  setGroupTransform(candidateElbow, lerp(points.elbowCandidate.x, 816, bend), lerp(points.elbowCandidate.y, 352, bend), lerp(0.96, 0.72, bend), 0);
  setGroupTransform(candidateSwitch, lerp(points.switchCandidate.x, 912, bend), lerp(points.switchCandidate.y, 390, bend), lerp(0.95, 0.68, bend), 6);
  setOpacity(candidateStep, lerp(0.26, 0.05, bend));
  setOpacity(candidateElbow, lerp(0.28, 0.05, bend));
  setOpacity(candidateSwitch, lerp(1, 0.12, bend));

  setOpacity(corridorGuide, clamp((progress - 0.02) * 1.7, 0, 0.86));
  setOpacity(centerGuide, clamp((progress - 0.04) * 1.6, 0, 0.84));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(gateLeft, lerp(gates.left.x, gates.squeezeLeft.x, easeInOut(bend)), gates.left.y, 1, 0);
  setGroupTransform(gateTop, gates.top.x, lerp(gates.top.y, gates.squeezeTop.y, easeInOut(bend)), 1, 0);
  setGroupTransform(gateRight, lerp(gates.right.x, gates.squeezeRight.x, easeInOut(bend)), gates.right.y, 1, 0);
  setGroupTransform(gateMid, lerp(gates.mid.x, gates.squeezeMid.x, easeInOut(bend)), gates.mid.y, 1, 0);
  [gateLeft, gateTop, gateRight, gateMid].forEach((element) => setOpacity(element, clamp((progress - 0.04) * 1.7, 0, 0.98)));

  setOpacity(switchShell, clamp((progress - 0.5) * 0.42, 0, 0.16));
  setOpacity(switchBase, clamp((progress - 0.56) * 0.44, 0, 0.18));
  setOpacity(innerBase, clamp((progress - 0.62) * 0.44, 0, 0.14));
  setOpacity(turnSlotTop, clamp((progress - 0.54) * 1.2, 0, 0.24));
  setOpacity(turnSlotMid, clamp((progress - 0.68) * 1.2, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.86, 0, 1));
  const position = pointOnSwitch(routeProgress);
  const innerProgress = clamp((routeProgress - 0.46) / 0.34, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, clamp(0.06 - progress * 0.16, 0, 0.06));

  [searchGuideA, searchGuideB, searchGuideC, candidateStep, candidateElbow, candidateSwitch].forEach((element) => setOpacity(element, 0));
  setOpacity(corridorGuide, lerp(0.86, 0.1, progress));
  setOpacity(centerGuide, lerp(0.84, 0.1, progress));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 0.42));
  [gateLeft, gateTop, gateRight, gateMid].forEach((element) => setOpacity(element, clamp(1 - progress * 1.15, 0, 1)));

  setOpacity(switchShell, lerp(0.24, 0.98, routeProgress));
  setOpacity(switchBase, lerp(0.16, 0.34, routeProgress));
  setPathWindow(switchTrace, SWITCH_TRACE_LENGTH, SWITCH_TRACE_LENGTH * routeProgress, 1);
  setOpacity(innerBase, clamp((progress - 0.32) * 1.2, 0, 0.26));
  setPathWindow(innerTrace, INNER_TRACE_LENGTH, INNER_TRACE_LENGTH * innerProgress, 0.72 * innerProgress);
  setOpacity(turnSlotTop, clamp((0.34 - progress) * 1.3, 0, 0.24));
  setOpacity(turnSlotMid, clamp((0.6 - progress) * 1.1, 0, 0.24));

  setOpacity(anchorGrid, clamp((progress - 0.7) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.18));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.resolution, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);

  [
    searchGuideA,
    searchGuideB,
    searchGuideC,
    candidateStep,
    candidateElbow,
    candidateSwitch,
    corridorGuide,
    centerGuide,
    pressureHalo,
    gateLeft,
    gateTop,
    gateRight,
    gateMid,
    turnSlotTop,
    turnSlotMid,
  ].forEach((element) => setOpacity(element, 0));

  setOpacity(switchShell, lerp(0.98, 0.92, settle));
  setOpacity(switchBase, lerp(0.34, 0.28, settle));
  setPathWindow(switchTrace, SWITCH_TRACE_LENGTH, SWITCH_TRACE_LENGTH, lerp(1, 0.16, settle));
  setOpacity(innerBase, lerp(0.26, 0.3, settle));
  setPathWindow(innerTrace, INNER_TRACE_LENGTH, INNER_TRACE_LENGTH, lerp(0.72, 0.2, settle));
  setOpacity(anchorGrid, lerp(0.12, 0.16, settle));
  setOpacity(resolutionHalo, lerp(0.18, 0.28, settle));
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
