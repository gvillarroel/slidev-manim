const TOTAL_DURATION = 35_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 6_000 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 10_000 },
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
const mirrorAxis = document.getElementById("mirror-axis");

const candidateTop = document.getElementById("candidate-top");
const candidateMid = document.getElementById("candidate-mid");
const candidateBottom = document.getElementById("candidate-bottom");
const echoTop = document.getElementById("echo-top");
const echoMid = document.getElementById("echo-mid");
const echoBottom = document.getElementById("echo-bottom");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const tensionGroup = document.getElementById("tension-group");
const shutterLeft = document.getElementById("shutter-left");
const shutterRight = document.getElementById("shutter-right");
const slitGuide = document.getElementById("slit-guide");
const seamRule = document.getElementById("seam-rule");

const transformGroup = document.getElementById("transform-group");
const focusRing = document.getElementById("focus-ring");
const focusRingSecondary = document.getElementById("focus-ring-secondary");
const frameParts = [
  document.getElementById("frame-corner-tl"),
  document.getElementById("frame-corner-tr"),
  document.getElementById("frame-corner-bl"),
  document.getElementById("frame-corner-br"),
];
const frameRuleTop = document.getElementById("frame-rule-top");
const frameRuleBottom = document.getElementById("frame-rule-bottom");
const mirrorCore = document.getElementById("mirror-core");
const focusLine = document.getElementById("focus-line");
const echoLinkLeft = document.getElementById("echo-link-left");
const echoLinkRight = document.getElementById("echo-link-right");
const echoNodeLeft = document.getElementById("echo-node-left");
const echoNodeRight = document.getElementById("echo-node-right");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRule = document.getElementById("resolution-rule");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const FOCUS_LINE_LENGTH = focusLine.getTotalLength();
const ECHO_LEFT_LENGTH = echoLinkLeft.getTotalLength();
const ECHO_RIGHT_LENGTH = echoLinkRight.getTotalLength();

const COLORS = {
  gray: "#b5b5b5",
  lightGray: "#cfcfcf",
  dark: "#4f4f4f",
};

const points = {
  start: { x: 280, y: 450 },
  approach: { x: 430, y: 450 },
  searchTop: { x: 560, y: 322 },
  searchMid: { x: 656, y: 450 },
  searchBottom: { x: 560, y: 578 },
  preGate: { x: 760, y: 450 },
  seam: { x: 860, y: 450 },
  transform: { x: 940, y: 450 },
  final: { x: 860, y: 450 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "180 150 540 640",
  search: "240 148 560 652",
  tension: "690 168 370 654",
  transformation: "760 140 460 690",
  resolution: "676 72 420 780",
};

const PORTRAIT_STAGE_TRANSFORMS = {
  appearance: { x: 460, y: 450, scale: 1.04 },
  search: { x: 570, y: 450, scale: 1.08 },
  tension: { x: 860, y: 450, scale: 1.16 },
  transformation: { x: 936, y: 450, scale: 1.18 },
  resolution: { x: 860, y: 450, scale: 1.08 },
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
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
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
    setOpacity(element, 0.84);
    return;
  }
  if (mode === "visited") {
    setStrokeColor(element, COLORS.gray);
    setOpacity(element, 0.34);
    return;
  }
  if (mode === "faint") {
    setStrokeColor(element, COLORS.lightGray);
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
  setOpacity(mirrorAxis, 0);

  [
    candidateTop,
    candidateMid,
    candidateBottom,
    echoTop,
    echoMid,
    echoBottom,
    searchArcTop,
    searchArcMid,
    searchArcBottom,
  ].forEach((element) => setOpacity(element, 0));
  [candidateTop, candidateMid, candidateBottom].forEach((element) => setStrokeColor(element, COLORS.gray));

  setOpacity(tensionGroup, 0);
  setRectX(shutterLeft, 724);
  setRectWidth(shutterLeft, 102);
  setRectX(shutterRight, 894);
  setRectWidth(shutterRight, 102);
  setRectX(slitGuide, 844);
  setRectWidth(slitGuide, 32);
  setOpacity(seamRule, 0.62);

  setOpacity(transformGroup, 0);
  setOpacity(focusRing, 0);
  setOpacity(focusRingSecondary, 0);
  focusRing.setAttribute("r", "62");
  focusRingSecondary.setAttribute("r", "104");
  [
    ...frameParts,
    frameRuleTop,
    frameRuleBottom,
    mirrorCore,
    focusLine,
    echoLinkLeft,
    echoLinkRight,
    echoNodeLeft,
    echoNodeRight,
  ].forEach((element) => setOpacity(element, 0));
  applyStrokeReveal(focusLine, 0, FOCUS_LINE_LENGTH);
  applyStrokeReveal(echoLinkLeft, 0, ECHO_LEFT_LENGTH);
  applyStrokeReveal(echoLinkRight, 0, ECHO_RIGHT_LENGTH);
  transformGroup.setAttribute("transform", "");

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
  setOpacity(destinationGroup, 0.16 + progress * 0.12);
  setOpacity(mirrorAxis, 0.22 + progress * 0.12);

  setCandidateState(candidateTop, progress > 0.62 ? "faint" : "hidden");
  setCandidateState(candidateMid, progress > 0.72 ? "faint" : "hidden");
  setCandidateState(candidateBottom, progress > 0.8 ? "faint" : "hidden");
}

function renderSearch(progress) {
  const pulse = 0.18 + pulseWave(progress, 2.2) * 0.16;
  let position = points.searchTop;

  if (progress < 0.22) {
    position = mixPoint(points.approach, points.searchTop, easeOut(progress / 0.22));
  } else if (progress < 0.56) {
    position = mixPoint(points.searchTop, points.searchMid, easeInOut((progress - 0.22) / 0.34));
  } else if (progress < 0.84) {
    position = mixPoint(points.searchMid, points.searchBottom, easeInOut((progress - 0.56) / 0.28));
  } else {
    position = mixPoint(points.searchBottom, points.preGate, easeOut((progress - 0.84) / 0.16));
  }

  applyDot(position, 17, 70, 1, pulse);
  setOpacity(travelSpine, 0.24);
  setTrailWindow(lerp(220, 708, progress), 0.34);
  setOpacity(destinationGroup, 0.24);
  setOpacity(mirrorAxis, 0.34);

  setCandidateState(candidateTop, progress < 0.28 ? "active" : "visited");
  setCandidateState(candidateMid, progress < 0.22 ? "faint" : progress < 0.62 ? "active" : "visited");
  setCandidateState(candidateBottom, progress < 0.56 ? "faint" : progress < 0.9 ? "active" : "visited");

  setOpacity(echoTop, clamp((progress - 0.14) / 0.16, 0, 1) * 0.54);
  setOpacity(echoMid, clamp((progress - 0.42) / 0.16, 0, 1) * 0.5);
  setOpacity(echoBottom, clamp((progress - 0.72) / 0.12, 0, 1) * 0.46);
  setOpacity(searchArcTop, clamp((progress - 0.06) / 0.18, 0, 1) * 0.42);
  setOpacity(searchArcMid, clamp((progress - 0.3) / 0.18, 0, 1) * 0.4);
  setOpacity(searchArcBottom, clamp((progress - 0.6) / 0.18, 0, 1) * 0.38);
}

function renderTension(progress) {
  const entryProgress = clamp(progress / 0.34, 0, 1);
  const squeezeProgress = easeInOut(clamp((progress - 0.18) / 0.6, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.24, 0, 1));
  const position = mixPoint(points.preGate, points.seam, easeOut(entryProgress));

  applyDot(
    position,
    lerp(17, 19, squeezeProgress),
    lerp(68, 54, squeezeProgress),
    1,
    0.24 + pulseWave(progress, 1.4) * 0.08,
    lerp(1, 0.42, squeezeProgress),
    lerp(1, 1.74, squeezeProgress),
  );
  setOpacity(travelSpine, 0.12);
  setTrailWindow(lerp(708, 224, progress), 0.22 * residue);
  setOpacity(destinationGroup, 0.18);
  setOpacity(mirrorAxis, 0.28);

  setCandidateState(candidateTop, "visited");
  setCandidateState(candidateMid, "visited");
  setCandidateState(candidateBottom, "visited");
  setOpacity(candidateTop, 0.18 * residue);
  setOpacity(candidateMid, 0.16 * residue);
  setOpacity(candidateBottom, 0.14 * residue);
  setOpacity(echoTop, 0.18 * residue);
  setOpacity(echoMid, 0.16 * residue);
  setOpacity(echoBottom, 0.14 * residue);
  setOpacity(searchArcTop, 0.12 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcBottom, 0.1 * residue);

  setOpacity(tensionGroup, 1);
  setRectX(shutterLeft, lerp(724, 800, squeezeProgress));
  setRectWidth(shutterLeft, lerp(102, 40, squeezeProgress));
  setRectX(shutterRight, lerp(894, 880, squeezeProgress));
  setRectWidth(shutterRight, lerp(102, 40, squeezeProgress));
  setRectX(slitGuide, lerp(844, 846, squeezeProgress));
  setRectWidth(slitGuide, lerp(32, 28, squeezeProgress));
  setOpacity(seamRule, lerp(0.62, 0.18, squeezeProgress));
}

function renderTransformation(progress) {
  const moveProgress = easeOut(clamp(progress / 0.18, 0, 1));
  const chamberProgress = easeOut(clamp((progress - 0.1) / 0.38, 0, 1));
  const coreProgress = clamp((progress - 0.22) / 0.34, 0, 1);
  const echoProgress = clamp((progress - 0.42) / 0.28, 0, 1);
  const position = mixPoint(points.seam, points.transform, moveProgress);
  const groupScale = lerp(0.9, 1, chamberProgress);
  const tensionFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));

  applyDot(position, lerp(19, 17, progress), lerp(54, 122, chamberProgress), 1, 0.24 + pulseWave(progress, 2.2) * 0.1);
  setOpacity(travelSpine, 0.08 * tensionFade);
  setTrailWindow(196, 0.14 * tensionFade);
  setOpacity(destinationGroup, 0.18 * (1 - chamberProgress));
  setOpacity(mirrorAxis, 0.22 * (1 - chamberProgress));

  setOpacity(tensionGroup, 0.92 * tensionFade);
  setRectX(shutterLeft, lerp(800, 760, chamberProgress));
  setRectWidth(shutterLeft, lerp(40, 30, chamberProgress));
  setRectX(shutterRight, lerp(880, 950, chamberProgress));
  setRectWidth(shutterRight, lerp(40, 30, chamberProgress));
  setOpacity(seamRule, 0.12 * tensionFade);

  setOpacity(transformGroup, 1);
  transformGroup.setAttribute(
    "transform",
    `translate(${points.transform.x} ${points.transform.y}) scale(${groupScale} ${groupScale}) translate(${-points.transform.x} ${-points.transform.y})`,
  );
  focusRing.setAttribute("r", lerp(62, 110, chamberProgress).toFixed(2));
  focusRingSecondary.setAttribute("r", lerp(104, 154, chamberProgress).toFixed(2));
  setOpacity(focusRing, chamberProgress * 0.9);
  setOpacity(focusRingSecondary, chamberProgress * 0.48);

  frameParts.forEach((element) => setOpacity(element, chamberProgress * 0.9));
  [frameRuleTop, frameRuleBottom, mirrorCore].forEach((element) => {
    setOpacity(element, clamp((progress - 0.16) / 0.28, 0, 1) * 0.88);
  });

  setOpacity(focusLine, coreProgress * 0.92);
  applyStrokeReveal(focusLine, coreProgress, FOCUS_LINE_LENGTH);

  [echoLinkLeft, echoLinkRight].forEach((element, index) => {
    const local = clamp(echoProgress - index * 0.08, 0, 1);
    setOpacity(element, local * 0.82);
    applyStrokeReveal(element, local, index === 0 ? ECHO_LEFT_LENGTH : ECHO_RIGHT_LENGTH);
  });
  setOpacity(echoNodeLeft, clamp(echoProgress - 0.02, 0, 1) * 0.84);
  setOpacity(echoNodeRight, clamp(echoProgress - 0.1, 0, 1) * 0.82);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, points.final.x - points.transform.x, settle);
  const ringFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  const haloPulse = 0.18 + pulseWave(progress, 1.5) * 0.08;

  applyDot({ x: points.transform.x + shift, y: points.final.y }, 17, lerp(116, 82, progress), 1, haloPulse);
  setOpacity(travelSpine, 0);
  setTrailWindow(0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(mirrorAxis, 0);
  setOpacity(tensionGroup, 0);

  setOpacity(transformGroup, 1);
  transformGroup.setAttribute("transform", `translate(${shift.toFixed(2)} 0)`);
  focusRing.setAttribute("r", lerp(110, 82, settle).toFixed(2));
  focusRingSecondary.setAttribute("r", lerp(154, 112, settle).toFixed(2));
  setOpacity(focusRing, 0.04 + ringFade * 0.07);
  setOpacity(focusRingSecondary, 0.01 + ringFade * 0.03);

  frameParts.forEach((element) => setOpacity(element, 0.94));
  [frameRuleTop, frameRuleBottom, mirrorCore].forEach((element) => setOpacity(element, 0.9));
  setOpacity(focusLine, 0.78);
  applyStrokeReveal(focusLine, 1, FOCUS_LINE_LENGTH);
  [echoLinkLeft, echoLinkRight].forEach((element, index) => {
    setOpacity(element, lerp(index === 0 ? 0.3 : 0.26, 0, settle));
    applyStrokeReveal(element, 1, index === 0 ? ECHO_LEFT_LENGTH : ECHO_RIGHT_LENGTH);
  });
  setOpacity(echoNodeLeft, lerp(0.32, 0, settle));
  setOpacity(echoNodeRight, lerp(0.3, 0, settle));

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionHalo, 0.12);
  setOpacity(resolutionRule, 0.62);
  setCircleCenter(resolutionHalo, { x: points.transform.x + shift, y: points.final.y });
  resolutionHalo.setAttribute("r", lerp(132, 112, progress).toFixed(2));
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
