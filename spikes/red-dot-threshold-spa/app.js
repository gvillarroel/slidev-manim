const TOTAL_DURATION = 31_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 6_000 },
  { id: "tension", label: "tension", duration: 5_000 },
  { id: "transformation", label: "transformation", duration: 6_000 },
  { id: "resolution", label: "resolution", duration: 9_000 },
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

const searchTop = document.getElementById("search-aperture-top");
const searchMid = document.getElementById("search-aperture-mid");
const searchBottom = document.getElementById("search-aperture-bottom");
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoMid = document.getElementById("search-echo-mid");
const searchEchoBottom = document.getElementById("search-echo-bottom");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const thresholdGroup = document.getElementById("threshold-group");
const wallLeft = document.getElementById("wall-left");
const wallRight = document.getElementById("wall-right");
const slitGuide = document.getElementById("slit-guide");

const unfoldGroup = document.getElementById("unfold-group");
const orbitRing = document.getElementById("orbit-ring");
const orbitRingSecondary = document.getElementById("orbit-ring-secondary");
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
const centerThread = document.getElementById("center-thread");
const supportLinkTop = document.getElementById("support-link-top");
const supportLinkBottom = document.getElementById("support-link-bottom");
const supportNodeTop = document.getElementById("support-node-top");
const supportNodeBottom = document.getElementById("support-node-bottom");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRule = document.getElementById("resolution-rule");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const CENTER_THREAD_LENGTH = centerThread.getTotalLength();
const SUPPORT_TOP_LENGTH = supportLinkTop.getTotalLength();
const SUPPORT_BOTTOM_LENGTH = supportLinkBottom.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  gray: "#b5b5b5",
  dark: "#4f4f4f",
};

const points = {
  start: { x: 280, y: 450 },
  approach: { x: 420, y: 404 },
  searchTop: { x: 520, y: 308 },
  searchMid: { x: 642, y: 450 },
  searchBottom: { x: 520, y: 594 },
  preGate: { x: 694, y: 510 },
  gate: { x: 850, y: 450 },
  transform: { x: 970, y: 450 },
  final: { x: 860, y: 450 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "170 160 520 640",
  search: "250 158 500 650",
  tension: "680 170 360 650",
  transformation: "716 156 360 660",
  resolution: "680 70 360 780",
};

const PORTRAIT_STAGE_TRANSFORMS = {
  appearance: { x: 430, y: 450, scale: 1.06 },
  search: { x: 570, y: 450, scale: 1.1 },
  tension: { x: 850, y: 450, scale: 1.16 },
  transformation: { x: 944, y: 450, scale: 1.18 },
  resolution: { x: 860, y: 450, scale: 1.06 },
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

function setRectWidth(element, width) {
  element.setAttribute("width", width.toFixed(2));
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
    setOpacity(element, 0.82);
    return;
  }
  if (mode === "visited") {
    setStrokeColor(element, COLORS.mutedRed);
    setOpacity(element, 0.34);
    return;
  }
  if (mode === "faint") {
    setStrokeColor(element, COLORS.gray);
    setOpacity(element, 0.16);
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

  setOpacity(thresholdGroup, 0);
  setRectX(wallLeft, 670);
  setRectX(wallRight, 942);
  setRectX(slitGuide, 786);
  setRectWidth(slitGuide, 128);

  setOpacity(unfoldGroup, 0);
  setOpacity(orbitRing, 0);
  setOpacity(orbitRingSecondary, 0);
  orbitRing.setAttribute("r", "56");
  orbitRingSecondary.setAttribute("r", "92");
  [...frameParts, frameRuleTop, frameRuleBottom, framePierLeft, framePierRight, centerThread, supportLinkTop, supportLinkBottom, supportNodeTop, supportNodeBottom].forEach(
    (element) => setOpacity(element, 0),
  );
  applyStrokeReveal(centerThread, 0, CENTER_THREAD_LENGTH);
  applyStrokeReveal(supportLinkTop, 0, SUPPORT_TOP_LENGTH);
  applyStrokeReveal(supportLinkBottom, 0, SUPPORT_BOTTOM_LENGTH);
  unfoldGroup.setAttribute("transform", "");

  setOpacity(resolutionGroup, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRule, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.approach, eased);
  const haloPulse = 0.22 + pulseWave(progress, 1.15) * 0.18;

  applyDot(position, lerp(14, 18, eased), lerp(48, 78, eased), 0.92, haloPulse);
  setOpacity(travelSpine, 0.18 + progress * 0.08);
  setTrailWindow(228 * eased, 0.26);
  setOpacity(destinationGroup, 0.14 + progress * 0.08);

  setCandidateState(searchTop, progress > 0.62 ? "faint" : "hidden");
  setCandidateState(searchMid, progress > 0.72 ? "faint" : "hidden");
  setCandidateState(searchBottom, progress > 0.8 ? "faint" : "hidden");
}

function renderSearch(progress) {
  const pulse = 0.18 + pulseWave(progress, 2.2) * 0.16;
  let position = points.searchTop;

  if (progress < 0.24) {
    position = mixPoint(points.approach, points.searchTop, easeOut(progress / 0.24));
  } else if (progress < 0.56) {
    position = mixPoint(points.searchTop, points.searchMid, easeInOut((progress - 0.24) / 0.32));
  } else if (progress < 0.86) {
    position = mixPoint(points.searchMid, points.searchBottom, easeInOut((progress - 0.56) / 0.3));
  } else {
    position = mixPoint(points.searchBottom, points.preGate, easeOut((progress - 0.86) / 0.14));
  }

  applyDot(position, 17, 70, 1, pulse);
  setOpacity(travelSpine, 0.24);
  setTrailWindow(lerp(220, 690, progress), 0.34);
  setOpacity(destinationGroup, 0.2);

  setCandidateState(searchTop, progress < 0.32 ? "active" : "visited");
  setCandidateState(searchMid, progress < 0.24 ? "faint" : progress < 0.66 ? "active" : "visited");
  setCandidateState(searchBottom, progress < 0.56 ? "faint" : progress < 0.9 ? "active" : "visited");

  setOpacity(searchEchoTop, clamp((progress - 0.18) / 0.18, 0, 1) * 0.52);
  setOpacity(searchEchoMid, clamp((progress - 0.48) / 0.16, 0, 1) * 0.48);
  setOpacity(searchEchoBottom, clamp((progress - 0.76) / 0.12, 0, 1) * 0.44);
  setOpacity(searchArcTop, clamp((progress - 0.08) / 0.18, 0, 1) * 0.44);
  setOpacity(searchArcMid, clamp((progress - 0.32) / 0.18, 0, 1) * 0.42);
  setOpacity(searchArcBottom, clamp((progress - 0.62) / 0.18, 0, 1) * 0.4);
}

function renderTension(progress) {
  const entryProgress = clamp(progress / 0.34, 0, 1);
  const squeezeProgress = easeInOut(clamp((progress - 0.2) / 0.6, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.22, 0, 1));
  const position = mixPoint(points.preGate, points.gate, easeOut(entryProgress));

  applyDot(
    position,
    lerp(17, 19, squeezeProgress),
    lerp(68, 52, squeezeProgress),
    1,
    0.24 + pulseWave(progress, 1.4) * 0.08,
    lerp(1, 0.44, squeezeProgress),
    lerp(1, 1.72, squeezeProgress),
  );
  setOpacity(travelSpine, 0.12);
  setTrailWindow(lerp(690, 230, progress), 0.22 * residue);
  setOpacity(destinationGroup, 0.16);

  setCandidateState(searchTop, "visited");
  setCandidateState(searchMid, "visited");
  setCandidateState(searchBottom, "visited");
  setOpacity(searchTop, 0.18 * residue);
  setOpacity(searchMid, 0.16 * residue);
  setOpacity(searchBottom, 0.14 * residue);
  setOpacity(searchEchoTop, 0.18 * residue);
  setOpacity(searchEchoMid, 0.16 * residue);
  setOpacity(searchEchoBottom, 0.14 * residue);
  setOpacity(searchArcTop, 0.12 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcBottom, 0.1 * residue);

  setOpacity(thresholdGroup, 1);
  setRectX(wallLeft, lerp(670, 742, squeezeProgress));
  setRectX(wallRight, lerp(942, 870, squeezeProgress));
  setRectX(slitGuide, lerp(786, 830, squeezeProgress));
  setRectWidth(slitGuide, lerp(128, 40, squeezeProgress));
}

function renderTransformation(progress) {
  const moveProgress = easeOut(clamp(progress / 0.18, 0, 1));
  const chamberProgress = easeOut(clamp((progress - 0.12) / 0.36, 0, 1));
  const threadProgress = clamp((progress - 0.24) / 0.36, 0, 1);
  const supportProgress = clamp((progress - 0.42) / 0.3, 0, 1);
  const position = mixPoint(points.gate, points.transform, moveProgress);
  const groupScale = lerp(0.88, 1, chamberProgress);
  const thresholdFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));

  applyDot(position, lerp(19, 17, progress), lerp(52, 124, chamberProgress), 1, 0.24 + pulseWave(progress, 2.2) * 0.1);
  setOpacity(travelSpine, 0.08 * thresholdFade);
  setTrailWindow(200, 0.14 * thresholdFade);
  setOpacity(destinationGroup, 0.18 * (1 - chamberProgress));

  setOpacity(thresholdGroup, 0.92 * thresholdFade);
  setRectX(wallLeft, lerp(742, 706, chamberProgress));
  setRectX(wallRight, lerp(870, 906, chamberProgress));
  setRectX(slitGuide, lerp(830, 818, chamberProgress));
  setRectWidth(slitGuide, lerp(40, 64, chamberProgress));

  setOpacity(unfoldGroup, 1);
  unfoldGroup.setAttribute(
    "transform",
    `translate(${points.transform.x} ${points.transform.y}) scale(${groupScale} ${groupScale}) translate(${-points.transform.x} ${-points.transform.y})`,
  );
  orbitRing.setAttribute("r", lerp(56, 126, chamberProgress).toFixed(2));
  orbitRingSecondary.setAttribute("r", lerp(92, 158, chamberProgress).toFixed(2));
  setOpacity(orbitRing, chamberProgress * 0.92);
  setOpacity(orbitRingSecondary, chamberProgress * 0.48);

  frameParts.forEach((element) => setOpacity(element, chamberProgress * 0.9));
  [frameRuleTop, frameRuleBottom, framePierLeft, framePierRight].forEach((element) => {
    setOpacity(element, clamp((progress - 0.18) / 0.28, 0, 1) * 0.86);
  });

  setOpacity(centerThread, threadProgress * 0.92);
  applyStrokeReveal(centerThread, threadProgress, CENTER_THREAD_LENGTH);

  [supportLinkTop, supportLinkBottom].forEach((element, index) => {
    const local = clamp(supportProgress - index * 0.08, 0, 1);
    setOpacity(element, local * 0.82);
    applyStrokeReveal(element, local, index === 0 ? SUPPORT_TOP_LENGTH : SUPPORT_BOTTOM_LENGTH);
  });
  setOpacity(supportNodeTop, clamp(supportProgress - 0.02, 0, 1) * 0.86);
  setOpacity(supportNodeBottom, clamp(supportProgress - 0.1, 0, 1) * 0.82);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, points.final.x - points.transform.x, settle);
  const ringFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  const haloPulse = 0.18 + pulseWave(progress, 1.5) * 0.08;

  applyDot({ x: points.transform.x + shift, y: points.final.y }, 17, lerp(118, 82, progress), 1, haloPulse);
  setOpacity(travelSpine, 0);
  setTrailWindow(0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(thresholdGroup, 0);

  setOpacity(unfoldGroup, 1);
  unfoldGroup.setAttribute("transform", `translate(${shift.toFixed(2)} 0)`);
  orbitRing.setAttribute("r", lerp(126, 84, settle).toFixed(2));
  orbitRingSecondary.setAttribute("r", lerp(158, 112, settle).toFixed(2));
  setOpacity(orbitRing, 0.04 + ringFade * 0.08);
  setOpacity(orbitRingSecondary, 0.01 + ringFade * 0.03);

  frameParts.forEach((element) => setOpacity(element, 0.96));
  [frameRuleTop, frameRuleBottom, framePierLeft, framePierRight].forEach((element) => setOpacity(element, 0.9));
  setOpacity(centerThread, 0.76);
  applyStrokeReveal(centerThread, 1, CENTER_THREAD_LENGTH);
  [supportLinkTop, supportLinkBottom].forEach((element, index) => {
    setOpacity(element, lerp(index === 0 ? 0.32 : 0.28, 0, settle));
    applyStrokeReveal(element, 1, index === 0 ? SUPPORT_TOP_LENGTH : SUPPORT_BOTTOM_LENGTH);
  });
  setOpacity(supportNodeTop, lerp(0.34, 0, settle));
  setOpacity(supportNodeBottom, lerp(0.32, 0, settle));

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionHalo, 0.12);
  setOpacity(resolutionRule, 0.62);
  setCircleCenter(resolutionHalo, { x: points.transform.x + shift, y: points.final.y });
  resolutionHalo.setAttribute("r", lerp(128, 112, progress).toFixed(2));
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
