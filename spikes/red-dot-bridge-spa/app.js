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
const candidateArch = document.getElementById("candidate-arch");
const candidateTruss = document.getElementById("candidate-truss");
const candidateCable = document.getElementById("candidate-cable");
const passageTop = document.getElementById("passage-top");
const passageBottom = document.getElementById("passage-bottom");
const passageLeft = document.getElementById("passage-left");
const passageRight = document.getElementById("passage-right");
const passageHalo = document.getElementById("passage-halo");
const bridgeLoopBase = document.getElementById("bridge-loop-base");
const bridgeLoopActive = document.getElementById("bridge-loop-active");
const bridgeBaseTop = document.getElementById("bridge-base-top");
const bridgeBaseBottom = document.getElementById("bridge-base-bottom");
const slotLeft = document.getElementById("slot-left");
const slotCrown = document.getElementById("slot-crown");
const slotRight = document.getElementById("slot-right");
const deckLeft = document.getElementById("deck-left");
const deckCrown = document.getElementById("deck-crown");
const deckRight = document.getElementById("deck-right");
const memoryArc = document.getElementById("memory-arc");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const BRIDGE_LOOP_LENGTH = bridgeLoopActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 560, y: 450 },
  arch: { x: 636, y: 318 },
  truss: { x: 820, y: 262 },
  cable: { x: 1024, y: 352 },
  gate: { x: 820, y: 450 },
};

const system = {
  left: { x: 650, y: 458 },
  crown: { x: 820, y: 312 },
  right: { x: 990, y: 458 },
  settleLeft: { x: 666, y: 450 },
  settleCrown: { x: 820, y: 326 },
  settleRight: { x: 974, y: 450 },
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

function pointOnLoop(progress) {
  const length = clamp(progress, 0, 1) * BRIDGE_LOOP_LENGTH;
  const point = bridgeLoopActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.4;
  }
  return clamp(1 - (progress - threshold) / 0.16, 0, 1) * 0.4;
}

function cardState(progress, threshold) {
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
    search: 42,
    tension: 34,
    transformation: 30,
    resolution: 18,
  };
  const offsetY = offsets[phaseId] ?? 18;
  sceneRoot.setAttribute("transform", `translate(0 ${offsetY})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 120, width: 1120 },
    search: { x: 180, width: 1040 },
    tension: { x: 340, width: 920 },
    transformation: { x: 420, width: 820 },
    resolution: { x: 450, width: 780 },
  };
  const frame = frames[phaseId] ?? { x: 0, width: 1600 };
  svg.setAttribute("viewBox", `${frame.x} 0 ${frame.width} 900`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -14) translate(800 450) scale(1.04) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
  } else {
    layoutRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
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

  setGroupTransform(candidateArch, points.arch.x, points.arch.y, 1, 0);
  setGroupTransform(candidateTruss, points.truss.x, points.truss.y, 1, 0);
  setGroupTransform(candidateCable, points.cable.x, points.cable.y, 1, 0);
  [candidateArch, candidateTruss, candidateCable].forEach((element) => setOpacity(element, 0));

  [passageTop, passageBottom, passageLeft, passageRight, passageHalo].forEach((element) => setOpacity(element, 0));
  setGroupTransform(passageLeft, points.gate.x - 66, points.gate.y, 1, 0);
  setGroupTransform(passageRight, points.gate.x + 66, points.gate.y, 1, 0);

  [slotLeft, slotCrown, slotRight].forEach((element) => setOpacity(element, 0));
  setGroupTransform(slotLeft, system.left.x, system.left.y, 1, 0);
  setGroupTransform(slotCrown, system.crown.x, system.crown.y, 1, 0);
  setGroupTransform(slotRight, system.right.x, system.right.y, 1, 0);

  [deckLeft, deckCrown, deckRight].forEach((element) => setOpacity(element, 0));
  setGroupTransform(deckLeft, system.left.x, system.left.y, 1, 0);
  setGroupTransform(deckCrown, system.crown.x, system.crown.y, 1, 0);
  setGroupTransform(deckRight, system.right.x, system.right.y, 1, 0);

  [bridgeLoopBase, bridgeBaseTop, bridgeBaseBottom, memoryArc, resolutionHalo, resolutionRing].forEach((element) =>
    setOpacity(element, 0),
  );
  setPathWindow(bridgeLoopActive, BRIDGE_LOOP_LENGTH, 0, 0);
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
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  const preview = clamp((progress - 0.44) * 1.7, 0, 1);
  setOpacity(searchGuideA, preview * 0.14);
  setOpacity(candidateArch, preview * 0.12);
  setOpacity(candidateTruss, preview * 0.09);
  setOpacity(candidateCable, preview * 0.06);
  setOpacity(passageTop, preview * 0.1);
  setOpacity(passageBottom, preview * 0.1);
  setOpacity(passageLeft, preview * 0.1);
  setOpacity(passageRight, preview * 0.1);
  setOpacity(passageHalo, preview * 0.12);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.28, from: points.ingress, to: points.arch },
    { start: 0.28, end: 0.56, from: points.arch, to: points.truss },
    { start: 0.56, end: 0.82, from: points.truss, to: points.cable },
    { start: 0.82, end: 1, from: points.cable, to: { x: 952, y: 416 } },
  ]);

  setDot(position, 18, 86, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.12, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.3 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.3 && progress < 0.6 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.6 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.24 + revealA * 0.18);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.26);

  const activeA = progress < 0.3 ? 1 : 0;
  const activeB = progress >= 0.3 && progress < 0.6 ? 1 : 0;
  const activeC = progress >= 0.6 ? 1 : 0;

  setGroupTransform(candidateArch, points.arch.x, points.arch.y, lerp(0.88, activeA ? 1.05 : 0.96, revealA), 0);
  setGroupTransform(candidateTruss, points.truss.x, points.truss.y, lerp(0.88, activeB ? 1.05 : 0.96, revealB), 0);
  setGroupTransform(candidateCable, points.cable.x, points.cable.y, lerp(0.84, activeC ? 1.04 : 0.95, revealC), 0);
  setOpacity(candidateArch, activeA ? 1 : revealA * 0.34 + 0.16);
  setOpacity(candidateTruss, activeB ? 1 : revealB * 0.32 + 0.14);
  setOpacity(candidateCable, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(passageTop, 0.1);
  setOpacity(passageBottom, 0.1);
  setOpacity(passageLeft, 0.08);
  setOpacity(passageRight, 0.08);
  setOpacity(passageHalo, 0.1);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.cable, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const gateGap = lerp(66, 28, easeInOut(clamp(progress / 0.66, 0, 1)));
  const collapse = clamp(progress / 0.7, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(86, 112, progress),
    1,
    0.24 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.68, compression),
    lerp(1, 1.58, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const archPosition = mixPoint(points.arch, { x: 742, y: 390 }, collapse);
  const trussPosition = mixPoint(points.truss, { x: 820, y: 344 }, collapse);
  const cablePosition = mixPoint(points.cable, { x: 902, y: 404 }, collapse);
  setGroupTransform(candidateArch, archPosition.x, archPosition.y, lerp(0.96, 0.72, collapse), lerp(0, -10, collapse));
  setGroupTransform(candidateTruss, trussPosition.x, trussPosition.y, lerp(0.96, 0.7, collapse), 0);
  setGroupTransform(candidateCable, cablePosition.x, cablePosition.y, lerp(0.95, 0.66, collapse), lerp(0, 8, collapse));
  setOpacity(candidateArch, lerp(0.34, 0.06, collapse));
  setOpacity(candidateTruss, lerp(0.3, 0.05, collapse));
  setOpacity(candidateCable, lerp(1, 0.12, collapse));

  setOpacity(passageTop, clamp((progress - 0.04) * 1.6, 0, 0.86));
  setOpacity(passageBottom, clamp((progress - 0.04) * 1.6, 0, 0.86));
  setOpacity(passageLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(passageRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(passageHalo, clamp((progress - 0.08) * 1.6, 0, 0.42));
  setGroupTransform(passageLeft, points.gate.x - gateGap, points.gate.y, 1, 0);
  setGroupTransform(passageRight, points.gate.x + gateGap, points.gate.y, 1, 0);

  setOpacity(slotLeft, clamp((progress - 0.44) * 1.3, 0, 0.26));
  setOpacity(slotCrown, clamp((progress - 0.52) * 1.3, 0, 0.26));
  setOpacity(slotRight, clamp((progress - 0.6) * 1.3, 0, 0.26));
}

function renderTransformation(progress) {
  const loopProgress = easeInOut(clamp(progress / 0.86, 0, 1));
  const position = pointOnLoop(loopProgress);
  const leftReveal = cardState(loopProgress, 0.16);
  const crownReveal = cardState(loopProgress, 0.38);
  const rightReveal = cardState(loopProgress, 0.58);

  setDot(position, 16, 94, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(bridgeLoopBase, lerp(0.08, 0.24, loopProgress));
  setPathWindow(bridgeLoopActive, BRIDGE_LOOP_LENGTH, BRIDGE_LOOP_LENGTH * loopProgress, 1);
  setOpacity(bridgeBaseTop, clamp((progress - 0.48) * 1.6, 0, 0.28));
  setOpacity(bridgeBaseBottom, clamp((progress - 0.62) * 1.5, 0, 0.22));

  setOpacity(passageTop, lerp(0.86, 0.1, progress));
  setOpacity(passageBottom, lerp(0.86, 0.1, progress));
  setOpacity(passageLeft, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(passageRight, clamp(1 - progress * 1.08, 0, 1));
  setOpacity(passageHalo, clamp(0.42 - progress * 0.5, 0, 1));
  setGroupTransform(passageLeft, points.gate.x - lerp(28, 48, progress), points.gate.y, 1, 0);
  setGroupTransform(passageRight, points.gate.x + lerp(28, 48, progress), points.gate.y, 1, 0);

  setOpacity(candidateArch, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateTruss, clamp(0.05 - progress * 0.08, 0, 1));
  setOpacity(candidateCable, clamp(0.12 - progress * 0.14, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotLeft, slotState(loopProgress, 0.16));
  setOpacity(slotCrown, slotState(loopProgress, 0.38));
  setOpacity(slotRight, slotState(loopProgress, 0.58));

  setGroupTransform(deckLeft, system.left.x, system.left.y, lerp(0.88, 1, easeOut(leftReveal)), 0);
  setGroupTransform(deckCrown, system.crown.x, system.crown.y, lerp(0.88, 1, easeOut(crownReveal)), 0);
  setGroupTransform(deckRight, system.right.x, system.right.y, lerp(0.88, 1, easeOut(rightReveal)), 0);
  setOpacity(deckLeft, leftReveal);
  setOpacity(deckCrown, crownReveal);
  setOpacity(deckRight, rightReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.64) * 1.4, 0, 0.18));
  setOpacity(resolutionRing, clamp((progress - 0.72) * 1.6, 0, 0.22));
  setOpacity(memoryArc, clamp((progress - 0.78) * 1.5, 0, 0.14));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(bridgeLoopBase, lerp(0.24, 0.12, settle));
  setPathWindow(bridgeLoopActive, BRIDGE_LOOP_LENGTH, BRIDGE_LOOP_LENGTH, lerp(1, 0.14, settle));
  setOpacity(bridgeBaseTop, lerp(0.28, 0.48, settle));
  setOpacity(bridgeBaseBottom, lerp(0.22, 0.38, settle));

  [passageTop, passageBottom, passageLeft, passageRight, passageHalo].forEach((element) => setOpacity(element, 0));
  [candidateArch, candidateTruss, candidateCable, slotLeft, slotCrown, slotRight].forEach((element) =>
    setOpacity(element, 0),
  );

  setGroupTransform(
    deckLeft,
    lerp(system.left.x, system.settleLeft.x, settle),
    lerp(system.left.y, system.settleLeft.y, settle),
    0.96,
    0,
  );
  setGroupTransform(
    deckCrown,
    lerp(system.crown.x, system.settleCrown.x, settle),
    lerp(system.crown.y, system.settleCrown.y, settle),
    0.97,
    0,
  );
  setGroupTransform(
    deckRight,
    lerp(system.right.x, system.settleRight.x, settle),
    lerp(system.right.y, system.settleRight.y, settle),
    0.96,
    0,
  );
  setOpacity(deckLeft, 0.92);
  setOpacity(deckCrown, 0.92);
  setOpacity(deckRight, 0.92);

  setOpacity(resolutionHalo, lerp(0.18, 0.3, settle));
  setOpacity(resolutionRing, lerp(0.22, 0.88, settle));
  setOpacity(memoryArc, lerp(0.14, 0.58, settle));
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

  if (state.playing) {
    state.currentElapsed = elapsed;
  } else {
    state.currentElapsed = elapsed;
  }

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
