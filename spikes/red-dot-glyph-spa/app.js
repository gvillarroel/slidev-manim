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
const candidateShelf = document.getElementById("candidate-shelf");
const candidateElbow = document.getElementById("candidate-elbow");
const candidateFlare = document.getElementById("candidate-flare");
const pressGuide = document.getElementById("press-guide");
const pressTop = document.getElementById("press-top");
const pressBottom = document.getElementById("press-bottom");
const pressLeft = document.getElementById("press-left");
const pressRight = document.getElementById("press-right");
const pressSlotLeft = document.getElementById("press-slot-left");
const pressSlotRight = document.getElementById("press-slot-right");
const pressBridge = document.getElementById("press-bridge");
const pressureHalo = document.getElementById("pressure-halo");
const glyphBack = document.getElementById("glyph-back");
const glyphFlare = document.getElementById("glyph-flare");
const glyphNode = document.getElementById("glyph-node");
const glyphTrace = document.getElementById("glyph-trace");
const glyphCorners = document.getElementById("glyph-corners");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const PRESS_GUIDE_LENGTH = pressGuide.getTotalLength();
const GLYPH_TRACE_LENGTH = glyphTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 392, y: 450 },
  ingress: { x: 562, y: 450 },
  shelf: { x: 688, y: 392 },
  elbow: { x: 820, y: 524 },
  flare: { x: 934, y: 430 },
  approach: { x: 882, y: 450 },
  gateEnd: { x: 748, y: 528 },
  center: { x: 800, y: 454 },
  flareTip: { x: 944, y: 374 },
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
  const offsetXs = {
    appearance: -8,
    search: -20,
    tension: -26,
    transformation: -34,
    resolution: -36,
  };
  const offsets = {
    appearance: -18,
    search: -16,
    tension: -12,
    transformation: -10,
    resolution: -8,
  };
  const offsetX = offsetXs[phaseId] ?? 0;
  const offsetY = offsets[phaseId] ?? 0;
  sceneRoot.setAttribute("transform", `translate(${offsetX} ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 118, y: 132, width: 1140, height: 676 },
    search: { x: 154, y: 124, width: 1128, height: 684 },
    tension: { x: 298, y: 122, width: 1010, height: 690 },
    transformation: { x: 332, y: 118, width: 1022, height: 706 },
    resolution: { x: 330, y: 122, width: 1038, height: 708 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -10) translate(800 450) scale(1.14) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
  } else {
    layoutRoot.setAttribute("transform", "translate(800 450) scale(1.06) translate(-800 -450)");
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

  setGroupTransform(candidateShelf, points.shelf.x, points.shelf.y, 1, -2);
  setGroupTransform(candidateElbow, points.elbow.x, points.elbow.y, 1, 0);
  setGroupTransform(candidateFlare, points.flare.x, points.flare.y, 1, 4);
  [candidateShelf, candidateElbow, candidateFlare].forEach((element) => setOpacity(element, 0));

  setOpacity(pressGuide, 0);
  setOpacity(pressTop, 0);
  setOpacity(pressBottom, 0);
  setOpacity(pressLeft, 0);
  setOpacity(pressRight, 0);
  setOpacity(pressSlotLeft, 0);
  setOpacity(pressSlotRight, 0);
  setOpacity(pressBridge, 0);
  setOpacity(pressureHalo, 0);
  [pressTop, pressBottom, pressLeft, pressRight, pressSlotLeft, pressSlotRight, pressBridge].forEach((element) => {
    setTranslate(element, 0, 0);
  });

  [glyphBack, glyphFlare, glyphNode].forEach((element) => {
    setOpacity(element, 0);
    setTranslate(element, 0, 0);
  });
  setPathWindow(glyphTrace, GLYPH_TRACE_LENGTH, 0, 0);
  setOpacity(glyphCorners, 0);
  setTranslate(glyphCorners, 0, 0);
  setOpacity(resolutionHalo, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.9);
  const preview = clamp((progress - 0.44) * 1.7, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 86, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.1) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.08) * 1.4, 0, 0.34));

  setOpacity(searchGuideA, preview * 0.26);
  setOpacity(candidateShelf, preview * 0.22);
  setOpacity(candidateElbow, preview * 0.04);
  setOpacity(candidateFlare, preview * 0.02);

  setOpacity(pressGuide, preview * 0.04);
  setOpacity(pressTop, preview * 0.04);
  setOpacity(pressBottom, preview * 0.02);
  setOpacity(pressLeft, preview * 0.05);
  setOpacity(pressRight, preview * 0.03);
  setOpacity(pressSlotLeft, preview * 0.02);
  setOpacity(pressSlotRight, preview * 0.02);
  setOpacity(pressBridge, preview * 0.01);
  setOpacity(pressureHalo, preview * 0.04);

  setOpacity(glyphBack, 0);
  setOpacity(glyphFlare, 0);
  setOpacity(glyphNode, 0);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.shelf },
    { start: 0.24, end: 0.56, from: points.shelf, to: points.elbow },
    { start: 0.56, end: 0.84, from: points.elbow, to: points.flare },
    { start: 0.84, end: 1, from: points.flare, to: points.approach },
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
  setOpacity(searchGuideA, 0.18 + revealA * 0.24);
  setOpacity(searchGuideB, 0.08 + revealB * 0.26);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  setGroupTransform(candidateShelf, points.shelf.x, points.shelf.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -2);
  setGroupTransform(candidateElbow, points.elbow.x, points.elbow.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateFlare, points.flare.x, points.flare.y, lerp(0.84, activeC ? 1.05 : 0.96, revealC), 4);
  setOpacity(candidateShelf, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateElbow, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateFlare, activeC ? 1 : revealC * 0.36 + 0.12);

  setOpacity(pressGuide, 0.12);
  setOpacity(pressTop, 0.08);
  setOpacity(pressBottom, 0.08);
  setOpacity(pressLeft, 0.08);
  setOpacity(pressRight, 0.08);
  setOpacity(pressSlotLeft, 0.08);
  setOpacity(pressSlotRight, 0.08);
  setOpacity(pressBridge, 0.06);
  setOpacity(pressureHalo, 0.08);

  setOpacity(glyphBack, 0.04);
  setOpacity(glyphFlare, 0.02);
  setOpacity(glyphNode, 0.02);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.46, 0, 1);
  const collapse = clamp((progress - 0.4) / 0.52, 0, 1);
  const pathPosition = pointOnPath(pressGuide, PRESS_GUIDE_LENGTH, easeInOut(travel));
  const position = mixPoint(pathPosition, points.center, easeInOut(collapse));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const verticalShift = lerp(0, 30, easeInOut(clamp(progress / 0.72, 0, 1)));
  const horizontalShift = lerp(0, 38, easeInOut(clamp(progress / 0.72, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(92, 128, progress),
    1,
    0.24 + pulseWave(progress, 2.1) * 0.1,
    lerp(1, 0.54, compression),
    lerp(1, 1.88, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.08, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const shelfPosition = mixPoint(points.shelf, { x: 724, y: 384 }, collapse);
  const elbowPosition = mixPoint(points.elbow, { x: 792, y: 514 }, collapse);
  const flarePosition = mixPoint(points.flare, { x: 872, y: 426 }, collapse);
  setGroupTransform(candidateShelf, shelfPosition.x, shelfPosition.y, lerp(0.96, 0.72, collapse), -6);
  setGroupTransform(candidateElbow, elbowPosition.x, elbowPosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateFlare, flarePosition.x, flarePosition.y, lerp(0.96, 0.72, collapse), 2);
  setOpacity(candidateShelf, lerp(0.28, 0.05, collapse));
  setOpacity(candidateElbow, lerp(0.28, 0.05, collapse));
  setOpacity(candidateFlare, lerp(1, 0.14, collapse));

  setOpacity(pressGuide, clamp((progress - 0.02) * 1.8, 0, 0.78));
  setOpacity(pressTop, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(pressBottom, clamp((progress - 0.06) * 1.5, 0, 0.96));
  setOpacity(pressLeft, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(pressRight, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(pressSlotLeft, clamp((progress - 0.12) * 1.5, 0, 0.58));
  setOpacity(pressSlotRight, clamp((progress - 0.12) * 1.5, 0, 0.58));
  setOpacity(pressBridge, clamp((progress - 0.18) * 1.5, 0, 0.46));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));

  setTranslate(pressTop, 0, verticalShift);
  setTranslate(pressBottom, 0, -verticalShift);
  setTranslate(pressLeft, horizontalShift, 0);
  setTranslate(pressRight, -horizontalShift, 0);
  setTranslate(pressSlotLeft, horizontalShift * 0.36, 0);
  setTranslate(pressSlotRight, -horizontalShift * 0.36, 0);

  setOpacity(glyphBack, clamp((progress - 0.68) * 1.6, 0, 0.18));
  setOpacity(glyphFlare, clamp((progress - 0.72) * 1.6, 0, 0.16));
  setOpacity(glyphNode, clamp((progress - 0.78) * 1.7, 0, 0.2));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.9, 0, 1));
  const position = pointOnPath(glyphTrace, GLYPH_TRACE_LENGTH, routeProgress);

  setDot(position, 16, 102, 1, 0.2 + pulseWave(progress, 2) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  setOpacity(pressGuide, lerp(0.78, 0.04, progress));
  setOpacity(pressTop, clamp(1 - progress * 1.2, 0, 1));
  setOpacity(pressBottom, clamp(0.96 - progress * 1.15, 0, 1));
  setOpacity(pressLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pressRight, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pressSlotLeft, clamp(0.58 - progress * 0.8, 0, 1));
  setOpacity(pressSlotRight, clamp(0.58 - progress * 0.8, 0, 1));
  setOpacity(pressBridge, clamp(0.46 - progress * 0.84, 0, 1));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.52, 0, 1));
  setTranslate(pressTop, 0, lerp(30, 14, progress));
  setTranslate(pressBottom, 0, lerp(-30, -12, progress));
  setTranslate(pressLeft, lerp(38, 18, progress), 0);
  setTranslate(pressRight, lerp(-38, -18, progress), 0);
  setTranslate(pressSlotLeft, lerp(14, 6, progress), 0);
  setTranslate(pressSlotRight, lerp(-14, -6, progress), 0);

  [candidateShelf, candidateElbow, candidateFlare, searchGuideA, searchGuideB, searchGuideC].forEach((element) => {
    setOpacity(element, 0);
  });

  setOpacity(glyphBack, clamp(progress * 1.5, 0, 0.94));
  setOpacity(glyphFlare, clamp((progress - 0.04) * 1.6, 0, 0.94));
  setOpacity(glyphNode, clamp((progress - 0.16) * 1.7, 0, 0.92));
  setPathWindow(glyphTrace, GLYPH_TRACE_LENGTH, GLYPH_TRACE_LENGTH * routeProgress, 0.9);
  setOpacity(glyphCorners, clamp((progress - 0.7) * 1.4, 0, 0.4));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.14));

  setTranslate(glyphBack, 0, lerp(0, -6, progress));
  setTranslate(glyphFlare, 0, lerp(0, -2, progress));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.2) * 0.05;
  const position = mixPoint(points.flareTip, points.center, settle);

  setDot(position, 16, 102, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [
    pressGuide,
    pressTop,
    pressBottom,
    pressLeft,
    pressRight,
    pressSlotLeft,
    pressSlotRight,
    pressBridge,
    pressureHalo,
  ].forEach((element) => {
    setOpacity(element, 0);
  });

  setOpacity(glyphBack, 0.92);
  setOpacity(glyphFlare, lerp(0.92, 0.76, settle));
  setOpacity(glyphNode, lerp(0.92, 1, settle));
  setPathWindow(glyphTrace, GLYPH_TRACE_LENGTH, GLYPH_TRACE_LENGTH, lerp(0.9, 0, settle));
  setOpacity(glyphCorners, lerp(0.4, 0.92, settle));
  setOpacity(resolutionHalo, lerp(0.14, 0.22, settle));

  setTranslate(glyphBack, 0, lerp(-6, -10, settle));
  setTranslate(glyphFlare, 0, lerp(-2, -8, settle));
  setTranslate(glyphCorners, 0, lerp(0, -4, settle));
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
