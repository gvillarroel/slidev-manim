const TOTAL_DURATION = 36_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 8_000 },
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
const candidateNotch = document.getElementById("candidate-notch");
const candidatePocket = document.getElementById("candidate-pocket");
const candidateWeave = document.getElementById("candidate-weave");
const gateGuide = document.getElementById("gate-guide");
const gateTop = document.getElementById("gate-top");
const gateBottom = document.getElementById("gate-bottom");
const gateLeft = document.getElementById("gate-left");
const gateRight = document.getElementById("gate-right");
const gateCenterRail = document.getElementById("gate-center-rail");
const gateFloor = document.getElementById("gate-floor");
const pressureWindow = document.getElementById("pressure-window");
const pressureHalo = document.getElementById("pressure-halo");
const weaveHorizontalBack = document.getElementById("weave-horizontal-back");
const weaveVerticalBack = document.getElementById("weave-vertical-back");
const weaveVerticalFront = document.getElementById("weave-vertical-front");
const weaveTurn = document.getElementById("weave-turn");
const weaveFront = document.getElementById("weave-front");
const weaveTrace = document.getElementById("weave-trace");
const weaveCorners = document.getElementById("weave-corners");
const resolutionFrame = document.getElementById("resolution-frame");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const GATE_GUIDE_LENGTH = gateGuide.getTotalLength();
const WEAVE_TRACE_LENGTH = weaveTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 302, y: 450 },
  ingress: { x: 562, y: 450 },
  notch: { x: 682, y: 386 },
  pocket: { x: 840, y: 522 },
  weave: { x: 1000, y: 378 },
  approach: { x: 964, y: 378 },
  gateEnd: { x: 782, y: 530 },
  center: { x: 820, y: 450 },
  upperRight: { x: 886, y: 392 },
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

function pointOnPath(path, totalLength, progress) {
  const length = clamp(progress, 0, 1) * totalLength;
  const point = path.getPointAtLength(length);
  return { x: point.x, y: point.y };
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

function setTranslate(element, x = 0, y = 0) {
  element.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
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
    search: 28,
    tension: 12,
    transformation: 4,
    resolution: -2,
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
    appearance: { x: 136, y: 150, width: 1050, height: 610 },
    search: { x: 184, y: 132, width: 1040, height: 640 },
    tension: { x: 376, y: 146, width: 908, height: 628 },
    transformation: { x: 416, y: 130, width: 848, height: 650 },
    resolution: { x: 436, y: 140, width: 808, height: 640 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -10) translate(800 450) scale(1.04) translate(-800 -450)",
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
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateNotch, points.notch.x, points.notch.y, 1, -2);
  setGroupTransform(candidatePocket, points.pocket.x, points.pocket.y, 1, 0);
  setGroupTransform(candidateWeave, points.weave.x, points.weave.y, 1, 4);
  [candidateNotch, candidatePocket, candidateWeave].forEach((element) => setOpacity(element, 0));

  setOpacity(gateGuide, 0);
  setOpacity(gateTop, 0);
  setOpacity(gateBottom, 0);
  setOpacity(gateLeft, 0);
  setOpacity(gateRight, 0);
  setOpacity(gateCenterRail, 0);
  setOpacity(gateFloor, 0);
  setOpacity(pressureWindow, 0);
  setOpacity(pressureHalo, 0);
  [gateTop, gateBottom, gateLeft, gateRight].forEach((element) => setTranslate(element, 0, 0));

  [weaveHorizontalBack, weaveVerticalBack, weaveVerticalFront, weaveTurn, weaveFront].forEach((element) => {
    setOpacity(element, 0);
    setTranslate(element, 0, 0);
  });
  setPathWindow(weaveTrace, WEAVE_TRACE_LENGTH, 0, 0);
  setOpacity(weaveCorners, 0);
  setTranslate(weaveCorners, 0, 0);
  setOpacity(resolutionFrame, 0);
  setOpacity(resolutionHalo, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.9);
  const preview = clamp((progress - 0.46) * 1.7, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 88, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.1) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.1) * 1.4, 0, 0.34));

  setOpacity(searchGuideA, preview * 0.24);
  setOpacity(candidateNotch, preview * 0.2);
  setOpacity(candidatePocket, preview * 0.12);
  setOpacity(candidateWeave, preview * 0.1);

  setOpacity(gateGuide, preview * 0.08);
  setOpacity(gateTop, preview * 0.08);
  setOpacity(gateBottom, preview * 0.06);
  setOpacity(gateLeft, preview * 0.08);
  setOpacity(gateRight, preview * 0.08);
  setOpacity(gateCenterRail, preview * 0.06);
  setOpacity(pressureWindow, preview * 0.06);
  setOpacity(pressureHalo, preview * 0.08);

  setOpacity(weaveHorizontalBack, preview * 0.08);
  setOpacity(weaveTurn, preview * 0.06);
  setOpacity(weaveVerticalBack, preview * 0.04);
  setOpacity(weaveVerticalFront, preview * 0.04);
  setOpacity(weaveFront, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.notch },
    { start: 0.24, end: 0.56, from: points.notch, to: points.pocket },
    { start: 0.56, end: 0.84, from: points.pocket, to: points.weave },
    { start: 0.84, end: 1, from: points.weave, to: points.approach },
  ]);

  const revealA = clamp(progress / 0.2, 0, 1);
  const revealB = clamp((progress - 0.2) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.52) / 0.24, 0, 1);
  const activeA = progress < 0.26 ? 1 : 0;
  const activeB = progress >= 0.26 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setDot(position, 18, 92, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.22, 0.05, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.04, progress));

  searchGuideA.setAttribute("stroke", activeA ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", activeB ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", activeC ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.2 + revealA * 0.22);
  setOpacity(searchGuideB, 0.1 + revealB * 0.24);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  setGroupTransform(candidateNotch, points.notch.x, points.notch.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -2);
  setGroupTransform(candidatePocket, points.pocket.x, points.pocket.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateWeave, points.weave.x, points.weave.y, lerp(0.84, activeC ? 1.05 : 0.96, revealC), 4);
  setOpacity(candidateNotch, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidatePocket, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateWeave, activeC ? 1 : revealC * 0.36 + 0.12);

  setOpacity(gateGuide, 0.12);
  setOpacity(gateTop, 0.08);
  setOpacity(gateBottom, 0.06);
  setOpacity(gateLeft, 0.08);
  setOpacity(gateRight, 0.08);
  setOpacity(gateCenterRail, 0.08);
  setOpacity(gateFloor, 0.06);
  setOpacity(pressureWindow, 0.08);
  setOpacity(pressureHalo, 0.08);

  setOpacity(weaveHorizontalBack, 0.08);
  setOpacity(weaveTurn, 0.06);
  setOpacity(weaveVerticalBack, 0.04);
  setOpacity(weaveVerticalFront, 0.04);
  setOpacity(weaveFront, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.46, 0, 1);
  const collapse = clamp((progress - 0.42) / 0.5, 0, 1);
  const pathPosition = pointOnPath(gateGuide, GATE_GUIDE_LENGTH, easeInOut(travel));
  const position = mixPoint(pathPosition, points.center, easeInOut(collapse));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const verticalShift = lerp(0, 28, easeInOut(clamp(progress / 0.7, 0, 1)));
  const horizontalShift = lerp(0, 42, easeInOut(clamp(progress / 0.7, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(92, 126, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.56, compression),
    lerp(1, 1.86, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.08, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const notchPosition = mixPoint(points.notch, { x: 730, y: 394 }, collapse);
  const pocketPosition = mixPoint(points.pocket, { x: 810, y: 518 }, collapse);
  const weavePosition = mixPoint(points.weave, { x: 920, y: 392 }, collapse);
  setGroupTransform(candidateNotch, notchPosition.x, notchPosition.y, lerp(0.96, 0.72, collapse), -6);
  setGroupTransform(candidatePocket, pocketPosition.x, pocketPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateWeave, weavePosition.x, weavePosition.y, lerp(0.96, 0.72, collapse), 2);
  setOpacity(candidateNotch, lerp(0.3, 0.06, collapse));
  setOpacity(candidatePocket, lerp(0.28, 0.05, collapse));
  setOpacity(candidateWeave, lerp(1, 0.14, collapse));

  setOpacity(gateGuide, clamp((progress - 0.02) * 1.8, 0, 0.78));
  setOpacity(gateTop, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(gateBottom, clamp((progress - 0.06) * 1.5, 0, 0.96));
  setOpacity(gateLeft, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(gateRight, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(gateCenterRail, clamp((progress - 0.12) * 1.5, 0, 0.58));
  setOpacity(gateFloor, clamp((progress - 0.18) * 1.5, 0, 0.52));
  setOpacity(pressureWindow, clamp((progress - 0.1) * 1.6, 0, 0.68));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));

  setTranslate(gateTop, 0, verticalShift);
  setTranslate(gateBottom, 0, -verticalShift);
  setTranslate(gateLeft, horizontalShift, 0);
  setTranslate(gateRight, -horizontalShift, 0);

  setOpacity(weaveHorizontalBack, clamp((progress - 0.68) * 1.6, 0, 0.18));
  setOpacity(weaveTurn, clamp((progress - 0.72) * 1.6, 0, 0.18));
  setOpacity(weaveVerticalBack, clamp((progress - 0.72) * 1.6, 0, 0.16));
  setOpacity(weaveVerticalFront, clamp((progress - 0.76) * 1.6, 0, 0.16));
  setOpacity(weaveFront, clamp((progress - 0.78) * 1.7, 0, 0.22));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.9, 0, 1));
  const position = pointOnPath(weaveTrace, WEAVE_TRACE_LENGTH, routeProgress);
  const open = easeOut(progress);

  setDot(position, 16, 100, 1, 0.2 + pulseWave(progress, 2.0) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  setOpacity(gateGuide, lerp(0.78, 0.04, progress));
  setOpacity(gateTop, clamp(1 - progress * 1.2, 0, 1));
  setOpacity(gateBottom, clamp(0.96 - progress * 1.15, 0, 1));
  setOpacity(gateLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(gateRight, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(gateCenterRail, clamp(0.58 - progress * 0.8, 0, 1));
  setOpacity(gateFloor, clamp(0.52 - progress * 0.84, 0, 1));
  setOpacity(pressureWindow, clamp(0.68 - progress * 1.0, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.52, 0, 1));
  setTranslate(gateTop, 0, lerp(28, 12, progress));
  setTranslate(gateBottom, 0, lerp(-28, -10, progress));
  setTranslate(gateLeft, lerp(42, 20, progress), 0);
  setTranslate(gateRight, lerp(-42, -18, progress), 0);

  [candidateNotch, candidatePocket, candidateWeave, searchGuideA, searchGuideB, searchGuideC].forEach((element) => {
    setOpacity(element, 0);
  });

  setOpacity(weaveHorizontalBack, clamp(progress * 1.5, 0, 0.94));
  setOpacity(weaveTurn, clamp((progress - 0.02) * 1.6, 0, 0.94));
  setOpacity(weaveVerticalBack, clamp((progress - 0.08) * 1.5, 0, 0.9));
  setOpacity(weaveVerticalFront, clamp((progress - 0.18) * 1.6, 0, 0.96));
  setOpacity(weaveFront, clamp((progress - 0.12) * 1.6, 0, 1));
  setPathWindow(weaveTrace, WEAVE_TRACE_LENGTH, WEAVE_TRACE_LENGTH * routeProgress, 0.9);
  setOpacity(weaveCorners, clamp((progress - 0.68) * 1.4, 0, 0.4));
  setOpacity(resolutionFrame, clamp((progress - 0.74) * 1.5, 0, 0.14));
  setOpacity(resolutionHalo, clamp((progress - 0.7) * 1.4, 0, 0.12));

  setTranslate(weaveHorizontalBack, 0, lerp(0, -8, open));
  setTranslate(weaveTurn, 0, lerp(0, 4, open));
  setTranslate(weaveVerticalBack, 0, lerp(0, -6, open));
  setTranslate(weaveVerticalFront, 0, lerp(0, 4, open));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.2) * 0.05;
  const position = mixPoint(points.upperRight, points.center, settle);

  setDot(position, 16, 100, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [gateGuide, gateTop, gateBottom, gateLeft, gateRight, gateCenterRail, gateFloor, pressureWindow, pressureHalo].forEach((element) => {
    setOpacity(element, 0);
  });

  setOpacity(weaveHorizontalBack, 0.92);
  setOpacity(weaveTurn, 0.92);
  setOpacity(weaveVerticalBack, 0.88);
  setOpacity(weaveVerticalFront, 0.92);
  setOpacity(weaveFront, lerp(1, 0.28, settle));
  setPathWindow(weaveTrace, WEAVE_TRACE_LENGTH, WEAVE_TRACE_LENGTH, lerp(0.9, 0, settle));
  setOpacity(weaveCorners, lerp(0.4, 0.92, settle));
  setOpacity(resolutionFrame, lerp(0.14, 0.1, settle));
  setOpacity(resolutionHalo, lerp(0.12, 0.22, settle));

  setTranslate(weaveHorizontalBack, 0, lerp(-8, -24, settle));
  setTranslate(weaveTurn, 0, lerp(4, 14, settle));
  setTranslate(weaveVerticalBack, 0, lerp(-6, -18, settle));
  setTranslate(weaveVerticalFront, 0, lerp(4, 20, settle));
  setTranslate(weaveCorners, 0, lerp(0, -4, settle));
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
