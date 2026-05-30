const TOTAL_DURATION = 36_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_600 },
  { id: "search", label: "search for form", duration: 6_800 },
  { id: "tension", label: "tension", duration: 6_200 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 10_400 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");
const timelineFill = document.getElementById("timeline-fill");
const toggleButton = document.getElementById("toggle-button");
const replayButton = document.getElementById("replay-button");
const phaseDots = Array.from(document.querySelectorAll("[data-phase-dot]"));

const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");
const travelSpine = document.getElementById("travel-spine");
const activeTrail = document.getElementById("active-trail");

const destinationGroup = document.getElementById("destination-group");

const searchTop = document.getElementById("search-pocket-top");
const searchMid = document.getElementById("search-pocket-mid");
const searchBottom = document.getElementById("search-pocket-bottom");
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoMid = document.getElementById("search-echo-mid");
const searchEchoBottom = document.getElementById("search-echo-bottom");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const lockGroup = document.getElementById("lock-group");
const shutterTop = document.getElementById("shutter-top");
const shutterBottom = document.getElementById("shutter-bottom");
const shutterLeft = document.getElementById("shutter-left");
const shutterRight = document.getElementById("shutter-right");
const lockSocket = document.getElementById("lock-socket");

const chamberGroup = document.getElementById("chamber-group");
const frameParts = [
  document.getElementById("frame-corner-tl"),
  document.getElementById("frame-corner-tr"),
  document.getElementById("frame-corner-bl"),
  document.getElementById("frame-corner-br"),
];
const frameRuleTop = document.getElementById("frame-rule-top");
const frameRuleBottom = document.getElementById("frame-rule-bottom");
const framePierLeft = document.getElementById("frame-pier-left");
const framePierRight = document.getElementById("frame-pier-right");
const centerSpine = document.getElementById("center-spine");
const crossbarTop = document.getElementById("crossbar-top");
const crossbarBottom = document.getElementById("crossbar-bottom");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionTicks = [
  document.getElementById("resolution-tick-top"),
  document.getElementById("resolution-tick-bottom"),
  document.getElementById("resolution-tick-left"),
  document.getElementById("resolution-tick-right"),
];

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const CENTER_SPINE_LENGTH = centerSpine.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  gray: "#b5b5b5",
  dark: "#4f4f4f",
};

const points = {
  start: { x: 260, y: 450 },
  approach: { x: 448, y: 450 },
  searchTop: { x: 560, y: 350 },
  searchMid: { x: 650, y: 450 },
  searchBottom: { x: 560, y: 550 },
  gate: { x: 820, y: 450 },
  transform: { x: 886, y: 450 },
  final: { x: 820, y: 450 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "170 160 530 640",
  search: "280 160 500 640",
  tension: "612 168 440 640",
  transformation: "676 156 440 660",
  resolution: "640 110 420 720",
};

const PORTRAIT_STAGE_TRANSFORMS = {
  appearance: { x: 430, y: 450, scale: 1.04 },
  search: { x: 574, y: 450, scale: 1.08 },
  tension: { x: 820, y: 450, scale: 1.12 },
  transformation: { x: 886, y: 450, scale: 1.16 },
  resolution: { x: 820, y: 450, scale: 1.1 },
};

function applyLayout(activePhase = "appearance") {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.82) {
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
    svg.setAttribute("viewBox", PORTRAIT_VIEWBOXES[activePhase] ?? PORTRAIT_VIEWBOXES.appearance);
    const transform = PORTRAIT_STAGE_TRANSFORMS[activePhase] ?? PORTRAIT_STAGE_TRANSFORMS.appearance;
    sceneRoot.setAttribute(
      "transform",
      `translate(${transform.x} ${transform.y}) scale(${transform.scale}) translate(${-transform.x} ${-transform.y})`,
    );
    svg.dataset.layout = "portrait";
  } else {
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    svg.setAttribute("viewBox", "0 0 1600 900");
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
}

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
  element.setAttribute("opacity", value.toFixed(3));
}

function setTransform(element, { x, y }, scaleX = 1, scaleY = 1) {
  element.setAttribute(
    "transform",
    `translate(${x} ${y}) scale(${scaleX} ${scaleY}) translate(${-x} ${-y})`,
  );
}

function setCircleCenter(element, { x, y }) {
  element.setAttribute("cx", x.toFixed(2));
  element.setAttribute("cy", y.toFixed(2));
}

function setStrokeColor(element, color) {
  element.setAttribute("stroke", color);
}

function setRectX(element, x) {
  element.setAttribute("x", x.toFixed(2));
}

function setRectY(element, y) {
  element.setAttribute("y", y.toFixed(2));
}

function setRectWidth(element, width) {
  element.setAttribute("width", width.toFixed(2));
}

function setRectHeight(element, height) {
  element.setAttribute("height", height.toFixed(2));
}

function setTrailWindow(visibleLength, opacity) {
  const clampedLength = clamp(visibleLength, 0, ACTIVE_TRAIL_LENGTH);
  activeTrail.style.strokeDasharray = `${clampedLength.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + 240).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = "0";
  setOpacity(activeTrail, opacity);
}

function applyStrokeReveal(element, amount, totalLength) {
  element.style.strokeDasharray = `${totalLength}`;
  element.style.strokeDashoffset = `${(1 - clamp(amount, 0, 1)) * totalLength}`;
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

function updateHud(info) {
  phaseLabel.textContent = info.phase.label;
  timelineFill.style.width = `${(info.totalProgress * 100).toFixed(2)}%`;
  phaseDots.forEach((dot, index) => {
    dot.classList.toggle("is-active", index === info.index);
    dot.classList.toggle("is-complete", index < info.index);
  });
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

function setCandidateState(element, mode) {
  if (mode === "active") {
    setStrokeColor(element, COLORS.dark);
    setOpacity(element, 0.84);
    return;
  }
  if (mode === "visited") {
    setStrokeColor(element, COLORS.mutedRed);
    setOpacity(element, 0.34);
    return;
  }
  if (mode === "faint") {
    setStrokeColor(element, COLORS.gray);
    setOpacity(element, 0.18);
    return;
  }
  setStrokeColor(element, COLORS.gray);
  setOpacity(element, 0);
}

function resetScene() {
  applyDot(points.start, 18, 72, 0, 0);
  setOpacity(travelSpine, 0);
  setTrailWindow(0, 0);
  setOpacity(destinationGroup, 0);

  [searchTop, searchMid, searchBottom, searchEchoTop, searchEchoMid, searchEchoBottom, searchArcTop, searchArcMid, searchArcBottom].forEach(
    (element) => setOpacity(element, 0),
  );
  [searchTop, searchMid, searchBottom].forEach((element) => setStrokeColor(element, COLORS.gray));

  setOpacity(lockGroup, 0);
  setRectY(shutterTop, 238);
  setRectY(shutterBottom, 538);
  setRectX(shutterLeft, 598);
  setRectX(shutterRight, 918);
  setRectX(lockSocket, 780);
  setRectY(lockSocket, 402);
  setRectWidth(lockSocket, 80);
  setRectHeight(lockSocket, 96);

  setOpacity(chamberGroup, 0);
  [...frameParts, frameRuleTop, frameRuleBottom, framePierLeft, framePierRight, centerSpine, crossbarTop, crossbarBottom].forEach(
    (element) => setOpacity(element, 0),
  );
  applyStrokeReveal(centerSpine, 0, CENTER_SPINE_LENGTH);
  chamberGroup.setAttribute("transform", "");

  setOpacity(resolutionGroup, 0);
  resolutionTicks.forEach((element) => setOpacity(element, 0));
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.approach, eased);
  const haloPulse = 0.22 + pulseWave(progress, 1.15) * 0.18;

  applyDot(position, lerp(14, 18, eased), lerp(48, 76, eased), 0.92, haloPulse);
  setOpacity(travelSpine, 0.18 + progress * 0.08);
  setTrailWindow(194 * eased, 0.26);
  setOpacity(destinationGroup, 0.16 + progress * 0.1);

  setCandidateState(searchTop, progress > 0.62 ? "faint" : "hidden");
  setCandidateState(searchMid, progress > 0.72 ? "faint" : "hidden");
  setCandidateState(searchBottom, progress > 0.8 ? "faint" : "hidden");
}

function renderSearch(progress) {
  const pulse = 0.18 + pulseWave(progress, 2.1) * 0.16;
  let position = points.searchTop;

  if (progress < 0.26) {
    position = mixPoint(points.approach, points.searchTop, easeOut(progress / 0.26));
  } else if (progress < 0.58) {
    position = mixPoint(points.searchTop, points.searchMid, easeInOut((progress - 0.26) / 0.32));
  } else if (progress < 0.86) {
    position = mixPoint(points.searchMid, points.searchBottom, easeInOut((progress - 0.58) / 0.28));
  } else {
    position = mixPoint(points.searchBottom, points.gate, easeOut((progress - 0.86) / 0.14));
  }

  applyDot(position, 17, 70, 1, pulse);
  setOpacity(travelSpine, 0.24);
  setTrailWindow(lerp(210, 720, progress), 0.34);
  setOpacity(destinationGroup, 0.22);

  setCandidateState(searchTop, progress < 0.34 ? "active" : "visited");
  setCandidateState(searchMid, progress < 0.26 ? "faint" : progress < 0.7 ? "active" : "visited");
  setCandidateState(searchBottom, progress < 0.58 ? "faint" : progress < 0.9 ? "active" : "visited");

  setOpacity(searchEchoTop, clamp((progress - 0.18) / 0.18, 0, 1) * 0.5);
  setOpacity(searchEchoMid, clamp((progress - 0.5) / 0.16, 0, 1) * 0.46);
  setOpacity(searchEchoBottom, clamp((progress - 0.74) / 0.12, 0, 1) * 0.42);
  setOpacity(searchArcTop, clamp((progress - 0.08) / 0.18, 0, 1) * 0.42);
  setOpacity(searchArcMid, clamp((progress - 0.32) / 0.18, 0, 1) * 0.42);
  setOpacity(searchArcBottom, clamp((progress - 0.62) / 0.18, 0, 1) * 0.38);
}

function renderTension(progress) {
  const squeeze = easeInOut(clamp((progress - 0.14) / 0.64, 0, 1));
  const approach = easeOut(clamp(progress / 0.3, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.22, 0, 1));
  const position = mixPoint(points.searchBottom, points.gate, approach);

  applyDot(
    position,
    lerp(17, 19, squeeze),
    lerp(68, 50, squeeze),
    1,
    0.22 + pulseWave(progress, 1.4) * 0.08,
    lerp(1, 0.56, squeeze),
    lerp(1, 1.58, squeeze),
  );
  setOpacity(travelSpine, 0.12);
  setTrailWindow(lerp(700, 210, progress), 0.22 * residue);
  setOpacity(destinationGroup, 0.18);

  setCandidateState(searchTop, "visited");
  setCandidateState(searchMid, "visited");
  setCandidateState(searchBottom, "visited");
  setOpacity(searchTop, 0.16 * residue);
  setOpacity(searchMid, 0.15 * residue);
  setOpacity(searchBottom, 0.14 * residue);
  setOpacity(searchEchoTop, 0.16 * residue);
  setOpacity(searchEchoMid, 0.14 * residue);
  setOpacity(searchEchoBottom, 0.12 * residue);
  setOpacity(searchArcTop, 0.1 * residue);
  setOpacity(searchArcMid, 0.1 * residue);
  setOpacity(searchArcBottom, 0.1 * residue);

  setOpacity(lockGroup, 1);
  setRectY(shutterTop, lerp(238, 300, squeeze));
  setRectY(shutterBottom, lerp(538, 476, squeeze));
  setRectX(shutterLeft, lerp(598, 670, squeeze));
  setRectX(shutterRight, lerp(918, 846, squeeze));
  setRectX(lockSocket, lerp(780, 794, squeeze));
  setRectY(lockSocket, lerp(402, 424, squeeze));
  setRectWidth(lockSocket, lerp(80, 52, squeeze));
  setRectHeight(lockSocket, lerp(96, 52, squeeze));
}

function renderTransformation(progress) {
  const moveProgress = easeOut(clamp(progress / 0.22, 0, 1));
  const chamberProgress = easeOut(clamp((progress - 0.08) / 0.34, 0, 1));
  const spineProgress = clamp((progress - 0.24) / 0.24, 0, 1);
  const crossbarProgress = clamp((progress - 0.42) / 0.24, 0, 1);
  const lockFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  const position = mixPoint(points.gate, points.transform, moveProgress);
  const groupScale = lerp(0.88, 1, chamberProgress);

  applyDot(position, lerp(19, 17, progress), lerp(50, 120, chamberProgress), 1, 0.22 + pulseWave(progress, 2.0) * 0.1);
  setOpacity(travelSpine, 0.08 * lockFade);
  setTrailWindow(180, 0.12 * lockFade);
  setOpacity(destinationGroup, 0.18 * (1 - chamberProgress));

  setOpacity(lockGroup, 0.94 * lockFade);
  setRectY(shutterTop, lerp(300, 268, chamberProgress));
  setRectY(shutterBottom, lerp(476, 508, chamberProgress));
  setRectX(shutterLeft, lerp(670, 702, chamberProgress));
  setRectX(shutterRight, lerp(846, 814, chamberProgress));

  setOpacity(chamberGroup, 1);
  chamberGroup.setAttribute(
    "transform",
    `translate(${points.transform.x} ${points.transform.y}) scale(${groupScale} ${groupScale}) translate(${-points.transform.x} ${-points.transform.y})`,
  );
  frameParts.forEach((element) => setOpacity(element, chamberProgress * 0.92));
  [frameRuleTop, frameRuleBottom, framePierLeft, framePierRight].forEach((element) => {
    setOpacity(element, clamp((progress - 0.14) / 0.24, 0, 1) * 0.88);
  });
  setOpacity(centerSpine, spineProgress * 0.92);
  applyStrokeReveal(centerSpine, spineProgress, CENTER_SPINE_LENGTH);
  setOpacity(crossbarTop, crossbarProgress * 0.82);
  setOpacity(crossbarBottom, clamp(crossbarProgress - 0.08, 0, 1) * 0.78);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, points.final.x - points.transform.x, settle);
  const chamberEase = 1 - easeOut(clamp(progress / 0.32, 0, 1));
  const haloPulse = 0.16 + pulseWave(progress, 1.5) * 0.08;

  applyDot({ x: points.transform.x + shift, y: points.final.y }, 17, lerp(108, 80, progress), 1, haloPulse);
  setOpacity(travelSpine, 0);
  setTrailWindow(0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(lockGroup, 0);

  setOpacity(chamberGroup, 1);
  chamberGroup.setAttribute("transform", `translate(${shift.toFixed(2)} 0)`);
  frameParts.forEach((element) => setOpacity(element, 0.96));
  [frameRuleTop, frameRuleBottom, framePierLeft, framePierRight].forEach((element) => setOpacity(element, 0.9));
  setOpacity(centerSpine, lerp(0.9, 0.72, settle));
  applyStrokeReveal(centerSpine, 1, CENTER_SPINE_LENGTH);
  setOpacity(crossbarTop, lerp(0.68, 0.18, settle));
  setOpacity(crossbarBottom, lerp(0.62, 0.12, settle));

  setOpacity(resolutionGroup, 1);
  resolutionTicks.forEach((element, index) => {
    const local = clamp(progress - index * 0.04, 0, 1);
    setOpacity(element, (0.3 + chamberEase * 0.34) * local);
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
  updateHud(info);
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
  toggleButton.textContent = nextPlaying ? "pause" : "play";
  toggleButton.setAttribute("aria-label", nextPlaying ? "Pause narrative" : "Play narrative");
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
  const elapsed = CAPTURE_MODE ? clamp(rawElapsed, 0, TOTAL_DURATION) : rawElapsed % TOTAL_DURATION;

  if (state.playing) {
    state.currentElapsed = elapsed;
  }

  render(elapsed);
  requestAnimationFrame(tick);
}

toggleButton.addEventListener("click", () => {
  if (state.playing) {
    state.elapsedBeforePause = state.currentElapsed;
    setPlaying(false);
  } else {
    state.startAt = performance.now();
    setPlaying(true);
  }
});

replayButton.addEventListener("click", () => {
  resetTimeline();
  if (!state.playing) {
    setPlaying(true);
  }
});

window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    toggleButton.click();
  } else if (event.key.toLowerCase() === "r") {
    replayButton.click();
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
  getState() {
    const info = phaseForElapsed(state.currentElapsed);
    return {
      currentElapsed: state.currentElapsed,
      totalDuration: TOTAL_DURATION,
      phase: info.phase.id,
      totalProgress: info.totalProgress,
      localProgress: info.localProgress,
      playing: state.playing,
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
