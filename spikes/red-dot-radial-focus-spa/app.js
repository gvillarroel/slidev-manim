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

const points = {
  start: { x: 332, y: 450 },
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
    { x: 404, y: -34 },
    { x: 440, y: 10 },
    { x: 396, y: 54 },
  ],
  c: [
    { x: -364, y: 88 },
    { x: -400, y: 132 },
    { x: -356, y: 176 },
  ],
};

const chipAnchors = {
  a: { x: 194, y: -182 },
  b: { x: 336, y: 12 },
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
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -48) translate(800 450) scale(1.14) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
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
  const position = mixPoint(points.start, { x: 560, y: 450 }, eased * 0.58);
  setDot(position, lerp(4, 19, eased), lerp(18, 82, eased), clamp(progress * 1.8, 0, 1), 0.26 + pulseWave(progress, 1.2) * 0.2);
  setOpacity(narrativeSpine, clamp((progress - 0.18) * 1.6, 0, 0.34));
  setTrailWindow(0, 0);

  setOpacity(hubHalo, clamp((progress - 0.42) * 1.6, 0, 0.18));
  setOpacity(hubShell, clamp((progress - 0.38) * 1.6, 0, 0.34));
  setOpacity(hubRing, clamp((progress - 0.46) * 1.6, 0, 0.18));
  setOpacity(futureSpokeA, clamp((progress - 0.42) * 1.5, 0, 0.22));
  setOpacity(futureSpokeB, clamp((progress - 0.48) * 1.5, 0, 0.18));
  setOpacity(futureSpokeC, clamp((progress - 0.54) * 1.5, 0, 0.18));
  setOpacity(slotA, clamp((progress - 0.46) * 1.5, 0, 0.18));
  setOpacity(slotB, clamp((progress - 0.52) * 1.5, 0, 0.14));
  setOpacity(slotC, clamp((progress - 0.58) * 1.5, 0, 0.14));
}

function renderFanout(progress) {
  const travelProgress = clamp(progress / 0.28, 0, 1);
  const position = mixPoint(points.start, points.hub, easeInOut(travelProgress));
  setDot(position, lerp(19, 18, progress), lerp(82, 112, progress), 1, 0.28 + pulseWave(progress, 1.6) * 0.12);
  setOpacity(narrativeSpine, 0.24);
  setTrailWindow(190 + progress * 330, 0.78);

  [hubHalo, hubShell, hubRing].forEach((element) => setOpacity(element, 0.62));

  const futureOpacity = clamp((progress - 0.12) * 1.4, 0, 0.4);
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
  setDot(points.hub, 18, 114, 1, 0.22 + pulseWave(progress, 2) * 0.08);
  setOpacity(narrativeSpine, 0.08);
  setTrailWindow(160, 0.18);
  [hubHalo, hubShell, hubRing].forEach((element) => setOpacity(element, element === hubRing ? 0.88 : 0.52));

  [futureSpokeA, futureSpokeB, futureSpokeC, slotA, slotB, slotC].forEach((element) => setOpacity(element, 0.06));
  setLineEnd(spokeA, localTargets.a, 0.96, COLORS.primaryRed, 6);
  setLineEnd(spokeB, localTargets.b, 0.72, COLORS.darkGray, 4.5);
  setLineEnd(spokeC, localTargets.c, 0.72, COLORS.darkGray, 4.5);
  setOpacity(cardA, 1);
  setOpacity(cardB, 0.84);
  setOpacity(cardC, 0.84);

  setGroupTransform(focusFrame, localTargets.a.x + 26, localTargets.a.y - 12, 1, 0);
  setOpacity(focusFrame, 1);
  setLineEnd(focusBeam, localTargets.a, 1, COLORS.primaryRed, 6);

  const chipOpacity = clamp((progress - 0.18) / 0.24, 0, 1);
  const chipScale = lerp(0.9, 1, easeOut(chipOpacity));
  setChipCloud(chipAnchors.a, chipSets.a, chipOpacity, chipScale);
}

function renderRotation(progress) {
  const rotation = lerp(0, 58, easeInOut(progress));
  const handoff = clamp((progress - 0.16) / 0.62, 0, 1);
  const focusLocal = mixPoint(localTargets.a, localTargets.b, handoff);
  const chipLocal = chipSets.a.map((point, index) => mixPoint(point, chipSets.b[index], handoff));
  const chipAnchor = mixPoint(chipAnchors.a, chipAnchors.b, handoff);

  setDot(points.hub, 18, 108, 1, 0.2 + pulseWave(progress, 2.2) * 0.08);
  setOpacity(narrativeSpine, 0.04);
  setTrailWindow(80, 0.08);
  setGroupTransform(orbitRig, points.hub.x, points.hub.y, 1, rotation);

  [hubHalo, hubShell, hubRing].forEach((element) => setOpacity(element, element === hubRing ? 0.92 : 0.5));
  setLineEnd(spokeA, localTargets.a, 0.78, handoff < 0.4 ? COLORS.primaryRed : COLORS.darkGray, handoff < 0.4 ? 6 : 4.5);
  setLineEnd(spokeB, localTargets.b, 0.96, handoff > 0.52 ? COLORS.primaryRed : COLORS.darkGray, handoff > 0.52 ? 6 : 4.5);
  setLineEnd(spokeC, localTargets.c, 0.74, COLORS.darkGray, 4.5);
  setOpacity(cardA, 0.92);
  setOpacity(cardB, 1);
  setOpacity(cardC, 0.88);

  setGroupTransform(focusFrame, focusLocal.x + 26, focusLocal.y - 12, 1, 0);
  setOpacity(focusFrame, 1);
  setLineEnd(focusBeam, focusLocal, 1, COLORS.primaryRed, 6);
  setChipCloud(chipAnchor, chipLocal, 1, 1);

  const shellPulse = 0.34 + pulseWave(progress, 1.6) * 0.08;
  setOpacity(hubShell, shellPulse);
}

function renderResolution(progress) {
  const settleRotation = lerp(58, 24, easeInOut(progress));
  const settleOffset = mixPoint({ x: 0, y: 0 }, { x: -18, y: -8 }, easeOut(progress));

  setDot({ x: points.hub.x + settleOffset.x, y: points.hub.y + settleOffset.y }, 17, 96, 1, 0.18 + pulseWave(progress, 1.4) * 0.06);
  setOpacity(narrativeSpine, 0);
  setTrailWindow(0, 0);

  setGroupTransform(orbitRig, points.hub.x + settleOffset.x, points.hub.y + settleOffset.y, 0.98, settleRotation);
  setLineEnd(spokeA, localTargets.a, 0.58, COLORS.darkGray, 4);
  setLineEnd(spokeB, localTargets.b, 0.58, COLORS.darkGray, 4);
  setLineEnd(spokeC, localTargets.c, 0.58, COLORS.darkGray, 4);
  setOpacity(cardA, 0.92);
  setOpacity(cardB, 0.92);
  setOpacity(cardC, 0.92);
  setOpacity(focusBeam, clamp(0.42 - progress * 0.7, 0, 1));
  setOpacity(focusFrame, clamp(0.34 - progress * 0.6, 0, 1));
  [chip1, chip2, chip3, chipLine1, chipLine2, chipLine3].forEach((element) => {
    setOpacity(element, clamp(0.4 - progress * 0.8, 0, 1));
  });

  setOpacity(hubHalo, 0.16);
  setOpacity(hubShell, 0.26);
  setOpacity(hubRing, 0.82);
  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionShell, 0.48);
  setOpacity(resolutionOrbit, 0.58);
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
