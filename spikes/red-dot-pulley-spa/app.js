const TOTAL_DURATION = 37_200;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_200 },
  { id: "search", label: "search for form", duration: 7_800 },
  { id: "tension", label: "tension", duration: 6_800 },
  { id: "transformation", label: "transformation", duration: 7_600 },
  { id: "resolution", label: "resolution", duration: 9_800 },
];
const PHASE_STARTS = {};

let elapsedSeed = 0;
for (const phase of PHASES) {
  PHASE_STARTS[phase.id] = elapsedSeed;
  elapsedSeed += phase.duration;
}

const CANDIDATE_LAYOUT = [
  { x: 706, y: 356, rotation: -4 },
  { x: 806, y: 446, rotation: 0 },
  { x: 722, y: 548, rotation: 4 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const entryLane = document.getElementById("entry-lane");
const activeTrail = document.getElementById("active-trail");
const beamTop = document.getElementById("beam-top");
const beamLeftHanger = document.getElementById("beam-left-hanger");
const beamRightHanger = document.getElementById("beam-right-hanger");
const wheelLeftRing = document.getElementById("wheel-left-ring");
const wheelRightRing = document.getElementById("wheel-right-ring");
const wheelLeftAxis = document.getElementById("wheel-left-axis");
const wheelRightAxis = document.getElementById("wheel-right-axis");
const knotSlotLeft = document.getElementById("knot-slot-left");
const knotSlotRight = document.getElementById("knot-slot-right");
const tailSlot = document.getElementById("tail-slot");
const searchPathTop = document.getElementById("search-path-top");
const searchPathMid = document.getElementById("search-path-mid");
const searchPathBottom = document.getElementById("search-path-bottom");
const candidateTop = document.getElementById("candidate-top");
const candidateMid = document.getElementById("candidate-mid");
const candidateBottom = document.getElementById("candidate-bottom");
const echoTop = document.getElementById("echo-top");
const echoMid = document.getElementById("echo-mid");
const echoBottom = document.getElementById("echo-bottom");
const channelLeft = document.getElementById("channel-left");
const channelRight = document.getElementById("channel-right");
const weightGuide = document.getElementById("weight-guide");
const tensionCrossbar = document.getElementById("tension-crossbar");
const weightHalo = document.getElementById("weight-halo");
const releasePathLeft = document.getElementById("release-path-left");
const releasePathTop = document.getElementById("release-path-top");
const releasePathDown = document.getElementById("release-path-down");
const braceLeft = document.getElementById("brace-left");
const braceRight = document.getElementById("brace-right");
const tailLine = document.getElementById("tail-line");
const wheelLeftSpokeH = document.getElementById("wheel-left-spoke-h");
const wheelLeftSpokeV = document.getElementById("wheel-left-spoke-v");
const wheelRightSpokeH = document.getElementById("wheel-right-spoke-h");
const wheelRightSpokeV = document.getElementById("wheel-right-spoke-v");
const resolutionBrackets = document.getElementById("resolution-brackets");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const RELEASE_LEFT_LENGTH = releasePathLeft.getTotalLength();
const RELEASE_TOP_LENGTH = releasePathTop.getTotalLength();
const RELEASE_DOWN_LENGTH = releasePathDown.getTotalLength();

const points = {
  start: { x: 420, y: 450 },
  appearanceSettle: { x: 520, y: 450 },
  searchTop: { x: 650, y: 356 },
  searchMid: { x: 764, y: 446 },
  searchBottom: { x: 674, y: 548 },
  gateEntry: { x: 820, y: 532 },
  gateHold: { x: 900, y: 534 },
  center: { x: 900, y: 520 },
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

function setDotTransform(element, point, scaleX = 1, scaleY = 1, rotation = 0) {
  element.setAttribute(
    "transform",
    `translate(${point.x} ${point.y}) rotate(${rotation}) scale(${scaleX} ${scaleY}) translate(${-point.x} ${-point.y})`,
  );
}

function setGroupTransform(element, x, y, rotation = 0, scale = 1) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotation.toFixed(2)}) scale(${scale.toFixed(3)})`,
  );
}

function setTrailWindow(visibleLength, opacity) {
  const clampedLength = clamp(visibleLength, 0, ACTIVE_TRAIL_LENGTH);
  activeTrail.style.strokeDasharray = `${clampedLength.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + 240).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = "0";
  setOpacity(activeTrail, opacity);
}

function setPathReveal(element, amount, opacity, length) {
  element.style.strokeDasharray = `${length.toFixed(2)}`;
  element.style.strokeDashoffset = `${((1 - clamp(amount, 0, 1)) * length).toFixed(2)}`;
  setOpacity(element, opacity);
}

function pointOnPath(path, length, progress) {
  const safeProgress = clamp(progress, 0, 1);
  return path.getPointAtLength(length * safeProgress);
}

function applyLayout(phaseId = svg.dataset.phase || "appearance") {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    let scale = 1.18;
    let translateY = -40;
    if (phaseId === "tension") {
      scale = 1.24;
      translateY = -32;
    } else if (phaseId === "transformation") {
      scale = 1.3;
      translateY = -52;
    } else if (phaseId === "resolution") {
      scale = 1.34;
      translateY = -60;
    }
    sceneRoot.setAttribute(
      "transform",
      `translate(0 ${translateY}) translate(800 450) scale(${scale}) translate(-800 -450)`,
    );
    svg.dataset.layout = "portrait";
  } else {
    sceneRoot.setAttribute(
      "transform",
      "translate(838 448) scale(1.06) translate(-838 -448)",
    );
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

function applyDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1, rotation = 0) {
  setCircleCenter(dotCore, position);
  setCircleCenter(dotHalo, position);
  dotCore.setAttribute("r", radius.toFixed(2));
  dotHalo.setAttribute("r", haloRadius.toFixed(2));
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  setDotTransform(dotCore, position, scaleX, scaleY, rotation);
  setDotTransform(dotHalo, position, scaleX, scaleY, rotation);
}

function setCandidateLayout(opacity) {
  [candidateTop, candidateMid, candidateBottom].forEach((element, index) => {
    const candidate = CANDIDATE_LAYOUT[index];
    setGroupTransform(element, candidate.x, candidate.y, candidate.rotation);
    setOpacity(element, opacity);
  });
}

function setReceiverScaffold({
  beam = 0,
  hangers = 0,
  rings = 0,
  axes = 0,
  knot = 0,
  tail = 0,
}) {
  setOpacity(beamTop, beam);
  setOpacity(beamLeftHanger, hangers);
  setOpacity(beamRightHanger, hangers);
  setOpacity(wheelLeftRing, rings);
  setOpacity(wheelRightRing, rings);
  setOpacity(wheelLeftAxis, axes);
  setOpacity(wheelRightAxis, axes);
  setOpacity(knotSlotLeft, knot);
  setOpacity(knotSlotRight, knot);
  setOpacity(tailSlot, tail);
}

function setResolvedStructure({
  braces = 0,
  tail = 0,
  spokes = 0,
}) {
  setOpacity(braceLeft, braces);
  setOpacity(braceRight, braces);
  setOpacity(tailLine, tail);
  setOpacity(wheelLeftSpokeH, spokes);
  setOpacity(wheelLeftSpokeV, spokes);
  setOpacity(wheelRightSpokeH, spokes);
  setOpacity(wheelRightSpokeV, spokes);
}

function resetScene() {
  applyDot(points.start, 18, 72, 0, 0);
  setOpacity(entryLane, 0);
  setTrailWindow(0, 0);

  setReceiverScaffold({
    beam: 0,
    hangers: 0,
    rings: 0,
    axes: 0,
    knot: 0,
    tail: 0,
  });
  setResolvedStructure({
    braces: 0,
    tail: 0,
    spokes: 0,
  });

  [
    searchPathTop,
    searchPathMid,
    searchPathBottom,
    echoTop,
    echoMid,
    echoBottom,
    channelLeft,
    channelRight,
    weightGuide,
    tensionCrossbar,
    weightHalo,
    resolutionBrackets,
    resolutionHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setCandidateLayout(0);
  setPathReveal(releasePathLeft, 0, 0, RELEASE_LEFT_LENGTH);
  setPathReveal(releasePathTop, 0, 0, RELEASE_TOP_LENGTH);
  setPathReveal(releasePathDown, 0, 0, RELEASE_DOWN_LENGTH);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.appearanceSettle, eased * 0.88);
  const dotOpacity = 0.74 + clamp(progress * 0.3, 0, 0.24);
  const haloPulse = 0.14 + pulseWave(progress, 1.05) * 0.15;

  applyDot(position, lerp(14, 19, eased), lerp(54, 86, eased), dotOpacity, haloPulse * dotOpacity);
  setOpacity(entryLane, 0.2 + progress * 0.18);
  setTrailWindow(0, 0);

  setReceiverScaffold({
    beam: 0.34 + progress * 0.2,
    hangers: 0.22 + progress * 0.12,
    rings: 0.3 + progress * 0.18,
    axes: 0.18 + progress * 0.1,
    knot: 0.22 + progress * 0.12,
    tail: 0.14 + progress * 0.08,
  });
  setCandidateLayout(0.2 + progress * 0.12);
  setOpacity(searchPathTop, 0.12 + progress * 0.1);
  setOpacity(searchPathMid, 0.12 + progress * 0.1);
  setOpacity(searchPathBottom, 0.12 + progress * 0.1);
  setOpacity(channelLeft, 0.12 + progress * 0.06);
  setOpacity(channelRight, 0.12 + progress * 0.06);
  setOpacity(tensionCrossbar, 0.08 + progress * 0.06);
}

function renderSearch(progress) {
  let position = points.searchTop;
  let scaleX = 1;
  let scaleY = 1;
  let rotation = -6;

  if (progress < 0.22) {
    const t = easeInOut(progress / 0.22);
    position = mixPoint(points.appearanceSettle, points.searchTop, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.08, t);
    rotation = lerp(0, -12, t);
  } else if (progress < 0.48) {
    const t = easeInOut((progress - 0.22) / 0.26);
    position = mixPoint(points.searchTop, points.searchMid, t);
    scaleX = lerp(0.92, 1.08, t);
    scaleY = lerp(1.08, 0.92, t);
    rotation = lerp(-12, 6, t);
  } else if (progress < 0.74) {
    const t = easeInOut((progress - 0.48) / 0.26);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    scaleX = lerp(1.08, 0.94, t);
    scaleY = lerp(0.92, 1.12, t);
    rotation = lerp(6, -8, t);
  } else {
    const t = easeInOut((progress - 0.74) / 0.26);
    position = mixPoint(points.searchBottom, points.gateEntry, t);
    scaleX = lerp(0.94, 1.06, t);
    scaleY = lerp(1.12, 0.94, t);
    rotation = lerp(-8, 0, t);
  }

  const candidateResidue = 1 - easeOut(clamp((progress - 0.82) / 0.18, 0, 1));

  applyDot(position, 19, 74, 1, 0.28 + pulseWave(progress, 2.1) * 0.12, scaleX, scaleY, rotation);
  setOpacity(entryLane, 0.14);
  setTrailWindow(112 + progress * 70, 0.18 - clamp((progress - 0.7) / 0.3, 0, 1) * 0.15);

  setReceiverScaffold({
    beam: 0.48,
    hangers: 0.3,
    rings: 0.44,
    axes: 0.24,
    knot: 0.28,
    tail: 0.16,
  });
  setCandidateLayout(0.72 * candidateResidue);

  setOpacity(searchPathTop, progress < 0.24 ? 0.62 : 0.16 * candidateResidue);
  setOpacity(searchPathMid, progress >= 0.22 && progress < 0.5 ? 0.62 : 0.16 * candidateResidue);
  setOpacity(searchPathBottom, progress >= 0.48 && progress < 0.76 ? 0.62 : 0.12 * candidateResidue);

  setOpacity(echoTop, progress >= 0.24 ? 0.34 * candidateResidue : 0);
  setOpacity(echoMid, progress >= 0.5 ? 0.34 * candidateResidue : 0);
  setOpacity(echoBottom, progress >= 0.76 ? 0.34 * candidateResidue : 0);

  setOpacity(channelLeft, 0.18);
  setOpacity(channelRight, 0.18);
  setOpacity(tensionCrossbar, 0.12);
}

function renderTension(progress) {
  const move = progress < 0.24
    ? mixPoint(points.gateEntry, points.gateHold, easeInOut(progress / 0.24))
    : points.gateHold;
  const squeeze = progress < 0.24
    ? easeOut(progress / 0.24)
    : progress < 0.8
      ? 1
      : 1 - easeInOut((progress - 0.8) / 0.2) * 0.22;
  const searchFade = 1 - easeOut(clamp((progress - 0.02) / 0.36, 0, 1));

  applyDot(
    move,
    19,
    lerp(84, 112, squeeze),
    1,
    0.34 + squeeze * 0.2,
    lerp(1.04, 0.74, squeeze),
    lerp(0.96, 1.72, squeeze),
    0,
  );

  setOpacity(entryLane, 0.04 * searchFade);
  setTrailWindow(210, 0.24 * (1 - easeOut(clamp((progress - 0.06) / 0.2, 0, 1))));

  setReceiverScaffold({
    beam: 0.54,
    hangers: 0.38,
    rings: 0.5,
    axes: 0.3,
    knot: 0.18,
    tail: 0.08,
  });
  setCandidateLayout(0.14 * searchFade);
  setOpacity(searchPathTop, 0.12 * searchFade);
  setOpacity(searchPathMid, 0.12 * searchFade);
  setOpacity(searchPathBottom, 0.12 * searchFade);
  setOpacity(echoTop, 0.14 * searchFade);
  setOpacity(echoMid, 0.14 * searchFade);
  setOpacity(echoBottom, 0.14 * searchFade);

  setOpacity(channelLeft, 0.76);
  setOpacity(channelRight, 0.76);
  setOpacity(weightGuide, 0.78);
  setOpacity(tensionCrossbar, 0.58);
  setOpacity(weightHalo, 0.24 + squeeze * 0.18);
}

function renderTransformation(progress) {
  const channelFade = 1 - easeOut(clamp(progress / 0.28, 0, 1));
  const leftReveal = clamp(progress / 0.34, 0, 1);
  const topReveal = clamp((progress - 0.24) / 0.34, 0, 1);
  const downReveal = clamp((progress - 0.52) / 0.34, 0, 1);

  let dotPosition = points.gateHold;
  if (progress < 0.34) {
    const t = easeInOut(progress / 0.34);
    const point = pointOnPath(releasePathLeft, RELEASE_LEFT_LENGTH, t);
    dotPosition = { x: point.x, y: point.y };
  } else if (progress < 0.62) {
    const t = easeInOut((progress - 0.34) / 0.28);
    const point = pointOnPath(releasePathTop, RELEASE_TOP_LENGTH, t);
    dotPosition = { x: point.x, y: point.y };
  } else if (progress < 0.94) {
    const t = easeInOut((progress - 0.62) / 0.32);
    const point = pointOnPath(releasePathDown, RELEASE_DOWN_LENGTH, t);
    dotPosition = { x: point.x, y: point.y };
  } else {
    const point = pointOnPath(releasePathDown, RELEASE_DOWN_LENGTH, 1);
    const t = easeInOut((progress - 0.94) / 0.06);
    dotPosition = mixPoint({ x: point.x, y: point.y }, points.center, t);
  }

  applyDot(dotPosition, lerp(18, 17, progress), lerp(96, 120, progress), 1, 0.24 + pulseWave(progress, 2.2) * 0.12);
  setTrailWindow(120, 0.04 * channelFade);

  setReceiverScaffold({
    beam: 0.56,
    hangers: 0.42,
    rings: 0.56,
    axes: 0.22,
    knot: 0.32 + progress * 0.1,
    tail: 0.16 + progress * 0.12,
  });
  setResolvedStructure({
    braces: clamp((progress - 0.32) / 0.34, 0, 1),
    tail: clamp((progress - 0.46) / 0.28, 0, 1),
    spokes: clamp((progress - 0.18) / 0.4, 0, 1) * 0.88,
  });

  setCandidateLayout(0);
  setOpacity(searchPathTop, 0);
  setOpacity(searchPathMid, 0);
  setOpacity(searchPathBottom, 0);
  setOpacity(echoTop, 0);
  setOpacity(echoMid, 0);
  setOpacity(echoBottom, 0);

  setOpacity(channelLeft, 0.5 * channelFade);
  setOpacity(channelRight, 0.5 * channelFade);
  setOpacity(weightGuide, 0.16 * channelFade);
  setOpacity(tensionCrossbar, 0.18 * channelFade);
  setOpacity(weightHalo, 0.12 * channelFade);

  setPathReveal(releasePathLeft, leftReveal, 0.92, RELEASE_LEFT_LENGTH);
  setPathReveal(releasePathTop, topReveal, 0.92, RELEASE_TOP_LENGTH);
  setPathReveal(releasePathDown, downReveal, 0.92, RELEASE_DOWN_LENGTH);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const traceFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  const bracketIn = clamp((progress - 0.2) / 0.36, 0, 1);
  const slotFade = 1 - easeOut(clamp((progress - 0.28) / 0.46, 0, 1));

  applyDot(points.center, 17, lerp(124, 88, progress), 1, 0.22 + pulseWave(progress, 1.5) * 0.08);
  setTrailWindow(0, 0);

  setReceiverScaffold({
    beam: 0.58,
    hangers: 0.44,
    rings: 0.58,
    axes: 0.14,
    knot: 0.16 * slotFade,
    tail: 0.12 * slotFade,
  });
  setResolvedStructure({
    braces: 1,
    tail: 1,
    spokes: 0.92,
  });

  setOpacity(channelLeft, 0);
  setOpacity(channelRight, 0);
  setOpacity(weightGuide, 0);
  setOpacity(tensionCrossbar, 0);
  setOpacity(weightHalo, 0);

  setPathReveal(releasePathLeft, 1, 0.18 * traceFade, RELEASE_LEFT_LENGTH);
  setPathReveal(releasePathTop, 1, 0.16 * traceFade, RELEASE_TOP_LENGTH);
  setPathReveal(releasePathDown, 1, 0.18 * traceFade, RELEASE_DOWN_LENGTH);

  setOpacity(resolutionHalo, 0.28);
  setOpacity(resolutionBrackets, 0.18 + bracketIn * 0.34);

  const settleLift = Math.sin(progress * Math.PI) * (1 - settle) * 2.4;
  [braceLeft, braceRight, tailLine].forEach((element) => {
    element.setAttribute("transform", `translate(0 ${settleLift.toFixed(2)})`);
  });
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
  applyLayout(info.phase.id);
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

applyLayout("appearance");
window.addEventListener("resize", () => applyLayout(svg.dataset.phase || "appearance"));
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
