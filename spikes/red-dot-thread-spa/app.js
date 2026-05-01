const TOTAL_DURATION = 34_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 8_000 },
];

const svg = document.getElementById("stage");
const layoutRoot = document.getElementById("layout-root");
const phaseLabel = document.getElementById("phase-label");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");
const loomLineA = document.getElementById("loom-line-a");
const loomLineB = document.getElementById("loom-line-b");
const gateHalo = document.getElementById("gate-halo");
const gateShell = document.getElementById("gate-shell");
const gateLeft = document.getElementById("gate-left");
const gateRight = document.getElementById("gate-right");
const threadBase = document.getElementById("thread-base");
const threadActive = document.getElementById("thread-active");
const slotA = document.getElementById("slot-a");
const slotB = document.getElementById("slot-b");
const slotC = document.getElementById("slot-c");
const cardA = document.getElementById("card-a");
const cardB = document.getElementById("card-b");
const cardC = document.getElementById("card-c");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const memoryArc = document.getElementById("memory-arc");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const THREAD_LENGTH = threadActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  darkGray: "#4f4f4f",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 320, y: 450 },
  ingress: { x: 566, y: 450 },
  candidateA: { x: 646, y: 314 },
  candidateB: { x: 824, y: 258 },
  candidateC: { x: 1044, y: 428 },
  gate: { x: 824, y: 450 },
};

const system = {
  slotA: { x: 646, y: 320 },
  slotB: { x: 1046, y: 398 },
  slotC: { x: 706, y: 646 },
  cardA: { x: 646, y: 320 },
  cardB: { x: 1046, y: 398 },
  cardC: { x: 706, y: 646 },
  settleA: { x: 666, y: 334 },
  settleB: { x: 1016, y: 410 },
  settleC: { x: 726, y: 622 },
};

const state = {
  playing: true,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
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

function pointOnThread(progress) {
  const length = clamp(progress, 0, 1) * THREAD_LENGTH;
  const point = threadActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.42;
  }
  return clamp(1 - (progress - threshold) / 0.16, 0, 1) * 0.42;
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

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 110, width: 1140 },
    search: { x: 170, width: 1060 },
    tension: { x: 330, width: 920 },
    transformation: { x: 420, width: 780 },
    resolution: { x: 450, width: 720 },
  };
  const frame = frames[phaseId] ?? { x: 0, width: 1600 };
  svg.setAttribute("viewBox", `${frame.x} 0 ${frame.width} 900`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -18) translate(800 450) scale(1.04) translate(-800 -450)",
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

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, 1, 0);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, 1, 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, 1, 0);
  [candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  [loomLineA, loomLineB, gateHalo, gateShell, gateLeft, gateRight].forEach((element) => setOpacity(element, 0));
  setGroupTransform(gateLeft, points.gate.x - 88, points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + 88, points.gate.y, 1, 0);

  [slotA, slotB, slotC].forEach((element) => setOpacity(element, 0));
  setGroupTransform(slotA, system.slotA.x, system.slotA.y, 1, 0);
  setGroupTransform(slotB, system.slotB.x, system.slotB.y, 1, 0);
  setGroupTransform(slotC, system.slotC.x, system.slotC.y, 1, 0);

  [cardA, cardB, cardC].forEach((element) => setOpacity(element, 0));
  setGroupTransform(cardA, system.cardA.x, system.cardA.y, 1, 0);
  setGroupTransform(cardB, system.cardB.x, system.cardB.y, 1, 0);
  setGroupTransform(cardC, system.cardC.x, system.cardC.y, 1, 0);

  setPathWindow(threadActive, THREAD_LENGTH, 0, 0);
  setOpacity(threadBase, 0);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRing, 0);
  setOpacity(memoryArc, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 84, eased),
    clamp(progress * 1.8, 0, 1),
    0.26 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.14) * 1.4, 0, 0.34));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  const preview = clamp((progress - 0.46) * 1.6, 0, 1);
  setOpacity(searchGuideA, preview * 0.16);
  setOpacity(candidateA, preview * 0.12);
  setOpacity(candidateB, preview * 0.08);
  setOpacity(candidateC, preview * 0.05);
  setOpacity(gateHalo, preview * 0.14);
  setOpacity(gateShell, preview * 0.18);
  setOpacity(gateLeft, preview * 0.16);
  setOpacity(gateRight, preview * 0.16);
  setGroupTransform(gateLeft, points.gate.x - 88, points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + 88, points.gate.y, 1, 0);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.3, from: points.ingress, to: points.candidateA },
    { start: 0.3, end: 0.58, from: points.candidateA, to: points.candidateB },
    { start: 0.58, end: 0.84, from: points.candidateB, to: points.candidateC },
    { start: 0.84, end: 1, from: points.candidateC, to: { x: 960, y: 438 } },
  ]);

  setDot(position, 18, 84, 1, 0.24 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.12, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, lerp(60, 220, progress), 0.72);

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.24) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.52) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.32 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.32 && progress < 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.62 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.26 + revealA * 0.18);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.08 + revealC * 0.26);

  const activeA = progress < 0.32 ? 1 : 0;
  const activeB = progress >= 0.32 && progress < 0.62 ? 1 : 0;
  const activeC = progress >= 0.62 ? 1 : 0;

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), 0);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, lerp(0.82, activeC ? 1.03 : 0.95, revealC), 0);
  setOpacity(candidateA, activeA ? 1 : revealA * 0.32 + 0.18);
  setOpacity(candidateB, activeB ? 1 : revealB * 0.32 + 0.14);
  setOpacity(candidateC, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(gateHalo, 0.08);
  setOpacity(gateShell, 0.12);
  setOpacity(gateLeft, 0.12);
  setOpacity(gateRight, 0.12);
  setGroupTransform(gateLeft, points.gate.x - 84, points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + 84, points.gate.y, 1, 0);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.candidateC, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const gateGap = lerp(88, 28, easeInOut(clamp(progress / 0.68, 0, 1)));
  const collapse = clamp(progress / 0.72, 0, 1);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(84, 108, progress),
    1,
    0.26 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 0.66, compression),
    lerp(1, 1.58, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.04, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, lerp(220, 320, progress), lerp(0.72, 0.18, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const candidateAPosition = mixPoint(points.candidateA, { x: 732, y: 382 }, collapse);
  const candidateBPosition = mixPoint(points.candidateB, { x: 824, y: 348 }, collapse);
  const candidateCPosition = mixPoint(points.candidateC, { x: 914, y: 440 }, collapse);

  setGroupTransform(candidateA, candidateAPosition.x, candidateAPosition.y, lerp(0.96, 0.74, collapse), lerp(0, -10, collapse));
  setGroupTransform(candidateB, candidateBPosition.x, candidateBPosition.y, lerp(0.96, 0.72, collapse), 0);
  setGroupTransform(candidateC, candidateCPosition.x, candidateCPosition.y, lerp(0.95, 0.66, collapse), lerp(0, 8, collapse));
  setOpacity(candidateA, lerp(0.34, 0.06, collapse));
  setOpacity(candidateB, lerp(0.3, 0.05, collapse));
  setOpacity(candidateC, lerp(1, 0.12, collapse));

  setOpacity(loomLineA, clamp((progress - 0.1) * 1.7, 0, 0.56));
  setOpacity(loomLineB, clamp((progress - 0.16) * 1.7, 0, 0.56));
  setOpacity(gateHalo, clamp((progress - 0.04) * 1.5, 0, 0.44));
  setOpacity(gateShell, clamp((progress - 0.06) * 1.6, 0, 0.68));
  setOpacity(gateLeft, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(gateRight, clamp((progress - 0.04) * 1.7, 0, 1));
  setGroupTransform(gateLeft, points.gate.x - gateGap, points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + gateGap, points.gate.y, 1, 0);

  setOpacity(slotA, clamp((progress - 0.4) * 1.4, 0, 0.28));
  setOpacity(slotB, clamp((progress - 0.48) * 1.4, 0, 0.3));
  setOpacity(slotC, clamp((progress - 0.56) * 1.4, 0, 0.3));
}

function renderTransformation(progress) {
  const threadProgress = easeInOut(clamp(progress / 0.86, 0, 1));
  const position = pointOnThread(threadProgress);
  const cardAReveal = cardState(threadProgress, 0.18);
  const cardBReveal = cardState(threadProgress, 0.5);
  const cardCReveal = cardState(threadProgress, 0.78);

  setDot(position, 16, 92, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(threadBase, lerp(0.08, 0.22, threadProgress));
  setPathWindow(threadActive, THREAD_LENGTH, THREAD_LENGTH * threadProgress, 1);

  setOpacity(loomLineA, lerp(0.56, 0.08, progress));
  setOpacity(loomLineB, lerp(0.56, 0.08, progress));
  setOpacity(gateHalo, clamp(0.44 - progress * 0.46, 0, 1));
  setOpacity(gateShell, clamp(0.68 - progress * 0.78, 0, 1));
  setOpacity(gateLeft, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(gateRight, clamp(1 - progress * 1.1, 0, 1));
  setGroupTransform(gateLeft, points.gate.x - lerp(28, 48, progress), points.gate.y, 1, 0);
  setGroupTransform(gateRight, points.gate.x + lerp(28, 48, progress), points.gate.y, 1, 0);

  setOpacity(candidateA, clamp(0.06 - progress * 0.08, 0, 1));
  setOpacity(candidateB, clamp(0.05 - progress * 0.07, 0, 1));
  setOpacity(candidateC, clamp(0.12 - progress * 0.14, 0, 1));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotA, slotState(threadProgress, 0.18));
  setOpacity(slotB, slotState(threadProgress, 0.5));
  setOpacity(slotC, slotState(threadProgress, 0.78));

  setGroupTransform(cardA, system.cardA.x, system.cardA.y, lerp(0.88, 1, easeOut(cardAReveal)), 0);
  setGroupTransform(cardB, system.cardB.x, system.cardB.y, lerp(0.88, 1, easeOut(cardBReveal)), 0);
  setGroupTransform(cardC, system.cardC.x, system.cardC.y, lerp(0.88, 1, easeOut(cardCReveal)), 0);
  setOpacity(cardA, cardAReveal);
  setOpacity(cardB, cardBReveal);
  setOpacity(cardC, cardCReveal);

  setOpacity(resolutionHalo, clamp((progress - 0.62) * 1.4, 0, 0.18));
  setOpacity(resolutionRing, clamp((progress - 0.7) * 1.6, 0, 0.24));
  setOpacity(memoryArc, clamp((progress - 0.72) * 1.5, 0, 0.2));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 94, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  setOpacity(threadBase, lerp(0.22, 0.44, settle));
  setPathWindow(threadActive, THREAD_LENGTH, THREAD_LENGTH, lerp(1, 0.24, settle));

  setOpacity(loomLineA, 0);
  setOpacity(loomLineB, 0);
  setOpacity(gateHalo, 0);
  setOpacity(gateShell, 0);
  setOpacity(gateLeft, 0);
  setOpacity(gateRight, 0);
  [candidateA, candidateB, candidateC, slotA, slotB, slotC].forEach((element) => setOpacity(element, 0));

  setGroupTransform(cardA, lerp(system.cardA.x, system.settleA.x, settle), lerp(system.cardA.y, system.settleA.y, settle), 0.96, 0);
  setGroupTransform(cardB, lerp(system.cardB.x, system.settleB.x, settle), lerp(system.cardB.y, system.settleB.y, settle), 0.97, 0);
  setGroupTransform(cardC, lerp(system.cardC.x, system.settleC.x, settle), lerp(system.cardC.y, system.settleC.y, settle), 0.96, 0);
  setOpacity(cardA, 0.92);
  setOpacity(cardB, 0.92);
  setOpacity(cardC, 0.92);

  setOpacity(resolutionHalo, lerp(0.18, 0.3, settle));
  setOpacity(resolutionRing, lerp(0.24, 0.88, settle));
  setOpacity(memoryArc, lerp(0.2, 0.56, settle));
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
  const elapsed = state.playing
    ? (state.elapsedBeforePause + (now - state.startAt)) % TOTAL_DURATION
    : state.elapsedBeforePause;

  if (state.playing) {
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
  getState() {
    const info = phaseForElapsed(state.currentElapsed);
    return {
      currentElapsed: state.currentElapsed,
      totalDuration: TOTAL_DURATION,
      phase: info.phase.id,
      totalProgress: info.totalProgress,
      localProgress: info.localProgress,
      playing: state.playing,
    };
  },
};

applyLayout();
window.addEventListener("resize", applyLayout);
resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
