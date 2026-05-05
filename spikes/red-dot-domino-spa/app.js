const TOTAL_DURATION = 36_500;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_500 },
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

const SLOT_LAYOUT = [
  { x: 900, y: 318, angle: 0 },
  { x: 1010, y: 384, angle: 58 },
  { x: 1034, y: 506, angle: 116 },
  { x: 958, y: 592, angle: 174 },
  { x: 826, y: 578, angle: 232 },
  { x: 772, y: 444, angle: 290 },
];

const CORRIDOR_BASES = [
  { x: 744, y: 562 },
  { x: 806, y: 544 },
  { x: 868, y: 524 },
  { x: 930, y: 504 },
  { x: 992, y: 484 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const entryLane = document.getElementById("entry-lane");
const activeTrail = document.getElementById("active-trail");
const targetRing = document.getElementById("target-ring");
const targetAxis = document.getElementById("target-axis");
const targetCross = document.getElementById("target-cross");
const searchPathTop = document.getElementById("search-path-top");
const searchPathMid = document.getElementById("search-path-mid");
const searchPathBottom = document.getElementById("search-path-bottom");
const candidateTop = document.getElementById("candidate-top");
const candidateMid = document.getElementById("candidate-mid");
const candidateBottom = document.getElementById("candidate-bottom");
const echoTop = document.getElementById("echo-top");
const echoMid = document.getElementById("echo-mid");
const echoBottom = document.getElementById("echo-bottom");
const corridorRailTop = document.getElementById("corridor-rail-top");
const corridorRailBottom = document.getElementById("corridor-rail-bottom");
const pressureGuide = document.getElementById("pressure-guide");
const pressureHalo = document.getElementById("pressure-halo");
const cascadeStem = document.getElementById("cascade-stem");
const cascadeArc = document.getElementById("cascade-arc");
const resolutionBrackets = document.getElementById("resolution-brackets");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const slotEls = SLOT_LAYOUT.map((_, index) => document.getElementById(`slot-${index}`));
const corridorBars = CORRIDOR_BASES.map((_, index) => document.getElementById(`bar-${index}`));
const finalBars = SLOT_LAYOUT.map((_, index) => document.getElementById(`final-bar-${index}`));

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const STEM_LENGTH = cascadeStem.getTotalLength();
const ARC_LENGTH = cascadeArc.getTotalLength();

const points = {
  start: { x: 410, y: 450 },
  appearanceSettle: { x: 510, y: 450 },
  searchTop: { x: 580, y: 336 },
  searchMid: { x: 716, y: 418 },
  searchBottom: { x: 480, y: 570 },
  pushStart: { x: 708, y: 558 },
  pushHold: { x: 734, y: 550 },
  center: { x: 900, y: 450 },
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

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    sceneRoot.setAttribute(
      "transform",
      "translate(0 -54) translate(800 450) scale(1.16) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
    sceneRoot.setAttribute(
      "transform",
      "translate(850 450) scale(1.08) translate(-850 -450)",
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

function setSlotLayout(opacity) {
  SLOT_LAYOUT.forEach((slot, index) => {
    setGroupTransform(slotEls[index], slot.x, slot.y, slot.angle);
    setOpacity(slotEls[index], opacity);
  });
}

function resetScene() {
  applyDot(points.start, 18, 72, 0, 0);
  setOpacity(entryLane, 0);
  setTrailWindow(0, 0);

  [
    targetRing,
    targetAxis,
    targetCross,
    searchPathTop,
    searchPathMid,
    searchPathBottom,
    candidateTop,
    candidateMid,
    candidateBottom,
    echoTop,
    echoMid,
    echoBottom,
    corridorRailTop,
    corridorRailBottom,
    pressureGuide,
    pressureHalo,
    resolutionBrackets,
    resolutionHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setSlotLayout(0);
  setPathReveal(cascadeStem, 0, 0, STEM_LENGTH);
  setPathReveal(cascadeArc, 0, 0, ARC_LENGTH);

  setGroupTransform(candidateTop, 724, 336, 0);
  setGroupTransform(candidateMid, 834, 418, 0);
  setGroupTransform(candidateBottom, 748, 570, 0);

  CORRIDOR_BASES.forEach((base, index) => {
    setGroupTransform(corridorBars[index], base.x, base.y, 0);
    setOpacity(corridorBars[index], 0);
  });

  SLOT_LAYOUT.forEach((slot, index) => {
    setGroupTransform(finalBars[index], slot.x, slot.y, slot.angle);
    setOpacity(finalBars[index], 0);
  });
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.appearanceSettle, eased * 0.88);
  const dotOpacity = 0.74 + clamp(progress * 0.3, 0, 0.26);
  const haloPulse = 0.14 + pulseWave(progress, 1.1) * 0.16;

  applyDot(position, lerp(14, 19, eased), lerp(54, 86, eased), dotOpacity, haloPulse * dotOpacity);
  setOpacity(entryLane, 0.2 + progress * 0.18);
  setTrailWindow(0, 0);

  setOpacity(targetRing, 0.34 + progress * 0.18);
  setOpacity(targetAxis, 0.26 + progress * 0.14);
  setOpacity(targetCross, 0.12 + progress * 0.1);
  setSlotLayout(0.28 + progress * 0.14);

  setOpacity(searchPathTop, 0.14 + progress * 0.12);
  setOpacity(searchPathMid, 0.14 + progress * 0.12);
  setOpacity(searchPathBottom, 0.14 + progress * 0.12);
  setOpacity(candidateTop, 0.22 + progress * 0.16);
  setOpacity(candidateMid, 0.22 + progress * 0.16);
  setOpacity(candidateBottom, 0.22 + progress * 0.16);

  setOpacity(corridorRailTop, 0.16 + progress * 0.1);
  setOpacity(corridorRailBottom, 0.16 + progress * 0.1);
  CORRIDOR_BASES.forEach((base, index) => {
    setGroupTransform(corridorBars[index], base.x, base.y, 0);
    setOpacity(corridorBars[index], 0.14 + progress * 0.08);
  });
}

function renderSearch(progress) {
  let position = points.searchTop;
  let scaleX = 1;
  let scaleY = 1;
  let rotation = -6;

  if (progress < 0.24) {
    const t = easeInOut(progress / 0.24);
    position = mixPoint(points.appearanceSettle, points.searchTop, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.08, t);
    rotation = lerp(0, -10, t);
  } else if (progress < 0.5) {
    const t = easeInOut((progress - 0.24) / 0.26);
    position = mixPoint(points.searchTop, points.searchMid, t);
    scaleX = lerp(0.92, 1.08, t);
    scaleY = lerp(1.08, 0.92, t);
    rotation = lerp(-10, 8, t);
  } else if (progress < 0.76) {
    const t = easeInOut((progress - 0.5) / 0.26);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    scaleX = lerp(1.08, 0.96, t);
    scaleY = lerp(0.92, 1.12, t);
    rotation = lerp(8, -8, t);
  } else {
    const t = easeInOut((progress - 0.76) / 0.24);
    position = mixPoint(points.searchBottom, points.pushStart, t);
    scaleX = lerp(0.96, 1.08, t);
    scaleY = lerp(1.12, 0.92, t);
    rotation = lerp(-8, 0, t);
  }

  applyDot(position, 19, 74, 1, 0.28 + pulseWave(progress, 2.1) * 0.14, scaleX, scaleY, rotation);
  setOpacity(entryLane, 0.14);
  setTrailWindow(106 + progress * 62, 0.2 - clamp((progress - 0.5) / 0.5, 0, 1) * 0.17);
  const candidateResidue = 1 - easeOut(clamp((progress - 0.76) / 0.18, 0, 1));

  setOpacity(targetRing, 0.48);
  setOpacity(targetAxis, 0.34);
  setOpacity(targetCross, 0.18);
  setSlotLayout(0.4);

  setOpacity(searchPathTop, progress < 0.26 ? 0.62 : 0.16 * candidateResidue);
  setOpacity(searchPathMid, progress >= 0.24 && progress < 0.52 ? 0.62 : 0.16 * candidateResidue);
  setOpacity(searchPathBottom, progress >= 0.5 && progress < 0.76 ? 0.16 : 0.12 * candidateResidue);
  setOpacity(candidateTop, 0.72 * candidateResidue);
  setOpacity(candidateMid, 0.72 * candidateResidue);
  setOpacity(candidateBottom, 0.72 * candidateResidue);
  setOpacity(echoTop, progress >= 0.26 ? 0.36 * candidateResidue : 0);
  setOpacity(echoMid, progress >= 0.54 ? 0.34 * candidateResidue : 0);
  setOpacity(echoBottom, progress >= 0.82 ? 0.36 * candidateResidue : 0);

  setOpacity(corridorRailTop, 0.22);
  setOpacity(corridorRailBottom, 0.22);
  CORRIDOR_BASES.forEach((base, index) => {
    setGroupTransform(corridorBars[index], base.x, base.y, 0);
    setOpacity(corridorBars[index], 0.22 - index * 0.02);
  });
  SLOT_LAYOUT.forEach((slot, index) => {
    setGroupTransform(finalBars[index], slot.x, slot.y, slot.angle);
    const previewOpacity = index === 1 || index === 2 ? 0.26 : index === 0 || index === 3 ? 0.18 : 0.1;
    setOpacity(finalBars[index], previewOpacity);
  });
}

function renderTension(progress) {
  const move = progress < 0.26
    ? mixPoint(points.pushStart, points.pushHold, easeInOut(progress / 0.26))
    : progress < 0.78
      ? points.pushHold
      : mixPoint(points.pushHold, { x: 774, y: 538 }, easeInOut((progress - 0.78) / 0.22));
  const squeeze = progress < 0.26
    ? easeOut(progress / 0.26)
    : progress < 0.76
      ? 1
      : 1 - easeInOut((progress - 0.76) / 0.24);
  const pulse = progress > 0.28 && progress < 0.7 ? (pulseWave((progress - 0.28) / 0.42, 2.4) - 0.5) * 5 : 0;
  const residue = 1 - easeOut(clamp((progress - 0.04) / 0.38, 0, 1));

  applyDot(
    move,
    19,
    lerp(82, 110, squeeze),
    1,
    0.34 + squeeze * 0.18,
    lerp(1.02, 1.78, squeeze),
    lerp(0.98, 0.7, squeeze),
    -8,
  );
  setOpacity(entryLane, 0.04 * residue);
  setTrailWindow(210, 0.28 * (1 - easeOut(clamp((progress - 0.06) / 0.24, 0, 1))));

  setOpacity(targetRing, 0.24 + squeeze * 0.08);
  setOpacity(targetAxis, 0.16 + squeeze * 0.06);
  setOpacity(targetCross, 0.04);
  setSlotLayout(0.16 + squeeze * 0.06);

  setOpacity(searchPathTop, 0.12 * residue);
  setOpacity(searchPathMid, 0.12 * residue);
  setOpacity(searchPathBottom, 0.12 * residue);
  setOpacity(candidateTop, 0.14 * residue);
  setOpacity(candidateMid, 0.14 * residue);
  setOpacity(candidateBottom, 0.14 * residue);
  setOpacity(echoTop, 0.16 * residue);
  setOpacity(echoMid, 0.14 * residue);
  setOpacity(echoBottom, 0.16 * residue);

  setOpacity(corridorRailTop, 0.54);
  setOpacity(corridorRailBottom, 0.54);
  setOpacity(pressureGuide, 0.72);
  setOpacity(pressureHalo, 0.24 + squeeze * 0.18);

  const targetAngles = [30, 22, 16, 10, 5];
  CORRIDOR_BASES.forEach((base, index) => {
    const angle = lerp(0, targetAngles[index], squeeze) + pulse * (1 - index * 0.16);
    setGroupTransform(corridorBars[index], base.x, base.y, angle);
    setOpacity(corridorBars[index], 1);
  });
}

function renderTransformation(progress) {
  const corridorFade = 1 - easeOut(clamp(progress / 0.28, 0, 1));
  const stemReveal = clamp(progress / 0.34, 0, 1);
  const arcReveal = clamp((progress - 0.24) / 0.54, 0, 1);
  const ringTakeover = clamp((progress - 0.18) / 0.66, 0, 1);

  let dotPosition = points.center;
  if (progress < 0.38) {
    const t = easeOut(progress / 0.38);
    const point = pointOnPath(cascadeStem, STEM_LENGTH, t);
    dotPosition = { x: point.x, y: point.y };
  } else if (progress < 0.9) {
    const t = easeInOut((progress - 0.38) / 0.52);
    const point = pointOnPath(cascadeArc, ARC_LENGTH, t);
    dotPosition = { x: point.x, y: point.y };
  } else {
    const t = easeInOut((progress - 0.9) / 0.1);
    const point = pointOnPath(cascadeArc, ARC_LENGTH, 1);
    dotPosition = mixPoint({ x: point.x, y: point.y }, points.center, t);
  }

  applyDot(dotPosition, lerp(18, 17, progress), lerp(98, 120, ringTakeover), 1, 0.24 + pulseWave(progress, 2.2) * 0.12);

  setOpacity(entryLane, 0);
  setTrailWindow(120, 0.05 * corridorFade);

  setOpacity(targetRing, 0.18 + ringTakeover * 0.14);
  setOpacity(targetAxis, 0.12 + ringTakeover * 0.08);
  setOpacity(targetCross, 0.04 + ringTakeover * 0.04);
  setSlotLayout(0.2 + ringTakeover * 0.12);

  setOpacity(searchPathTop, 0);
  setOpacity(searchPathMid, 0);
  setOpacity(searchPathBottom, 0);
  setOpacity(candidateTop, 0);
  setOpacity(candidateMid, 0);
  setOpacity(candidateBottom, 0);
  setOpacity(echoTop, 0);
  setOpacity(echoMid, 0);
  setOpacity(echoBottom, 0);

  setOpacity(corridorRailTop, 0.4 * corridorFade);
  setOpacity(corridorRailBottom, 0.4 * corridorFade);
  setOpacity(pressureGuide, 0.18 * corridorFade);
  setOpacity(pressureHalo, 0.12 * corridorFade);
  CORRIDOR_BASES.forEach((base, index) => {
    const angle = lerp(30 - index * 4, 78 - index * 4, progress);
    const x = lerp(base.x, SLOT_LAYOUT[Math.min(index + 1, SLOT_LAYOUT.length - 1)].x, clamp((progress - 0.08 - index * 0.06) / 0.46, 0, 1));
    const y = lerp(base.y, SLOT_LAYOUT[Math.min(index + 1, SLOT_LAYOUT.length - 1)].y, clamp((progress - 0.08 - index * 0.06) / 0.46, 0, 1));
    setGroupTransform(corridorBars[index], x, y, angle, 1 - progress * 0.18);
    setOpacity(corridorBars[index], 0.74 * corridorFade * (1 - index * 0.08));
  });

  setPathReveal(cascadeStem, stemReveal, 0.92, STEM_LENGTH);
  setPathReveal(cascadeArc, arcReveal, 0.92, ARC_LENGTH);

  SLOT_LAYOUT.forEach((slot, index) => {
    const inProgress = clamp((progress - 0.2 - index * 0.08) / 0.34, 0, 1);
    const eased = easeOut(inProgress);
    const angle = lerp(slot.angle - 34, slot.angle, eased);
    const x = lerp(slot.x - 28, slot.x, eased);
    const y = lerp(slot.y + 18, slot.y, eased);
    setGroupTransform(finalBars[index], x, y, angle, 0.9 + eased * 0.1);
    setOpacity(finalBars[index], eased);
  });
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const traceFade = 1 - easeOut(clamp(progress / 0.36, 0, 1));
  const bracketIn = clamp((progress - 0.2) / 0.4, 0, 1);
  const slotFade = 1 - easeOut(clamp((progress - 0.3) / 0.48, 0, 1));

  applyDot(points.center, 17, lerp(122, 88, progress), 1, 0.22 + pulseWave(progress, 1.5) * 0.08);
  setTrailWindow(0, 0);

  setOpacity(targetRing, 0.34);
  setOpacity(targetAxis, 0.24);
  setOpacity(targetCross, 0.08);
  SLOT_LAYOUT.forEach((slot, index) => {
    setGroupTransform(slotEls[index], slot.x, slot.y, slot.angle);
    setOpacity(slotEls[index], 0.18 * slotFade);
  });

  setOpacity(corridorRailTop, 0);
  setOpacity(corridorRailBottom, 0);
  setOpacity(pressureGuide, 0);
  setOpacity(pressureHalo, 0);
  CORRIDOR_BASES.forEach((base, index) => {
    setGroupTransform(corridorBars[index], base.x, base.y, 76 - index * 4);
    setOpacity(corridorBars[index], 0);
  });

  setPathReveal(cascadeStem, 1, 0.2 * traceFade, STEM_LENGTH);
  setPathReveal(cascadeArc, 1, 0.18 * traceFade, ARC_LENGTH);

  SLOT_LAYOUT.forEach((slot, index) => {
    setGroupTransform(finalBars[index], slot.x, slot.y, slot.angle + Math.sin((progress + index * 0.08) * Math.PI) * (1 - settle) * 3);
    setOpacity(finalBars[index], 1);
  });
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
