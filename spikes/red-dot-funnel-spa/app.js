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
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");
const tensionHalo = document.getElementById("tension-halo");
const mergeLeftGuide = document.getElementById("merge-left-guide");
const mergeRightGuide = document.getElementById("merge-right-guide");
const stemSlot = document.getElementById("stem-slot");
const throatLeft = document.getElementById("throat-left");
const throatRight = document.getElementById("throat-right");
const funnelBase = document.getElementById("funnel-base");
const funnelActive = document.getElementById("funnel-active");
const mergeTick = document.getElementById("merge-tick");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const FUNNEL_LENGTH = funnelActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 302, y: 454 },
  ingress: { x: 600, y: 454 },
  candidateA: { x: 716, y: 344 },
  candidateB: { x: 832, y: 332 },
  candidateC: { x: 892, y: 352 },
  approach: { x: 882, y: 428 },
  throat: { x: 860, y: 452 },
};

const system = {
  candidateASettle: { x: 756, y: 382 },
  candidateBSettle: { x: 840, y: 388 },
  candidateCSettle: { x: 890, y: 410 },
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

function pointOnFunnel(progress) {
  const length = clamp(progress, 0, 1) * FUNNEL_LENGTH;
  const point = funnelActive.getPointAtLength(length);
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

function applySceneOffset(phaseId) {
  const offsets = {
    appearance: 18,
    search: 20,
    tension: 14,
    transformation: 10,
    resolution: 0,
  };
  const offsetY = offsets[phaseId] ?? 0;
  const offsetX = phaseId === "appearance" ? 52 : phaseId === "search" ? -18 : 0;
  sceneRoot.setAttribute("transform", `translate(${offsetX} ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 136, y: 150, width: 1088, height: 620 },
    search: { x: 154, y: 162, width: 1120, height: 600 },
    tension: { x: 356, y: 154, width: 920, height: 640 },
    transformation: { x: 462, y: 142, width: 820, height: 680 },
    resolution: { x: 486, y: 152, width: 780, height: 656 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -22) translate(800 450) scale(1.03) translate(-800 -450)",
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

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, 1, 0);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, 1, 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, 1, 0);
  [candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  [tensionHalo, mergeLeftGuide, mergeRightGuide, stemSlot, throatLeft, throatRight].forEach((element) => setOpacity(element, 0));
  setGroupTransform(throatLeft, points.throat.x - 52, points.throat.y, 1, 0);
  setGroupTransform(throatRight, points.throat.x + 52, points.throat.y, 1, 0);

  setOpacity(funnelBase, 0);
  setPathWindow(funnelActive, FUNNEL_LENGTH, 0, 0);
  setOpacity(mergeTick, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRing, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.2) * 0.18,
  );

  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));

  const preview = clamp((progress - 0.48) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(candidateA, preview * 0.1);
  setOpacity(candidateB, preview * 0.08);
  setOpacity(candidateC, preview * 0.08);
  setOpacity(mergeLeftGuide, preview * 0.1);
  setOpacity(mergeRightGuide, preview * 0.1);
  setOpacity(stemSlot, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.3, from: points.ingress, to: points.candidateA },
    { start: 0.3, end: 0.64, from: points.candidateA, to: points.candidateB },
    { start: 0.64, end: 0.9, from: points.candidateB, to: points.candidateC },
    { start: 0.9, end: 1, from: points.candidateC, to: points.approach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.16, 0.02, progress));

  const revealA = clamp(progress / 0.24, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.24, 0, 1);

  const activeA = progress < 0.34 ? 1 : 0;
  const activeB = progress >= 0.34 && progress < 0.72 ? 1 : 0;
  const activeC = progress >= 0.72 ? 1 : 0;

  searchGuideA.setAttribute("stroke", activeA ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", activeB ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", activeC ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, activeA ? 0.42 : 0.1 + revealA * 0.06);
  setOpacity(searchGuideB, activeB ? 0.38 : 0.08 + revealB * 0.08);
  setOpacity(searchGuideC, activeC ? 0.34 : 0.06 + revealC * 0.08);

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, lerp(0.88, activeA ? 1.06 : 0.96, revealA), lerp(-4, 0, revealA));
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, lerp(0.88, activeC ? 1.04 : 0.95, revealC), lerp(0, 6, revealC));
  setOpacity(candidateA, activeA ? 1 : revealA * 0.34 + 0.16);
  setOpacity(candidateB, activeB ? 1 : revealB * 0.34 + 0.16);
  setOpacity(candidateC, activeC ? 1 : revealC * 0.34 + 0.16);

  setOpacity(mergeLeftGuide, 0.08);
  setOpacity(mergeRightGuide, 0.08);
  setOpacity(stemSlot, 0.06);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.approach, points.throat, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const throatGap = lerp(52, 20, easeInOut(clamp(progress / 0.72, 0, 1)));
  const collapse = clamp(progress / 0.74, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(88, 112, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.66, compression),
    lerp(1, 1.58, compression),
  );

  setOpacity(narrativeSpine, lerp(0.12, 0.03, progress));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.16, 0, progress));
  });

  setGroupTransform(
    candidateA,
    lerp(points.candidateA.x, system.candidateASettle.x, collapse),
    lerp(points.candidateA.y, system.candidateASettle.y, collapse),
    lerp(0.96, 0.72, collapse),
    lerp(0, -6, collapse),
  );
  setGroupTransform(
    candidateB,
    lerp(points.candidateB.x, system.candidateBSettle.x, collapse),
    lerp(points.candidateB.y, system.candidateBSettle.y, collapse),
    lerp(0.96, 0.76, collapse),
    0,
  );
  setGroupTransform(
    candidateC,
    lerp(points.candidateC.x, system.candidateCSettle.x, collapse),
    lerp(points.candidateC.y, system.candidateCSettle.y, collapse),
    lerp(0.95, 0.72, collapse),
    lerp(0, 8, collapse),
  );
  setOpacity(candidateA, lerp(0.34, 0.06, collapse));
  setOpacity(candidateB, lerp(0.34, 0.08, collapse));
  setOpacity(candidateC, lerp(1, 0.14, collapse));

  setOpacity(tensionHalo, clamp((progress - 0.02) * 1.4, 0, 0.88));
  setOpacity(mergeLeftGuide, clamp((progress - 0.04) * 1.6, 0, 0.54));
  setOpacity(mergeRightGuide, clamp((progress - 0.04) * 1.6, 0, 0.54));
  setOpacity(stemSlot, clamp((progress - 0.1) * 1.4, 0, 0.3));
  setOpacity(throatLeft, clamp((progress - 0.04) * 1.6, 0, 1));
  setOpacity(throatRight, clamp((progress - 0.04) * 1.6, 0, 1));
  setGroupTransform(throatLeft, points.throat.x - throatGap, points.throat.y, 1, 0);
  setGroupTransform(throatRight, points.throat.x + throatGap, points.throat.y, 1, 0);
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.86, 0, 1));
  const position = pointOnFunnel(routeProgress);
  const guideFade = lerp(0.54, 0.14, progress);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);

  setOpacity(funnelBase, lerp(0.08, 0.3, routeProgress));
  setPathWindow(funnelActive, FUNNEL_LENGTH, FUNNEL_LENGTH * routeProgress, 1);

  setOpacity(tensionHalo, lerp(0.88, 0.12, progress));
  setOpacity(mergeLeftGuide, guideFade);
  setOpacity(mergeRightGuide, guideFade);
  setOpacity(stemSlot, lerp(0.3, 0.06, progress));
  setOpacity(throatLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(throatRight, clamp(1 - progress * 1.1, 0, 1));
  setGroupTransform(throatLeft, points.throat.x - lerp(20, 34, progress), points.throat.y, 1, 0);
  setGroupTransform(throatRight, points.throat.x + lerp(20, 34, progress), points.throat.y, 1, 0);

  setOpacity(candidateA, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateB, clamp(0.08 - progress * 0.1, 0, 1));
  setOpacity(candidateC, clamp(0.14 - progress * 0.18, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(resolutionHalo, clamp((progress - 0.62) * 1.4, 0, 0.18));
  setOpacity(resolutionRing, clamp((progress - 0.72) * 1.6, 0, 0.24));
  setOpacity(mergeTick, clamp((progress - 0.78) * 1.5, 0, 0.12));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.throat, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(tensionHalo, 0);
  [searchGuideA, searchGuideB, searchGuideC, candidateA, candidateB, candidateC, throatLeft, throatRight, mergeLeftGuide, mergeRightGuide, stemSlot].forEach(
    (element) => setOpacity(element, 0),
  );

  setOpacity(funnelBase, lerp(0.3, 0.48, settle));
  setPathWindow(funnelActive, FUNNEL_LENGTH, FUNNEL_LENGTH, lerp(1, 0.28, settle));
  setOpacity(mergeTick, lerp(0.12, 0.24, settle));
  setOpacity(resolutionHalo, lerp(0.18, 0.32, settle));
  setOpacity(resolutionRing, lerp(0.24, 0.9, settle));
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
