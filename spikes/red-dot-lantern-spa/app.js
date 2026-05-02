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
const candidateCanopy = document.getElementById("candidate-canopy");
const candidateKite = document.getElementById("candidate-kite");
const candidateSleeve = document.getElementById("candidate-sleeve");

const tensionHalo = document.getElementById("tension-halo");
const throatGuide = document.getElementById("throat-guide");
const outerFrame = document.getElementById("outer-frame");
const lowerCradle = document.getElementById("lower-cradle");
const leftShutter = document.getElementById("left-shutter");
const rightShutter = document.getElementById("right-shutter");
const topStem = document.getElementById("top-stem");
const topBar = document.getElementById("top-bar");
const memoryLeft = document.getElementById("memory-left");
const memoryRight = document.getElementById("memory-right");
const shellLeft = document.getElementById("shell-left");
const shellRight = document.getElementById("shell-right");
const topBand = document.getElementById("top-band");
const bottomBand = document.getElementById("bottom-band");
const activeTopBand = document.getElementById("active-top-band");
const activeBottomBand = document.getElementById("active-bottom-band");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ACTIVE_TOP_LENGTH = activeTopBand.getTotalLength();
const ACTIVE_BOTTOM_LENGTH = activeBottomBand.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 302, y: 454 },
  entry: { x: 556, y: 454 },
  canopy: { x: 676, y: 392 },
  kite: { x: 846, y: 338 },
  sleeve: { x: 1000, y: 410 },
  mouth: { x: 932, y: 454 },
  pocket: { x: 846, y: 454 },
  apex: { x: 846, y: 336 },
  center: { x: 846, y: 454 },
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

function setEllipseRadius(element, rx, ry) {
  element.setAttribute("rx", rx.toFixed(2));
  element.setAttribute("ry", ry.toFixed(2));
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
    appearance: 10,
    search: 22,
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
    appearance: { x: 120, y: 142, width: 1120, height: 644 },
    search: { x: 170, y: 132, width: 1120, height: 658 },
    tension: { x: 562, y: 100, width: 568, height: 760 },
    transformation: { x: 584, y: 76, width: 528, height: 794 },
    resolution: { x: 610, y: 74, width: 472, height: 796 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -12) translate(800 450) scale(1.055) translate(-800 -450)",
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

  setGroupTransform(candidateCanopy, points.canopy.x, points.canopy.y, 1, -3);
  setGroupTransform(candidateKite, points.kite.x, points.kite.y, 1, 0);
  setGroupTransform(candidateSleeve, points.sleeve.x, points.sleeve.y, 1, 2);
  [candidateCanopy, candidateKite, candidateSleeve].forEach((element) => setOpacity(element, 0));

  setEllipseRadius(tensionHalo, 152, 124);
  setOpacity(tensionHalo, 0);
  setOpacity(throatGuide, 0);
  setGroupTransform(outerFrame, points.pocket.x, points.pocket.y, 1, 0);
  setGroupTransform(lowerCradle, points.pocket.x, points.pocket.y + 108, 1, 0);
  setGroupTransform(leftShutter, points.pocket.x - 118, points.pocket.y, 1, 0);
  setGroupTransform(rightShutter, points.pocket.x + 118, points.pocket.y, 1, 0);
  setOpacity(outerFrame, 0);
  setOpacity(lowerCradle, 0);
  setOpacity(leftShutter, 0);
  setOpacity(rightShutter, 0);
  setOpacity(topStem, 0);
  setOpacity(topBar, 0);
  setOpacity(memoryLeft, 0);
  setOpacity(memoryRight, 0);
  [shellLeft, shellRight, topBand, bottomBand].forEach((element) => setOpacity(element, 0));
  setPathWindow(activeTopBand, ACTIVE_TOP_LENGTH, 0, 0);
  setPathWindow(activeBottomBand, ACTIVE_BOTTOM_LENGTH, 0, 0);
  setEllipseRadius(resolutionHalo, 128, 164);
  setEllipseRadius(resolutionRing, 86, 118);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRing, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.entry, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(16, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.1) * 1.5, 0, 0.34));

  const preview = clamp((progress - 0.42) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.14);
  setOpacity(candidateCanopy, preview * 0.12);
  setOpacity(candidateKite, preview * 0.08);
  setOpacity(candidateSleeve, preview * 0.06);
  setOpacity(throatGuide, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.entry, to: points.canopy },
    { start: 0.24, end: 0.54, from: points.canopy, to: points.kite },
    { start: 0.54, end: 0.82, from: points.kite, to: points.sleeve },
    { start: 0.82, end: 1, from: points.sleeve, to: points.mouth },
  ]);

  setDot(position, 18, 84, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.14, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.24, 0.12, progress));

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

  setGroupTransform(candidateCanopy, points.canopy.x, points.canopy.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), -4);
  setGroupTransform(candidateKite, points.kite.x, points.kite.y, lerp(0.9, activeB ? 1.05 : 0.97, revealB), 0);
  setGroupTransform(candidateSleeve, points.sleeve.x, points.sleeve.y, lerp(0.88, activeC ? 1.05 : 0.97, revealC), 3);
  setOpacity(candidateCanopy, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateKite, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateSleeve, activeC ? 1 : revealC * 0.34 + 0.12);
  setOpacity(throatGuide, 0.12);
}

function renderTension(progress) {
  const ingress = easeInOut(clamp(progress / 0.28, 0, 1));
  const squeeze = clamp((progress - 0.22) / 0.34, 0, 1);
  const position = mixPoint(points.mouth, points.pocket, ingress);
  const shutterOffset = lerp(118, 48, easeInOut(squeeze));
  const compression = clamp((progress - 0.34) / 0.32, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(84, 110, progress),
    1,
    0.24 + pulseWave(progress, 2.0) * 0.1,
    lerp(1, 0.78, compression),
    lerp(1, 1.18, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.18 : 0.12, 0, progress));
  });

  setGroupTransform(candidateCanopy, lerp(points.canopy.x, 730, progress), lerp(points.canopy.y, 430, progress), lerp(0.98, 0.78, progress), -10);
  setGroupTransform(candidateKite, lerp(points.kite.x, 846, progress), lerp(points.kite.y, 388, progress), lerp(0.98, 0.7, progress), 0);
  setGroupTransform(candidateSleeve, lerp(points.sleeve.x, 962, progress), lerp(points.sleeve.y, 436, progress), lerp(1, 0.78, progress), 8);
  setOpacity(candidateCanopy, lerp(0.28, 0.04, progress));
  setOpacity(candidateKite, lerp(0.22, 0.04, progress));
  setOpacity(candidateSleeve, lerp(0.78, 0.06, progress));

  setEllipseRadius(tensionHalo, lerp(152, 168, progress), lerp(124, 134, progress));
  setOpacity(tensionHalo, clamp((progress - 0.02) * 1.5, 0, 0.22));
  setOpacity(throatGuide, lerp(0.12, 0.28, progress));
  setGroupTransform(outerFrame, points.pocket.x, points.pocket.y, lerp(0.94, 1, progress), 0);
  setOpacity(outerFrame, clamp((progress - 0.04) * 1.8, 0, 1));
  setGroupTransform(lowerCradle, points.pocket.x, lerp(points.pocket.y + 118, points.pocket.y + 108, progress), 1, 0);
  setOpacity(lowerCradle, clamp((progress - 0.1) * 1.6, 0, 0.92));
  setGroupTransform(leftShutter, points.pocket.x - shutterOffset, points.pocket.y, 1, 0);
  setGroupTransform(rightShutter, points.pocket.x + shutterOffset, points.pocket.y, 1, 0);
  setOpacity(leftShutter, clamp((progress - 0.16) * 1.8, 0, 1));
  setOpacity(rightShutter, clamp((progress - 0.16) * 1.8, 0, 1));
}

function renderTransformation(progress) {
  const route = segmentedPoint(progress, [
    { start: 0, end: 0.34, from: points.pocket, to: points.apex },
    { start: 0.34, end: 1, from: points.apex, to: points.center },
  ]);
  const arcLift = Math.sin(clamp((progress - 0.34) / 0.66, 0, 1) * Math.PI) * 18;
  const position =
    progress <= 0.34
      ? route
      : {
          x: route.x,
          y: route.y - arcLift,
        };
  const shellReveal = easeInOut(clamp((progress - 0.08) / 0.72, 0, 1));
  const activeTopReveal = easeInOut(clamp((progress - 0.18) / 0.34, 0, 1));
  const activeBottomReveal = easeInOut(clamp((progress - 0.46) / 0.32, 0, 1));

  setDot(
    position,
    16,
    100,
    1,
    0.22 + pulseWave(progress, 1.9) * 0.08,
    lerp(0.78, 1, shellReveal),
    lerp(1.18, 1, shellReveal),
  );
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [searchGuideA, searchGuideB, searchGuideC, candidateCanopy, candidateKite, candidateSleeve].forEach((element) => setOpacity(element, 0));
  setOpacity(throatGuide, clamp(0.28 - progress * 0.34, 0, 1));
  setEllipseRadius(tensionHalo, lerp(168, 138, progress), lerp(134, 152, progress));
  setOpacity(tensionHalo, lerp(0.22, 0.12, progress));
  setGroupTransform(outerFrame, points.pocket.x, points.pocket.y, lerp(1, 1.04, progress), 0);
  setOpacity(outerFrame, lerp(1, 0.08, progress));
  setGroupTransform(lowerCradle, points.pocket.x, lerp(points.pocket.y + 108, points.pocket.y + 118, progress), 1, 0);
  setOpacity(lowerCradle, lerp(0.92, 0.06, progress));
  setGroupTransform(leftShutter, points.pocket.x - lerp(48, 122, progress), points.pocket.y, 1, 0);
  setGroupTransform(rightShutter, points.pocket.x + lerp(48, 122, progress), points.pocket.y, 1, 0);
  setOpacity(leftShutter, lerp(1, 0, clamp((progress - 0.18) * 1.45, 0, 1)));
  setOpacity(rightShutter, lerp(1, 0, clamp((progress - 0.18) * 1.45, 0, 1)));

  setOpacity(topStem, clamp((progress - 0.1) * 1.7, 0, 0.82));
  setOpacity(topBar, clamp((progress - 0.16) * 1.8, 0, 0.74));
  setOpacity(memoryLeft, clamp((progress - 0.2) * 1.45, 0, 0.26));
  setOpacity(memoryRight, clamp((progress - 0.2) * 1.45, 0, 0.26));
  [shellLeft, shellRight, topBand, bottomBand].forEach((element) => setOpacity(element, clamp(shellReveal * 1.1, 0, 0.92)));
  setPathWindow(activeTopBand, ACTIVE_TOP_LENGTH, ACTIVE_TOP_LENGTH * activeTopReveal, activeTopReveal * 0.94);
  setPathWindow(activeBottomBand, ACTIVE_BOTTOM_LENGTH, ACTIVE_BOTTOM_LENGTH * activeBottomReveal, activeBottomReveal * 0.94);
  setOpacity(resolutionHalo, clamp((progress - 0.42) * 1.45, 0, 0.24));
  setOpacity(resolutionRing, clamp((progress - 0.62) * 1.45, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(throatGuide, 0);
  setOpacity(tensionHalo, 0);
  setOpacity(outerFrame, 0);
  setOpacity(lowerCradle, 0);
  setOpacity(leftShutter, 0);
  setOpacity(rightShutter, 0);

  setOpacity(topStem, lerp(0.82, 0.72, settle));
  setOpacity(topBar, lerp(0.74, 0.64, settle));
  setOpacity(memoryLeft, lerp(0.18, 0.1, settle));
  setOpacity(memoryRight, lerp(0.18, 0.1, settle));
  setOpacity(shellLeft, lerp(0.92, 0.84, settle));
  setOpacity(shellRight, lerp(0.92, 0.84, settle));
  setOpacity(topBand, lerp(0.92, 0.84, settle));
  setOpacity(bottomBand, lerp(0.92, 0.84, settle));
  setPathWindow(activeTopBand, ACTIVE_TOP_LENGTH, ACTIVE_TOP_LENGTH, lerp(0.12, 0.03, settle));
  setPathWindow(activeBottomBand, ACTIVE_BOTTOM_LENGTH, ACTIVE_BOTTOM_LENGTH, lerp(0.18, 0.04, settle));
  setEllipseRadius(resolutionHalo, 128, 164);
  setEllipseRadius(resolutionRing, lerp(84, 86, settle), lerp(116, 118, settle));
  setOpacity(resolutionHalo, lerp(0.24, 0.32, settle));
  setOpacity(resolutionRing, lerp(0.22, 0.86, settle));
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
