const TOTAL_DURATION = 36_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 6_500 },
  { id: "transformation", label: "transformation", duration: 7_500 },
  { id: "resolution", label: "resolution", duration: 10_000 },
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
const throatCollar = document.getElementById("throat-collar");
const jawLeft = document.getElementById("jaw-left");
const jawRight = document.getElementById("jaw-right");
const throatBraceTop = document.getElementById("throat-brace-top");
const throatBraceBottom = document.getElementById("throat-brace-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const crankGroup = document.getElementById("crank-group");
const traceArc = document.getElementById("trace-arc");
const traceArm = document.getElementById("trace-arm");
const traceHandle = document.getElementById("trace-handle");
const wheelShell = document.getElementById("wheel-shell");
const wheelInner = document.getElementById("wheel-inner");
const counterArcTop = document.getElementById("counter-arc-top");
const counterArcBottom = document.getElementById("counter-arc-bottom");
const armBody = document.getElementById("arm-body");
const counterArm = document.getElementById("counter-arm");
const handleBar = document.getElementById("handle-bar");
const pinBrace = document.getElementById("pin-brace");
const axleCore = document.getElementById("axle-core");
const pinShell = document.getElementById("pin-shell");
const resolutionBrackets = document.getElementById("resolution-brackets");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TRACE_LENGTHS = new Map([
  [traceArc, traceArc.getTotalLength()],
  [traceArm, traceArm.getTotalLength()],
  [traceHandle, traceHandle.getTotalLength()],
]);

const points = {
  start: { x: 290, y: 450 },
  appearanceSettle: { x: 392, y: 450 },
  searchTop: { x: 730, y: 332 },
  searchMid: { x: 856, y: 406 },
  searchBottom: { x: 754, y: 566 },
  throatEntry: { x: 760, y: 450 },
  throatCenter: { x: 884, y: 450 },
  center: { x: 900, y: 450 },
  pinFinal: { x: 978, y: 386 },
};

const state = {
  playing: true,
  looping: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "120 0 980 900",
  search: "240 0 900 900",
  tension: "540 0 720 900",
  transformation: "590 0 720 900",
  resolution: "650 0 620 900",
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

function setGroupTransform(element, translateX = 0, translateY = 0, rotation = 0, origin = points.center) {
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

function applyLayout(activePhase = "appearance") {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
    svg.setAttribute("viewBox", PORTRAIT_VIEWBOXES[activePhase] ?? PORTRAIT_VIEWBOXES.appearance);
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "portrait";
  } else {
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svg.setAttribute("viewBox", "0 0 1600 900");
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
    throatCollar,
    jawLeft,
    jawRight,
    throatBraceTop,
    throatBraceBottom,
    pressureHalo,
    crankGroup,
    wheelShell,
    wheelInner,
    counterArcTop,
    counterArcBottom,
    armBody,
    counterArm,
    handleBar,
    pinBrace,
    axleCore,
    pinShell,
    resolutionBrackets,
    resolutionHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setPathReveal(traceArc, 0, 0);
  setPathReveal(traceArm, 0, 0);
  setPathReveal(traceHandle, 0, 0);

  setGroupTransform(candidateTop, 730, 332, -8, { x: 0, y: 0 });
  setGroupTransform(candidateMid, 856, 406, 4, { x: 0, y: 0 });
  setGroupTransform(candidateBottom, 754, 566, 12, { x: 0, y: 0 });
  setGroupTransform(jawLeft, 786, 450, 0, { x: 0, y: 0 });
  setGroupTransform(jawRight, 982, 450, 0, { x: 0, y: 0 });
  setGroupTransform(crankGroup, 18, 0, 18);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.appearanceSettle, eased * 0.88);
  const dotOpacity = 0.72 + clamp(progress * 0.32, 0, 0.28);
  const haloPulse = 0.16 + pulseWave(progress, 1.1) * 0.16;

  applyDot(position, lerp(14, 19, eased), lerp(56, 86, eased), dotOpacity, haloPulse * dotOpacity);
  setOpacity(entryLane, 0.2 + progress * 0.2);
  setTrailWindow(0, 0);

  setOpacity(hubGuide, 0.28 + progress * 0.18);
  setOpacity(hubAxis, 0.24 + progress * 0.16);
  setOpacity(hubCross, 0.1 + progress * 0.08);
  setOpacity(searchArcTop, 0.16 + progress * 0.1);
  setOpacity(searchArcMid, 0.14 + progress * 0.1);
  setOpacity(searchArcBottom, 0.16 + progress * 0.1);
  setOpacity(candidateTop, 0.22 + progress * 0.18);
  setOpacity(candidateMid, 0.22 + progress * 0.18);
  setOpacity(candidateBottom, 0.22 + progress * 0.18);
  setOpacity(throatAxis, 0.12 + progress * 0.08);
  setOpacity(throatCollar, 0.08 + progress * 0.06);
  setOpacity(jawLeft, 0.08 + progress * 0.06);
  setOpacity(jawRight, 0.08 + progress * 0.06);
  setOpacity(throatBraceTop, 0.1 + progress * 0.06);
  setOpacity(throatBraceBottom, 0.1 + progress * 0.06);
  setGroupTransform(jawLeft, 786, 450, 0, { x: 0, y: 0 });
  setGroupTransform(jawRight, 982, 450, 0, { x: 0, y: 0 });
}

function renderSearch(progress) {
  let position = points.searchTop;
  let scaleX = 1;
  let scaleY = 1;

  if (progress < 0.24) {
    const t = easeInOut(progress / 0.24);
    position = mixPoint(points.appearanceSettle, points.searchTop, t);
    scaleX = lerp(1, 0.94, t);
    scaleY = lerp(1, 1.08, t);
  } else if (progress < 0.52) {
    const t = easeInOut((progress - 0.24) / 0.28);
    position = mixPoint(points.searchTop, points.searchMid, t);
    scaleX = lerp(0.94, 1.1, t);
    scaleY = lerp(1.08, 0.92, t);
  } else if (progress < 0.68) {
    const t = easeInOut((progress - 0.52) / 0.16);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    scaleX = lerp(1.1, 0.96, t);
    scaleY = lerp(0.92, 1.12, t);
  } else {
    const t = easeInOut((progress - 0.68) / 0.32);
    position = mixPoint(points.searchBottom, points.throatEntry, t);
    scaleX = lerp(0.96, 1.08, t);
    scaleY = lerp(1.12, 0.92, t);
  }

  applyDot(position, 19, 72, 1, 0.28 + pulseWave(progress, 2.2) * 0.15, scaleX, scaleY);
  setOpacity(entryLane, 0.28);
  const trailFade = progress < 0.62 ? 0.72 : lerp(0.72, 0.16, easeOut((progress - 0.62) / 0.38));
  setTrailWindow(150 + progress * 170, trailFade);

  setOpacity(hubGuide, 0.42);
  setOpacity(hubAxis, 0.34);
  setOpacity(hubCross, 0.12);
  setOpacity(searchArcTop, 0.62);
  setOpacity(searchArcMid, 0.62);
  setOpacity(searchArcBottom, 0.62);
  setOpacity(candidateTop, 0.72);
  setOpacity(candidateMid, 0.72);
  setOpacity(candidateBottom, 0.72);
  setOpacity(echoTop, progress >= 0.3 ? 0.36 : 0);
  setOpacity(echoMid, progress >= 0.58 ? 0.34 : 0);
  setOpacity(echoBottom, progress >= 0.78 ? 0.38 : 0);
  setOpacity(throatAxis, 0.24);
  setOpacity(throatCollar, 0.18);
  setOpacity(jawLeft, 0.2);
  setOpacity(jawRight, 0.2);
  setOpacity(throatBraceTop, 0.22);
  setOpacity(throatBraceBottom, 0.22);
  setGroupTransform(jawLeft, 786, 450, 0, { x: 0, y: 0 });
  setGroupTransform(jawRight, 982, 450, 0, { x: 0, y: 0 });
}

function renderTension(progress) {
  const moveIn = progress < 0.26
    ? mixPoint(points.throatEntry, points.throatCenter, easeInOut(progress / 0.26))
    : progress < 0.8
      ? points.throatCenter
      : mixPoint(points.throatCenter, points.center, easeInOut((progress - 0.8) / 0.2));
  const squeeze = progress < 0.26
    ? easeOut(progress / 0.26)
    : progress < 0.74
      ? 1
      : 1 - easeInOut((progress - 0.74) / 0.26);
  const pulse = progress > 0.3 && progress < 0.7 ? (pulseWave((progress - 0.3) / 0.4, 2.2) - 0.5) * 8 : 0;
  const leftShift = lerp(-98, -34, squeeze) + pulse * 0.25;
  const rightShift = lerp(98, 34, squeeze) - pulse * 0.25;
  const braceOffset = lerp(0, 24, squeeze);
  const residue = 1 - easeOut(clamp((progress - 0.08) / 0.34, 0, 1));
  const trailFade = 1 - easeOut(clamp((progress - 0.18) / 0.32, 0, 1));

  applyDot(
    moveIn,
    19,
    lerp(78, 108, squeeze),
    1,
    0.34 + squeeze * 0.16,
    lerp(1.02, 1.8, squeeze),
    lerp(0.98, 0.68, squeeze),
  );
  setOpacity(entryLane, 0.08 * residue);
  setTrailWindow(420 + progress * 110, 0.56 * trailFade);

  setOpacity(hubGuide, 0.2 * residue);
  setOpacity(hubAxis, 0.16 * residue);
  setOpacity(hubCross, 0.08 * residue);
  setOpacity(searchArcTop, 0.12 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcBottom, 0.12 * residue);
  setOpacity(candidateTop, 0.12 * residue);
  setOpacity(candidateMid, 0.12 * residue);
  setOpacity(candidateBottom, 0.12 * residue);
  setOpacity(echoTop, 0.14 * residue);
  setOpacity(echoMid, 0.14 * residue);
  setOpacity(echoBottom, 0.14 * residue);

  setOpacity(throatAxis, 0.52);
  setOpacity(throatCollar, 0.46);
  setOpacity(jawLeft, 1);
  setOpacity(jawRight, 1);
  setOpacity(throatBraceTop, 0.68);
  setOpacity(throatBraceBottom, 0.68);
  setOpacity(pressureHalo, 0.32 + squeeze * 0.16);
  setGroupTransform(jawLeft, 884 + leftShift, 450, 0, { x: 0, y: 0 });
  setGroupTransform(jawRight, 884 + rightShift, 450, 0, { x: 0, y: 0 });
  throatBraceTop.setAttribute("d", `M ${(818 - braceOffset).toFixed(2)} 342 H ${(950 + braceOffset).toFixed(2)}`);
  throatBraceBottom.setAttribute("d", `M ${(818 - braceOffset).toFixed(2)} 558 H ${(950 + braceOffset).toFixed(2)}`);
}

function transformationDotPosition(progress) {
  if (progress < 0.24) {
    return mixPoint(points.throatCenter, points.center, easeOut(progress / 0.24));
  }
  return mixPoint(points.center, points.pinFinal, easeInOut((progress - 0.24) / 0.76));
}

function renderTransformation(progress) {
  const dotPosition = transformationDotPosition(progress);
  const shift = lerp(18, 0, easeOut(clamp((progress - 0.14) / 0.8, 0, 1)));
  const turn = lerp(18, 0, easeOut(clamp((progress - 0.08) / 0.68, 0, 1)));
  const corridorResidue = 1 - easeOut(clamp(progress / 0.18, 0, 1));
  const wheelGrow = clamp((progress - 0.12) / 0.34, 0, 1);
  const traceGrow = clamp((progress - 0.18) / 0.58, 0, 1);
  const bodyGrow = clamp((progress - 0.34) / 0.3, 0, 1);
  const handleGrow = clamp((progress - 0.5) / 0.28, 0, 1);
  const bracketSeed = clamp((progress - 0.7) / 0.2, 0, 1);

  applyDot(dotPosition, lerp(19, 17, progress), lerp(98, 122, traceGrow), 1, 0.26 + pulseWave(progress, 2.1) * 0.12);
  setOpacity(entryLane, 0);
  setTrailWindow(210, 0.14 * corridorResidue);
  setOpacity(throatAxis, 0.14 * corridorResidue);
  setOpacity(throatCollar, 0.1 * corridorResidue);
  setOpacity(jawLeft, 0.12 * corridorResidue);
  setOpacity(jawRight, 0.12 * corridorResidue);
  setOpacity(throatBraceTop, 0.12 * corridorResidue);
  setOpacity(throatBraceBottom, 0.12 * corridorResidue);
  setOpacity(pressureHalo, 0.1 * corridorResidue);

  setOpacity(crankGroup, 1);
  setGroupTransform(crankGroup, shift, 0, turn);
  setOpacity(wheelShell, 0.2 + wheelGrow * 0.24);
  setOpacity(wheelInner, 0.14 + wheelGrow * 0.16);
  setOpacity(counterArcTop, 0.16 + bodyGrow * 0.18);
  setOpacity(counterArcBottom, 0.14 + bodyGrow * 0.18);
  setOpacity(armBody, bodyGrow);
  setOpacity(counterArm, clamp(bodyGrow - 0.08, 0, 1));
  setOpacity(handleBar, clamp(handleGrow, 0, 1));
  setOpacity(pinBrace, clamp(handleGrow - 0.12, 0, 1) * 0.76);
  setOpacity(axleCore, 0.2 + bodyGrow * 0.72);
  setOpacity(pinShell, 0.18 + handleGrow * 0.72);
  setOpacity(resolutionHalo, bracketSeed * 0.18);
  setOpacity(resolutionBrackets, bracketSeed * 0.14);
  setPathReveal(traceArc, clamp(traceGrow * 1.04, 0, 1), 0.92);
  setPathReveal(traceArm, clamp((traceGrow - 0.14) * 1.3, 0, 1), 0.92);
  setPathReveal(traceHandle, clamp((traceGrow - 0.38) * 1.7, 0, 1), 0.9);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, -10, progress < 0.34 ? 0 : easeOut((progress - 0.34) / 0.66));
  const traceFade = 1 - easeOut(clamp(progress / 0.44, 0, 1));
  const bracketIn = clamp((progress - 0.2) / 0.38, 0, 1);

  applyDot(points.pinFinal, 17, lerp(116, 86, progress), 1, 0.22 + pulseWave(progress, 1.6) * 0.08);
  setTrailWindow(0, 0);
  setOpacity(crankGroup, 1);
  setGroupTransform(crankGroup, shift, 0, 0);

  setOpacity(wheelShell, 0.42);
  setOpacity(wheelInner, 0.28);
  setOpacity(counterArcTop, 0.38);
  setOpacity(counterArcBottom, 0.36);
  setOpacity(armBody, 1);
  setOpacity(counterArm, 0.7);
  setOpacity(handleBar, 0.76);
  setOpacity(pinBrace, 0.34);
  setOpacity(axleCore, 0.98);
  setOpacity(pinShell, 0.96);
  setOpacity(resolutionHalo, 0.3);
  setOpacity(resolutionBrackets, 0.18 + bracketIn * 0.34);
  setPathReveal(traceArc, 1, 0.2 * traceFade);
  setPathReveal(traceArm, 1, 0.18 * traceFade);
  setPathReveal(traceHandle, 1, 0.16 * traceFade);
  setTransform(dotCore, points.pinFinal, lerp(1.06, 1, settle), lerp(1.06, 1, settle));
  setTransform(dotHalo, points.pinFinal, lerp(1.08, 1, settle), lerp(1.08, 1, settle));
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

  applyLayout(info.phase.id);
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

resetScene();
render(0);
window.addEventListener("resize", () => {
  const info = phaseForElapsed(state.currentElapsed);
  applyLayout(info.phase.id);
});

const requestedPhase = new URLSearchParams(window.location.search).get("phase");
if (requestedPhase && PHASE_STARTS[requestedPhase] !== undefined) {
  freezeOnPhase(requestedPhase);
  state.elapsedBeforePause = state.currentElapsed;
  setPlaying(false);
}

window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
