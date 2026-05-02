const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateCradle = document.getElementById("candidate-cradle");
const candidatePedestal = document.getElementById("candidate-pedestal");
const candidateSling = document.getElementById("candidate-sling");
const pivotGuide = document.getElementById("pivot-guide");
const pivotSupport = document.getElementById("pivot-support");
const beamGroup = document.getElementById("beam-group");
const rightSeat = document.getElementById("right-seat");
const leftHanger = document.getElementById("left-hanger");
const rightHanger = document.getElementById("right-hanger");
const leftWeight = document.getElementById("left-weight");
const rightWeight = document.getElementById("right-weight");
const topStem = document.getElementById("top-stem");
const crownBar = document.getElementById("crown-bar");
const memoryArc = document.getElementById("memory-arc");
const balanceHalo = document.getElementById("balance-halo");
const balanceRing = document.getElementById("balance-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";
const BEAM_HALF = 196;
const RESOLVED_BEAM_HALF = 136;

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 470 },
  ingress: { x: 560, y: 470 },
  cradle: { x: 676, y: 406 },
  pedestal: { x: 846, y: 338 },
  sling: { x: 1008, y: 404 },
  perch: { x: 1026, y: 438 },
  pivot: { x: 846, y: 458 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
  looping: true,
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

function segmentedPoint(progress, segments) {
  for (const segment of segments) {
    if (progress <= segment.end) {
      const local = clamp((progress - segment.start) / (segment.end - segment.start), 0, 1);
      return mixPoint(segment.from, segment.to, easeInOut(local));
    }
  }
  return segments[segments.length - 1].to;
}

function setOpacity(element, value) {
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
}

function setCircleCenter(element, point) {
  element.setAttribute("cx", point.x.toFixed(2));
  element.setAttribute("cy", point.y.toFixed(2));
}

function setRadius(element, radius) {
  element.setAttribute("r", radius.toFixed(2));
}

function setGroupTransform(element, x, y, scale = 1, rotate = 0) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scale.toFixed(3)})`,
  );
}

function setLine(element, x1, y1, x2, y2) {
  element.setAttribute("x1", x1.toFixed(2));
  element.setAttribute("y1", y1.toFixed(2));
  element.setAttribute("x2", x2.toFixed(2));
  element.setAttribute("y2", y2.toFixed(2));
}

function setDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1) {
  setCircleCenter(dotCore, position);
  setCircleCenter(dotHalo, position);
  dotCore.setAttribute("r", radius.toFixed(2));
  dotHalo.setAttribute("r", haloRadius.toFixed(2));
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  dotCore.setAttribute(
    "transform",
    `translate(${position.x} ${position.y}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-position.x} ${-position.y})`,
  );
  dotHalo.setAttribute(
    "transform",
    `translate(${position.x} ${position.y}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-position.x} ${-position.y})`,
  );
}

function setPathWindow(element, totalLength, visibleLength, opacity) {
  const clamped = clamp(visibleLength, 0, totalLength);
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 200).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function beamEndpoint(angle, side, halfLength = BEAM_HALF) {
  const radians = (angle * Math.PI) / 180;
  const dx = halfLength * side;
  return {
    x: points.pivot.x + Math.cos(radians) * dx,
    y: points.pivot.y + Math.sin(radians) * dx,
  };
}

function setBeamState(angle, opacity, scale = 1) {
  beamGroup.setAttribute(
    "transform",
    `translate(${points.pivot.x.toFixed(2)} ${points.pivot.y.toFixed(2)}) rotate(${angle.toFixed(2)}) scale(${scale.toFixed(3)} 1)`,
  );
  setOpacity(beamGroup, opacity);
}

function setWeight(weight, hanger, anchor, length, opacity, scale = 1) {
  setLine(hanger, anchor.x, anchor.y, anchor.x, anchor.y + length);
  setGroupTransform(weight, anchor.x, anchor.y + length, scale, 0);
  setOpacity(hanger, opacity);
  setOpacity(weight, opacity);
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

function applySceneOffset(phaseId) {
  const offsets = {
    appearance: 12,
    search: 30,
    tension: 16,
    transformation: 8,
    resolution: 0,
  };
  const offsetY = offsets[phaseId] ?? 0;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 118, y: 156, width: 1090, height: 628 },
    search: { x: 150, y: 146, width: 1112, height: 628 },
    tension: { x: 320, y: 152, width: 1004, height: 620 },
    transformation: { x: 608, y: 86, width: 476, height: 860 },
    resolution: { x: 651, y: 78, width: 390, height: 820 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -14) translate(800 450) scale(1.045) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
  } else {
    layoutRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  }
  svg.setAttribute("viewBox", FULL_VIEWBOX);
}

function resetScene() {
  setDot(points.start, 18, 72, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateCradle, points.cradle.x, points.cradle.y, 1, -2);
  setGroupTransform(candidatePedestal, points.pedestal.x, points.pedestal.y, 1, 0);
  setGroupTransform(candidateSling, points.sling.x, points.sling.y, 1, 2);
  [candidateCradle, candidatePedestal, candidateSling].forEach((element) => setOpacity(element, 0));

  setOpacity(pivotGuide, 0);
  setOpacity(pivotSupport, 0);
  setBeamState(0, 0, 1);
  setOpacity(rightSeat, 0);
  setWeight(leftWeight, leftHanger, beamEndpoint(0, -1), 0, 0);
  setWeight(rightWeight, rightHanger, beamEndpoint(0, 1), 0, 0);
  setLine(topStem, points.pivot.x, points.pivot.y - 132, points.pivot.x, points.pivot.y - 14);
  setLine(crownBar, points.pivot.x - 72, points.pivot.y - 132, points.pivot.x + 72, points.pivot.y - 132);
  setOpacity(topStem, 0);
  setOpacity(crownBar, 0);
  setOpacity(memoryArc, 0);
  setRadius(balanceHalo, 146);
  setRadius(balanceRing, 96);
  setOpacity(balanceHalo, 0);
  setOpacity(balanceRing, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(16, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.5, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.14);
  setOpacity(candidateCradle, preview * 0.12);
  setOpacity(candidatePedestal, preview * 0.08);
  setOpacity(candidateSling, preview * 0.06);
  setOpacity(pivotGuide, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.cradle },
    { start: 0.24, end: 0.54, from: points.cradle, to: points.pedestal },
    { start: 0.54, end: 0.82, from: points.pedestal, to: points.sling },
    { start: 0.82, end: 1, from: points.sling, to: points.perch },
  ]);

  setDot(position, 18, 84, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.14, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.24, 0.13, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.2 + revealA * 0.22);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateCradle, points.cradle.x, points.cradle.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), -4);
  setGroupTransform(candidatePedestal, points.pedestal.x, points.pedestal.y, lerp(0.9, activeB ? 1.05 : 0.97, revealB), 0);
  setGroupTransform(candidateSling, points.sling.x, points.sling.y, lerp(0.88, activeC ? 1.05 : 0.97, revealC), 3);
  setOpacity(candidateCradle, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidatePedestal, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateSling, activeC ? 1 : revealC * 0.34 + 0.12);
  setOpacity(pivotGuide, 0.14);
}

function renderTension(progress) {
  const beamProgress = easeInOut(clamp(progress / 0.72, 0, 1));
  const angle = lerp(0, 16, beamProgress);
  const rightFlat = beamEndpoint(0, 1);
  const rightEnd = beamEndpoint(angle, 1);
  const leftEnd = beamEndpoint(angle, -1);
  const seatLanding = mixPoint(points.perch, rightFlat, easeOut(clamp(progress / 0.22, 0, 1)));
  const position = mixPoint(seatLanding, rightEnd, easeInOut(clamp((progress - 0.16) / 0.56, 0, 1)));
  const compression = clamp((progress - 0.34) / 0.28, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(84, 106, progress),
    1,
    0.22 + pulseWave(progress, 2.1) * 0.1,
    lerp(1, 1.16, compression),
    lerp(1, 0.82, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.18 : 0.14, 0, progress));
  });

  setGroupTransform(
    candidateCradle,
    lerp(points.cradle.x, 742, progress),
    lerp(points.cradle.y, 446, progress),
    lerp(0.98, 0.78, progress),
    -10,
  );
  setGroupTransform(
    candidatePedestal,
    lerp(points.pedestal.x, 852, progress),
    lerp(points.pedestal.y, 384, progress),
    lerp(0.98, 0.72, progress),
    0,
  );
  setGroupTransform(
    candidateSling,
    lerp(points.sling.x, 1000, progress),
    lerp(points.sling.y, 430, progress),
    lerp(1, 0.74, progress),
    8,
  );
  setOpacity(candidateCradle, lerp(0.28, 0.04, progress));
  setOpacity(candidatePedestal, lerp(0.22, 0.04, progress));
  setOpacity(candidateSling, lerp(0.72, 0.08, progress));

  setOpacity(pivotGuide, lerp(0.14, 0.28, progress));
  setOpacity(pivotSupport, clamp((progress - 0.04) * 1.6, 0, 0.88));
  setBeamState(angle, clamp((progress - 0.02) * 1.8, 0, 1), 1);

  const seatOpacity = clamp((progress - 0.08) * 1.8, 0, 1);
  setGroupTransform(rightSeat, rightEnd.x, rightEnd.y + 22, 1, 0);
  setOpacity(rightSeat, seatOpacity);

  setWeight(leftWeight, leftHanger, leftEnd, lerp(74, 176, easeOut(clamp(progress / 0.78, 0, 1))), 0.9);
  setWeight(rightWeight, rightHanger, rightEnd, lerp(22, 56, clamp((progress - 0.4) / 0.4, 0, 1)), 0.14);
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.84, 0, 1));
  const angle = lerp(16, 0, routeProgress);
  const beamHalf = lerp(BEAM_HALF, RESOLVED_BEAM_HALF, routeProgress);
  const beamScale = beamHalf / BEAM_HALF;
  const start = beamEndpoint(16, 1);
  const basePosition = mixPoint(start, points.pivot, routeProgress);
  const lift = Math.sin(routeProgress * Math.PI) * 44;
  const position = {
    x: basePosition.x,
    y: basePosition.y - lift,
  };
  const leftEnd = beamEndpoint(angle, -1, beamHalf);
  const rightEnd = beamEndpoint(angle, 1, beamHalf);
  const rightWeightReveal = clamp((progress - 0.18) / 0.34, 0, 1);

  setDot(
    position,
    16,
    96,
    1,
    0.21 + pulseWave(progress, 2.0) * 0.08,
    lerp(1.16, 1, routeProgress),
    lerp(0.82, 1, routeProgress),
  );
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [searchGuideA, searchGuideB, searchGuideC, candidateCradle, candidatePedestal, candidateSling].forEach((element) =>
    setOpacity(element, 0),
  );
  setOpacity(pivotGuide, clamp(0.28 - progress * 0.4, 0, 1));
  setOpacity(pivotSupport, lerp(0.88, 0.42, progress));
  setBeamState(angle, 1, beamScale);

  setGroupTransform(rightSeat, rightEnd.x, rightEnd.y + 18, 1, 0);
  setOpacity(rightSeat, clamp(1 - progress * 1.35, 0, 1));

  setWeight(leftWeight, leftHanger, leftEnd, lerp(176, 120, routeProgress), 0.84);
  setWeight(rightWeight, rightHanger, rightEnd, lerp(44, 120, rightWeightReveal), 0.2 + rightWeightReveal * 0.64);

  setOpacity(topStem, clamp((progress - 0.18) * 1.5, 0, 0.78));
  setOpacity(crownBar, clamp((progress - 0.24) * 1.6, 0, 0.7));
  setOpacity(memoryArc, clamp((progress - 0.32) * 1.35, 0, 0.26));
  setRadius(balanceHalo, lerp(122, 136, progress));
  setRadius(balanceRing, lerp(82, 90, progress));
  setOpacity(balanceHalo, clamp((progress - 0.56) * 1.45, 0, 0.22));
  setOpacity(balanceRing, clamp((progress - 0.68) * 1.45, 0, 0.24));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;
  const beamHalf = lerp(RESOLVED_BEAM_HALF, 132, settle);
  const beamScale = beamHalf / BEAM_HALF;
  const leftEnd = beamEndpoint(0, -1, beamHalf);
  const rightEnd = beamEndpoint(0, 1, beamHalf);

  setDot(points.pivot, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setBeamState(0, lerp(0.94, 0.84, settle), beamScale);
  setOpacity(pivotGuide, 0);
  setOpacity(pivotSupport, lerp(0.34, 0.2, settle));
  setOpacity(rightSeat, 0);

  setWeight(leftWeight, leftHanger, leftEnd, lerp(120, 114, settle), 0.84);
  setWeight(rightWeight, rightHanger, rightEnd, lerp(120, 114, settle), 0.84);

  setOpacity(topStem, lerp(0.78, 0.72, settle));
  setOpacity(crownBar, lerp(0.7, 0.62, settle));
  setOpacity(memoryArc, lerp(0.26, 0.12, settle));
  setRadius(balanceHalo, 136);
  setRadius(balanceRing, 86);
  setOpacity(balanceHalo, lerp(0.22, 0.32, settle));
  setOpacity(balanceRing, lerp(0.24, 0.9, settle));
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);
  applySceneOffset(info.phase.id);
  applyFraming(info.phase.id);

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

  updatePhaseLabel(info);
  svg.dataset.phase = info.phase.id;
  state.currentElapsed = elapsed;
}

function setPlaying(nextPlaying) {
  if (state.playing === nextPlaying) {
    return;
  }
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
  let elapsed = state.elapsedBeforePause;
  if (state.playing) {
    const rawElapsed = state.elapsedBeforePause + (now - state.startAt);
    if (state.looping) {
      elapsed = rawElapsed % TOTAL_DURATION;
    } else {
      elapsed = Math.min(rawElapsed, TOTAL_DURATION - 1);
      if (rawElapsed >= TOTAL_DURATION) {
        state.playing = false;
        state.elapsedBeforePause = elapsed;
      }
    }
  }

  state.currentElapsed = elapsed;
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
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
