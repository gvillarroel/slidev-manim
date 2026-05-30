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
const candidateJaw = document.getElementById("candidate-jaw");
const candidateChannel = document.getElementById("candidate-channel");
const candidateLadder = document.getElementById("candidate-ladder");
const throatGuide = document.getElementById("throat-guide");
const sliderRoute = document.getElementById("slider-route");
const rackLeft = document.getElementById("rack-left");
const rackRight = document.getElementById("rack-right");
const topStop = document.getElementById("top-stop");
const splitLeft = document.getElementById("split-left");
const splitRight = document.getElementById("split-right");
const pressureHalo = document.getElementById("pressure-halo");
const resolutionAxis = document.getElementById("resolution-axis");
const resolutionHalo = document.getElementById("resolution-halo");
const closureTrace = document.getElementById("closure-trace");
const sliderShell = document.getElementById("slider-shell");
const sliderPull = document.getElementById("slider-pull");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const THROAT_GUIDE_LENGTH = throatGuide.getTotalLength();
const SLIDER_ROUTE_LENGTH = sliderRoute.getTotalLength();
const CLOSURE_TRACE_LENGTH = closureTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 302, y: 450 },
  ingress: { x: 560, y: 450 },
  jaw: { x: 684, y: 390 },
  channel: { x: 846, y: 510 },
  ladder: { x: 1000, y: 390 },
  approach: { x: 944, y: 450 },
  center: { x: 820, y: 452 },
  lift: { x: 820, y: 364 },
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

function setShell(point, scale = 1) {
  sliderShell.setAttribute(
    "transform",
    `translate(${point.x.toFixed(2)} ${point.y.toFixed(2)}) scale(${scale.toFixed(3)})`,
  );
}

function setRackSpread(spread, yShift = 0) {
  setTranslate(rackLeft, -spread, yShift);
  setTranslate(rackRight, spread, yShift);
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
    appearance: 14,
    search: 28,
    tension: 18,
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
    appearance: { x: 134, y: 156, width: 1060, height: 628 },
    search: { x: 176, y: 136, width: 1084, height: 646 },
    tension: { x: 374, y: 144, width: 900, height: 636 },
    transformation: { x: 634, y: 104, width: 372, height: 758 },
    resolution: { x: 646, y: 90, width: 348, height: 780 },
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

  setGroupTransform(candidateJaw, points.jaw.x, points.jaw.y, 1, -2);
  setGroupTransform(candidateChannel, points.channel.x, points.channel.y, 1, 0);
  setGroupTransform(candidateLadder, points.ladder.x, points.ladder.y, 1, 2);
  [candidateJaw, candidateChannel, candidateLadder].forEach((element) => setOpacity(element, 0));

  setOpacity(throatGuide, 0);
  setRackSpread(54, 0);
  setOpacity(rackLeft, 0);
  setOpacity(rackRight, 0);
  setOpacity(topStop, 0);
  setOpacity(splitLeft, 0);
  setOpacity(splitRight, 0);
  setOpacity(pressureHalo, 0);
  setOpacity(resolutionAxis, 0);
  setOpacity(resolutionHalo, 0);
  setPathWindow(closureTrace, CLOSURE_TRACE_LENGTH, 0, 0);
  setShell(points.center, 0.82);
  setOpacity(sliderShell, 0);
  setOpacity(sliderPull, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.84);
  const preview = clamp((progress - 0.44) * 1.8, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(16, 78, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.1) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.5, 0, 0.34));

  setOpacity(searchGuideA, preview * 0.22);
  setOpacity(candidateJaw, preview * 0.18);
  setOpacity(candidateChannel, preview * 0.12);
  setOpacity(candidateLadder, preview * 0.08);
  setOpacity(throatGuide, preview * 0.06);

  setRackSpread(56, 0);
  setOpacity(rackLeft, preview * 0.08);
  setOpacity(rackRight, preview * 0.08);
  setOpacity(topStop, preview * 0.06);
  setOpacity(splitLeft, preview * 0.04);
  setOpacity(splitRight, preview * 0.04);
  setOpacity(sliderShell, preview * 0.08);
  setOpacity(sliderPull, 0);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.jaw },
    { start: 0.24, end: 0.56, from: points.jaw, to: points.channel },
    { start: 0.56, end: 0.84, from: points.channel, to: points.ladder },
    { start: 0.84, end: 1, from: points.ladder, to: points.approach },
  ]);

  const revealA = clamp(progress / 0.2, 0, 1);
  const revealB = clamp((progress - 0.2) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.52) / 0.24, 0, 1);
  const activeA = progress < 0.26 ? 1 : 0;
  const activeB = progress >= 0.26 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setDot(position, 18, 86, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.14, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.24, 0.12, progress));

  searchGuideA.setAttribute("stroke", activeA ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", activeB ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", activeC ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.2 + revealA * 0.22);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.24);

  setGroupTransform(candidateJaw, points.jaw.x, points.jaw.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), -4);
  setGroupTransform(candidateChannel, points.channel.x, points.channel.y, lerp(0.9, activeB ? 1.05 : 0.97, revealB), 0);
  setGroupTransform(candidateLadder, points.ladder.x, points.ladder.y, lerp(0.88, activeC ? 1.05 : 0.97, revealC), 3);
  setOpacity(candidateJaw, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateChannel, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateLadder, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(throatGuide, 0.12);
  setRackSpread(52, 0);
  setOpacity(rackLeft, 0.08);
  setOpacity(rackRight, 0.08);
  setOpacity(topStop, 0.06);
  setOpacity(splitLeft, 0.04);
  setOpacity(splitRight, 0.04);
  setOpacity(sliderShell, 0.08);
  setOpacity(sliderPull, 0);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.46, 0, 1);
  const collapse = clamp((progress - 0.34) / 0.46, 0, 1);
  const pathPosition = pointOnPath(throatGuide, THROAT_GUIDE_LENGTH, easeInOut(travel));
  const position = mixPoint(pathPosition, points.center, easeInOut(collapse));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const spread = lerp(56, 18, easeInOut(clamp(progress / 0.76, 0, 1)));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(86, 110, progress),
    1,
    0.22 + pulseWave(progress, 2.1) * 0.1,
    lerp(1, 0.66, compression),
    lerp(1, 1.56, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.18 : 0.14, 0, progress));
  });

  setGroupTransform(candidateJaw, lerp(points.jaw.x, 736, progress), lerp(points.jaw.y, 410, progress), lerp(0.98, 0.76, progress), -10);
  setGroupTransform(candidateChannel, lerp(points.channel.x, 836, progress), lerp(points.channel.y, 486, progress), lerp(0.98, 0.74, progress), 0);
  setGroupTransform(candidateLadder, lerp(points.ladder.x, 944, progress), lerp(points.ladder.y, 414, progress), lerp(1, 0.74, progress), 8);
  setOpacity(candidateJaw, lerp(0.28, 0.04, progress));
  setOpacity(candidateChannel, lerp(0.22, 0.04, progress));
  setOpacity(candidateLadder, lerp(0.72, 0.08, progress));

  setOpacity(throatGuide, clamp((progress - 0.04) * 1.8, 0, 0.78));
  setRackSpread(spread, 0);
  setOpacity(rackLeft, clamp((progress - 0.06) * 1.7, 0, 0.96));
  setOpacity(rackRight, clamp((progress - 0.06) * 1.7, 0, 0.96));
  setOpacity(topStop, clamp((progress - 0.08) * 1.6, 0, 0.16));
  setOpacity(splitLeft, clamp((progress - 0.14) * 1.6, 0, 0.12));
  setOpacity(splitRight, clamp((progress - 0.14) * 1.6, 0, 0.12));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));

  setShell(position, lerp(0.84, 1.04, progress));
  setOpacity(sliderShell, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(sliderPull, 0);
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.82, 0, 1));
  const position = pointOnPath(sliderRoute, SLIDER_ROUTE_LENGTH, routeProgress);

  setDot(position, 16, 98, 1, 0.2 + pulseWave(progress, 2) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [searchGuideA, searchGuideB, searchGuideC, candidateJaw, candidateChannel, candidateLadder].forEach((element) =>
    setOpacity(element, 0),
  );

  setOpacity(throatGuide, lerp(0.78, 0.08, progress));
  setRackSpread(lerp(18, 0, routeProgress), 0);
  setOpacity(rackLeft, 0.94);
  setOpacity(rackRight, 0.94);
  setOpacity(topStop, clamp((progress - 0.14) * 1.6, 0, 0.9));
  setOpacity(splitLeft, clamp((progress - 0.24) * 1.6, 0, 0.62));
  setOpacity(splitRight, clamp((progress - 0.24) * 1.6, 0, 0.62));
  setOpacity(pressureHalo, clamp(0.42 - progress * 0.52, 0, 1));
  setOpacity(resolutionAxis, clamp((progress - 0.58) * 1.6, 0, 0.22));
  setOpacity(resolutionHalo, clamp((progress - 0.66) * 1.5, 0, 0.14));

  setShell(position, lerp(1.04, 0.98, routeProgress));
  setOpacity(sliderShell, 1);
  setOpacity(sliderPull, clamp((progress - 0.42) * 1.8, 0, 0.84));
  setPathWindow(closureTrace, CLOSURE_TRACE_LENGTH, CLOSURE_TRACE_LENGTH * clamp(progress * 1.08, 0, 1), 0.86);
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;
  const position = mixPoint(points.lift, points.center, settle);

  setDot(position, 16, 98, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);
  setOpacity(throatGuide, 0);
  setOpacity(pressureHalo, 0);

  setRackSpread(0, 0);
  setOpacity(rackLeft, 0.9);
  setOpacity(rackRight, 0.9);
  setOpacity(topStop, 0.84);
  setOpacity(splitLeft, 0.52);
  setOpacity(splitRight, 0.52);
  setOpacity(resolutionAxis, lerp(0.22, 0.72, settle));
  setOpacity(resolutionHalo, lerp(0.14, 0.26, settle));

  setShell(position, lerp(0.98, 0.9, settle));
  setOpacity(sliderShell, 0.94);
  setOpacity(sliderPull, 0.84);
  setPathWindow(closureTrace, CLOSURE_TRACE_LENGTH, CLOSURE_TRACE_LENGTH, lerp(0.86, 0, settle));
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
