const TOTAL_DURATION = 35_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const approachSpine = document.getElementById("approach-spine");
const pendingShell = document.getElementById("pending-shell");
const shellBase = document.getElementById("shell-base");
const shellInner = document.getElementById("shell-inner");

const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");

const tensionHalo = document.getElementById("tension-halo");
const impactBumper = document.getElementById("impact-bumper");
const impactKeeper = document.getElementById("impact-keeper");
const topGuide = document.getElementById("top-guide");
const bottomGuide = document.getElementById("bottom-guide");

const routeBase = document.getElementById("deflect-route-base");
const routeActive = document.getElementById("deflect-route-active");
const resolutionRule = document.getElementById("resolution-rule");
const resolutionFrame = document.getElementById("resolution-frame");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ROUTE_LENGTH = routeActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  lineGray: "#cfcfcf",
  dark: "#4f4f4f",
};

const points = {
  start: { x: 296, y: 450 },
  ingress: { x: 612, y: 450 },
  candidateA: { x: 746, y: 338 },
  candidateB: { x: 770, y: 562 },
  candidateC: { x: 846, y: 448 },
  impact: { x: 836, y: 450 },
  resolution: { x: 974, y: 468 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
  looping: !CAPTURE_MODE,
};

const PORTRAIT_VIEWBOXES = {
  appearance: "150 146 760 640",
  search: "260 138 860 660",
  tension: "650 156 460 642",
  transformation: "740 138 470 670",
  resolution: "744 138 520 690",
};

const PORTRAIT_STAGE_TRANSFORMS = {
  appearance: { x: 520, y: 450, scale: 1.04 },
  search: { x: 690, y: 450, scale: 1.08 },
  tension: { x: 878, y: 450, scale: 1.14 },
  transformation: { x: 980, y: 456, scale: 1.15 },
  resolution: { x: 972, y: 468, scale: 1.08 },
};

const SCENE_OFFSETS = {
  appearance: { x: 84, y: 0 },
  search: { x: 42, y: 0 },
  tension: { x: 0, y: 0 },
  transformation: { x: -92, y: 0 },
  resolution: { x: -112, y: 0 },
};

const PORTRAIT_SCENE_OFFSETS = {
  appearance: { x: 84, y: 0 },
  search: { x: 42, y: 0 },
  tension: { x: 0, y: 0 },
  transformation: { x: -56, y: 0 },
  resolution: { x: -18, y: 0 },
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
  element.style.strokeDasharray = `${clamped.toFixed(2)} ${(totalLength + 220).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function pointOnRoute(progress) {
  const length = clamp(progress, 0, 1) * ROUTE_LENGTH;
  const point = routeActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
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

function applyFraming(phaseId) {
  const offset = SCENE_OFFSETS[phaseId] ?? SCENE_OFFSETS.appearance;
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.82) {
    const portraitOffset = PORTRAIT_SCENE_OFFSETS[phaseId] ?? PORTRAIT_SCENE_OFFSETS.appearance;
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
    svg.setAttribute("viewBox", PORTRAIT_VIEWBOXES[phaseId] ?? PORTRAIT_VIEWBOXES.appearance);
    const transform = PORTRAIT_STAGE_TRANSFORMS[phaseId] ?? PORTRAIT_STAGE_TRANSFORMS.appearance;
    sceneRoot.setAttribute(
      "transform",
      `translate(${portraitOffset.x} ${portraitOffset.y}) translate(${transform.x} ${transform.y}) scale(${transform.scale}) translate(${-transform.x} ${-transform.y})`,
    );
    svg.dataset.layout = "portrait";
    return;
  }

  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.setAttribute("viewBox", FULL_VIEWBOX);
  sceneRoot.setAttribute("transform", `translate(${offset.x} ${offset.y})`);
  svg.dataset.layout = "landscape";
}

function resetScene() {
  setDot(points.start, 18, 74, 0, 0);
  setOpacity(approachSpine, 0);
  setOpacity(pendingShell, 0);
  setOpacity(shellBase, 0);
  setOpacity(shellInner, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, 1, 0);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, 1, 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, 1, 0);
  [candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  setOpacity(tensionHalo, 0);
  setOpacity(impactBumper, 0);
  setOpacity(impactKeeper, 0);
  topGuide.setAttribute("x1", "782");
  topGuide.setAttribute("x2", "1006");
  bottomGuide.setAttribute("x1", "782");
  bottomGuide.setAttribute("x2", "1006");
  setOpacity(topGuide, 0);
  setOpacity(bottomGuide, 0);

  setOpacity(routeBase, 0);
  setPathWindow(routeActive, ROUTE_LENGTH, 0, 0);
  setOpacity(resolutionRule, 0);
  setOpacity(resolutionFrame, 0);
  setOpacity(resolutionHalo, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);
  const preview = clamp((progress - 0.34) * 1.6, 0, 1);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(20, 86, eased),
    clamp(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.1) * 0.18,
  );

  setOpacity(approachSpine, clamp((progress - 0.12) * 1.4, 0, 0.34));
  setOpacity(pendingShell, 0.08 + preview * 0.12);
  setOpacity(shellBase, 0.1 + preview * 0.12);
  setOpacity(shellInner, preview * 0.08);

  setOpacity(searchGuideA, preview * 0.12);
  setOpacity(candidateA, preview * 0.08);
  setOpacity(candidateB, preview * 0.06);
  setOpacity(candidateC, preview * 0.08);
  setOpacity(impactBumper, 0.04 + preview * 0.08);
  setOpacity(impactKeeper, 0.04 + preview * 0.07);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.ingress, to: points.candidateA },
    { start: 0.24, end: 0.56, from: points.candidateA, to: points.candidateB },
    { start: 0.56, end: 0.84, from: points.candidateB, to: points.candidateC },
    { start: 0.84, end: 1, from: points.candidateC, to: points.impact },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(approachSpine, lerp(0.22, 0.06, progress));
  setOpacity(pendingShell, 0.12 + progress * 0.08);
  setOpacity(shellBase, 0.16 + progress * 0.08);
  setOpacity(shellInner, 0.06 + progress * 0.08);

  const revealA = clamp(progress / 0.18, 0, 1);
  const revealB = clamp((progress - 0.18) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.52) / 0.22, 0, 1);

  const activeA = progress < 0.32 ? 1 : 0;
  const activeB = progress >= 0.32 && progress < 0.64 ? 1 : 0;
  const activeC = progress >= 0.64 ? 1 : 0;

  searchGuideA.setAttribute("stroke", activeA ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", activeB ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", activeC ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, activeA ? 0.42 : 0.08 + revealA * 0.08);
  setOpacity(searchGuideB, activeB ? 0.38 : 0.08 + revealB * 0.08);
  setOpacity(searchGuideC, activeC ? 0.38 : 0.08 + revealC * 0.08);

  setGroupTransform(
    candidateA,
    points.candidateA.x,
    points.candidateA.y,
    lerp(0.88, activeA ? 1.06 : 0.96, revealA),
    lerp(-8, 0, revealA),
  );
  setGroupTransform(
    candidateB,
    points.candidateB.x,
    points.candidateB.y,
    lerp(0.88, activeB ? 1.06 : 0.96, revealB),
    lerp(8, 0, revealB),
  );
  setGroupTransform(
    candidateC,
    points.candidateC.x,
    points.candidateC.y,
    lerp(0.88, activeC ? 1.06 : 0.96, revealC),
    lerp(-6, 0, revealC),
  );

  [candidateA, candidateB, candidateC].forEach((element, index) => {
    const reveal = index === 0 ? revealA : index === 1 ? revealB : revealC;
    const active = index === 0 ? activeA : index === 1 ? activeB : activeC;
    setOpacity(element, active ? 1 : reveal * 0.34 + 0.18);
  });

  setOpacity(impactBumper, 0.12);
  setOpacity(impactKeeper, 0.1);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.36, 0, 1);
  const compression = Math.sin(clamp(progress / 0.84, 0, 1) * Math.PI);
  const close = easeInOut(clamp(progress / 0.72, 0, 1));
  const position = mixPoint(points.candidateC, points.impact, easeInOut(travel));
  const topX1 = lerp(782, 818, close);
  const topX2 = lerp(1006, 972, close);
  const bottomX1 = lerp(782, 816, close);
  const bottomX2 = lerp(1006, 968, close);
  const residue = 1 - easeOut(clamp(progress / 0.28, 0, 1));

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 114, progress),
    1,
    0.24 + pulseWave(progress, 2.1) * 0.1,
    lerp(1, 0.54, compression),
    lerp(1, 1.6, compression),
  );

  setOpacity(approachSpine, lerp(0.08, 0.02, progress));
  setOpacity(pendingShell, 0.2 + progress * 0.12);
  setOpacity(shellBase, 0.24 + progress * 0.16);
  setOpacity(shellInner, 0.08 + progress * 0.1);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.mutedRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.24 : 0.16, 0, progress));
  });
  setOpacity(candidateA, lerp(0.38, 0.06, progress));
  setOpacity(candidateB, lerp(0.38, 0.06, progress));
  setOpacity(candidateC, lerp(1, 0.14, progress));

  setOpacity(tensionHalo, clamp((progress - 0.02) * 1.4, 0, 0.86));
  setOpacity(impactBumper, clamp((progress - 0.04) * 1.5, 0, 1));
  setOpacity(impactKeeper, clamp((progress - 0.06) * 1.5, 0, 1));
  topGuide.setAttribute("x1", topX1.toFixed(2));
  topGuide.setAttribute("x2", topX2.toFixed(2));
  bottomGuide.setAttribute("x1", bottomX1.toFixed(2));
  bottomGuide.setAttribute("x2", bottomX2.toFixed(2));
  setOpacity(topGuide, clamp((progress - 0.08) * 1.4, 0, 0.54));
  setOpacity(bottomGuide, clamp((progress - 0.08) * 1.4, 0, 0.54));

  setOpacity(routeBase, 0.04 + progress * 0.06);
  setPathWindow(routeActive, ROUTE_LENGTH, ROUTE_LENGTH * 0.1, 0.06 * residue);
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.88, 0, 1));
  const position = pointOnRoute(routeProgress);
  const cleanup = easeOut(clamp(progress / 0.46, 0, 1));
  const frameReveal = clamp((progress - 0.58) / 0.24, 0, 1);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.2) * 0.08);
  setOpacity(approachSpine, 0);
  setOpacity(pendingShell, lerp(0.32, 0.08, progress));
  setOpacity(shellBase, lerp(0.4, 0.08, progress));
  setOpacity(shellInner, lerp(0.12, 0, progress));

  [searchGuideA, searchGuideB, searchGuideC, candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  setOpacity(tensionHalo, lerp(0.86, 0.1, progress));
  setOpacity(impactBumper, lerp(1, 0.08, cleanup));
  setOpacity(impactKeeper, lerp(1, 0.08, cleanup));
  setOpacity(topGuide, lerp(0.54, 0.06, cleanup));
  setOpacity(bottomGuide, lerp(0.54, 0.06, cleanup));

  setOpacity(routeBase, lerp(0.14, 0.44, routeProgress));
  setPathWindow(routeActive, ROUTE_LENGTH, ROUTE_LENGTH * routeProgress, 1);
  setOpacity(resolutionHalo, clamp((progress - 0.6) * 1.2, 0, 0.16));
  setOpacity(resolutionFrame, frameReveal * 0.54);
  setOpacity(resolutionRule, clamp((progress - 0.74) * 1.6, 0, 0.26));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.resolution, 16, 96, 1, holdPulse);
  [
    approachSpine,
    pendingShell,
    shellBase,
    shellInner,
    searchGuideA,
    searchGuideB,
    searchGuideC,
    candidateA,
    candidateB,
    candidateC,
    tensionHalo,
    impactBumper,
    impactKeeper,
    topGuide,
    bottomGuide,
  ].forEach((element) => setOpacity(element, 0));

  setOpacity(routeBase, lerp(0.44, 0.54, settle));
  setPathWindow(routeActive, ROUTE_LENGTH, ROUTE_LENGTH, lerp(1, 0.2, settle));
  setOpacity(resolutionRule, lerp(0.26, 0.62, settle));
  setOpacity(resolutionFrame, lerp(0.54, 0.9, settle));
  setOpacity(resolutionHalo, lerp(0.16, 0.28, settle));
  resolutionHalo.setAttribute("r", lerp(148, 126, settle).toFixed(2));
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);
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

window.addEventListener("resize", () => {
  const info = phaseForElapsed(state.currentElapsed);
  applyFraming(info.phase.id);
});

resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
