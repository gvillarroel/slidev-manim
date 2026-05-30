const TOTAL_DURATION = 32_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 6_500 },
  { id: "tension", label: "tension", duration: 5_500 },
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

const searchTop = document.getElementById("search-slot-top");
const searchMid = document.getElementById("search-slot-mid");
const searchBottom = document.getElementById("search-slot-bottom");
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoMid = document.getElementById("search-echo-mid");
const searchEchoBottom = document.getElementById("search-echo-bottom");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const shearGroup = document.getElementById("shear-group");
const shearTopSlab = document.getElementById("shear-top-slab");
const shearBottomSlab = document.getElementById("shear-bottom-slab");
const shearSeamGuide = document.getElementById("shear-seam-guide");
const shearTrackTop = document.getElementById("shear-track-top");
const shearTrackBottom = document.getElementById("shear-track-bottom");
const pressureTickTop = document.getElementById("pressure-tick-top");
const pressureTickBottom = document.getElementById("pressure-tick-bottom");

const transformGroup = document.getElementById("transform-group");
const transformTopShelf = document.getElementById("transform-top-shelf");
const transformTopStep = document.getElementById("transform-top-step");
const transformBottomShelf = document.getElementById("transform-bottom-shelf");
const transformBottomStep = document.getElementById("transform-bottom-step");
const outerCornerTl = document.getElementById("outer-corner-tl");
const outerCornerTr = document.getElementById("outer-corner-tr");
const outerCornerBl = document.getElementById("outer-corner-bl");
const outerCornerBr = document.getElementById("outer-corner-br");
const centerSeam = document.getElementById("center-seam");
const braceTop = document.getElementById("brace-top");
const braceBottom = document.getElementById("brace-bottom");
const braceNodeTop = document.getElementById("brace-node-top");
const braceNodeBottom = document.getElementById("brace-node-bottom");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionDatum = document.getElementById("resolution-datum");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const CENTER_SEAM_LENGTH = centerSeam.getTotalLength();
const BRACE_TOP_LENGTH = braceTop.getTotalLength();
const BRACE_BOTTOM_LENGTH = braceBottom.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  gray: "#b5b5b5",
  dark: "#4f4f4f",
};

const points = {
  start: { x: 280, y: 450 },
  approach: { x: 420, y: 450 },
  searchTop: { x: 528, y: 316 },
  searchMid: { x: 664, y: 450 },
  searchBottom: { x: 520, y: 582 },
  preShear: { x: 706, y: 486 },
  shear: { x: 840, y: 450 },
  transform: { x: 924, y: 450 },
  final: { x: 860, y: 450 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "186 166 522 624",
  search: "260 164 504 632",
  tension: "650 168 392 650",
  transformation: "708 174 392 612",
  resolution: "696 178 372 588",
};

const PORTRAIT_STAGE_TRANSFORMS = {
  appearance: { x: 438, y: 450, scale: 1.1 },
  search: { x: 568, y: 450, scale: 1.14 },
  tension: { x: 846, y: 450, scale: 1.18 },
  transformation: { x: 900, y: 450, scale: 1.24 },
  resolution: { x: 860, y: 438, scale: 1.3 },
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
    setStrokeColor(element, COLORS.primaryRed);
    setOpacity(element, 0.96);
    return;
  }
  if (mode === "visited") {
    setStrokeColor(element, COLORS.mutedRed);
    setOpacity(element, 0.52);
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

  [
    searchTop,
    searchMid,
    searchBottom,
    searchEchoTop,
    searchEchoMid,
    searchEchoBottom,
    searchArcTop,
    searchArcMid,
    searchArcBottom,
  ].forEach((element) => setOpacity(element, 0));
  [searchTop, searchMid, searchBottom].forEach((element) => setStrokeColor(element, COLORS.gray));

  setOpacity(shearGroup, 0);
  setRectX(shearTopSlab, 752);
  setRectX(shearBottomSlab, 618);
  setTransform(shearSeamGuide, points.shear, 1, 1);
  [shearSeamGuide, shearTrackTop, shearTrackBottom, pressureTickTop, pressureTickBottom].forEach((element) => setOpacity(element, 0));

  setOpacity(transformGroup, 0);
  transformGroup.setAttribute("transform", "");
  [
    transformTopShelf,
    transformTopStep,
    transformBottomShelf,
    transformBottomStep,
    outerCornerTl,
    outerCornerTr,
    outerCornerBl,
    outerCornerBr,
    centerSeam,
    braceTop,
    braceBottom,
    braceNodeTop,
    braceNodeBottom,
  ].forEach((element) => setOpacity(element, 0));
  applyStrokeReveal(centerSeam, 0, CENTER_SEAM_LENGTH);
  applyStrokeReveal(braceTop, 0, BRACE_TOP_LENGTH);
  applyStrokeReveal(braceBottom, 0, BRACE_BOTTOM_LENGTH);

  setOpacity(resolutionGroup, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionDatum, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.approach, eased);
  const haloPulse = 0.22 + pulseWave(progress, 1.1) * 0.18;

  applyDot(position, lerp(14, 18, eased), lerp(48, 82, eased), 0.92, haloPulse);
  setOpacity(travelSpine, 0.18 + progress * 0.08);
  setTrailWindow(232 * eased, 0.24);
  setOpacity(destinationGroup, 0.2 + progress * 0.12);

  setCandidateState(searchTop, progress > 0.62 ? "faint" : "hidden");
  setCandidateState(searchMid, progress > 0.72 ? "faint" : "hidden");
  setCandidateState(searchBottom, progress > 0.82 ? "faint" : "hidden");
}

function renderSearch(progress) {
  const pulse = 0.2 + pulseWave(progress, 2.2) * 0.14;
  let position = points.searchTop;

  if (progress < 0.24) {
    position = mixPoint(points.approach, points.searchTop, easeOut(progress / 0.24));
  } else if (progress < 0.58) {
    position = mixPoint(points.searchTop, points.searchMid, easeInOut((progress - 0.24) / 0.34));
  } else if (progress < 0.88) {
    position = mixPoint(points.searchMid, points.searchBottom, easeInOut((progress - 0.58) / 0.3));
  } else {
    position = mixPoint(points.searchBottom, points.preShear, easeOut((progress - 0.88) / 0.12));
  }

  applyDot(position, 17, 70, 1, pulse);
  setOpacity(travelSpine, 0.24);
  setTrailWindow(lerp(220, 700, progress), 0.32);
  setOpacity(destinationGroup, 0.24);

  setCandidateState(searchTop, progress < 0.34 ? "active" : "visited");
  setCandidateState(searchMid, progress < 0.24 ? "faint" : progress < 0.7 ? "active" : "visited");
  setCandidateState(searchBottom, progress < 0.58 ? "faint" : progress < 0.92 ? "active" : "visited");

  setOpacity(searchEchoTop, clamp((progress - 0.18) / 0.18, 0, 1) * 0.46);
  setOpacity(searchEchoMid, clamp((progress - 0.5) / 0.14, 0, 1) * 0.42);
  setOpacity(searchEchoBottom, clamp((progress - 0.8) / 0.1, 0, 1) * 0.4);
  setOpacity(searchArcTop, clamp((progress - 0.08) / 0.16, 0, 1) * 0.42);
  setOpacity(searchArcMid, clamp((progress - 0.34) / 0.16, 0, 1) * 0.4);
  setOpacity(searchArcBottom, clamp((progress - 0.62) / 0.16, 0, 1) * 0.38);
}

function renderTension(progress) {
  const entryProgress = clamp(progress / 0.32, 0, 1);
  const squeezeProgress = easeInOut(clamp((progress - 0.16) / 0.64, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.24, 0, 1));
  const position = mixPoint(points.preShear, points.shear, easeOut(entryProgress));

  applyDot(
    position,
    lerp(17, 19, squeezeProgress),
    lerp(68, 54, squeezeProgress),
    1,
    0.22 + pulseWave(progress, 1.4) * 0.08,
    lerp(1, 0.52, squeezeProgress),
    lerp(1, 1.66, squeezeProgress),
  );
  setOpacity(travelSpine, 0.1);
  setTrailWindow(lerp(700, 220, progress), 0.2 * residue);
  setOpacity(destinationGroup, 0.14);

  setCandidateState(searchTop, "visited");
  setCandidateState(searchMid, "visited");
  setCandidateState(searchBottom, "visited");
  setOpacity(searchEchoTop, 0.16 * residue);
  setOpacity(searchEchoMid, 0.14 * residue);
  setOpacity(searchEchoBottom, 0.12 * residue);
  setOpacity(searchArcTop, 0.12 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcBottom, 0.1 * residue);

  setOpacity(shearGroup, 1);
  setRectX(shearTopSlab, lerp(752, 706, squeezeProgress));
  setRectX(shearBottomSlab, lerp(618, 776, squeezeProgress));
  setTransform(shearSeamGuide, points.shear, lerp(1, 0.64, squeezeProgress), 1);
  setOpacity(shearSeamGuide, 0.42 + squeezeProgress * 0.26);
  setOpacity(shearTrackTop, 0.5);
  setOpacity(shearTrackBottom, 0.5);
  setOpacity(pressureTickTop, 0.72);
  setOpacity(pressureTickBottom, 0.72);
}

function renderTransformation(progress) {
  const moveProgress = easeOut(clamp(progress / 0.18, 0, 1));
  const frameProgress = easeOut(clamp((progress - 0.1) / 0.34, 0, 1));
  const seamProgress = clamp((progress - 0.28) / 0.28, 0, 1);
  const braceProgress = clamp((progress - 0.44) / 0.26, 0, 1);
  const shearFade = 1 - easeOut(clamp(progress / 0.3, 0, 1));
  const position = mixPoint(points.shear, points.transform, moveProgress);
  const groupScale = lerp(0.92, 1, frameProgress);

  applyDot(position, lerp(19, 17, progress), lerp(54, 118, frameProgress), 1, 0.24 + pulseWave(progress, 2.1) * 0.1);
  setOpacity(travelSpine, 0.08 * shearFade);
  setTrailWindow(190, 0.12 * shearFade);
  setOpacity(destinationGroup, 0.18 * (1 - frameProgress));

  setOpacity(shearGroup, 0.94 * shearFade);
  setRectX(shearTopSlab, lerp(706, 730, frameProgress));
  setRectX(shearBottomSlab, lerp(776, 742, frameProgress));
  setTransform(shearSeamGuide, points.shear, lerp(0.64, 1, frameProgress), 1);
  setOpacity(shearSeamGuide, 0.52 * shearFade);
  setOpacity(shearTrackTop, 0.42 * shearFade);
  setOpacity(shearTrackBottom, 0.42 * shearFade);
  setOpacity(pressureTickTop, 0.6 * shearFade);
  setOpacity(pressureTickBottom, 0.6 * shearFade);

  setOpacity(transformGroup, 1);
  transformGroup.setAttribute(
    "transform",
    `translate(${points.transform.x} ${points.transform.y}) scale(${groupScale} ${groupScale}) translate(${-points.transform.x} ${-points.transform.y})`,
  );
  [
    transformTopShelf,
    transformTopStep,
    transformBottomShelf,
    transformBottomStep,
    outerCornerTl,
    outerCornerTr,
    outerCornerBl,
    outerCornerBr,
  ].forEach((element) => setOpacity(element, frameProgress * 0.94));

  setOpacity(centerSeam, seamProgress * 0.92);
  applyStrokeReveal(centerSeam, seamProgress, CENTER_SEAM_LENGTH);

  [braceTop, braceBottom].forEach((element, index) => {
    const local = clamp(braceProgress - index * 0.08, 0, 1);
    setOpacity(element, local * 0.78);
    applyStrokeReveal(element, local, index === 0 ? BRACE_TOP_LENGTH : BRACE_BOTTOM_LENGTH);
  });
  setOpacity(braceNodeTop, clamp(braceProgress - 0.02, 0, 1) * 0.8);
  setOpacity(braceNodeBottom, clamp(braceProgress - 0.1, 0, 1) * 0.76);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, points.final.x - points.transform.x, settle);
  const braceFade = lerp(0.34, 0.06, settle);
  const haloPulse = 0.14 + pulseWave(progress, 1.3) * 0.06;

  applyDot({ x: points.transform.x + shift, y: points.final.y }, 17, lerp(112, 78, progress), 1, haloPulse);
  setOpacity(travelSpine, 0);
  setTrailWindow(0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(shearGroup, 0);

  setOpacity(transformGroup, 1);
  transformGroup.setAttribute("transform", `translate(${shift.toFixed(2)} 0)`);
  [
    transformTopShelf,
    transformTopStep,
    transformBottomShelf,
    transformBottomStep,
    outerCornerTl,
    outerCornerTr,
    outerCornerBl,
    outerCornerBr,
  ].forEach((element) => setOpacity(element, 0.96));
  setOpacity(centerSeam, 0.82);
  applyStrokeReveal(centerSeam, 1, CENTER_SEAM_LENGTH);
  setOpacity(braceTop, braceFade);
  setOpacity(braceBottom, braceFade * 0.92);
  applyStrokeReveal(braceTop, 1, BRACE_TOP_LENGTH);
  applyStrokeReveal(braceBottom, 1, BRACE_BOTTOM_LENGTH);
  setOpacity(braceNodeTop, braceFade * 0.84);
  setOpacity(braceNodeBottom, braceFade * 0.78);

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionHalo, 0.1);
  setOpacity(resolutionDatum, 0.62);
  setCircleCenter(resolutionHalo, { x: points.transform.x + shift, y: points.final.y });
  resolutionHalo.setAttribute("r", lerp(126, 110, progress).toFixed(2));
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
