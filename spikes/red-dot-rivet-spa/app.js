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
const candidateLap = document.getElementById("candidate-lap");
const candidateBrace = document.getElementById("candidate-brace");
const candidateRivet = document.getElementById("candidate-rivet");
const socketGuide = document.getElementById("socket-guide");
const pressureHalo = document.getElementById("pressure-halo");
const plateLeft = document.getElementById("plate-left");
const plateRight = document.getElementById("plate-right");
const strapTop = document.getElementById("strap-top");
const strapBottom = document.getElementById("strap-bottom");
const memoryCross = document.getElementById("memory-cross");
const lockRouteBase = document.getElementById("lock-route-base");
const lockRouteActive = document.getElementById("lock-route-active");
const rivetRing = document.getElementById("rivet-ring");
const slotNorth = document.getElementById("slot-north");
const slotEast = document.getElementById("slot-east");
const slotSouth = document.getElementById("slot-south");
const slotWest = document.getElementById("slot-west");
const tabNorth = document.getElementById("tab-north");
const tabEast = document.getElementById("tab-east");
const tabSouth = document.getElementById("tab-south");
const tabWest = document.getElementById("tab-west");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const LOCK_ROUTE_LENGTH = lockRouteActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 566, y: 450 },
  lapCandidate: { x: 644, y: 390 },
  braceCandidate: { x: 832, y: 336 },
  rivetCandidate: { x: 1006, y: 394 },
  jointApproach: { x: 930, y: 452 },
  joint: { x: 820, y: 450 },
};

const system = {
  north: { x: 820, y: 392 },
  east: { x: 878, y: 450 },
  south: { x: 820, y: 508 },
  west: { x: 762, y: 450 },
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

function setGroupTransform(element, x, y, scale = 1, rotate = 0) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scale.toFixed(3)})`,
  );
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

function pointOnLockRoute(progress) {
  const length = clamp(progress, 0, 1) * LOCK_ROUTE_LENGTH;
  const point = lockRouteActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.16, 0, 1) * 0.42;
}

function tabReveal(progress, threshold) {
  return clamp((progress - threshold) / 0.14, 0, 1);
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
    appearance: 18,
    search: 30,
    tension: 14,
    transformation: 6,
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
    appearance: { x: 148, y: 132, width: 1096, height: 642 },
    search: { x: 164, y: 120, width: 1116, height: 666 },
    tension: { x: 348, y: 126, width: 948, height: 654 },
    transformation: { x: 344, y: 112, width: 956, height: 680 },
    resolution: { x: 392, y: 130, width: 860, height: 648 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -16) translate(800 450) scale(1.04) translate(-800 -450)",
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

function setJointGap(gap, opacity) {
  const leftX = 844 - gap;
  const rightX = 796 + gap;
  const topY = 474 - gap;
  const bottomY = 426 + gap;

  setGroupTransform(plateLeft, leftX, points.joint.y, 1, 0);
  setGroupTransform(plateRight, rightX, points.joint.y, 1, 0);
  setGroupTransform(strapTop, points.joint.x, topY, 1, 0);
  setGroupTransform(strapBottom, points.joint.x, bottomY, 1, 0);
  [plateLeft, plateRight, strapTop, strapBottom].forEach((element) => setOpacity(element, opacity));
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateLap, points.lapCandidate.x, points.lapCandidate.y, 1, -4);
  setGroupTransform(candidateBrace, points.braceCandidate.x, points.braceCandidate.y, 1, 0);
  setGroupTransform(candidateRivet, points.rivetCandidate.x, points.rivetCandidate.y, 1, 4);
  [candidateLap, candidateBrace, candidateRivet].forEach((element) => setOpacity(element, 0));

  setOpacity(socketGuide, 0);
  setOpacity(pressureHalo, 0);
  setJointGap(52, 0);

  setOpacity(memoryCross, 0);
  setOpacity(lockRouteBase, 0);
  setPathWindow(lockRouteActive, LOCK_ROUTE_LENGTH, 0, 0);
  setOpacity(rivetRing, 0);

  setGroupTransform(slotNorth, system.north.x, system.north.y, 1, 0);
  setGroupTransform(slotEast, system.east.x, system.east.y, 1, 0);
  setGroupTransform(slotSouth, system.south.x, system.south.y, 1, 0);
  setGroupTransform(slotWest, system.west.x, system.west.y, 1, 0);
  [slotNorth, slotEast, slotSouth, slotWest].forEach((slot) => setOpacity(slot, 0));

  setGroupTransform(tabNorth, system.north.x, system.north.y, 1, 0);
  setGroupTransform(tabEast, system.east.x, system.east.y, 1, 0);
  setGroupTransform(tabSouth, system.south.x, system.south.y, 1, 0);
  setGroupTransform(tabWest, system.west.x, system.west.y, 1, 0);
  [tabNorth, tabEast, tabSouth, tabWest].forEach((tab) => setOpacity(tab, 0));

  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(candidateLap, preview * 0.12);
  setOpacity(candidateBrace, preview * 0.1);
  setOpacity(candidateRivet, preview * 0.08);
  setOpacity(socketGuide, preview * 0.08);
  setJointGap(52, preview * 0.05);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.lapCandidate },
    { start: 0.28, end: 0.58, from: points.lapCandidate, to: points.braceCandidate },
    { start: 0.58, end: 0.84, from: points.braceCandidate, to: points.rivetCandidate },
    { start: 0.84, end: 1, from: points.rivetCandidate, to: points.jointApproach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.22, 0.08, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * clamp(0.16 + progress * 0.84, 0, 1), lerp(0.14, 0.06, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.24 + revealA * 0.2);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateLap, points.lapCandidate.x, points.lapCandidate.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -4);
  setGroupTransform(candidateBrace, points.braceCandidate.x, points.braceCandidate.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateRivet, points.rivetCandidate.x, points.rivetCandidate.y, lerp(0.84, activeC ? 1.05 : 0.95, revealC), 4);
  setOpacity(candidateLap, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateBrace, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateRivet, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(socketGuide, 0.14);
  setJointGap(48, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.jointApproach, points.joint, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const collapse = clamp(progress / 0.76, 0, 1);
  const gap = lerp(46, 10, easeInOut(clamp(progress / 0.72, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 122, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.56, compression),
    lerp(1, 1.86, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.08, 0, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const lapPosition = mixPoint(points.lapCandidate, { x: 728, y: 404 }, collapse);
  const bracePosition = mixPoint(points.braceCandidate, { x: 816, y: 360 }, collapse);
  const rivetPosition = mixPoint(points.rivetCandidate, { x: 904, y: 400 }, collapse);
  setGroupTransform(candidateLap, lapPosition.x, lapPosition.y, lerp(0.96, 0.72, collapse), -6);
  setGroupTransform(candidateBrace, bracePosition.x, bracePosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateRivet, rivetPosition.x, rivetPosition.y, lerp(0.95, 0.68, collapse), 6);
  setOpacity(candidateLap, lerp(0.3, 0.05, collapse));
  setOpacity(candidateBrace, lerp(0.28, 0.05, collapse));
  setOpacity(candidateRivet, lerp(1, 0.12, collapse));

  setOpacity(socketGuide, clamp((progress - 0.04) * 1.7, 0, 0.82));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setJointGap(gap, clamp((progress - 0.04) * 1.7, 0, 1));

  setOpacity(rivetRing, clamp((progress - 0.58) * 0.42, 0, 0.14));
  setOpacity(slotNorth, clamp((progress - 0.42) * 1.3, 0, 0.24));
  setOpacity(slotEast, clamp((progress - 0.52) * 1.3, 0, 0.24));
  setOpacity(slotSouth, clamp((progress - 0.62) * 1.3, 0, 0.24));
  setOpacity(slotWest, clamp((progress - 0.72) * 1.3, 0, 0.24));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnLockRoute(routeProgress);
  const northReveal = tabReveal(routeProgress, 0.12);
  const eastReveal = tabReveal(routeProgress, 0.34);
  const southReveal = tabReveal(routeProgress, 0.56);
  const westReveal = tabReveal(routeProgress, 0.78);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * 0.22, clamp(0.04 - progress * 0.06, 0, 1));

  setOpacity(memoryCross, clamp((progress - 0.64) * 1.4, 0, 0.14));
  setOpacity(lockRouteBase, lerp(0.16, 0.24, routeProgress));
  setPathWindow(lockRouteActive, LOCK_ROUTE_LENGTH, LOCK_ROUTE_LENGTH * routeProgress, 1);
  setOpacity(rivetRing, lerp(0.18, 0.98, routeProgress));

  setOpacity(socketGuide, lerp(0.82, 0.08, progress));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setJointGap(lerp(10, 26, progress), 1);

  setOpacity(candidateLap, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateBrace, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateRivet, clamp(0.12 - progress * 0.16, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotNorth, slotState(routeProgress, 0.12));
  setOpacity(slotEast, slotState(routeProgress, 0.34));
  setOpacity(slotSouth, slotState(routeProgress, 0.56));
  setOpacity(slotWest, slotState(routeProgress, 0.78));

  setGroupTransform(tabNorth, system.north.x, system.north.y, lerp(0.9, 1, easeOut(northReveal)), 0);
  setGroupTransform(tabEast, system.east.x, system.east.y, lerp(0.9, 1, easeOut(eastReveal)), 0);
  setGroupTransform(tabSouth, system.south.x, system.south.y, lerp(0.9, 1, easeOut(southReveal)), 0);
  setGroupTransform(tabWest, system.west.x, system.west.y, lerp(0.9, 1, easeOut(westReveal)), 0);
  setOpacity(tabNorth, northReveal);
  setOpacity(tabEast, eastReveal);
  setOpacity(tabSouth, southReveal);
  setOpacity(tabWest, westReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.7) * 1.4, 0, 0.18));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.joint, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(memoryCross, lerp(0.14, 0.16, settle));
  setOpacity(lockRouteBase, lerp(0.24, 0.08, settle));
  setPathWindow(lockRouteActive, LOCK_ROUTE_LENGTH, LOCK_ROUTE_LENGTH, lerp(1, 0.14, settle));
  setOpacity(rivetRing, lerp(0.98, 0.92, settle));

  [socketGuide, pressureHalo, candidateLap, candidateBrace, candidateRivet, slotNorth, slotEast, slotSouth, slotWest].forEach((element) =>
    setOpacity(element, 0),
  );
  setJointGap(lerp(26, 28, settle), 0.92);

  setGroupTransform(tabNorth, system.north.x, lerp(system.north.y, system.north.y - 2, settle), 0.97, 0);
  setGroupTransform(tabEast, lerp(system.east.x, system.east.x + 2, settle), system.east.y, 0.97, 0);
  setGroupTransform(tabSouth, system.south.x, lerp(system.south.y, system.south.y + 2, settle), 0.97, 0);
  setGroupTransform(tabWest, lerp(system.west.x, system.west.x - 2, settle), system.west.y, 0.97, 0);
  setOpacity(tabNorth, 0.92);
  setOpacity(tabEast, 0.92);
  setOpacity(tabSouth, 0.92);
  setOpacity(tabWest, 0.92);

  setOpacity(resolutionHalo, lerp(0.18, 0.28, settle));
  setOpacity(resolutionFrame, lerp(0.22, 0.7, settle));
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
