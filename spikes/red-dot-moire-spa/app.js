const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 6_500 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 9_500 },
];

const PHASE_STARTS = {};
let phaseSeed = 0;
for (const phase of PHASES) {
  PHASE_STARTS[phase.id] = phaseSeed;
  phaseSeed += phase.duration;
}

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const entryLane = document.getElementById("entry-lane");
const activeTrail = document.getElementById("active-trail");
const lensGuide = document.getElementById("lens-guide");
const lensAxisVertical = document.getElementById("lens-axis-vertical");
const lensAxisHorizontal = document.getElementById("lens-axis-horizontal");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");
const candidateTop = document.getElementById("candidate-top");
const candidateMid = document.getElementById("candidate-mid");
const candidateBottom = document.getElementById("candidate-bottom");
const echoTop = document.getElementById("echo-top");
const echoMid = document.getElementById("echo-mid");
const echoBottom = document.getElementById("echo-bottom");
const corridorAxis = document.getElementById("corridor-axis");
const corridorLeft = document.getElementById("corridor-left");
const corridorRight = document.getElementById("corridor-right");
const corridorBraceTop = document.getElementById("corridor-brace-top");
const corridorBraceBottom = document.getElementById("corridor-brace-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const moireGroup = document.getElementById("moire-group");
const traceTop = document.getElementById("trace-top");
const traceMid = document.getElementById("trace-mid");
const traceBottom = document.getElementById("trace-bottom");
const ringOuter = document.getElementById("ring-outer");
const ringMid = document.getElementById("ring-mid");
const ringInner = document.getElementById("ring-inner");
const ringTall = document.getElementById("ring-tall");
const ringSlim = document.getElementById("ring-slim");
const waveTop = document.getElementById("wave-top");
const waveBottom = document.getElementById("wave-bottom");
const waveLeft = document.getElementById("wave-left");
const waveRight = document.getElementById("wave-right");
const resolutionBrackets = document.getElementById("resolution-brackets");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TRACE_LENGTHS = new Map([
  [traceTop, traceTop.getTotalLength()],
  [traceMid, traceMid.getTotalLength()],
  [traceBottom, traceBottom.getTotalLength()],
]);

const points = {
  start: { x: 286, y: 450 },
  appearanceSettle: { x: 402, y: 450 },
  searchTop: { x: 726, y: 324 },
  searchMid: { x: 842, y: 400 },
  searchBottom: { x: 726, y: 580 },
  corridorEntry: { x: 748, y: 450 },
  corridorCenter: { x: 872, y: 450 },
  lens: { x: 850, y: 450 },
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

function setGroupTransform(element, translateX = 0, translateY = 0, rotation = 0, origin = points.lens) {
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
      "translate(0 -24) translate(800 450) scale(1.05) translate(-800 -450)",
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
    lensGuide,
    lensAxisVertical,
    lensAxisHorizontal,
    searchArcTop,
    searchArcMid,
    searchArcBottom,
    candidateTop,
    candidateMid,
    candidateBottom,
    echoTop,
    echoMid,
    echoBottom,
    corridorAxis,
    corridorLeft,
    corridorRight,
    corridorBraceTop,
    corridorBraceBottom,
    pressureHalo,
    moireGroup,
    ringOuter,
    ringMid,
    ringInner,
    ringTall,
    ringSlim,
    waveTop,
    waveBottom,
    waveLeft,
    waveRight,
    resolutionBrackets,
    resolutionHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setPathReveal(traceTop, 0, 0);
  setPathReveal(traceMid, 0, 0);
  setPathReveal(traceBottom, 0, 0);

  setGroupTransform(candidateTop, 726, 324, 0, { x: 0, y: 0 });
  setGroupTransform(candidateMid, 842, 400, 0, { x: 0, y: 0 });
  setGroupTransform(candidateBottom, 726, 580, 0, { x: 0, y: 0 });
  setGroupTransform(corridorLeft, 872, 450, 0, { x: 0, y: 0 });
  setGroupTransform(corridorRight, 872, 450, 0, { x: 0, y: 0 });
  setGroupTransform(moireGroup, 0, 0, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.appearanceSettle, eased * 0.88);
  const dotOpacity = 0.72 + clamp(progress * 0.28, 0, 0.28);
  const haloPulse = 0.14 + pulseWave(progress, 1.1) * 0.16;

  applyDot(position, lerp(14, 19, eased), lerp(56, 88, eased), dotOpacity, haloPulse * dotOpacity);
  setOpacity(entryLane, 0.22 + progress * 0.2);
  setTrailWindow(0, 0);

  setOpacity(lensGuide, 0.28 + progress * 0.2);
  setOpacity(lensAxisVertical, 0.24 + progress * 0.18);
  setOpacity(lensAxisHorizontal, 0.1 + progress * 0.08);
  setOpacity(searchArcTop, 0.18 + progress * 0.12);
  setOpacity(searchArcMid, 0.16 + progress * 0.1);
  setOpacity(searchArcBottom, 0.18 + progress * 0.12);
  setOpacity(candidateTop, 0.24 + progress * 0.22);
  setOpacity(candidateMid, 0.24 + progress * 0.2);
  setOpacity(candidateBottom, 0.24 + progress * 0.22);
  setOpacity(corridorAxis, 0.14 + progress * 0.08);
  setOpacity(corridorLeft, 0.08 + progress * 0.08);
  setOpacity(corridorRight, 0.08 + progress * 0.08);
  setOpacity(corridorBraceTop, 0.12 + progress * 0.06);
  setOpacity(corridorBraceBottom, 0.12 + progress * 0.06);

  setGroupTransform(candidateTop, 726, 324, -4);
  setGroupTransform(candidateMid, 842, 400, 0);
  setGroupTransform(candidateBottom, 726, 580, 4);
  setGroupTransform(corridorLeft, 764, 450, 0);
  setGroupTransform(corridorRight, 980, 450, 0);
}

function renderSearch(progress) {
  let position = points.searchTop;
  let scaleX = 1;
  let scaleY = 1;

  if (progress < 0.24) {
    const t = easeInOut(progress / 0.24);
    position = mixPoint(points.appearanceSettle, points.searchTop, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.1, t);
  } else if (progress < 0.5) {
    const t = easeInOut((progress - 0.24) / 0.26);
    position = mixPoint(points.searchTop, points.searchMid, t);
    scaleX = lerp(0.92, 1.08, t);
    scaleY = lerp(1.1, 0.92, t);
  } else if (progress < 0.72) {
    const t = easeInOut((progress - 0.5) / 0.22);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    scaleX = lerp(1.08, 0.94, t);
    scaleY = lerp(0.92, 1.12, t);
  } else {
    const t = easeInOut((progress - 0.72) / 0.28);
    position = mixPoint(points.searchBottom, points.corridorEntry, t);
    scaleX = lerp(0.94, 1.08, t);
    scaleY = lerp(1.12, 0.92, t);
  }

  applyDot(position, 19, 74, 1, 0.28 + pulseWave(progress, 2.1) * 0.16, scaleX, scaleY);
  setOpacity(entryLane, 0.28);
  setTrailWindow(154 + progress * 168, 0.74 - clamp((progress - 0.68) / 0.32, 0, 1) * 0.18);

  setOpacity(lensGuide, 0.36);
  setOpacity(lensAxisVertical, 0.3);
  setOpacity(lensAxisHorizontal, 0.12);
  setOpacity(searchArcTop, 0.62);
  setOpacity(searchArcMid, 0.62);
  setOpacity(searchArcBottom, 0.62);
  setOpacity(candidateTop, 0.74);
  setOpacity(candidateMid, 0.74);
  setOpacity(candidateBottom, 0.74);
  setOpacity(echoTop, progress >= 0.3 ? 0.36 : 0);
  setOpacity(echoMid, progress >= 0.56 ? 0.34 : 0);
  setOpacity(echoBottom, progress >= 0.82 ? 0.36 : 0);
  setOpacity(corridorAxis, 0.18);
  setOpacity(corridorLeft, 0.14);
  setOpacity(corridorRight, 0.14);
  setOpacity(corridorBraceTop, 0.16);
  setOpacity(corridorBraceBottom, 0.16);

  setGroupTransform(candidateTop, 726, 324, -8);
  setGroupTransform(candidateMid, 842, 400, 0);
  setGroupTransform(candidateBottom, 726, 580, 8);
  setGroupTransform(corridorLeft, 764, 450, 0);
  setGroupTransform(corridorRight, 980, 450, 0);
}

function renderTension(progress) {
  const moveIn = progress < 0.26
    ? mixPoint(points.corridorEntry, points.corridorCenter, easeInOut(progress / 0.26))
    : progress < 0.8
      ? points.corridorCenter
      : mixPoint(points.corridorCenter, points.lens, easeInOut((progress - 0.8) / 0.2));
  const squeeze = progress < 0.26
    ? easeOut(progress / 0.26)
    : progress < 0.76
      ? 1
      : 1 - easeInOut((progress - 0.76) / 0.24);
  const pulse = progress > 0.28 && progress < 0.72 ? (pulseWave((progress - 0.28) / 0.44, 2.6) - 0.5) * 8 : 0;
  const leftShift = lerp(-108, -46, squeeze) + pulse * 0.24;
  const rightShift = lerp(108, 46, squeeze) - pulse * 0.24;
  const braceOffset = lerp(0, 32, squeeze);
  const residue = 1 - easeOut(clamp((progress - 0.06) / 0.34, 0, 1));
  const trailFade = 1 - easeOut(clamp((progress - 0.14) / 0.28, 0, 1));

  applyDot(
    moveIn,
    19,
    lerp(80, 110, squeeze),
    1,
    0.34 + squeeze * 0.18,
    lerp(1.02, 0.68, squeeze),
    lerp(0.98, 1.58, squeeze),
  );
  setOpacity(entryLane, 0.08 * residue);
  setTrailWindow(438 + progress * 102, 0.56 * trailFade);

  setOpacity(lensGuide, 0.22 * residue);
  setOpacity(lensAxisVertical, 0.18 * residue);
  setOpacity(lensAxisHorizontal, 0.08 * residue);
  setOpacity(searchArcTop, 0.12 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcBottom, 0.12 * residue);
  setOpacity(candidateTop, 0.14 * residue);
  setOpacity(candidateMid, 0.12 * residue);
  setOpacity(candidateBottom, 0.14 * residue);
  setOpacity(echoTop, 0.16 * residue);
  setOpacity(echoMid, 0.14 * residue);
  setOpacity(echoBottom, 0.16 * residue);

  setOpacity(corridorAxis, 0.56);
  setOpacity(corridorLeft, 1);
  setOpacity(corridorRight, 1);
  setOpacity(corridorBraceTop, 0.68);
  setOpacity(corridorBraceBottom, 0.68);
  setOpacity(pressureHalo, 0.3 + squeeze * 0.16);
  setGroupTransform(corridorLeft, 872 + leftShift, 450, 0);
  setGroupTransform(corridorRight, 872 + rightShift, 450, 0);
  corridorBraceTop.setAttribute("d", `M ${(786 - braceOffset).toFixed(2)} 336 H ${(958 + braceOffset).toFixed(2)}`);
  corridorBraceBottom.setAttribute("d", `M ${(786 - braceOffset).toFixed(2)} 564 H ${(958 + braceOffset).toFixed(2)}`);
}

function renderTransformation(progress) {
  const entry = progress < 0.2 ? mixPoint(points.corridorCenter, points.lens, easeOut(progress / 0.2)) : points.lens;
  const systemShift = lerp(0, -28, easeOut(clamp((progress - 0.16) / 0.7, 0, 1)));
  const traceGrow = clamp((progress - 0.08) / 0.68, 0, 1);
  const ringsGrow = clamp((progress - 0.3) / 0.42, 0, 1);
  const waveGrow = clamp((progress - 0.48) / 0.28, 0, 1);
  const lensTurn = lerp(6, -6, easeOut(progress));
  const dotPosition = { x: entry.x + systemShift, y: entry.y };
  const corridorResidue = 1 - easeOut(clamp(progress / 0.18, 0, 1));

  applyDot(dotPosition, lerp(19, 17, progress), lerp(96, 122, traceGrow), 1, 0.26 + pulseWave(progress, 2.2) * 0.12);
  setTrailWindow(220, 0.14 * corridorResidue);
  setOpacity(corridorAxis, 0.14 * corridorResidue);
  setOpacity(corridorLeft, 0.12 * corridorResidue);
  setOpacity(corridorRight, 0.12 * corridorResidue);
  setOpacity(corridorBraceTop, 0.12 * corridorResidue);
  setOpacity(corridorBraceBottom, 0.12 * corridorResidue);
  setOpacity(pressureHalo, 0.1 * corridorResidue);

  setOpacity(moireGroup, 1);
  setGroupTransform(moireGroup, systemShift, 0, lensTurn);
  setPathReveal(traceTop, clamp(traceGrow * 1.08, 0, 1), 0.92);
  setPathReveal(traceMid, clamp((traceGrow - 0.16) * 1.28, 0, 1), 0.92);
  setPathReveal(traceBottom, clamp((traceGrow - 0.32) * 1.48, 0, 1), 0.92);
  setOpacity(ringOuter, 0.24 + ringsGrow * 0.18);
  setOpacity(ringMid, 0.22 + ringsGrow * 0.18);
  setOpacity(ringInner, 0.18 + ringsGrow * 0.2);
  setOpacity(ringTall, 0.16 + ringsGrow * 0.18);
  setOpacity(ringSlim, 0.14 + ringsGrow * 0.18);
  setOpacity(waveTop, waveGrow * 0.58);
  setOpacity(waveBottom, clamp(waveGrow - 0.08, 0, 1) * 0.54);
  setOpacity(waveLeft, clamp(waveGrow - 0.16, 0, 1) * 0.46);
  setOpacity(waveRight, clamp(waveGrow - 0.16, 0, 1) * 0.46);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(-28, 0, settle);
  const turn = lerp(-6, 0, settle);
  const traceFade = 1 - easeOut(clamp(progress / 0.42, 0, 1));
  const bracketIn = clamp((progress - 0.22) / 0.42, 0, 1);

  applyDot(points.lens, 17, lerp(120, 88, progress), 1, 0.22 + pulseWave(progress, 1.5) * 0.08);
  setTrailWindow(0, 0);
  setOpacity(moireGroup, 1);
  setGroupTransform(moireGroup, shift, 0, turn);
  setOpacity(ringOuter, 0.4);
  setOpacity(ringMid, 0.38);
  setOpacity(ringInner, 0.32);
  setOpacity(ringTall, 0.28);
  setOpacity(ringSlim, 0.24);
  setOpacity(waveTop, 0.42);
  setOpacity(waveBottom, 0.38);
  setOpacity(waveLeft, 0.26);
  setOpacity(waveRight, 0.26);
  setPathReveal(traceTop, 1, 0.22 * traceFade);
  setPathReveal(traceMid, 1, 0.2 * traceFade);
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
