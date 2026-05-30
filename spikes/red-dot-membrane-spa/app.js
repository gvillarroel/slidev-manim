const TOTAL_DURATION = 32_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_200 },
  { id: "search", label: "search for form", duration: 6_200 },
  { id: "tension", label: "tension", duration: 5_400 },
  { id: "transformation", label: "transformation", duration: 6_000 },
  { id: "resolution", label: "resolution", duration: 9_200 },
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
const destinationCore = document.getElementById("destination-core");

const searchTop = document.getElementById("search-curve-top");
const searchMid = document.getElementById("search-curve-mid");
const searchBottom = document.getElementById("search-curve-bottom");
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoMid = document.getElementById("search-echo-mid");
const searchEchoBottom = document.getElementById("search-echo-bottom");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const tensionGroup = document.getElementById("tension-group");
const membraneUpper = document.getElementById("membrane-upper");
const membraneLower = document.getElementById("membrane-lower");
const pinchField = document.getElementById("pinch-field");
const tensionEchoTop = document.getElementById("tension-echo-top");
const tensionEchoBottom = document.getElementById("tension-echo-bottom");

const transformationGroup = document.getElementById("transformation-group");
const rippleInner = document.getElementById("ripple-inner");
const rippleOuter = document.getElementById("ripple-outer");
const frameParts = [
  document.getElementById("frame-corner-tl"),
  document.getElementById("frame-corner-tr"),
  document.getElementById("frame-corner-bl"),
  document.getElementById("frame-corner-br"),
];
const frameLeft = document.getElementById("frame-left");
const frameRight = document.getElementById("frame-right");
const waveTop = document.getElementById("wave-top");
const waveBottom = document.getElementById("wave-bottom");
const axisLine = document.getElementById("axis-line");
const tetherTopLeft = document.getElementById("tether-top-left");
const tetherTopRight = document.getElementById("tether-top-right");
const tetherBottomLeft = document.getElementById("tether-bottom-left");
const tetherBottomRight = document.getElementById("tether-bottom-right");
const tethers = [tetherTopLeft, tetherTopRight, tetherBottomLeft, tetherBottomRight];

const resolutionGroup = document.getElementById("resolution-group");
const calmHalo = document.getElementById("calm-halo");
const settleRule = document.getElementById("settle-rule");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const WAVE_TOP_LENGTH = waveTop.getTotalLength();
const WAVE_BOTTOM_LENGTH = waveBottom.getTotalLength();
const AXIS_LENGTH = axisLine.getTotalLength();
const TETHER_LENGTHS = tethers.map((element) => element.getTotalLength());

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  gray: "#b5b5b5",
  dark: "#4f4f4f",
};

const points = {
  start: { x: 250, y: 450 },
  approach: { x: 430, y: 450 },
  searchTop: { x: 556, y: 332 },
  searchMid: { x: 662, y: 450 },
  searchBottom: { x: 556, y: 566 },
  preGate: { x: 758, y: 450 },
  gate: { x: 860, y: 450 },
  transform: { x: 968, y: 450 },
  final: { x: 880, y: 450 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "130 156 620 648",
  search: "228 156 560 648",
  tension: "674 164 420 632",
  transformation: "628 124 560 654",
  resolution: "520 92 680 716",
};

const PORTRAIT_STAGE_TRANSFORMS = {
  appearance: { x: 430, y: 450, scale: 1.04 },
  search: { x: 560, y: 450, scale: 1.08 },
  tension: { x: 880, y: 450, scale: 1.13 },
  transformation: { x: 930, y: 450, scale: 1.08 },
  resolution: { x: 880, y: 450, scale: 0.98 },
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

function setPath(element, d) {
  element.setAttribute("d", d);
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
    setOpacity(element, 0.16);
    return;
  }
  setStrokeColor(element, COLORS.gray);
  setOpacity(element, 0);
}

function buildMembranePath(topLift, bottomLift, sideInset) {
  const left = 818 + sideInset;
  const right = 942 - sideInset;
  const upperY = 450 - topLift;
  const lowerY = 450 + bottomLift;
  setPath(
    membraneUpper,
    `M ${left} 450 C ${lerp(left + 18, left + 34, 0.6)} 450, 846 ${upperY}, 860 ${upperY} C 874 ${upperY}, 888 450, ${right} 450`,
  );
  setPath(
    membraneLower,
    `M ${left} 450 C ${lerp(left + 18, left + 34, 0.6)} 450, 846 ${lowerY}, 860 ${lowerY} C 874 ${lowerY}, 888 450, ${right} 450`,
  );
}

function resetScene() {
  applyDot(points.start, 18, 72, 0, 0);
  setOpacity(travelSpine, 0);
  setTrailWindow(0, 0);

  setOpacity(destinationGroup, 0);
  setOpacity(destinationCore, 0);

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

  setOpacity(tensionGroup, 0);
  setOpacity(membraneUpper, 0);
  setOpacity(membraneLower, 0);
  buildMembranePath(14, 14, 0);
  setOpacity(pinchField, 0);
  setOpacity(tensionEchoTop, 0);
  setOpacity(tensionEchoBottom, 0);

  setOpacity(transformationGroup, 0);
  setOpacity(rippleInner, 0);
  setOpacity(rippleOuter, 0);
  rippleInner.setAttribute("r", "58");
  rippleOuter.setAttribute("r", "92");
  [...frameParts, frameLeft, frameRight, waveTop, waveBottom, axisLine, ...tethers].forEach((element) => setOpacity(element, 0));
  applyStrokeReveal(waveTop, 0, WAVE_TOP_LENGTH);
  applyStrokeReveal(waveBottom, 0, WAVE_BOTTOM_LENGTH);
  applyStrokeReveal(axisLine, 0, AXIS_LENGTH);
  tethers.forEach((element, index) => applyStrokeReveal(element, 0, TETHER_LENGTHS[index]));
  transformationGroup.setAttribute("transform", "");

  setOpacity(resolutionGroup, 0);
  setOpacity(calmHalo, 0);
  setOpacity(settleRule, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.approach, eased);
  const haloPulse = 0.22 + pulseWave(progress, 1.15) * 0.16;

  applyDot(position, lerp(14, 18, eased), lerp(46, 78, eased), 0.92, haloPulse);
  setOpacity(travelSpine, 0.18 + progress * 0.08);
  setTrailWindow(230 * eased, 0.24);
  setOpacity(destinationGroup, 0.16 + progress * 0.1);
  setOpacity(destinationCore, 0.08 + progress * 0.12);

  setCandidateState(searchTop, progress > 0.54 ? "faint" : "hidden");
  setCandidateState(searchMid, progress > 0.66 ? "faint" : "hidden");
  setCandidateState(searchBottom, progress > 0.78 ? "faint" : "hidden");
}

function renderSearch(progress) {
  const pulse = 0.2 + pulseWave(progress, 2.1) * 0.16;
  let position = points.searchTop;

  if (progress < 0.26) {
    position = mixPoint(points.approach, points.searchTop, easeOut(progress / 0.26));
  } else if (progress < 0.56) {
    position = mixPoint(points.searchTop, points.searchMid, easeInOut((progress - 0.26) / 0.3));
  } else if (progress < 0.84) {
    position = mixPoint(points.searchMid, points.searchBottom, easeInOut((progress - 0.56) / 0.28));
  } else {
    position = mixPoint(points.searchBottom, points.preGate, easeOut((progress - 0.84) / 0.16));
  }

  applyDot(position, 17, 70, 1, pulse);
  setOpacity(travelSpine, 0.24);
  setTrailWindow(lerp(230, 760, progress), 0.34);
  setOpacity(destinationGroup, 0.2);
  setOpacity(destinationCore, 0.14);

  setCandidateState(searchTop, progress < 0.34 ? "active" : "visited");
  setCandidateState(searchMid, progress < 0.26 ? "faint" : progress < 0.68 ? "active" : "visited");
  setCandidateState(searchBottom, progress < 0.56 ? "faint" : progress < 0.92 ? "active" : "visited");

  setOpacity(searchEchoTop, clamp((progress - 0.18) / 0.16, 0, 1) * 0.52);
  setOpacity(searchEchoMid, clamp((progress - 0.46) / 0.16, 0, 1) * 0.48);
  setOpacity(searchEchoBottom, clamp((progress - 0.74) / 0.14, 0, 1) * 0.44);
  setOpacity(searchArcTop, clamp((progress - 0.08) / 0.16, 0, 1) * 0.42);
  setOpacity(searchArcMid, clamp((progress - 0.32) / 0.18, 0, 1) * 0.4);
  setOpacity(searchArcBottom, clamp((progress - 0.62) / 0.18, 0, 1) * 0.38);
}

function renderTension(progress) {
  const entryProgress = clamp(progress / 0.34, 0, 1);
  const pinchProgress = easeInOut(clamp((progress - 0.18) / 0.58, 0, 1));
  const residue = 1 - easeOut(clamp(progress / 0.24, 0, 1));
  const position = mixPoint(points.preGate, points.gate, easeOut(entryProgress));

  applyDot(
    position,
    lerp(17, 19, pinchProgress),
    lerp(68, 52, pinchProgress),
    1,
    0.24 + pulseWave(progress, 1.5) * 0.08,
    lerp(1, 0.58, pinchProgress),
    lerp(1, 1.52, pinchProgress),
  );
  setOpacity(travelSpine, 0.12);
  setTrailWindow(lerp(760, 240, progress), 0.22 * residue);
  setOpacity(destinationGroup, 0.12);
  setOpacity(destinationCore, 0.08);

  setCandidateState(searchTop, "visited");
  setCandidateState(searchMid, "visited");
  setCandidateState(searchBottom, "visited");
  setOpacity(searchTop, 0.18 * residue);
  setOpacity(searchMid, 0.16 * residue);
  setOpacity(searchBottom, 0.14 * residue);
  setOpacity(searchEchoTop, 0.18 * residue);
  setOpacity(searchEchoMid, 0.16 * residue);
  setOpacity(searchEchoBottom, 0.14 * residue);
  setOpacity(searchArcTop, 0.14 * residue);
  setOpacity(searchArcMid, 0.12 * residue);
  setOpacity(searchArcBottom, 0.1 * residue);

  setOpacity(tensionGroup, 1);
  setOpacity(membraneUpper, 0.96);
  setOpacity(membraneLower, 0.96);
  buildMembranePath(lerp(14, 52, pinchProgress), lerp(14, 52, pinchProgress), lerp(0, 26, pinchProgress));
  pinchField.setAttribute("rx", lerp(82, 62, pinchProgress).toFixed(2));
  pinchField.setAttribute("ry", lerp(116, 96, pinchProgress).toFixed(2));
  setOpacity(pinchField, 0.08 + pinchProgress * 0.24);
  setOpacity(tensionEchoTop, 0.24 + pulseWave(progress, 1.2) * 0.12);
  setOpacity(tensionEchoBottom, 0.2 + pulseWave(progress, 1.2) * 0.1);
}

function renderTransformation(progress) {
  const moveProgress = easeOut(clamp(progress / 0.18, 0, 1));
  const frameProgress = clamp((progress - 0.1) / 0.32, 0, 1);
  const waveProgress = clamp((progress - 0.16) / 0.28, 0, 1);
  const axisProgress = clamp((progress - 0.26) / 0.24, 0, 1);
  const tetherProgress = clamp((progress - 0.34) / 0.3, 0, 1);
  const rippleProgress = clamp((progress - 0.12) / 0.26, 0, 1);
  const position = mixPoint(points.gate, points.transform, moveProgress);
  const groupScale = lerp(0.9, 1, easeOut(frameProgress));
  const tensionFade = 1 - easeOut(clamp(progress / 0.32, 0, 1));

  applyDot(position, lerp(19, 17, progress), lerp(52, 122, frameProgress), 1, 0.24 + pulseWave(progress, 2.1) * 0.1);
  setOpacity(travelSpine, 0.08 * tensionFade);
  setTrailWindow(220, 0.14 * tensionFade);
  setOpacity(destinationGroup, 0.12 * (1 - frameProgress));
  setOpacity(destinationCore, 0.12 * (1 - frameProgress));

  setOpacity(tensionGroup, 0.92 * tensionFade);
  setOpacity(membraneUpper, 0.96 * tensionFade);
  setOpacity(membraneLower, 0.96 * tensionFade);
  buildMembranePath(lerp(52, 28, frameProgress), lerp(52, 28, frameProgress), lerp(26, 12, frameProgress));
  setOpacity(pinchField, (0.12 + 0.18 * tensionFade) * tensionFade);
  setOpacity(tensionEchoTop, 0.3 * tensionFade);
  setOpacity(tensionEchoBottom, 0.28 * tensionFade);

  setOpacity(transformationGroup, 1);
  transformationGroup.setAttribute(
    "transform",
    `translate(${points.transform.x} ${points.transform.y}) scale(${groupScale} ${groupScale}) translate(${-points.transform.x} ${-points.transform.y})`,
  );

  rippleInner.setAttribute("r", lerp(58, 112, rippleProgress).toFixed(2));
  rippleOuter.setAttribute("r", lerp(92, 150, rippleProgress).toFixed(2));
  setOpacity(rippleInner, rippleProgress * 0.9);
  setOpacity(rippleOuter, rippleProgress * 0.48);

  frameParts.forEach((element) => setOpacity(element, frameProgress * 0.92));
  setOpacity(frameLeft, frameProgress * 0.88);
  setOpacity(frameRight, frameProgress * 0.88);
  setOpacity(waveTop, waveProgress * 0.94);
  setOpacity(waveBottom, waveProgress * 0.94);
  applyStrokeReveal(waveTop, waveProgress, WAVE_TOP_LENGTH);
  applyStrokeReveal(waveBottom, waveProgress, WAVE_BOTTOM_LENGTH);

  setOpacity(axisLine, axisProgress * 0.9);
  applyStrokeReveal(axisLine, axisProgress, AXIS_LENGTH);

  tethers.forEach((element, index) => {
    const local = clamp(tetherProgress - index * 0.06, 0, 1);
    setOpacity(element, local * 0.82);
    applyStrokeReveal(element, local, TETHER_LENGTHS[index]);
  });
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, points.final.x - points.transform.x, settle);
  const rippleFade = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  const haloPulse = 0.18 + pulseWave(progress, 1.4) * 0.08;

  applyDot({ x: points.transform.x + shift, y: points.final.y }, 17, lerp(118, 80, progress), 1, haloPulse);
  setOpacity(travelSpine, 0);
  setTrailWindow(0, 0);
  setOpacity(destinationGroup, 0);
  setOpacity(destinationCore, 0);
  setOpacity(tensionGroup, 0);

  setOpacity(transformationGroup, 1);
  transformationGroup.setAttribute("transform", `translate(${shift.toFixed(2)} 0)`);
  rippleInner.setAttribute("r", lerp(112, 84, settle).toFixed(2));
  rippleOuter.setAttribute("r", lerp(150, 114, settle).toFixed(2));
  setOpacity(rippleInner, 0.05 + rippleFade * 0.06);
  setOpacity(rippleOuter, 0.015 + rippleFade * 0.025);

  frameParts.forEach((element) => setOpacity(element, 0.96));
  setOpacity(frameLeft, 0.9);
  setOpacity(frameRight, 0.9);
  setOpacity(waveTop, 0.92);
  setOpacity(waveBottom, 0.92);
  applyStrokeReveal(waveTop, 1, WAVE_TOP_LENGTH);
  applyStrokeReveal(waveBottom, 1, WAVE_BOTTOM_LENGTH);
  setOpacity(axisLine, 0.72);
  applyStrokeReveal(axisLine, 1, AXIS_LENGTH);

  tethers.forEach((element, index) => {
    setOpacity(element, lerp(0.34 - index * 0.03, 0.12, settle));
    applyStrokeReveal(element, 1, TETHER_LENGTHS[index]);
  });

  setOpacity(resolutionGroup, 1);
  setOpacity(calmHalo, 0.12);
  setOpacity(settleRule, 0.62);
  setCircleCenter(calmHalo, { x: points.transform.x + shift, y: points.final.y });
  calmHalo.setAttribute("r", lerp(128, 112, progress).toFixed(2));
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
