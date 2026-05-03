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
const candidateHook = document.getElementById("candidate-hook");
const candidateFork = document.getElementById("candidate-fork");
const candidateCradle = document.getElementById("candidate-cradle");

const pivotGlowShape = document.getElementById("pivot-glow-shape");
const guideAxis = document.getElementById("guide-axis");
const swingArcBase = document.getElementById("swing-arc-base");
const swingArcActive = document.getElementById("swing-arc-active");
const topBeam = document.getElementById("top-beam");
const topStem = document.getElementById("top-stem");
const rodLine = document.getElementById("rod-line");
const stopBracket = document.getElementById("stop-bracket");

const leftStand = document.getElementById("left-stand");
const rightStand = document.getElementById("right-stand");
const baseRule = document.getElementById("base-rule");
const echoLeft = document.getElementById("echo-left");
const echoRight = document.getElementById("echo-right");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const SWING_ARC_LENGTH = swingArcActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const pivot = { x: 846, y: 294 };
const pendulumLength = 266;

const points = {
  start: { x: 304, y: 454 },
  ingress: { x: 398, y: 454 },
  hookCandidate: { x: 690, y: 360 },
  forkCandidate: { x: 846, y: 322 },
  cradleCandidate: { x: 1004, y: 390 },
  tensionExtreme: { x: 976, y: 520 },
  final: { x: 846, y: 560 },
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

function setLine(element, from, to) {
  element.setAttribute("x1", from.x.toFixed(2));
  element.setAttribute("y1", from.y.toFixed(2));
  element.setAttribute("x2", to.x.toFixed(2));
  element.setAttribute("y2", to.y.toFixed(2));
}

function pointOnPendulum(angleDegrees) {
  const radians = (angleDegrees * Math.PI) / 180;
  return {
    x: pivot.x + Math.sin(radians) * pendulumLength,
    y: pivot.y + Math.cos(radians) * pendulumLength,
  };
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
    search: 18,
    tension: 6,
    transformation: 0,
    resolution: -6,
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
    appearance: { x: 120, y: 160, width: 1080, height: 620 },
    search: { x: 170, y: 118, width: 1120, height: 650 },
    tension: { x: 452, y: 122, width: 790, height: 660 },
    transformation: { x: 272, y: 98, width: 1130, height: 706 },
    resolution: { x: 330, y: 110, width: 1030, height: 694 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -14) translate(800 450) scale(1.04) translate(-800 -450)",
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

  setGroupTransform(candidateHook, points.hookCandidate.x, points.hookCandidate.y, 1, -6);
  setGroupTransform(candidateFork, points.forkCandidate.x, points.forkCandidate.y, 1, 0);
  setGroupTransform(candidateCradle, points.cradleCandidate.x, points.cradleCandidate.y, 1, 6);
  [candidateHook, candidateFork, candidateCradle].forEach((element) => setOpacity(element, 0));

  setOpacity(pivotGlowShape, 0);
  setOpacity(guideAxis, 0);
  setOpacity(swingArcBase, 0);
  setPathWindow(swingArcActive, SWING_ARC_LENGTH, 0, 0);
  setOpacity(topBeam, 0);
  setOpacity(topStem, 0);
  setOpacity(rodLine, 0);
  setGroupTransform(stopBracket, points.tensionExtreme.x + 14, points.tensionExtreme.y, 1, 0);
  setOpacity(stopBracket, 0);
  setLine(rodLine, pivot, points.final);

  [leftStand, rightStand, baseRule, echoLeft, echoRight, resolutionHalo].forEach((element) => setOpacity(element, 0));
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.88);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.22 + pulseWave(progress, 1.2) * 0.16,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.5, 0, 0.34));

  const preview = clamp((progress - 0.34) * 1.6, 0, 1);
  setOpacity(searchGuideA, preview * 0.14);
  setOpacity(candidateHook, preview * 0.1);
  setOpacity(candidateFork, preview * 0.08);
  setOpacity(candidateCradle, preview * 0.05);
  setOpacity(pivotGlowShape, preview * 0.08);
  setOpacity(guideAxis, preview * 0.08);
  setOpacity(swingArcBase, preview * 0.06);
  setOpacity(topBeam, preview * 0.08);
  setOpacity(topStem, preview * 0.06);
  setOpacity(rodLine, preview * 0.02);
  setOpacity(leftStand, preview * 0.02);
  setOpacity(rightStand, preview * 0.02);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.hookCandidate },
    { start: 0.28, end: 0.58, from: points.hookCandidate, to: points.forkCandidate },
    { start: 0.58, end: 0.82, from: points.forkCandidate, to: points.cradleCandidate },
    { start: 0.82, end: 1, from: points.cradleCandidate, to: points.tensionExtreme },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.24, 0.06, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 260 + progress * 640, 0.78);

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.22 + revealA * 0.18);
  setOpacity(searchGuideB, 0.1 + revealB * 0.18);
  setOpacity(searchGuideC, 0.08 + revealC * 0.18);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(
    candidateHook,
    points.hookCandidate.x,
    points.hookCandidate.y,
    lerp(0.88, activeA ? 1.06 : 0.96, revealA),
    -6,
  );
  setGroupTransform(
    candidateFork,
    points.forkCandidate.x,
    points.forkCandidate.y,
    lerp(0.88, activeB ? 1.06 : 0.96, revealB),
    0,
  );
  setGroupTransform(
    candidateCradle,
    points.cradleCandidate.x,
    points.cradleCandidate.y,
    lerp(0.84, activeC ? 1.06 : 0.96, revealC),
    6,
  );
  setOpacity(candidateHook, activeA ? 1 : revealA * 0.18 + 0.08);
  setOpacity(candidateFork, activeB ? 1 : revealB * 0.18 + 0.08);
  setOpacity(candidateCradle, activeC ? 1 : revealC * 0.18 + 0.08);

  setOpacity(pivotGlowShape, 0.08);
  setOpacity(guideAxis, 0.1);
  setOpacity(swingArcBase, 0.08);
  setOpacity(topBeam, 0.08);
  setOpacity(topStem, 0.08);
  setOpacity(leftStand, 0.03);
  setOpacity(rightStand, 0.03);
  setOpacity(baseRule, 0.03);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.32, 0, 1);
  const position = mixPoint(points.cradleCandidate, points.tensionExtreme, easeInOut(travel));
  const hold = progress < 0.4
    ? easeOut(progress / 0.4)
    : progress < 0.82
      ? 1
      : 1 - easeInOut((progress - 0.82) / 0.18);

  setDot(
    position,
    lerp(18, 16, hold),
    lerp(88, 118, hold),
    1,
    0.26 + hold * 0.14,
    lerp(1, 1.28, hold),
    lerp(1, 0.78, hold),
  );
  setOpacity(narrativeSpine, 0.06);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.6, 0.18, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const collapse = clamp(progress / 0.74, 0, 1);
  setGroupTransform(candidateHook, lerp(points.hookCandidate.x, 760, collapse), lerp(points.hookCandidate.y, 338, collapse), lerp(0.96, 0.72, collapse), -10);
  setGroupTransform(candidateFork, lerp(points.forkCandidate.x, 846, collapse), lerp(points.forkCandidate.y, 302, collapse), lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateCradle, lerp(points.cradleCandidate.x, 932, collapse), lerp(points.cradleCandidate.y, 364, collapse), lerp(0.96, 0.72, collapse), 10);
  setOpacity(candidateHook, lerp(0.18, 0.02, collapse));
  setOpacity(candidateFork, lerp(0.2, 0.03, collapse));
  setOpacity(candidateCradle, lerp(0.84, 0.08, collapse));

  setOpacity(pivotGlowShape, 0.26 + hold * 0.16);
  setOpacity(guideAxis, 0.44);
  setOpacity(swingArcBase, 0.24);
  setOpacity(topBeam, 1);
  setOpacity(topStem, 0.92);
  setLine(rodLine, pivot, position);
  setOpacity(rodLine, 1);
  setGroupTransform(stopBracket, position.x + 16, position.y, 1, 0);
  setOpacity(stopBracket, 0.96);

  setOpacity(leftStand, clamp((progress - 0.52) * 1.2, 0, 0.18));
  setOpacity(rightStand, clamp((progress - 0.52) * 1.2, 0, 0.18));
  setOpacity(baseRule, clamp((progress - 0.62) * 1.1, 0, 0.12));
}

function renderTransformation(progress) {
  let position = points.final;
  let arcProgress = 1;

  if (progress < 0.56) {
    const swing = easeInOut(progress / 0.56);
    const angle = lerp(29, -26, swing);
    position = pointOnPendulum(angle);
    arcProgress = swing;
  } else {
    const returnProgress = easeInOut((progress - 0.56) / 0.44);
    const leftPoint = pointOnPendulum(-26);
    position = mixPoint(leftPoint, points.final, returnProgress);
    arcProgress = 1;
  }

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 180 + (1 - progress) * 120, 0.16);

  setOpacity(pivotGlowShape, lerp(0.42, 0.18, progress));
  setOpacity(guideAxis, lerp(0.44, 0.18, progress));
  setOpacity(swingArcBase, lerp(0.24, 0.34, progress));
  setPathWindow(swingArcActive, SWING_ARC_LENGTH, SWING_ARC_LENGTH * arcProgress, clamp((progress - 0.04) * 1.5, 0, 1));
  setOpacity(topBeam, 1);
  setOpacity(topStem, 0.92);
  setLine(rodLine, pivot, position);
  setOpacity(rodLine, 1);
  setOpacity(stopBracket, clamp(1 - progress * 1.5, 0, 1));

  [candidateHook, candidateFork, candidateCradle, searchGuideA, searchGuideB, searchGuideC].forEach((element) => setOpacity(element, 0));

  setOpacity(leftStand, clamp((progress - 0.12) * 1.4, 0, 1));
  setOpacity(rightStand, clamp((progress - 0.12) * 1.4, 0, 1));
  setOpacity(baseRule, clamp((progress - 0.2) * 1.4, 0, 0.84));
  setOpacity(echoLeft, clamp((progress - 0.62) * 1.6, 0, 0.18));
  setOpacity(echoRight, clamp((progress - 0.62) * 1.6, 0, 0.18));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.6, 0, 0.16));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.final, 16, lerp(98, 88, progress), 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(pivotGlowShape, lerp(0.18, 0.12, settle));
  setOpacity(guideAxis, lerp(0.18, 0.04, settle));
  setOpacity(swingArcBase, lerp(0.34, 0.12, settle));
  setPathWindow(swingArcActive, SWING_ARC_LENGTH, SWING_ARC_LENGTH, lerp(1, 0.18, settle));
  setOpacity(topBeam, 1);
  setOpacity(topStem, 0.92);
  setLine(rodLine, pivot, points.final);
  setOpacity(rodLine, 1);
  setOpacity(stopBracket, 0);

  setOpacity(leftStand, 0.94);
  setOpacity(rightStand, 0.94);
  setOpacity(baseRule, lerp(0.84, 0.94, settle));
  setOpacity(echoLeft, lerp(0.18, 0.12, settle));
  setOpacity(echoRight, lerp(0.18, 0.12, settle));
  setOpacity(resolutionHalo, lerp(0.16, 0.28, settle));
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
