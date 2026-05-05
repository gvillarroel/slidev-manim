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
const hubGuide = document.getElementById("hub-guide");
const hubAxis = document.getElementById("hub-axis");
const hubCross = document.getElementById("hub-cross");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");
const candidateTop = document.getElementById("candidate-top");
const candidateMid = document.getElementById("candidate-mid");
const candidateBottom = document.getElementById("candidate-bottom");
const echoTop = document.getElementById("echo-top");
const echoMid = document.getElementById("echo-mid");
const echoBottom = document.getElementById("echo-bottom");
const throatAxis = document.getElementById("throat-axis");
const throatLeft = document.getElementById("throat-left");
const throatRight = document.getElementById("throat-right");
const throatBraceTop = document.getElementById("throat-brace-top");
const throatBraceBottom = document.getElementById("throat-brace-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const turbineGroup = document.getElementById("turbine-group");
const traceTop = document.getElementById("trace-top");
const traceRight = document.getElementById("trace-right");
const traceBottom = document.getElementById("trace-bottom");
const bladeTop = document.getElementById("blade-top");
const bladeRight = document.getElementById("blade-right");
const bladeBottom = document.getElementById("blade-bottom");
const innerTop = document.getElementById("inner-top");
const innerRight = document.getElementById("inner-right");
const innerBottom = document.getElementById("inner-bottom");
const hubShell = document.getElementById("hub-shell");
const hubRing = document.getElementById("hub-ring");
const outerArcTop = document.getElementById("outer-arc-top");
const outerArcBottom = document.getElementById("outer-arc-bottom");
const resolutionBrackets = document.getElementById("resolution-brackets");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TRACE_LENGTHS = new Map([
  [traceTop, traceTop.getTotalLength()],
  [traceRight, traceRight.getTotalLength()],
  [traceBottom, traceBottom.getTotalLength()],
]);

const points = {
  start: { x: 290, y: 450 },
  appearanceSettle: { x: 392, y: 450 },
  searchTop: { x: 734, y: 328 },
  searchMid: { x: 848, y: 392 },
  searchBottom: { x: 770, y: 554 },
  throatEntry: { x: 760, y: 450 },
  throatCenter: { x: 872, y: 450 },
  hub: { x: 850, y: 450 },
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

function setGroupTransform(element, translateX = 0, translateY = 0, rotation = 0, origin = points.hub) {
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
    sceneRoot.setAttribute(
      "transform",
      "translate(0 -68) translate(800 450) scale(1.18) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
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
    hubGuide,
    hubAxis,
    hubCross,
    searchArcTop,
    searchArcMid,
    searchArcBottom,
    candidateTop,
    candidateMid,
    candidateBottom,
    echoTop,
    echoMid,
    echoBottom,
    throatAxis,
    throatLeft,
    throatRight,
    throatBraceTop,
    throatBraceBottom,
    pressureHalo,
    turbineGroup,
    bladeTop,
    bladeRight,
    bladeBottom,
    innerTop,
    innerRight,
    innerBottom,
    hubShell,
    hubRing,
    outerArcTop,
    outerArcBottom,
    resolutionBrackets,
    resolutionHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setPathReveal(traceTop, 0, 0);
  setPathReveal(traceRight, 0, 0);
  setPathReveal(traceBottom, 0, 0);

  setGroupTransform(candidateTop, 734, 328, 0, { x: 0, y: 0 });
  setGroupTransform(candidateMid, 848, 392, 0, { x: 0, y: 0 });
  setGroupTransform(candidateBottom, 734, 572, 0, { x: 0, y: 0 });
  setGroupTransform(throatLeft, 872, 450, 0, { x: 0, y: 0 });
  setGroupTransform(throatRight, 872, 450, 0, { x: 0, y: 0 });
  setGroupTransform(turbineGroup, 0, 0, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const dotOpacity = 0.72 + clamp(progress * 0.32, 0, 0.28);
  const haloPulse = 0.16 + pulseWave(progress, 1.1) * 0.16;
  const position = mixPoint(points.start, points.appearanceSettle, eased * 0.86);

  applyDot(position, lerp(14, 19, eased), lerp(56, 86, eased), dotOpacity, haloPulse * dotOpacity);
  setOpacity(entryLane, 0.2 + progress * 0.2);
  setTrailWindow(0, 0);

  setOpacity(hubGuide, 0.28 + progress * 0.2);
  setOpacity(hubAxis, 0.22 + progress * 0.18);
  setOpacity(hubCross, 0.1 + progress * 0.09);
  setOpacity(searchArcTop, 0.18 + progress * 0.12);
  setOpacity(searchArcMid, 0.16 + progress * 0.1);
  setOpacity(searchArcBottom, 0.18 + progress * 0.12);
  setOpacity(candidateTop, 0.26 + progress * 0.22);
  setOpacity(candidateMid, 0.24 + progress * 0.2);
  setOpacity(candidateBottom, 0.26 + progress * 0.22);
  setOpacity(throatAxis, 0.14 + progress * 0.06);
  setOpacity(throatLeft, 0.08 + progress * 0.06);
  setOpacity(throatRight, 0.08 + progress * 0.06);
  setOpacity(throatBraceTop, 0.12 + progress * 0.06);
  setOpacity(throatBraceBottom, 0.12 + progress * 0.06);
  setGroupTransform(throatLeft, 776, 450, -6);
  setGroupTransform(throatRight, 968, 450, 6);
}

function renderSearch(progress) {
  let position = points.searchTop;
  let scaleX = 1;
  let scaleY = 1;

  if (progress < 0.24) {
    const t = easeInOut(progress / 0.24);
    position = mixPoint(points.appearanceSettle, points.searchTop, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.08, t);
  } else if (progress < 0.5) {
    const t = easeInOut((progress - 0.24) / 0.26);
    position = mixPoint(points.searchTop, points.searchMid, t);
    scaleX = lerp(0.92, 1.08, t);
    scaleY = lerp(1.08, 0.92, t);
  } else if (progress < 0.72) {
    const t = easeInOut((progress - 0.5) / 0.22);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    scaleX = lerp(1.08, 0.96, t);
    scaleY = lerp(0.92, 1.12, t);
  } else {
    const t = easeInOut((progress - 0.72) / 0.28);
    position = mixPoint(points.searchBottom, points.throatEntry, t);
    scaleX = lerp(0.96, 1.08, t);
    scaleY = lerp(1.12, 0.92, t);
  }

  applyDot(position, 19, 72, 1, 0.28 + pulseWave(progress, 2.2) * 0.15, scaleX, scaleY);
  setOpacity(entryLane, 0.28);
  setTrailWindow(156 + progress * 160, 0.74 - clamp((progress - 0.68) / 0.32, 0, 1) * 0.18);

  setOpacity(hubGuide, 0.36);
  setOpacity(hubAxis, 0.28);
  setOpacity(hubCross, 0.12);
  setOpacity(searchArcTop, 0.62);
  setOpacity(searchArcMid, 0.62);
  setOpacity(searchArcBottom, 0.62);
  setOpacity(candidateTop, 0.72);
  setOpacity(candidateMid, 0.72);
  setOpacity(candidateBottom, 0.72);
  setOpacity(echoTop, progress >= 0.3 ? 0.38 : 0);
  setOpacity(echoMid, progress >= 0.56 ? 0.34 : 0);
  setOpacity(echoBottom, progress >= 0.82 ? 0.38 : 0);
  setOpacity(throatAxis, 0.18);
  setOpacity(throatLeft, 0.12);
  setOpacity(throatRight, 0.12);
  setOpacity(throatBraceTop, 0.16);
  setOpacity(throatBraceBottom, 0.16);
  setGroupTransform(throatLeft, 776, 450, -6);
  setGroupTransform(throatRight, 968, 450, 6);
}

function renderTension(progress) {
  const moveIn = progress < 0.26
    ? mixPoint(points.throatEntry, points.throatCenter, easeInOut(progress / 0.26))
    : progress < 0.78
      ? points.throatCenter
      : mixPoint(points.throatCenter, points.hub, easeInOut((progress - 0.78) / 0.22));
  const squeeze = progress < 0.26
    ? easeOut(progress / 0.26)
    : progress < 0.76
      ? 1
      : 1 - easeInOut((progress - 0.76) / 0.24);
  const pulse = progress > 0.28 && progress < 0.72 ? (pulseWave((progress - 0.28) / 0.44, 2.4) - 0.5) * 10 : 0;
  const leftShift = lerp(-96, -34, squeeze) + pulse * 0.2;
  const rightShift = lerp(96, 34, squeeze) - pulse * 0.2;
  const braceOffset = lerp(0, 26, squeeze);
  const residue = 1 - easeOut(clamp((progress - 0.06) / 0.36, 0, 1));
  const trailFade = 1 - easeOut(clamp((progress - 0.18) / 0.32, 0, 1));

  applyDot(moveIn, 19, lerp(78, 106, squeeze), 1, 0.34 + squeeze * 0.16, lerp(1.02, 1.84, squeeze), lerp(0.98, 0.68, squeeze));
  setOpacity(entryLane, 0.08 * residue);
  setTrailWindow(430 + progress * 100, 0.56 * trailFade);

  setOpacity(hubGuide, 0.22 * residue);
  setOpacity(hubAxis, 0.16 * residue);
  setOpacity(hubCross, 0.08 * residue);
  setOpacity(searchArcTop, 0.12 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcBottom, 0.12 * residue);
  setOpacity(candidateTop, 0.14 * residue);
  setOpacity(candidateMid, 0.12 * residue);
  setOpacity(candidateBottom, 0.14 * residue);
  setOpacity(echoTop, 0.16 * residue);
  setOpacity(echoMid, 0.14 * residue);
  setOpacity(echoBottom, 0.16 * residue);

  setOpacity(throatAxis, 0.5);
  setOpacity(throatLeft, 1);
  setOpacity(throatRight, 1);
  setOpacity(throatBraceTop, 0.66);
  setOpacity(throatBraceBottom, 0.66);
  setOpacity(pressureHalo, 0.3 + squeeze * 0.16);
  setGroupTransform(throatLeft, 872 + leftShift, 450, -6);
  setGroupTransform(throatRight, 872 + rightShift, 450, 6);
  throatBraceTop.setAttribute("d", `M ${(806 - braceOffset).toFixed(2)} 342 H ${(938 + braceOffset).toFixed(2)}`);
  throatBraceBottom.setAttribute("d", `M ${(806 - braceOffset).toFixed(2)} 558 H ${(938 + braceOffset).toFixed(2)}`);
}

function renderTransformation(progress) {
  const entry = progress < 0.2 ? mixPoint(points.throatCenter, points.hub, easeOut(progress / 0.2)) : points.hub;
  const systemShift = lerp(0, -36, easeOut(clamp((progress - 0.18) / 0.74, 0, 1)));
  const traceGrow = clamp((progress - 0.1) / 0.66, 0, 1);
  const bladesGrow = clamp((progress - 0.34) / 0.42, 0, 1);
  const innerGrow = clamp((progress - 0.52) / 0.28, 0, 1);
  const rotorTurn = lerp(10, -12, easeOut(progress));
  const dotPosition = { x: entry.x + systemShift, y: entry.y };
  const corridorResidue = 1 - easeOut(clamp(progress / 0.18, 0, 1));

  applyDot(dotPosition, lerp(19, 17, progress), lerp(94, 120, traceGrow), 1, 0.26 + pulseWave(progress, 2.2) * 0.12);
  setOpacity(entryLane, 0);
  setTrailWindow(220, 0.14 * corridorResidue);
  setOpacity(throatAxis, 0.14 * corridorResidue);
  setOpacity(throatLeft, 0.12 * corridorResidue);
  setOpacity(throatRight, 0.12 * corridorResidue);
  setOpacity(throatBraceTop, 0.12 * corridorResidue);
  setOpacity(throatBraceBottom, 0.12 * corridorResidue);
  setOpacity(pressureHalo, 0.1 * corridorResidue);

  setOpacity(turbineGroup, 1);
  setGroupTransform(turbineGroup, systemShift, 0, rotorTurn);
  setOpacity(hubShell, 0.22 + traceGrow * 0.18);
  setOpacity(hubRing, 0.16 + traceGrow * 0.18);
  setOpacity(outerArcTop, 0.2 + innerGrow * 0.18);
  setOpacity(outerArcBottom, 0.18 + innerGrow * 0.16);
  setPathReveal(traceTop, clamp(traceGrow * 1.08, 0, 1), 0.92);
  setPathReveal(traceRight, clamp((traceGrow - 0.14) * 1.2, 0, 1), 0.92);
  setPathReveal(traceBottom, clamp((traceGrow - 0.3) * 1.5, 0, 1), 0.92);
  setOpacity(bladeTop, bladesGrow);
  setOpacity(bladeRight, clamp(bladesGrow - 0.08, 0, 1));
  setOpacity(bladeBottom, clamp(bladesGrow - 0.18, 0, 1));
  setOpacity(innerTop, innerGrow);
  setOpacity(innerRight, clamp(innerGrow - 0.1, 0, 1));
  setOpacity(innerBottom, clamp(innerGrow - 0.2, 0, 1));
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(-36, 0, settle);
  const turn = lerp(-12, 0, settle);
  const traceFade = 1 - easeOut(clamp(progress / 0.44, 0, 1));
  const bracketIn = clamp((progress - 0.24) / 0.4, 0, 1);

  applyDot(points.hub, 17, lerp(118, 86, progress), 1, 0.22 + pulseWave(progress, 1.6) * 0.08);
  setTrailWindow(0, 0);
  setOpacity(turbineGroup, 1);
  setGroupTransform(turbineGroup, shift, 0, turn);

  setOpacity(hubShell, 0.38);
  setOpacity(hubRing, 0.3);
  setOpacity(bladeTop, 1);
  setOpacity(bladeRight, 1);
  setOpacity(bladeBottom, 1);
  setOpacity(innerTop, 0.42);
  setOpacity(innerRight, 0.38);
  setOpacity(innerBottom, 0.34);
  setOpacity(outerArcTop, 0.42);
  setOpacity(outerArcBottom, 0.36);
  setPathReveal(traceTop, 1, 0.22 * traceFade);
  setPathReveal(traceRight, 1, 0.2 * traceFade);
  setPathReveal(traceBottom, 1, 0.18 * traceFade);
  setOpacity(resolutionHalo, 0.32);
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
