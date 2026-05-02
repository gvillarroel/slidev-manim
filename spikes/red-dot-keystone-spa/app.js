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
const phaseStatus = document.getElementById("phase-status");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const guideA = document.getElementById("guide-a");
const guideB = document.getElementById("guide-b");
const guideC = document.getElementById("guide-c");
const guideD = document.getElementById("guide-d");
const candidateArch = document.getElementById("candidate-arch");
const candidateNotch = document.getElementById("candidate-notch");
const candidateCradle = document.getElementById("candidate-cradle");

const tensionGroup = document.getElementById("tension-group");
const pocketHalo = document.getElementById("pocket-halo");
const pocketLeft = document.getElementById("pocket-left");
const pocketRight = document.getElementById("pocket-right");
const pocketCap = document.getElementById("pocket-cap");
const pocketSlot = document.getElementById("pocket-slot");
const pocketBase = document.getElementById("pocket-base");

const lockGroup = document.getElementById("lock-group");
const traceLeftBase = document.getElementById("trace-left-base");
const traceRightBase = document.getElementById("trace-right-base");
const traceLeftActive = document.getElementById("trace-left-active");
const traceRightActive = document.getElementById("trace-right-active");
const memoryArch = document.getElementById("memory-arch");
const supportLeft = document.getElementById("support-left");
const supportRight = document.getElementById("support-right");
const supportCap = document.getElementById("support-cap");
const supportBase = document.getElementById("support-base");
const supportLeftRule = document.getElementById("support-left-rule");
const supportRightRule = document.getElementById("support-right-rule");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionRing = document.getElementById("resolution-ring");
const resolutionAura = document.getElementById("resolution-aura");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const TRACE_LEFT_LENGTH = traceLeftActive.getTotalLength();
const TRACE_RIGHT_LENGTH = traceRightActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  lineGray: "#cfcfcf",
  passiveGray: "#b5b5b5",
};

const points = {
  start: { x: 306, y: 452 },
  searchA: { x: 524, y: 360 },
  searchB: { x: 760, y: 330 },
  searchC: { x: 628, y: 566 },
  pocket: { x: 860, y: 452 },
  capTrace: { x: 820, y: 318 },
  rightTrace: { x: 948, y: 420 },
  leftTrace: { x: 692, y: 420 },
  final: { x: 820, y: 452 },
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

function setGroupTransform(element, x, y, scale = 1) {
  element.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${scale.toFixed(3)})`);
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

function updatePhaseStatus(info) {
  phaseStatus.textContent = info.phase.label;
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 120, width: 1080 },
    search: { x: 190, width: 980 },
    tension: { x: 430, width: 760 },
    transformation: { x: 330, width: 980 },
    resolution: { x: 340, width: 960 },
  };
  const frame = frames[phaseId] ?? { x: 0, width: 1600 };
  svg.setAttribute("viewBox", `${frame.x} 0 ${frame.width} 900`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -16) translate(800 450) scale(1.05) translate(-800 -450)",
    );
    sceneRoot.setAttribute("transform", "translate(0 14)");
    svg.dataset.layout = "portrait";
  } else {
    layoutRoot.setAttribute("transform", "");
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
  svg.setAttribute("viewBox", FULL_VIEWBOX);
}

function resetScene() {
  setDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [guideA, guideB, guideC, guideD].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateArch, points.searchA.x, points.searchA.y, 1);
  setGroupTransform(candidateNotch, points.searchB.x, points.searchB.y, 1);
  setGroupTransform(candidateCradle, points.searchC.x, points.searchC.y, 1);
  [candidateArch, candidateNotch, candidateCradle].forEach((element) => setOpacity(element, 0));

  setOpacity(tensionGroup, 0);
  setOpacity(pocketHalo, 0);
  pocketLeft.setAttribute("transform", "translate(808 458)");
  pocketRight.setAttribute("transform", "translate(912 458)");
  pocketCap.setAttribute("transform", "translate(860 354)");
  setOpacity(pocketSlot, 0);
  setOpacity(pocketBase, 0);

  setOpacity(lockGroup, 0);
  [traceLeftBase, traceRightBase, traceLeftActive, traceRightActive, memoryArch].forEach((path) => setOpacity(path, 0));
  [supportLeft, supportRight, supportCap, supportBase, supportLeftRule, supportRightRule].forEach((element) =>
    setOpacity(element, 0),
  );
  setPathWindow(traceLeftActive, TRACE_LEFT_LENGTH, 0, 0);
  setPathWindow(traceRightActive, TRACE_RIGHT_LENGTH, 0, 0);

  setOpacity(resolutionGroup, 0);
  setOpacity(resolutionRing, 0);
  setOpacity(resolutionAura, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(clamp((progress - 0.08) / 0.92, 0, 1));
  const position = mixPoint(points.start, { x: 398, y: 452 }, eased * 0.86);

  setDot(position, lerp(6, 18, eased), lerp(20, 82, eased), clamp(progress * 1.8, 0, 1), 0.16 + pulseWave(progress, 1.1) * 0.08);
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.2, 0, 0.32));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(guideA, clamp((progress - 0.18) * 1.6, 0, 0.22));
  setOpacity(guideB, clamp((progress - 0.24) * 1.6, 0, 0.18));
  setOpacity(guideC, clamp((progress - 0.3) * 1.6, 0, 0.16));
  setOpacity(guideD, clamp((progress - 0.36) * 1.6, 0, 0.14));
  setOpacity(candidateArch, clamp((progress - 0.22) * 1.5, 0, 0.28));
  setOpacity(candidateNotch, clamp((progress - 0.3) * 1.5, 0, 0.24));
  setOpacity(candidateCradle, clamp((progress - 0.38) * 1.5, 0, 0.22));

  setOpacity(tensionGroup, clamp((progress - 0.48) * 1.4, 0, 0.14));
  setOpacity(pocketSlot, clamp((progress - 0.52) * 1.4, 0, 0.16));
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.start, to: points.searchA },
    { start: 0.28, end: 0.56, from: points.searchA, to: points.searchB },
    { start: 0.56, end: 0.82, from: points.searchB, to: points.searchC },
    { start: 0.82, end: 1, from: points.searchC, to: points.pocket },
  ]);

  setDot(position, 18, 84, 1, 0.22 + pulseWave(progress, 1.9) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.14, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 220 + progress * 270, 0.78);

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  guideA.setAttribute("stroke", progress < 0.32 ? COLORS.primaryRed : COLORS.lineGray);
  guideB.setAttribute("stroke", progress >= 0.32 && progress < 0.6 ? COLORS.primaryRed : COLORS.lineGray);
  guideC.setAttribute("stroke", progress >= 0.6 && progress < 0.82 ? COLORS.primaryRed : COLORS.lineGray);
  guideD.setAttribute("stroke", progress >= 0.82 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(guideA, 0.24 + revealA * 0.18);
  setOpacity(guideB, 0.18 + revealB * 0.18);
  setOpacity(guideC, 0.18 + revealC * 0.18);
  setOpacity(guideD, clamp((progress - 0.68) * 1.4, 0, 0.28));

  setGroupTransform(candidateArch, points.searchA.x, points.searchA.y, lerp(0.9, progress < 0.32 ? 1.07 : 0.97, revealA));
  setGroupTransform(candidateNotch, points.searchB.x, points.searchB.y, lerp(0.9, progress >= 0.32 && progress < 0.6 ? 1.07 : 0.97, revealB));
  setGroupTransform(candidateCradle, points.searchC.x, points.searchC.y, lerp(0.9, progress >= 0.6 ? 1.07 : 0.97, revealC));
  setOpacity(candidateArch, progress < 0.32 ? 0.94 : 0.34);
  setOpacity(candidateNotch, progress >= 0.32 && progress < 0.6 ? 0.94 : 0.3);
  setOpacity(candidateCradle, progress >= 0.6 ? 0.94 : 0.28);

  const archPaths = candidateArch.querySelectorAll("path");
  const notchPaths = candidateNotch.querySelectorAll("path");
  const cradlePath = candidateCradle.querySelector("path");
  archPaths[0].setAttribute("stroke", progress < 0.32 ? COLORS.primaryRed : COLORS.passiveGray);
  notchPaths[0].setAttribute("stroke", progress >= 0.32 && progress < 0.6 ? COLORS.primaryRed : COLORS.passiveGray);
  cradlePath.setAttribute("stroke", progress >= 0.6 ? COLORS.primaryRed : COLORS.passiveGray);

  setOpacity(tensionGroup, 0.2);
  setOpacity(pocketSlot, 0.22);
  setOpacity(pocketBase, 0.12);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.34, 0, 1);
  const position = mixPoint(points.searchC, points.pocket, easeInOut(travel));
  const compression = progress < 0.3
    ? easeOut(progress / 0.3)
    : progress < 0.76
      ? 1
      : 1 - easeInOut((progress - 0.76) / 0.24);
  const pulse = progress > 0.28 && progress < 0.74
    ? (pulseWave((progress - 0.28) / 0.46, 2.2) - 0.5) * 10
    : 0;

  const shoulderGap = lerp(104, 58, compression) + pulse * 0.4;
  const capY = lerp(354, 324, compression) + pulse * 0.2;

  setDot(
    position,
    lerp(18, 16, compression),
    lerp(84, 112, compression),
    1,
    0.24 + compression * 0.16,
    lerp(1, 1.62, compression),
    lerp(1, 0.68, compression),
  );
  setOpacity(narrativeSpine, 0.12);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 610 + progress * 120, 0.86);

  [guideA, guideB, guideC, guideD].forEach((guide, index) => {
    setOpacity(guide, lerp(index === 3 ? 0.28 : 0.2, 0, progress));
  });

  const searchCollapse = clamp(progress / 0.64, 0, 1);
  setGroupTransform(candidateArch, lerp(points.searchA.x, 760, searchCollapse), lerp(points.searchA.y, 392, searchCollapse), lerp(0.97, 0.72, searchCollapse));
  setGroupTransform(candidateNotch, lerp(points.searchB.x, 820, searchCollapse), lerp(points.searchB.y, 338, searchCollapse), lerp(0.97, 0.68, searchCollapse));
  setGroupTransform(candidateCradle, lerp(points.searchC.x, 860, searchCollapse), lerp(points.searchC.y, 548, searchCollapse), lerp(0.97, 0.74, searchCollapse));
  setOpacity(candidateArch, lerp(0.32, 0.06, searchCollapse));
  setOpacity(candidateNotch, lerp(0.3, 0.08, searchCollapse));
  setOpacity(candidateCradle, lerp(0.94, 0.12, searchCollapse));

  setOpacity(tensionGroup, 1);
  setOpacity(pocketHalo, 0.16 + compression * 0.18);
  pocketLeft.setAttribute("transform", `translate(${(860 - shoulderGap).toFixed(2)} 458)`);
  pocketRight.setAttribute("transform", `translate(${(860 + shoulderGap).toFixed(2)} 458)`);
  pocketCap.setAttribute("transform", `translate(860 ${capY.toFixed(2)})`);
  setOpacity(pocketSlot, 0.54);
  setOpacity(pocketBase, 0.4);

  setOpacity(lockGroup, clamp((progress - 0.52) * 1.2, 0, 0.16));
  setOpacity(traceLeftBase, clamp((progress - 0.64) * 1.5, 0, 0.12));
  setOpacity(traceRightBase, clamp((progress - 0.64) * 1.5, 0, 0.12));
}

function renderTransformation(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.22, from: points.pocket, to: points.capTrace },
    { start: 0.22, end: 0.5, from: points.capTrace, to: points.rightTrace },
    { start: 0.5, end: 0.78, from: points.rightTrace, to: points.leftTrace },
    { start: 0.78, end: 1, from: points.leftTrace, to: points.final },
  ]);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0.04);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 220 + (1 - progress) * 120, 0.18);

  setOpacity(tensionGroup, lerp(1, 0.1, progress));
  setOpacity(pocketHalo, lerp(0.34, 0, progress));
  pocketLeft.setAttribute("transform", `translate(${lerp(802, 756, progress).toFixed(2)} 458)`);
  pocketRight.setAttribute("transform", `translate(${lerp(918, 964, progress).toFixed(2)} 458)`);
  pocketCap.setAttribute("transform", `translate(860 ${lerp(324, 300, progress).toFixed(2)})`);
  setOpacity(pocketSlot, lerp(0.54, 0, progress));
  setOpacity(pocketBase, lerp(0.4, 0, progress));

  setOpacity(lockGroup, 1);
  setOpacity(traceLeftBase, clamp((progress - 0.1) * 1.2, 0, 0.48));
  setOpacity(traceRightBase, clamp((progress - 0.1) * 1.2, 0, 0.48));
  setPathWindow(traceRightActive, TRACE_RIGHT_LENGTH, TRACE_RIGHT_LENGTH * clamp((progress - 0.18) / 0.28, 0, 1), clamp((progress - 0.18) * 1.7, 0, 1));
  setPathWindow(traceLeftActive, TRACE_LEFT_LENGTH, TRACE_LEFT_LENGTH * clamp((progress - 0.48) / 0.28, 0, 1), clamp((progress - 0.48) * 1.8, 0, 1));

  const capReveal = clamp((progress - 0.08) / 0.16, 0, 1);
  const rightReveal = clamp((progress - 0.26) / 0.18, 0, 1);
  const leftReveal = clamp((progress - 0.54) / 0.18, 0, 1);
  const baseReveal = clamp((progress - 0.68) / 0.16, 0, 1);

  setOpacity(supportCap, capReveal);
  setOpacity(supportRight, rightReveal);
  setOpacity(supportLeft, leftReveal);
  setOpacity(supportBase, baseReveal);
  setOpacity(supportRightRule, clamp((progress - 0.34) / 0.16, 0, 0.56));
  setOpacity(supportLeftRule, clamp((progress - 0.6) / 0.16, 0, 0.56));
  setOpacity(memoryArch, clamp((progress - 0.72) / 0.2, 0, 0.22));

  supportCap.setAttribute(
    "transform",
    `translate(0 ${(lerp(18, 0, easeOut(capReveal))).toFixed(2)}) scale(${lerp(0.92, 1, capReveal).toFixed(3)})`,
  );
  supportRight.setAttribute(
    "transform",
    `translate(${(lerp(24, 0, easeOut(rightReveal))).toFixed(2)} 0) scale(${lerp(0.92, 1, rightReveal).toFixed(3)})`,
  );
  supportLeft.setAttribute(
    "transform",
    `translate(${(lerp(-24, 0, easeOut(leftReveal))).toFixed(2)} 0) scale(${lerp(0.92, 1, leftReveal).toFixed(3)})`,
  );
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const pulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.final, 16, lerp(98, 86, progress), 1, pulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [guideA, guideB, guideC, guideD, candidateArch, candidateNotch, candidateCradle, tensionGroup].forEach((element) =>
    setOpacity(element, 0),
  );

  setOpacity(lockGroup, 1);
  setOpacity(traceLeftBase, lerp(0.48, 0.34, settle));
  setOpacity(traceRightBase, lerp(0.48, 0.34, settle));
  setPathWindow(traceRightActive, TRACE_RIGHT_LENGTH, TRACE_RIGHT_LENGTH, lerp(1, 0.1, settle));
  setPathWindow(traceLeftActive, TRACE_LEFT_LENGTH, TRACE_LEFT_LENGTH, lerp(1, 0.1, settle));
  setOpacity(memoryArch, lerp(0.22, 0.56, settle));
  setOpacity(supportCap, 0.94);
  setOpacity(supportRight, 0.94);
  setOpacity(supportLeft, 0.94);
  setOpacity(supportBase, lerp(0.8, 0.94, settle));
  setOpacity(supportRightRule, 0.52);
  setOpacity(supportLeftRule, 0.52);

  supportCap.setAttribute("transform", "");
  supportRight.setAttribute("transform", "");
  supportLeft.setAttribute("transform", "");

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionRing, lerp(0.24, 0.82, settle));
  setOpacity(resolutionAura, lerp(0.2, 0.34, settle));
  resolutionRing.setAttribute("r", lerp(110, 92, settle).toFixed(2));
  resolutionAura.setAttribute("r", lerp(168, 150, settle).toFixed(2));
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

  svg.dataset.phase = info.phase.id;
  updatePhaseStatus(info);
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
