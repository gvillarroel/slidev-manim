const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 6_500 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 9_500 },
];

const PHASE_STARTS = {};
let elapsedSeed = 0;
for (const phase of PHASES) {
  PHASE_STARTS[phase.id] = elapsedSeed;
  elapsedSeed += phase.duration;
}

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const entryLane = document.getElementById("entry-lane");
const activeTrail = document.getElementById("active-trail");
const glassLeftGuide = document.getElementById("glass-left-guide");
const glassRightGuide = document.getElementById("glass-right-guide");
const axisGuide = document.getElementById("axis-guide");
const topSlot = document.getElementById("top-slot");
const bottomSlot = document.getElementById("bottom-slot");
const waistGuide = document.getElementById("waist-guide");
const searchArcLeft = document.getElementById("search-arc-left");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcRight = document.getElementById("search-arc-right");
const searchArcReturn = document.getElementById("search-arc-return");
const candidateLeft = document.getElementById("candidate-left");
const candidateMid = document.getElementById("candidate-mid");
const candidateRight = document.getElementById("candidate-right");
const echoLeft = document.getElementById("echo-left");
const echoMid = document.getElementById("echo-mid");
const echoRight = document.getElementById("echo-right");
const waistLeft = document.getElementById("waist-left");
const waistRight = document.getElementById("waist-right");
const waistCapTop = document.getElementById("waist-cap-top");
const waistCapBottom = document.getElementById("waist-cap-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const hourglassGroup = document.getElementById("hourglass-group");
const traceUpperLeft = document.getElementById("trace-upper-left");
const traceUpperRight = document.getElementById("trace-upper-right");
const traceLowerLeft = document.getElementById("trace-lower-left");
const traceLowerRight = document.getElementById("trace-lower-right");
const glassLeft = document.getElementById("glass-left");
const glassRight = document.getElementById("glass-right");
const rimTop = document.getElementById("rim-top");
const rimBottom = document.getElementById("rim-bottom");
const pocketTop = document.getElementById("pocket-top");
const pocketBottom = document.getElementById("pocket-bottom");
const grainStream = document.getElementById("grain-stream");
const grainBed = document.getElementById("grain-bed");
const waistRing = document.getElementById("waist-ring");
const resolutionBrackets = document.getElementById("resolution-brackets");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TRACE_LENGTHS = new Map([
  [traceUpperLeft, traceUpperLeft.getTotalLength()],
  [traceUpperRight, traceUpperRight.getTotalLength()],
  [traceLowerLeft, traceLowerLeft.getTotalLength()],
  [traceLowerRight, traceLowerRight.getTotalLength()],
]);

const points = {
  start: { x: 290, y: 450 },
  appearanceSettle: { x: 520, y: 450 },
  searchLeft: { x: 706, y: 330 },
  searchMid: { x: 850, y: 300 },
  searchRight: { x: 956, y: 372 },
  waistApproach: { x: 804, y: 388 },
  waistCenter: { x: 850, y: 450 },
  lowerSettle: { x: 850, y: 548 },
};

const state = {
  playing: true,
  looping: true,
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

function setOpacity(element, value) {
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
}

function setCircleCenter(element, point) {
  element.setAttribute("cx", point.x.toFixed(2));
  element.setAttribute("cy", point.y.toFixed(2));
}

function setTransform(element, point, scaleX = 1, scaleY = 1, rotation = 0) {
  element.setAttribute(
    "transform",
    `translate(${point.x} ${point.y}) rotate(${rotation}) scale(${scaleX} ${scaleY}) translate(${-point.x} ${-point.y})`,
  );
}

function setGroupTransform(element, translateX = 0, translateY = 0, rotation = 0, origin = points.waistCenter) {
  element.setAttribute(
    "transform",
    `translate(${translateX.toFixed(2)} ${translateY.toFixed(2)}) rotate(${rotation.toFixed(2)} ${origin.x} ${origin.y})`,
  );
}

function setTrailWindow(visibleLength, opacity) {
  const clampedLength = clamp(visibleLength, 0, ACTIVE_TRAIL_LENGTH);
  activeTrail.style.strokeDasharray = `${clampedLength.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + 240).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = "0";
  setOpacity(activeTrail, opacity);
}

function setPathReveal(element, amount, opacity) {
  const length = TRACE_LENGTHS.get(element) ?? element.getTotalLength();
  element.style.strokeDasharray = `${length.toFixed(2)}`;
  element.style.strokeDashoffset = `${((1 - clamp(amount, 0, 1)) * length).toFixed(2)}`;
  setOpacity(element, opacity);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
    sceneRoot.setAttribute(
      "transform",
      "translate(800 450) scale(1.08) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
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

function updateLiveLabel(info) {
  phaseLabel.textContent = info.phase.label;
}

function applyDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1) {
  setCircleCenter(dotCore, position);
  setCircleCenter(dotHalo, position);
  dotCore.setAttribute("r", radius.toFixed(2));
  dotHalo.setAttribute("r", haloRadius.toFixed(2));
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  setTransform(dotCore, position, scaleX, scaleY);
  setTransform(dotHalo, position, scaleX, scaleY);
}

function resetScene() {
  applyDot(points.start, 18, 74, 0, 0);
  setOpacity(entryLane, 0);
  setTrailWindow(0, 0);

  [
    glassLeftGuide,
    glassRightGuide,
    axisGuide,
    topSlot,
    bottomSlot,
    waistGuide,
    searchArcLeft,
    searchArcMid,
    searchArcRight,
    searchArcReturn,
    candidateLeft,
    candidateMid,
    candidateRight,
    echoLeft,
    echoMid,
    echoRight,
    waistLeft,
    waistRight,
    waistCapTop,
    waistCapBottom,
    pressureHalo,
    hourglassGroup,
    glassLeft,
    glassRight,
    rimTop,
    rimBottom,
    pocketTop,
    pocketBottom,
    grainStream,
    grainBed,
    waistRing,
    resolutionBrackets,
    resolutionHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setPathReveal(traceUpperLeft, 0, 0);
  setPathReveal(traceUpperRight, 0, 0);
  setPathReveal(traceLowerLeft, 0, 0);
  setPathReveal(traceLowerRight, 0, 0);

  setGroupTransform(candidateLeft, 706, 330, -10, { x: 0, y: 0 });
  setGroupTransform(candidateMid, 850, 300, 0, { x: 0, y: 0 });
  setGroupTransform(candidateRight, 956, 372, 10, { x: 0, y: 0 });
  setGroupTransform(waistLeft, 850, 450, 0, { x: 0, y: 0 });
  setGroupTransform(waistRight, 850, 450, 0, { x: 0, y: 0 });
  setGroupTransform(hourglassGroup, 0, 0, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.appearanceSettle, eased * 0.88);
  const dotOpacity = 0.72 + clamp(progress * 0.28, 0, 0.28);
  const haloPulse = 0.16 + pulseWave(progress, 1.1) * 0.16;

  applyDot(position, lerp(14, 19, eased), lerp(56, 86, eased), dotOpacity, haloPulse * dotOpacity);
  setOpacity(entryLane, 0.22 + progress * 0.2);
  setTrailWindow(0, 0);

  setOpacity(glassLeftGuide, 0.3 + progress * 0.22);
  setOpacity(glassRightGuide, 0.3 + progress * 0.22);
  setOpacity(axisGuide, 0.22 + progress * 0.16);
  setOpacity(topSlot, 0.2 + progress * 0.14);
  setOpacity(bottomSlot, 0.2 + progress * 0.14);
  setOpacity(waistGuide, 0.12 + progress * 0.08);
  setOpacity(searchArcLeft, 0.16 + progress * 0.1);
  setOpacity(searchArcMid, 0.16 + progress * 0.1);
  setOpacity(searchArcRight, 0.16 + progress * 0.1);
  setOpacity(searchArcReturn, 0.14 + progress * 0.08);
  setOpacity(candidateLeft, 0.28 + progress * 0.22);
  setOpacity(candidateMid, 0.28 + progress * 0.22);
  setOpacity(candidateRight, 0.28 + progress * 0.22);
  setOpacity(waistLeft, 0.12 + progress * 0.08);
  setOpacity(waistRight, 0.12 + progress * 0.08);
  setOpacity(waistCapTop, 0.14 + progress * 0.08);
  setOpacity(waistCapBottom, 0.14 + progress * 0.08);

  setGroupTransform(waistLeft, 760, 450, 0);
  setGroupTransform(waistRight, 940, 450, 0);
}

function renderSearch(progress) {
  let position = points.searchLeft;
  let scaleX = 1;
  let scaleY = 1;
  const lateReturn = clamp((progress - 0.72) / 0.28, 0, 1);

  if (progress < 0.24) {
    const t = easeInOut(progress / 0.24);
    position = mixPoint(points.appearanceSettle, points.searchLeft, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.08, t);
  } else if (progress < 0.5) {
    const t = easeInOut((progress - 0.24) / 0.26);
    position = mixPoint(points.searchLeft, points.searchMid, t);
    scaleX = lerp(0.92, 1.08, t);
    scaleY = lerp(1.08, 0.92, t);
  } else if (progress < 0.72) {
    const t = easeInOut((progress - 0.5) / 0.22);
    position = mixPoint(points.searchMid, points.searchRight, t);
    scaleX = lerp(1.08, 0.96, t);
    scaleY = lerp(0.92, 1.12, t);
  } else {
    const t = easeInOut((progress - 0.72) / 0.28);
    position = mixPoint(points.searchRight, points.waistApproach, t);
    scaleX = lerp(0.96, 1.08, t);
    scaleY = lerp(1.12, 0.92, t);
  }

  applyDot(position, 19, 72, 1, 0.28 + pulseWave(progress, 2.1) * 0.16, scaleX, scaleY);
  setOpacity(entryLane, 0.22 - lateReturn * 0.14);
  setTrailWindow(110 + progress * 110, 0.42 - lateReturn * 0.34);

  setOpacity(glassLeftGuide, 0.42);
  setOpacity(glassRightGuide, 0.42);
  setOpacity(axisGuide, 0.32);
  setOpacity(topSlot, 0.34);
  setOpacity(bottomSlot, 0.18);
  setOpacity(waistGuide, 0.16 + lateReturn * 0.16);
  setOpacity(searchArcLeft, 0.62);
  setOpacity(searchArcMid, 0.62);
  setOpacity(searchArcRight, 0.62);
  setOpacity(searchArcReturn, 0.54);
  setOpacity(candidateLeft, 0.74);
  setOpacity(candidateMid, 0.74);
  setOpacity(candidateRight, 0.74);
  setOpacity(echoLeft, progress >= 0.28 ? 0.34 : 0);
  setOpacity(echoMid, progress >= 0.54 ? 0.32 : 0);
  setOpacity(echoRight, progress >= 0.8 ? 0.34 : 0);
  setOpacity(waistLeft, 0.12 + lateReturn * 0.08);
  setOpacity(waistRight, 0.12 + lateReturn * 0.08);
  setOpacity(waistCapTop, 0.16 + lateReturn * 0.08);
  setOpacity(waistCapBottom, 0.16 + lateReturn * 0.08);

  setGroupTransform(waistLeft, 760, 450, 0);
  setGroupTransform(waistRight, 940, 450, 0);
}

function renderTension(progress) {
  const moveIn = progress < 0.24
    ? mixPoint(points.waistApproach, points.waistCenter, easeInOut(progress / 0.24))
    : progress < 0.8
      ? points.waistCenter
      : mixPoint(points.waistCenter, mixPoint(points.waistCenter, points.lowerSettle, 0.18), easeInOut((progress - 0.8) / 0.2));
  const squeeze = progress < 0.24
    ? easeOut(progress / 0.24)
    : progress < 0.76
      ? 1
      : 1 - easeInOut((progress - 0.76) / 0.24);
  const pulse = progress > 0.28 && progress < 0.72 ? (pulseWave((progress - 0.28) / 0.44, 2.6) - 0.5) * 10 : 0;
  const leftShift = lerp(-90, -24, squeeze) + pulse * 0.22;
  const rightShift = lerp(90, 24, squeeze) - pulse * 0.22;
  const braceOffset = lerp(0, 22, squeeze);
  const residue = 1 - easeOut(clamp((progress - 0.04) / 0.34, 0, 1));
  const trailFade = 1 - easeOut(clamp((progress - 0.16) / 0.28, 0, 1));

  applyDot(
    moveIn,
    19,
    lerp(82, 112, squeeze),
    1,
    0.34 + squeeze * 0.18,
    lerp(1.02, 0.66, squeeze),
    lerp(0.98, 1.76, squeeze),
  );
  setOpacity(entryLane, 0.08 * residue);
  setTrailWindow(434 + progress * 100, 0.56 * trailFade);

  setOpacity(glassLeftGuide, 0.22 * residue);
  setOpacity(glassRightGuide, 0.22 * residue);
  setOpacity(axisGuide, 0.16 * residue);
  setOpacity(topSlot, 0.12 * residue);
  setOpacity(bottomSlot, 0.12 * residue);
  setOpacity(waistGuide, 0.1 * residue);
  setOpacity(searchArcLeft, 0.12 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcRight, 0.12 * residue);
  setOpacity(searchArcReturn, 0.1 * residue);
  setOpacity(candidateLeft, 0.14 * residue);
  setOpacity(candidateMid, 0.14 * residue);
  setOpacity(candidateRight, 0.14 * residue);
  setOpacity(echoLeft, 0.16 * residue);
  setOpacity(echoMid, 0.16 * residue);
  setOpacity(echoRight, 0.16 * residue);

  setOpacity(waistLeft, 1);
  setOpacity(waistRight, 1);
  setOpacity(waistCapTop, 0.68);
  setOpacity(waistCapBottom, 0.68);
  setOpacity(pressureHalo, 0.3 + squeeze * 0.18);
  setGroupTransform(waistLeft, 850 + leftShift, 450, 0);
  setGroupTransform(waistRight, 850 + rightShift, 450, 0);
  waistCapTop.setAttribute("d", `M ${(794 - braceOffset).toFixed(2)} 344 H ${(906 + braceOffset).toFixed(2)}`);
  waistCapBottom.setAttribute("d", `M ${(794 - braceOffset).toFixed(2)} 556 H ${(906 + braceOffset).toFixed(2)}`);
}

function renderTransformation(progress) {
  const dotPosition = progress < 0.26
    ? mixPoint(points.waistCenter, points.lowerSettle, easeInOut(progress / 0.26))
    : points.lowerSettle;
  const traceGrow = clamp((progress - 0.06) / 0.62, 0, 1);
  const glassGrow = clamp((progress - 0.24) / 0.38, 0, 1);
  const pocketGrow = clamp((progress - 0.44) / 0.28, 0, 1);
  const settleTurn = lerp(4, -2, easeOut(progress));
  const corridorResidue = 1 - easeOut(clamp(progress / 0.16, 0, 1));

  applyDot(dotPosition, lerp(19, 17, progress), lerp(96, 118, traceGrow), 1, 0.26 + pulseWave(progress, 2.2) * 0.12);
  setTrailWindow(220, 0.14 * corridorResidue);
  setOpacity(waistLeft, 0.14 * corridorResidue);
  setOpacity(waistRight, 0.14 * corridorResidue);
  setOpacity(waistCapTop, 0.12 * corridorResidue);
  setOpacity(waistCapBottom, 0.12 * corridorResidue);
  setOpacity(pressureHalo, 0.1 * corridorResidue);

  setOpacity(hourglassGroup, 1);
  setGroupTransform(hourglassGroup, 0, 0, settleTurn);
  setPathReveal(traceUpperLeft, clamp(traceGrow * 1.12, 0, 1), 0.94);
  setPathReveal(traceUpperRight, clamp((traceGrow - 0.08) * 1.2, 0, 1), 0.94);
  setPathReveal(traceLowerLeft, clamp((traceGrow - 0.22) * 1.34, 0, 1), 0.94);
  setPathReveal(traceLowerRight, clamp((traceGrow - 0.3) * 1.5, 0, 1), 0.94);
  setOpacity(glassLeft, 0.22 + glassGrow * 0.22);
  setOpacity(glassRight, 0.22 + glassGrow * 0.22);
  setOpacity(rimTop, 0.18 + glassGrow * 0.2);
  setOpacity(rimBottom, 0.18 + glassGrow * 0.2);
  setOpacity(pocketTop, 0.16 + pocketGrow * 0.18);
  setOpacity(pocketBottom, 0.16 + pocketGrow * 0.18);
  setOpacity(grainStream, clamp((progress - 0.34) / 0.24, 0, 1) * 0.6);
  setOpacity(grainBed, clamp((progress - 0.56) / 0.18, 0, 1) * 0.48);
  setOpacity(waistRing, 0.14 + glassGrow * 0.18);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const turn = lerp(-2, 0, settle);
  const traceFade = 1 - easeOut(clamp(progress / 0.42, 0, 1));
  const bracketIn = clamp((progress - 0.24) / 0.38, 0, 1);

  applyDot(points.lowerSettle, 17, lerp(116, 82, progress), 1, 0.2 + pulseWave(progress, 1.5) * 0.08);
  setTrailWindow(0, 0);
  setOpacity(hourglassGroup, 1);
  setGroupTransform(hourglassGroup, 0, 0, turn);
  setOpacity(glassLeft, 0.4);
  setOpacity(glassRight, 0.4);
  setOpacity(rimTop, 0.36);
  setOpacity(rimBottom, 0.36);
  setOpacity(pocketTop, 0.28);
  setOpacity(pocketBottom, 0.3);
  setOpacity(grainStream, 0.2);
  setOpacity(grainBed, 0.32);
  setOpacity(waistRing, 0.3);
  setPathReveal(traceUpperLeft, 1, 0.2 * traceFade);
  setPathReveal(traceUpperRight, 1, 0.2 * traceFade);
  setPathReveal(traceLowerLeft, 1, 0.18 * traceFade);
  setPathReveal(traceLowerRight, 1, 0.18 * traceFade);
  setOpacity(resolutionHalo, 0.3);
  setOpacity(resolutionBrackets, 0.2 + bracketIn * 0.34);
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

  svg.dataset.phase = info.phase.id;
  updateLiveLabel(info);
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

function freezeOnPhase(id) {
  const phase = PHASES.find((item) => item.id === id);
  if (!phase) return;
  state.elapsedBeforePause = PHASE_STARTS[id] + phase.duration * 0.72;
  state.currentElapsed = state.elapsedBeforePause;
  state.startAt = performance.now();
  render(state.currentElapsed);
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

const requestedPhase = new URLSearchParams(window.location.search).get("phase");
if (requestedPhase && PHASE_STARTS[requestedPhase] !== undefined) {
  freezeOnPhase(requestedPhase);
  state.elapsedBeforePause = state.currentElapsed;
  setPlaying(false);
}

window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
