const TOTAL_DURATION = 34_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "fanout", label: "fan-out", duration: 7_000 },
  { id: "focus", label: "focus", duration: 7_000 },
  { id: "rotation", label: "rotation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");
const hubHalo = document.getElementById("hub-halo");
const hubShell = document.getElementById("hub-shell");
const hubRing = document.getElementById("hub-ring");

const futureSpokeA = document.getElementById("future-spoke-a");
const futureSpokeB = document.getElementById("future-spoke-b");
const futureSpokeC = document.getElementById("future-spoke-c");
const slotA = document.getElementById("slot-a");
const slotB = document.getElementById("slot-b");
const slotC = document.getElementById("slot-c");

const systemRig = document.getElementById("system-rig");
const orbitRig = document.getElementById("orbit-rig");
const spokeA = document.getElementById("spoke-a");
const spokeB = document.getElementById("spoke-b");
const spokeC = document.getElementById("spoke-c");
const focusBeam = document.getElementById("focus-beam");
const cardA = document.getElementById("card-a");
const cardB = document.getElementById("card-b");
const cardC = document.getElementById("card-c");
const focusFrame = document.getElementById("focus-frame");
const chipLine1 = document.getElementById("chip-line-1");
const chipLine2 = document.getElementById("chip-line-2");
const chipLine3 = document.getElementById("chip-line-3");
const chip1 = document.getElementById("chip-1");
const chip2 = document.getElementById("chip-2");
const chip3 = document.getElementById("chip-3");
const resolutionGroup = document.getElementById("resolution-group");
const resolutionShell = document.getElementById("resolution-shell");
const resolutionOrbit = document.getElementById("resolution-orbit");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  darkGray: "#4f4f4f",
  lineGray: "#cfcfcf",
};

const ORBIT_TURN = 24;
const ROTATION_DETAIL_OPACITY = 0.46;
const ROTATION_BEAM_OPACITY = 0.65;

const points = {
  start: { x: 500, y: 450 },
  ingress: { x: 604, y: 450 },
  hub: { x: 824, y: 450 },
};

const localTargets = {
  a: { x: 110, y: -182 },
  b: { x: 248, y: 12 },
  c: { x: -156, y: 138 },
};

const chipSets = {
  a: [
    { x: 286, y: -220 },
    { x: 322, y: -176 },
    { x: 278, y: -132 },
  ],
  b: [
    { x: 392, y: -28 },
    { x: 430, y: 14 },
    { x: 392, y: 56 },
  ],
  c: [
    { x: -364, y: 88 },
    { x: -400, y: 132 },
    { x: -356, y: 176 },
  ],
};

const chipAnchors = {
  a: { x: 194, y: -182 },
  b: { x: 346, y: 12 },
  c: { x: -250, y: 140 },
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
  element.setAttribute("opacity", value.toFixed(3));
}

function setCircleCenter(element, { x, y }) {
  element.setAttribute("cx", x.toFixed(2));
  element.setAttribute("cy", y.toFixed(2));
}

function setGroupTransform(element, x, y, scale = 1, rotate = 0) {
  element.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scale.toFixed(3)})`);
}

function setDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1) {
  setCircleCenter(dotCore, position);
  setCircleCenter(dotHalo, position);
  dotCore.setAttribute("r", radius.toFixed(2));
  dotHalo.setAttribute("r", haloRadius.toFixed(2));
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  dotCore.setAttribute("transform", `translate(${position.x} ${position.y}) scale(${scaleX} ${scaleY}) translate(${-position.x} ${-position.y})`);
  dotHalo.setAttribute("transform", `translate(${position.x} ${position.y}) scale(${scaleX} ${scaleY}) translate(${-position.x} ${-position.y})`);
}

function setTrailWindow(visibleLength, opacity) {
  const clamped = clamp(visibleLength, 0, ACTIVE_TRAIL_LENGTH);
  activeTrail.style.strokeDasharray = `${clamped.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + 200).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = "0";
  setOpacity(activeTrail, opacity);
}

function setLineEnd(line, target, opacity, color = COLORS.darkGray, width = 4.5) {
  line.setAttribute("x2", target.x.toFixed(2));
  line.setAttribute("y2", target.y.toFixed(2));
  line.setAttribute("stroke", color);
  line.setAttribute("stroke-width", width.toFixed(2));
  setOpacity(line, opacity);
}

function setChipCloud(anchor, pointsLocal, opacity, scale = 1) {
  const chips = [chip1, chip2, chip3];
  const lines = [chipLine1, chipLine2, chipLine3];
  pointsLocal.forEach((point, index) => {
    setGroupTransform(chips[index], point.x, point.y, scale, 0);
    lines[index].setAttribute("x1", anchor.x.toFixed(2));
    lines[index].setAttribute("y1", anchor.y.toFixed(2));
    lines[index].setAttribute("x2", point.x.toFixed(2));
    lines[index].setAttribute("y2", point.y.toFixed(2));
    setOpacity(chips[index], opacity * 0.92);
    setOpacity(lines[index], opacity * 0.7);
  });
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

function updatePhaseLabel(info) {
  phaseLabel.textContent = info.phase.label;
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    svg.setAttribute("viewBox", "360 0 880 900");
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -48) translate(800 450) scale(1.14) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
    svg.setAttribute("viewBox", "0 0 1600 900");
    layoutRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setTrailWindow(0, 0);

  [hubHalo, hubShell, hubRing].forEach((element) => setOpacity(element, 0));
  [futureSpokeA, futureSpokeB, futureSpokeC, slotA, slotB, slotC].forEach((element) => setOpacity(element, 0));

  [spokeA, spokeB, spokeC, focusBeam, cardA, cardB, cardC, focusFrame, chip1, chip2, chip3, chipLine1, chipLine2, chipLine3].forEach((element) => setOpacity(element, 0));
  setGroupTransform(systemRig, 0, 0, 1, 0);
  setGroupTransform(orbitRig, points.hub.x, points.hub.y, 1, 0);
  setGroupTransform(focusFrame, 0, 0, 1, 0);
  setGroupTransform(chip1, 0, 0, 1, 0);
  setGroupTransform(chip2, 0, 0, 1, 0);
  setGroupTransform(chip3, 0, 0, 1, 0);
  setOpacity(resolutionGroup, 0);
  setOpacity(resolutionShell, 0);
  setOpacity(resolutionOrbit, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased);
  setDot(position, lerp(12, 19, eased), lerp(48, 82, eased), lerp(0.72, 1, eased), 0.2 + pulseWave(progress, 1.2) * 0.14);
  setOpacity(narrativeSpine, lerp(0.16, 0.34, eased));
  setTrailWindow(0, 0);

  setOpacity(hubHalo, lerp(0.08, 0.18, eased));
  setOpacity(hubShell, lerp(0.2, 0.34, eased));
  setOpacity(hubRing, lerp(0.22, 0.3, eased));
  setOpacity(futureSpokeA, lerp(0.26, 0.32, eased));
  setOpacity(futureSpokeB, lerp(0.23, 0.28, eased));
  setOpacity(futureSpokeC, lerp(0.23, 0.28, eased));
  setOpacity(slotA, lerp(0.22, 0.28, eased));
  setOpacity(slotB, lerp(0.2, 0.24, eased));
  setOpacity(slotC, lerp(0.2, 0.24, eased));
}

function renderFanout(progress) {
  const travelProgress = clamp(progress / 0.28, 0, 1);
  const position = mixPoint(points.ingress, points.hub, easeInOut(travelProgress));
  setDot(position, lerp(19, 18, progress), lerp(82, 112, progress), 1, 0.28 + pulseWave(progress, 1.6) * 0.12);
  setOpacity(narrativeSpine, 0.24);
  const routeExit = easeOut(clamp((progress - 0.34) / 0.28, 0, 1));
  setTrailWindow(lerp(260, 0, routeExit), lerp(0.64, 0.08, routeExit));

  [hubHalo, hubShell, hubRing].forEach((element) => setOpacity(element, 0.62));

  const futureOpacity = lerp(0.34, 0.4, clamp(progress / 0.18, 0, 1));
  [futureSpokeA, futureSpokeB, futureSpokeC].forEach((element) => setOpacity(element, futureOpacity));
  [slotA, slotB, slotC].forEach((element) => setOpacity(element, futureOpacity * 0.9));

  const revealA = clamp((progress - 0.28) / 0.18, 0, 1);
  const revealB = clamp((progress - 0.46) / 0.18, 0, 1);
  const revealC = clamp((progress - 0.64) / 0.18, 0, 1);

  setLineEnd(spokeA, localTargets.a, revealA, revealA > 0.75 ? COLORS.darkGray : COLORS.primaryRed, revealA > 0.75 ? 4.5 : 6);
  setLineEnd(spokeB, localTargets.b, revealB, revealB > 0.75 ? COLORS.darkGray : COLORS.primaryRed, revealB > 0.75 ? 4.5 : 6);
  setLineEnd(spokeC, localTargets.c, revealC, revealC > 0.75 ? COLORS.darkGray : COLORS.primaryRed, revealC > 0.75 ? 4.5 : 6);

  setGroupTransform(cardA, 0, 0, lerp(0.74, 1, easeOut(revealA)), 0);
  setGroupTransform(cardB, 0, 0, lerp(0.74, 1, easeOut(revealB)), 0);
  setGroupTransform(cardC, 0, 0, lerp(0.74, 1, easeOut(revealC)), 0);
  setOpacity(cardA, revealA);
  setOpacity(cardB, revealB);
  setOpacity(cardC, revealC);
}

function renderFocus(progress) {
  const focusIn = easeOut(clamp(progress / 0.32, 0, 1));
  setDot(points.hub, 18, 114, 1, 0.22 + pulseWave(progress, 2) * 0.08);
  setOpacity(narrativeSpine, lerp(0.24, 0.08, focusIn));
  setTrailWindow(lerp(520, 160, focusIn), lerp(0.78, 0.18, focusIn));
  [hubHalo, hubShell, hubRing].forEach((element) => setOpacity(element, element === hubRing ? lerp(0.62, 0.88, focusIn) : lerp(0.62, 0.52, focusIn)));

  [futureSpokeA, futureSpokeB, futureSpokeC, slotA, slotB, slotC].forEach((element) => setOpacity(element, lerp(0.36, 0.06, focusIn)));
  setLineEnd(spokeA, localTargets.a, lerp(1, 0.96, focusIn), focusIn > 0.22 ? COLORS.primaryRed : COLORS.darkGray, lerp(4.5, 6, focusIn));
  setLineEnd(spokeB, localTargets.b, lerp(1, 0.72, focusIn), COLORS.darkGray, 4.5);
  setLineEnd(spokeC, localTargets.c, lerp(1, 0.72, focusIn), COLORS.darkGray, 4.5);
  setOpacity(cardA, 1);
  setOpacity(cardB, lerp(1, 0.84, focusIn));
  setOpacity(cardC, lerp(1, 0.84, focusIn));

  setGroupTransform(focusFrame, localTargets.a.x + 26, localTargets.a.y - 12, 1, 0);
  setOpacity(focusFrame, focusIn);
  setLineEnd(focusBeam, localTargets.a, focusIn, COLORS.primaryRed, 6);

  const chipOpacity = clamp((progress - 0.18) / 0.24, 0, 1);
  const chipScale = lerp(0.9, 1, easeOut(chipOpacity));
  setChipCloud(chipAnchors.a, chipSets.a, chipOpacity, chipScale);
}

function renderRotation(progress) {
  const rotation = lerp(0, ORBIT_TURN, easeInOut(progress));
  const hubPosition = points.hub;
  const rotationIn = easeOut(clamp(progress / 0.24, 0, 1));
  const handoff = clamp((progress - 0.16) / 0.62, 0, 1);
  const focusLocal = mixPoint(localTargets.a, localTargets.b, handoff);
  const chipLocal = chipSets.a.map((point, index) => mixPoint(point, chipSets.b[index], handoff));
  const chipAnchor = mixPoint(chipAnchors.a, chipAnchors.b, handoff);

  setDot(hubPosition, 18, 108, 1, 0.2 + pulseWave(progress, 2.2) * 0.08);
  setOpacity(narrativeSpine, 0.04);
  setTrailWindow(80, 0.08);
  setGroupTransform(orbitRig, hubPosition.x, hubPosition.y, 1, rotation);

  [hubHalo, hubShell, hubRing].forEach((element) => setOpacity(element, element === hubRing ? 0.92 : 0.5));
  setLineEnd(spokeA, localTargets.a, 0.78, handoff < 0.4 ? COLORS.primaryRed : COLORS.darkGray, handoff < 0.4 ? 6 : 4.5);
  setLineEnd(spokeB, localTargets.b, lerp(0.72, 0.96, rotationIn), handoff > 0.52 ? COLORS.primaryRed : COLORS.darkGray, handoff > 0.52 ? 6 : 4.5);
  setLineEnd(spokeC, localTargets.c, lerp(0.72, 0.74, rotationIn), COLORS.darkGray, 4.5);
  setOpacity(cardA, lerp(1, 0.92, rotationIn));
  setOpacity(cardB, lerp(0.84, 1, rotationIn));
  setOpacity(cardC, lerp(0.84, 0.88, rotationIn));

  const detailExit = easeOut(clamp((progress - 0.36) / 0.42, 0, 1));
  setGroupTransform(focusFrame, focusLocal.x + 26, focusLocal.y - 12, 1, 0);
  setOpacity(focusFrame, 1 - detailExit);
  setLineEnd(focusBeam, focusLocal, lerp(1, ROTATION_BEAM_OPACITY, easeOut(progress)), COLORS.primaryRed, 6);
  setChipCloud(chipAnchor, chipLocal, lerp(1, ROTATION_DETAIL_OPACITY, detailExit), lerp(0.88, 0.82, detailExit));

  const shellPulse = 0.34 + pulseWave(progress, 1.6) * 0.08;
  setOpacity(hubShell, shellPulse);
}

function renderResolution(progress) {
  const resolveIn = easeOut(clamp(progress / 0.36, 0, 1));
  const settleRotation = lerp(ORBIT_TURN, 12, easeInOut(progress));
  const settleOffset = mixPoint({ x: 0, y: 0 }, { x: 0, y: 0 }, easeOut(progress));

  setDot({ x: points.hub.x + settleOffset.x, y: points.hub.y + settleOffset.y }, 17, 96, 1, 0.18 + pulseWave(progress, 1.4) * 0.06);
  setOpacity(narrativeSpine, 0);
  setTrailWindow(0, 0);

  setGroupTransform(orbitRig, points.hub.x + settleOffset.x, points.hub.y + settleOffset.y, 1.04, settleRotation);
  setLineEnd(spokeA, localTargets.a, 0.58, COLORS.darkGray, 4);
  setLineEnd(spokeB, localTargets.b, 0.58, COLORS.darkGray, 4);
  setLineEnd(spokeC, localTargets.c, 0.58, COLORS.darkGray, 4);
  setOpacity(cardA, 0.92);
  setOpacity(cardB, lerp(1, 0.92, resolveIn));
  setOpacity(cardC, lerp(0.88, 0.92, resolveIn));
  setLineEnd(focusBeam, localTargets.b, ROTATION_BEAM_OPACITY * clamp(1 - progress * 1.35, 0, 1), COLORS.primaryRed, 6);
  setGroupTransform(focusFrame, localTargets.b.x + 26, localTargets.b.y - 12, 1, 0);
  setOpacity(focusFrame, 0);
  setChipCloud(chipAnchors.b, chipSets.b, ROTATION_DETAIL_OPACITY * clamp(1 - progress * 1.45, 0, 1), 0.82);

  setOpacity(hubHalo, 0.16);
  setOpacity(hubShell, 0.26);
  setOpacity(hubRing, 0.82);
  setOpacity(resolutionGroup, resolveIn);
  setOpacity(resolutionShell, 0.48 * resolveIn);
  setOpacity(resolutionOrbit, 0.58 * resolveIn);
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);

  if (info.phase.id === "appearance") {
    renderAppearance(info.localProgress);
  } else if (info.phase.id === "fanout") {
    renderFanout(info.localProgress);
  } else if (info.phase.id === "focus") {
    renderFocus(info.localProgress);
  } else if (info.phase.id === "rotation") {
    renderRotation(info.localProgress);
  } else {
    renderResolution(info.localProgress);
  }

  updatePhaseLabel(info);
  svg.dataset.phase = info.phase.id;
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

function tick(now) {
  const elapsed = state.playing
    ? (state.elapsedBeforePause + (now - state.startAt)) % TOTAL_DURATION
    : state.elapsedBeforePause;

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

applyLayout();
window.addEventListener("resize", applyLayout);
resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
