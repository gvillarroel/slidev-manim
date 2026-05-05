const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 6_500 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 9_500 },
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
const coreGuide = document.getElementById("core-guide");
const coreAxis = document.getElementById("core-axis");
const futureBud = document.getElementById("future-bud");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcRight = document.getElementById("search-arc-right");
const searchArcBottom = document.getElementById("search-arc-bottom");
const candidateTop = document.getElementById("candidate-top");
const candidateRight = document.getElementById("candidate-right");
const candidateBottom = document.getElementById("candidate-bottom");
const echoTop = document.getElementById("echo-top");
const echoRight = document.getElementById("echo-right");
const echoBottom = document.getElementById("echo-bottom");
const futureBloom = document.getElementById("future-bloom");
const budSpine = document.getElementById("bud-spine");
const budLeft = document.getElementById("bud-left");
const budRight = document.getElementById("bud-right");
const budTop = document.getElementById("bud-top");
const budBottom = document.getElementById("bud-bottom");
const seamTop = document.getElementById("seam-top");
const seamBottom = document.getElementById("seam-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const bloomGroup = document.getElementById("bloom-group");
const traceNorth = document.getElementById("trace-north");
const traceEast = document.getElementById("trace-east");
const traceSouth = document.getElementById("trace-south");
const traceWest = document.getElementById("trace-west");
const petalNorth = document.getElementById("petal-north");
const petalEast = document.getElementById("petal-east");
const petalSouth = document.getElementById("petal-south");
const petalWest = document.getElementById("petal-west");
const innerNorth = document.getElementById("inner-north");
const innerEast = document.getElementById("inner-east");
const innerSouth = document.getElementById("inner-south");
const innerWest = document.getElementById("inner-west");
const coreRing = document.getElementById("core-ring");
const resolutionOrbit = document.getElementById("resolution-orbit");
const resolutionBrackets = document.getElementById("resolution-brackets");
const outerHalo = document.getElementById("outer-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TRACE_LENGTHS = new Map([
  [traceNorth, traceNorth.getTotalLength()],
  [traceEast, traceEast.getTotalLength()],
  [traceSouth, traceSouth.getTotalLength()],
  [traceWest, traceWest.getTotalLength()],
]);

const points = {
  start: { x: 320, y: 450 },
  appearanceSettle: { x: 434, y: 450 },
  searchTop: { x: 756, y: 348 },
  searchRight: { x: 930, y: 418 },
  searchBottom: { x: 792, y: 560 },
  budEntry: { x: 770, y: 450 },
  budCenter: { x: 860, y: 450 },
  traceNorth: { x: 860, y: 382 },
  traceEast: { x: 926, y: 450 },
  traceSouth: { x: 860, y: 518 },
  traceWest: { x: 794, y: 450 },
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

function setTransform(element, point, scaleX = 1, scaleY = 1, rotation = 0) {
  element.setAttribute(
    "transform",
    `translate(${point.x} ${point.y}) rotate(${rotation.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-point.x} ${-point.y})`,
  );
}

function setGroupPose(element, point, rotation = 0, scaleX = 1, scaleY = 1) {
  element.setAttribute(
    "transform",
    `translate(${point.x.toFixed(2)} ${point.y.toFixed(2)}) rotate(${rotation.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)})`,
  );
}

function setBloomPose(translateX = 0, translateY = 0, rotation = 0, scale = 1) {
  bloomGroup.setAttribute(
    "transform",
    `translate(${translateX.toFixed(2)} ${translateY.toFixed(2)}) rotate(${rotation.toFixed(2)} 860 450) scale(${scale.toFixed(3)} ${scale.toFixed(3)})`,
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

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    sceneRoot.setAttribute(
      "transform",
      "translate(0 -82) translate(800 450) scale(1.24) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
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
  applyDot(points.start, 18, 72, 0, 0);
  setOpacity(entryLane, 0);
  setTrailWindow(0, 0);

  [
    coreGuide,
    coreAxis,
    futureBud,
    searchArcTop,
    searchArcRight,
    searchArcBottom,
    candidateTop,
    candidateRight,
    candidateBottom,
    echoTop,
    echoRight,
    echoBottom,
    futureBloom,
    budSpine,
    budLeft,
    budRight,
    budTop,
    budBottom,
    seamTop,
    seamBottom,
    pressureHalo,
    bloomGroup,
    petalNorth,
    petalEast,
    petalSouth,
    petalWest,
    innerNorth,
    innerEast,
    innerSouth,
    innerWest,
    coreRing,
    resolutionOrbit,
    resolutionBrackets,
    outerHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setPathReveal(traceNorth, 0, 0);
  setPathReveal(traceEast, 0, 0);
  setPathReveal(traceSouth, 0, 0);
  setPathReveal(traceWest, 0, 0);

  setGroupPose(candidateTop, points.searchTop, 0);
  setGroupPose(candidateRight, points.searchRight, 0);
  setGroupPose(candidateBottom, points.searchBottom, 0);
  setGroupPose(budLeft, { x: 860 - 130, y: 450 }, 0);
  setGroupPose(budRight, { x: 860 + 130, y: 450 }, 0);
  setGroupPose(budTop, { x: 860, y: 450 - 102 }, 0);
  setGroupPose(budBottom, { x: 860, y: 450 + 102 }, 0);
  setBloomPose(0, 0, 0, 1);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.appearanceSettle, eased * 0.88);
  const haloPulse = 0.16 + pulseWave(progress, 1.1) * 0.15;

  applyDot(position, lerp(14, 18, eased), lerp(56, 84, eased), 0.76 + progress * 0.2, haloPulse);
  setOpacity(entryLane, 0.22 + progress * 0.16);
  setTrailWindow(0, 0);

  setOpacity(coreGuide, 0.3 + progress * 0.2);
  setOpacity(coreAxis, 0.22 + progress * 0.14);
  setOpacity(futureBud, 0.28 + progress * 0.14);
  setOpacity(searchArcTop, 0.22 + progress * 0.14);
  setOpacity(searchArcRight, 0.2 + progress * 0.14);
  setOpacity(searchArcBottom, 0.22 + progress * 0.14);
  setOpacity(candidateTop, 0.28 + progress * 0.18);
  setOpacity(candidateRight, 0.28 + progress * 0.18);
  setOpacity(candidateBottom, 0.28 + progress * 0.18);
  setOpacity(futureBloom, 0.18 + progress * 0.1);
  setOpacity(budSpine, 0.16 + progress * 0.1);
}

function renderSearch(progress) {
  let position = points.searchTop;
  let scaleX = 1;
  let scaleY = 1;

  if (progress < 0.26) {
    const t = easeInOut(progress / 0.26);
    position = mixPoint(points.appearanceSettle, points.searchTop, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.08, t);
  } else if (progress < 0.52) {
    const t = easeInOut((progress - 0.26) / 0.26);
    position = mixPoint(points.searchTop, points.searchRight, t);
    scaleX = lerp(0.92, 1.08, t);
    scaleY = lerp(1.08, 0.92, t);
  } else if (progress < 0.76) {
    const t = easeInOut((progress - 0.52) / 0.24);
    position = mixPoint(points.searchRight, points.searchBottom, t);
    scaleX = lerp(1.08, 0.94, t);
    scaleY = lerp(0.92, 1.12, t);
  } else {
    const t = easeInOut((progress - 0.76) / 0.24);
    position = mixPoint(points.searchBottom, points.budEntry, t);
    scaleX = lerp(0.94, 1.08, t);
    scaleY = lerp(1.12, 0.92, t);
  }

  applyDot(position, 18.5, 72, 1, 0.28 + pulseWave(progress, 2.2) * 0.16, scaleX, scaleY);
  setOpacity(entryLane, 0.1);
  setTrailWindow(56 + progress * 52, 0.28 - clamp((progress - 0.3) / 0.42, 0, 1) * 0.3);

  setOpacity(coreGuide, 0.42);
  setOpacity(coreAxis, 0.28);
  setOpacity(futureBud, 0.38);
  setOpacity(searchArcTop, 0.66);
  setOpacity(searchArcRight, 0.66);
  setOpacity(searchArcBottom, 0.66);
  setOpacity(candidateTop, 0.74);
  setOpacity(candidateRight, 0.74);
  setOpacity(candidateBottom, 0.74);
  setOpacity(echoTop, progress >= 0.28 ? 0.36 : 0);
  setOpacity(echoRight, progress >= 0.54 ? 0.34 : 0);
  setOpacity(echoBottom, progress >= 0.8 ? 0.36 : 0);
  setOpacity(futureBloom, 0.28);
  setOpacity(budSpine, 0.24);
}

function renderTension(progress) {
  const moveIn = progress < 0.24
    ? mixPoint(points.budEntry, points.budCenter, easeInOut(progress / 0.24))
    : progress < 0.82
      ? points.budCenter
      : mixPoint(points.budCenter, points.traceNorth, easeInOut((progress - 0.82) / 0.18));
  const squeeze = progress < 0.24
    ? easeOut(progress / 0.24)
    : progress < 0.74
      ? 1
      : 1 - easeInOut((progress - 0.74) / 0.26);
  const pulse = progress > 0.28 && progress < 0.72 ? (pulseWave((progress - 0.28) / 0.44, 2.4) - 0.5) * 12 : 0;
  const leftShift = lerp(-130, -48, squeeze) + pulse * 0.18;
  const rightShift = lerp(130, 48, squeeze) - pulse * 0.18;
  const topShift = lerp(-102, -34, squeeze) + pulse * 0.08;
  const bottomShift = lerp(102, 34, squeeze) - pulse * 0.08;
  const seamInset = lerp(0, 18, squeeze);
  const residue = 1 - easeOut(clamp((progress - 0.06) / 0.34, 0, 1));
  const trailFade = 1 - easeOut(clamp((progress - 0.18) / 0.34, 0, 1));

  applyDot(
    moveIn,
    18.5,
    lerp(80, 110, squeeze),
    1,
    0.34 + squeeze * 0.16,
    lerp(1.02, 1.9, squeeze),
    lerp(0.98, 0.62, squeeze),
  );
  setOpacity(entryLane, 0.08 * residue);
  setTrailWindow(422, 0.56 * trailFade);

  setOpacity(coreGuide, 0.18 * residue);
  setOpacity(coreAxis, 0.14 * residue);
  setOpacity(futureBud, 0.16 * residue);
  setOpacity(searchArcTop, 0.12 * residue);
  setOpacity(searchArcRight, 0.12 * residue);
  setOpacity(searchArcBottom, 0.12 * residue);
  setOpacity(candidateTop, 0.12 * residue);
  setOpacity(candidateRight, 0.12 * residue);
  setOpacity(candidateBottom, 0.12 * residue);
  setOpacity(echoTop, 0.14 * residue);
  setOpacity(echoRight, 0.12 * residue);
  setOpacity(echoBottom, 0.14 * residue);
  setOpacity(futureBloom, 0.08 * residue);

  setOpacity(budSpine, 0.5);
  setOpacity(budLeft, 1);
  setOpacity(budRight, 1);
  setOpacity(budTop, 0.94);
  setOpacity(budBottom, 0.94);
  setOpacity(seamTop, 0.66);
  setOpacity(seamBottom, 0.66);
  setOpacity(pressureHalo, 0.28 + squeeze * 0.18);
  setGroupPose(budLeft, { x: 860 + leftShift, y: 450 });
  setGroupPose(budRight, { x: 860 + rightShift, y: 450 });
  setGroupPose(budTop, { x: 860, y: 450 + topShift });
  setGroupPose(budBottom, { x: 860, y: 450 + bottomShift });
  seamTop.setAttribute("d", `M ${(794 - seamInset).toFixed(2)} 360 H ${(926 + seamInset).toFixed(2)}`);
  seamBottom.setAttribute("d", `M ${(794 - seamInset).toFixed(2)} 540 H ${(926 + seamInset).toFixed(2)}`);
}

function transformationDot(progress) {
  if (progress < 0.2) {
    return mixPoint(points.budCenter, points.traceNorth, easeInOut(progress / 0.2));
  }
  if (progress < 0.44) {
    return mixPoint(points.traceNorth, points.traceEast, easeInOut((progress - 0.2) / 0.24));
  }
  if (progress < 0.68) {
    return mixPoint(points.traceEast, points.traceSouth, easeInOut((progress - 0.44) / 0.24));
  }
  if (progress < 0.86) {
    return mixPoint(points.traceSouth, points.traceWest, easeInOut((progress - 0.68) / 0.18));
  }
  return mixPoint(points.traceWest, points.budCenter, easeInOut((progress - 0.86) / 0.14));
}

function renderTransformation(progress) {
  const dotPosition = transformationDot(progress);
  const corridorResidue = 1 - easeOut(clamp(progress / 0.18, 0, 1));
  const traceNorthGrow = clamp((progress - 0.04) / 0.26, 0, 1);
  const traceEastGrow = clamp((progress - 0.24) / 0.24, 0, 1);
  const traceSouthGrow = clamp((progress - 0.44) / 0.24, 0, 1);
  const traceWestGrow = clamp((progress - 0.64) / 0.2, 0, 1);
  const petalGrow = clamp((progress - 0.18) / 0.58, 0, 1);
  const innerGrow = clamp((progress - 0.46) / 0.3, 0, 1);
  const shift = lerp(-24, 0, easeOut(progress));
  const turn = lerp(8, 0, easeOut(progress));
  const scale = lerp(0.96, 1, easeOut(progress));

  applyDot(dotPosition, lerp(18.5, 17, progress), lerp(92, 118, petalGrow), 1, 0.26 + pulseWave(progress, 2.1) * 0.12);
  setTrailWindow(220, 0.12 * corridorResidue);
  setOpacity(budSpine, 0.14 * corridorResidue);
  setOpacity(budLeft, 0.12 * corridorResidue);
  setOpacity(budRight, 0.12 * corridorResidue);
  setOpacity(budTop, 0.1 * corridorResidue);
  setOpacity(budBottom, 0.1 * corridorResidue);
  setOpacity(seamTop, 0.12 * corridorResidue);
  setOpacity(seamBottom, 0.12 * corridorResidue);
  setOpacity(pressureHalo, 0.12 * corridorResidue);

  setOpacity(bloomGroup, 1);
  setBloomPose(shift, 0, turn, scale);
  setOpacity(coreRing, 0.2 + petalGrow * 0.18);
  setOpacity(resolutionOrbit, 0.12 + innerGrow * 0.16);
  setOpacity(outerHalo, 0.12 + innerGrow * 0.18);
  setPathReveal(traceNorth, traceNorthGrow, 0.92);
  setPathReveal(traceEast, traceEastGrow, 0.92);
  setPathReveal(traceSouth, traceSouthGrow, 0.92);
  setPathReveal(traceWest, traceWestGrow, 0.92);
  setOpacity(petalNorth, petalGrow);
  setOpacity(petalEast, clamp(petalGrow - 0.08, 0, 1));
  setOpacity(petalSouth, clamp(petalGrow - 0.18, 0, 1));
  setOpacity(petalWest, clamp(petalGrow - 0.28, 0, 1));
  setOpacity(innerNorth, innerGrow);
  setOpacity(innerEast, clamp(innerGrow - 0.08, 0, 1));
  setOpacity(innerSouth, clamp(innerGrow - 0.16, 0, 1));
  setOpacity(innerWest, clamp(innerGrow - 0.24, 0, 1));
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const traceFade = 1 - easeOut(clamp(progress / 0.42, 0, 1));
  const bracketIn = clamp((progress - 0.24) / 0.38, 0, 1);
  const orbitSettle = 0.24 + pulseWave(progress, 1.4) * 0.06;

  applyDot(points.budCenter, 17, lerp(112, 84, progress), 1, orbitSettle);
  setTrailWindow(0, 0);
  setOpacity(bloomGroup, 1);
  setBloomPose(0, 0, lerp(1.4, 0, settle), lerp(0.992, 1, settle));

  setOpacity(coreRing, 0.4);
  setOpacity(resolutionOrbit, 0.32);
  setOpacity(outerHalo, 0.34);
  setPathReveal(traceNorth, 1, 0.22 * traceFade);
  setPathReveal(traceEast, 1, 0.2 * traceFade);
  setPathReveal(traceSouth, 1, 0.18 * traceFade);
  setPathReveal(traceWest, 1, 0.16 * traceFade);
  setOpacity(petalNorth, 1);
  setOpacity(petalEast, 1);
  setOpacity(petalSouth, 1);
  setOpacity(petalWest, 1);
  setOpacity(innerNorth, 0.38);
  setOpacity(innerEast, 0.34);
  setOpacity(innerSouth, 0.3);
  setOpacity(innerWest, 0.26);
  setOpacity(resolutionBrackets, 0.22 + bracketIn * 0.32);
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
