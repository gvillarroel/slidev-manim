const TOTAL_DURATION = 36_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_200 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 8_800 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const narrativeSpine = document.getElementById("narrative-spine");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateHook = document.getElementById("candidate-hook");
const candidateLoop = document.getElementById("candidate-loop");
const candidateStock = document.getElementById("candidate-stock");

const tensionHalo = document.getElementById("tension-halo");
const stockBase = document.getElementById("stock-base");
const ringBase = document.getElementById("ring-base");
const shankBase = document.getElementById("shank-base");
const flukeLeftBase = document.getElementById("fluke-left-base");
const flukeRightBase = document.getElementById("fluke-right-base");
const keelBase = document.getElementById("keel-base");

const stockActive = document.getElementById("stock-active");
const ringActive = document.getElementById("ring-active");
const shankActive = document.getElementById("shank-active");
const flukeLeftActive = document.getElementById("fluke-left-active");
const flukeRightActive = document.getElementById("fluke-right-active");

const resolutionHalo = document.getElementById("resolution-halo");
const resolutionEcho = document.getElementById("resolution-echo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const STOCK_LENGTH = stockActive.getTotalLength();
const RING_LENGTH = ringActive.getTotalLength();
const SHANK_LENGTH = shankActive.getTotalLength();
const FLUKE_LEFT_LENGTH = flukeLeftActive.getTotalLength();
const FLUKE_RIGHT_LENGTH = flukeRightActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 294, y: 456 },
  ingress: { x: 618, y: 430 },
  hook: { x: 726, y: 362 },
  loop: { x: 858, y: 334 },
  stock: { x: 972, y: 394 },
  approach: { x: 916, y: 402 },
  ring: { x: 860, y: 438 },
  gate: { x: 860, y: 478 },
  shankBottom: { x: 860, y: 648 },
  leftTip: { x: 718, y: 668 },
  rightTip: { x: 1002, y: 668 },
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

function setTransformAround(element, center, scaleX = 1, scaleY = 1, rotate = 0) {
  element.setAttribute(
    "transform",
    `translate(${center.x} ${center.y}) rotate(${rotate.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-center.x} ${-center.y})`,
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
    appearance: { x: 42, y: 8 },
    search: { x: 8, y: 10 },
    tension: { x: 0, y: 8 },
    transformation: { x: 0, y: 2 },
    resolution: { x: 0, y: 0 },
  };
  const offset = offsets[phaseId] ?? { x: 0, y: 0 };
  sceneRoot.setAttribute("transform", `translate(${offset.x} ${offset.y})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 134, y: 140, width: 1120, height: 640 },
    search: { x: 168, y: 134, width: 1120, height: 640 },
    tension: { x: 388, y: 116, width: 936, height: 708 },
    transformation: { x: 454, y: 106, width: 828, height: 736 },
    resolution: { x: 492, y: 96, width: 760, height: 752 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -16) translate(800 450) scale(1.03) translate(-800 -450)",
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

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateHook, points.hook.x, points.hook.y, 1, 0);
  setGroupTransform(candidateLoop, points.loop.x, points.loop.y, 1, 0);
  setGroupTransform(candidateStock, points.stock.x, points.stock.y, 1, 0);
  [candidateHook, candidateLoop, candidateStock].forEach((element) => setOpacity(element, 0));

  [stockBase, ringBase, shankBase, flukeLeftBase, flukeRightBase, keelBase, tensionHalo, resolutionHalo, resolutionEcho].forEach(
    (element) => setOpacity(element, 0),
  );
  [stockBase, ringBase, shankBase, flukeLeftBase, flukeRightBase, stockActive, ringActive, shankActive, flukeLeftActive, flukeRightActive].forEach(
    (element) => element.setAttribute("transform", ""),
  );
  [stockActive, ringActive, shankActive, flukeLeftActive, flukeRightActive].forEach((element) => {
    setPathWindow(element, 100, 0, 0);
  });
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);
  const preview = clamp((progress - 0.12) * 1.25, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.2) * 0.16,
  );

  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.4, 0, 0.34));

  setOpacity(stockBase, preview * 0.08);
  setOpacity(ringBase, preview * 0.08);
  setOpacity(shankBase, preview * 0.07);
  setOpacity(flukeLeftBase, preview * 0.06);
  setOpacity(flukeRightBase, preview * 0.06);
  setOpacity(keelBase, preview * 0.06);
  setTransformAround(stockBase, points.ring, 0.94, 1);
  setTransformAround(ringBase, points.ring, 0.96, 0.96);
  setTransformAround(flukeLeftBase, points.shankBottom, 0.84, 0.92);
  setTransformAround(flukeRightBase, points.shankBottom, 0.84, 0.92);

  const searchPreview = clamp((progress - 0.46) * 1.6, 0, 1);
  setOpacity(searchGuideA, searchPreview * 0.18);
  setOpacity(candidateHook, searchPreview * 0.12);
  setOpacity(candidateLoop, searchPreview * 0.1);
  setOpacity(candidateStock, searchPreview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.hook },
    { start: 0.28, end: 0.6, from: points.hook, to: points.loop },
    { start: 0.6, end: 0.88, from: points.loop, to: points.stock },
    { start: 0.88, end: 1, from: points.stock, to: points.approach },
  ]);

  setDot(position, 18, 86, 1, 0.22 + pulseWave(progress, 1.7) * 0.1);
  setOpacity(narrativeSpine, lerp(0.2, 0.08, progress));

  const revealA = clamp(progress / 0.24, 0, 1);
  const revealB = clamp((progress - 0.24) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.54) / 0.24, 0, 1);

  const activeA = progress < 0.34;
  const activeB = progress >= 0.34 && progress < 0.68;
  const activeC = progress >= 0.68;

  searchGuideA.setAttribute("stroke", activeA ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", activeB ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", activeC ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, activeA ? 0.42 : 0.12 + revealA * 0.06);
  setOpacity(searchGuideB, activeB ? 0.38 : 0.08 + revealB * 0.08);
  setOpacity(searchGuideC, activeC ? 0.34 : 0.06 + revealC * 0.08);

  setGroupTransform(candidateHook, points.hook.x, points.hook.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), lerp(-6, 0, revealA));
  setGroupTransform(candidateLoop, points.loop.x, points.loop.y, lerp(0.9, activeB ? 1.06 : 0.97, revealB), 0);
  setGroupTransform(candidateStock, points.stock.x, points.stock.y, lerp(0.9, activeC ? 1.06 : 0.97, revealC), lerp(0, 6, revealC));
  setOpacity(candidateHook, activeA ? 1 : revealA * 0.36 + 0.14);
  setOpacity(candidateLoop, activeB ? 1 : revealB * 0.36 + 0.14);
  setOpacity(candidateStock, activeC ? 1 : revealC * 0.36 + 0.14);

  setOpacity(stockBase, 0.1);
  setOpacity(ringBase, 0.1);
  setOpacity(shankBase, 0.08);
  setOpacity(flukeLeftBase, 0.08);
  setOpacity(flukeRightBase, 0.08);
  setOpacity(keelBase, 0.05);
  setTransformAround(stockBase, points.ring, 0.95, 1);
  setTransformAround(ringBase, points.ring, 0.97, 0.97);
  setTransformAround(flukeLeftBase, points.shankBottom, 0.86, 0.94);
  setTransformAround(flukeRightBase, points.shankBottom, 0.86, 0.94);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.44, 0, 1);
  const position = mixPoint(points.approach, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const fadeCandidates = clamp(progress / 0.7, 0, 1);
  const squeeze = easeInOut(clamp(progress / 0.72, 0, 1));
  const stockScale = lerp(0.95, 0.84, squeeze);
  const ringScale = lerp(0.97, 0.9, squeeze);
  const flukeScale = lerp(0.86, 0.68, squeeze);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 114, progress),
    1,
    0.24 + pulseWave(progress, 2.1) * 0.1,
    lerp(1, 0.7, compression),
    lerp(1, 1.54, compression),
  );

  setOpacity(narrativeSpine, lerp(0.14, 0.02, progress));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.26 : 0.12, 0, progress));
  });

  setGroupTransform(candidateHook, lerp(points.hook.x, 760, fadeCandidates), lerp(points.hook.y, 402, fadeCandidates), lerp(0.97, 0.72, fadeCandidates), -6);
  setGroupTransform(candidateLoop, lerp(points.loop.x, 860, fadeCandidates), lerp(points.loop.y, 358, fadeCandidates), lerp(0.97, 0.78, fadeCandidates), 0);
  setGroupTransform(candidateStock, lerp(points.stock.x, 954, fadeCandidates), lerp(points.stock.y, 420, fadeCandidates), lerp(0.97, 0.72, fadeCandidates), 6);
  setOpacity(candidateHook, lerp(0.32, 0.04, fadeCandidates));
  setOpacity(candidateLoop, lerp(0.4, 0.06, fadeCandidates));
  setOpacity(candidateStock, lerp(1, 0.1, fadeCandidates));

  setOpacity(tensionHalo, clamp((progress - 0.02) * 1.4, 0, 0.9));
  setOpacity(stockBase, clamp((progress - 0.04) * 1.6, 0, 0.74));
  setOpacity(ringBase, clamp((progress - 0.02) * 1.5, 0, 0.74));
  setOpacity(shankBase, clamp((progress - 0.06) * 1.5, 0, 0.72));
  setOpacity(flukeLeftBase, clamp((progress - 0.12) * 1.4, 0, 0.58));
  setOpacity(flukeRightBase, clamp((progress - 0.12) * 1.4, 0, 0.58));
  setOpacity(keelBase, clamp((progress - 0.16) * 1.4, 0, 0.2));
  setTransformAround(stockBase, points.ring, stockScale, 1);
  setTransformAround(ringBase, points.ring, ringScale, ringScale);
  setTransformAround(flukeLeftBase, points.shankBottom, flukeScale, 0.92);
  setTransformAround(flukeRightBase, points.shankBottom, flukeScale, 0.92);
}

function renderTransformation(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.14, from: points.gate, to: points.ring },
    { start: 0.14, end: 0.42, from: points.ring, to: points.shankBottom },
    { start: 0.42, end: 0.62, from: points.shankBottom, to: points.leftTip },
    { start: 0.62, end: 0.78, from: points.leftTip, to: points.shankBottom },
    { start: 0.78, end: 0.92, from: points.shankBottom, to: points.rightTip },
    { start: 0.92, end: 1, from: points.rightTip, to: points.ring },
  ]);
  const ringReveal = clamp(progress / 0.28, 0, 1);
  const stockReveal = clamp((progress - 0.02) / 0.24, 0, 1);
  const shankReveal = clamp((progress - 0.14) / 0.24, 0, 1);
  const leftReveal = clamp((progress - 0.38) / 0.24, 0, 1);
  const rightReveal = clamp((progress - 0.58) / 0.24, 0, 1);
  const stockScale = lerp(0.84, 1, easeOut(clamp(progress / 0.62, 0, 1)));
  const ringScale = lerp(0.9, 1, easeOut(clamp(progress / 0.5, 0, 1)));
  const flukeScale = lerp(0.68, 1, easeOut(clamp((progress - 0.16) / 0.68, 0, 1)));

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(tensionHalo, lerp(0.9, 0.16, progress));
  setOpacity(stockBase, lerp(0.74, 0.4, progress));
  setOpacity(ringBase, lerp(0.74, 0.44, progress));
  setOpacity(shankBase, lerp(0.72, 0.42, progress));
  setOpacity(flukeLeftBase, lerp(0.58, 0.36, progress));
  setOpacity(flukeRightBase, lerp(0.58, 0.36, progress));
  setOpacity(keelBase, lerp(0.2, 0.08, progress));
  setTransformAround(stockBase, points.ring, stockScale, 1);
  setTransformAround(ringBase, points.ring, ringScale, ringScale);
  setTransformAround(flukeLeftBase, points.shankBottom, flukeScale, 0.96);
  setTransformAround(flukeRightBase, points.shankBottom, flukeScale, 0.96);

  setPathWindow(stockActive, STOCK_LENGTH, STOCK_LENGTH * stockReveal, stockReveal);
  setPathWindow(ringActive, RING_LENGTH, RING_LENGTH * ringReveal, ringReveal);
  setPathWindow(shankActive, SHANK_LENGTH, SHANK_LENGTH * shankReveal, shankReveal);
  setPathWindow(flukeLeftActive, FLUKE_LEFT_LENGTH, FLUKE_LEFT_LENGTH * leftReveal, leftReveal);
  setPathWindow(flukeRightActive, FLUKE_RIGHT_LENGTH, FLUKE_RIGHT_LENGTH * rightReveal, rightReveal);
  setTransformAround(stockActive, points.ring, stockScale, 1);
  setTransformAround(ringActive, points.ring, ringScale, ringScale);
  setTransformAround(flukeLeftActive, points.shankBottom, flukeScale, 0.96);
  setTransformAround(flukeRightActive, points.shankBottom, flukeScale, 0.96);

  [searchGuideA, searchGuideB, searchGuideC, candidateHook, candidateLoop, candidateStock].forEach((element) => setOpacity(element, 0));

  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
  setOpacity(resolutionEcho, clamp((progress - 0.78) * 1.6, 0, 0.12));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.2) * 0.05;

  setDot(points.ring, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(tensionHalo, 0);
  [searchGuideA, searchGuideB, searchGuideC, candidateHook, candidateLoop, candidateStock].forEach((element) => setOpacity(element, 0));

  setOpacity(stockBase, lerp(0.4, 0.82, settle));
  setOpacity(ringBase, lerp(0.44, 0.86, settle));
  setOpacity(shankBase, lerp(0.42, 0.82, settle));
  setOpacity(flukeLeftBase, lerp(0.36, 0.82, settle));
  setOpacity(flukeRightBase, lerp(0.36, 0.82, settle));
  setOpacity(keelBase, lerp(0.08, 0.18, settle));
  setTransformAround(stockBase, points.ring, lerp(1, 1.02, settle), 1);
  setTransformAround(ringBase, points.ring, 1, 1);
  setTransformAround(flukeLeftBase, points.shankBottom, 1, 1);
  setTransformAround(flukeRightBase, points.shankBottom, 1, 1);

  setPathWindow(stockActive, STOCK_LENGTH, STOCK_LENGTH, lerp(1, 0.26, settle));
  setPathWindow(ringActive, RING_LENGTH, RING_LENGTH, lerp(1, 0.34, settle));
  setPathWindow(shankActive, SHANK_LENGTH, SHANK_LENGTH, lerp(1, 0.26, settle));
  setPathWindow(flukeLeftActive, FLUKE_LEFT_LENGTH, FLUKE_LEFT_LENGTH, lerp(1, 0.24, settle));
  setPathWindow(flukeRightActive, FLUKE_RIGHT_LENGTH, FLUKE_RIGHT_LENGTH, lerp(1, 0.24, settle));
  setTransformAround(stockActive, points.ring, lerp(1, 1.02, settle), 1);
  setTransformAround(ringActive, points.ring, 1, 1);
  setTransformAround(flukeLeftActive, points.shankBottom, 1, 1);
  setTransformAround(flukeRightActive, points.shankBottom, 1, 1);

  setOpacity(resolutionHalo, lerp(0.16, 0.28, settle));
  setOpacity(resolutionEcho, lerp(0.12, 0.7, settle));
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
