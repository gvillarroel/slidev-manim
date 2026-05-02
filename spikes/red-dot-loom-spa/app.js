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
const warpField = document.getElementById("warp-field");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");
const shedOutline = document.getElementById("shed-outline");
const combTop = document.getElementById("comb-top");
const combBottom = document.getElementById("comb-bottom");
const pressureHalo = document.getElementById("pressure-halo");
const weaveBase = document.getElementById("weave-base");
const weaveActive = document.getElementById("weave-active");
const slotTop = document.getElementById("slot-top");
const slotRight = document.getElementById("slot-right");
const slotBottom = document.getElementById("slot-bottom");
const slotLeft = document.getElementById("slot-left");
const bandTop = document.getElementById("band-top");
const bandRight = document.getElementById("band-right");
const bandBottom = document.getElementById("band-bottom");
const bandLeft = document.getElementById("band-left");
const memorySeamTop = document.getElementById("memory-seam-top");
const memorySeamBottom = document.getElementById("memory-seam-bottom");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const WEAVE_LENGTH = weaveActive.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
  darkGray: "#4f4f4f",
};

const points = {
  start: { x: 304, y: 450 },
  ingress: { x: 562, y: 450 },
  candidateA: { x: 646, y: 336 },
  candidateB: { x: 848, y: 322 },
  candidateC: { x: 1000, y: 400 },
  gateApproach: { x: 926, y: 450 },
  gate: { x: 820, y: 450 },
};

const weave = {
  top: { x: 820, y: 332 },
  right: { x: 936, y: 450 },
  bottom: { x: 820, y: 568 },
  left: { x: 704, y: 450 },
  settleTop: { x: 820, y: 316 },
  settleRight: { x: 956, y: 450 },
  settleBottom: { x: 820, y: 584 },
  settleLeft: { x: 684, y: 450 },
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

function pointOnWeave(progress) {
  const length = clamp(progress, 0, 1) * WEAVE_LENGTH;
  const point = weaveActive.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function slotState(progress, threshold) {
  if (progress < threshold) {
    return clamp(progress / Math.max(threshold, 0.001), 0, 1) * 0.36;
  }
  return clamp(1 - (progress - threshold) / 0.18, 0, 1) * 0.36;
}

function bandReveal(progress, threshold) {
  return clamp((progress - threshold) / 0.16, 0, 1);
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
    search: 34,
    tension: 8,
    transformation: 4,
    resolution: -2,
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
    appearance: { x: 118, y: 150, width: 1090, height: 630 },
    search: { x: 154, y: 144, width: 1106, height: 632 },
    tension: { x: 326, y: 158, width: 962, height: 606 },
    transformation: { x: 384, y: 154, width: 896, height: 618 },
    resolution: { x: 392, y: 138, width: 896, height: 646 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -18) translate(800 450) scale(1.035) translate(-800 -450)",
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
  setOpacity(warpField, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => {
    guide.setAttribute("stroke", COLORS.lineGray);
    setOpacity(guide, 0);
  });

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, 1, 0);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, 1, 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, 1, 0);
  [candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));

  setOpacity(shedOutline, 0);
  setGroupTransform(combTop, points.gate.x, 338, 1, 0);
  setGroupTransform(combBottom, points.gate.x, 562, 1, 0);
  setOpacity(combTop, 0);
  setOpacity(combBottom, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(weaveBase, 0);
  setPathWindow(weaveActive, WEAVE_LENGTH, 0, 0);

  setGroupTransform(slotTop, weave.top.x, weave.top.y, 1, 0);
  setGroupTransform(slotRight, weave.right.x, weave.right.y, 1, 0);
  setGroupTransform(slotBottom, weave.bottom.x, weave.bottom.y, 1, 0);
  setGroupTransform(slotLeft, weave.left.x, weave.left.y, 1, 0);
  [slotTop, slotRight, slotBottom, slotLeft].forEach((element) => setOpacity(element, 0));

  setGroupTransform(bandTop, weave.top.x, weave.top.y, 1, 0);
  setGroupTransform(bandRight, weave.right.x, weave.right.y, 1, 0);
  setGroupTransform(bandBottom, weave.bottom.x, weave.bottom.y, 1, 0);
  setGroupTransform(bandLeft, weave.left.x, weave.left.y, 1, 0);
  [bandTop, bandRight, bandBottom, bandLeft].forEach((element) => setOpacity(element, 0));

  setOpacity(memorySeamTop, 0);
  setOpacity(memorySeamBottom, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.82);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(18, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.24 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.12) * 1.5, 0, 0.34));
  setOpacity(warpField, clamp((progress - 0.34) * 1.1, 0, 0.2));

  const preview = clamp((progress - 0.46) * 1.8, 0, 1);
  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(candidateA, preview * 0.16);
  setOpacity(candidateB, preview * 0.1);
  setOpacity(candidateC, preview * 0.08);
  setOpacity(shedOutline, preview * 0.08);
  setOpacity(combTop, preview * 0.05);
  setOpacity(combBottom, preview * 0.05);
  setOpacity(pressureHalo, preview * 0.06);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.26, from: points.ingress, to: points.candidateA },
    { start: 0.26, end: 0.56, from: points.candidateA, to: points.candidateB },
    { start: 0.56, end: 0.82, from: points.candidateB, to: points.candidateC },
    { start: 0.82, end: 1, from: points.candidateC, to: points.gateApproach },
  ]);

  setDot(position, 18, 88, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.24, 0.08, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.04, progress));
  setOpacity(warpField, lerp(0.24, 0.34, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.48) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.28 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.28 && progress < 0.58 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.58 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.22 + revealA * 0.22);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.1 + revealC * 0.24);

  const activeA = progress < 0.28 ? 1 : 0;
  const activeB = progress >= 0.28 && progress < 0.58 ? 1 : 0;
  const activeC = progress >= 0.58 ? 1 : 0;

  setGroupTransform(candidateA, points.candidateA.x, points.candidateA.y, lerp(0.88, activeA ? 1.04 : 0.96, revealA), -3);
  setGroupTransform(candidateB, points.candidateB.x, points.candidateB.y, lerp(0.88, activeB ? 1.04 : 0.96, revealB), 0);
  setGroupTransform(candidateC, points.candidateC.x, points.candidateC.y, lerp(0.88, activeC ? 1.04 : 0.96, revealC), 3);
  setOpacity(candidateA, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateB, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateC, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(shedOutline, 0.16);
  setOpacity(combTop, 0.08);
  setOpacity(combBottom, 0.08);
  setOpacity(pressureHalo, 0.08);
}

function renderTension(progress) {
  const travel = clamp(progress / 0.42, 0, 1);
  const position = mixPoint(points.gateApproach, points.gate, easeInOut(travel));
  const compression = Math.sin(clamp(progress / 0.82, 0, 1) * Math.PI);
  const topY = lerp(338, 390, easeInOut(clamp(progress / 0.68, 0, 1)));
  const bottomY = lerp(562, 510, easeInOut(clamp(progress / 0.68, 0, 1)));
  const collapse = clamp(progress / 0.74, 0, 1);

  setDot(
    position,
    lerp(18, 17, progress),
    lerp(88, 122, progress),
    1,
    0.22 + pulseWave(progress, 2.2) * 0.1,
    lerp(1, 1.68, compression),
    lerp(1, 0.58, compression),
  );
  setOpacity(narrativeSpine, lerp(0.1, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.04, 0, progress));
  setOpacity(warpField, lerp(0.34, 0.5, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(0.18, 0, progress));
  });

  const candidateATarget = mixPoint(points.candidateA, { x: 738, y: 374 }, collapse);
  const candidateBTarget = mixPoint(points.candidateB, { x: 820, y: 346 }, collapse);
  const candidateCTarget = mixPoint(points.candidateC, { x: 904, y: 386 }, collapse);
  setGroupTransform(candidateA, candidateATarget.x, candidateATarget.y, lerp(0.96, 0.72, collapse), -4);
  setGroupTransform(candidateB, candidateBTarget.x, candidateBTarget.y, lerp(0.96, 0.68, collapse), 0);
  setGroupTransform(candidateC, candidateCTarget.x, candidateCTarget.y, lerp(0.96, 0.72, collapse), 4);
  setOpacity(candidateA, lerp(0.3, 0.08, collapse));
  setOpacity(candidateB, lerp(0.28, 0.06, collapse));
  setOpacity(candidateC, lerp(1, 0.12, collapse));

  setOpacity(shedOutline, clamp((progress - 0.04) * 1.7, 0, 1));
  setOpacity(combTop, clamp((progress - 0.02) * 1.6, 0, 1));
  setOpacity(combBottom, clamp((progress - 0.02) * 1.6, 0, 1));
  setOpacity(pressureHalo, clamp((progress - 0.08) * 1.5, 0, 0.44));
  setGroupTransform(combTop, points.gate.x, topY, 1, 0);
  setGroupTransform(combBottom, points.gate.x, bottomY, 1, 0);

  setOpacity(slotTop, clamp((progress - 0.42) * 1.2, 0, 0.2));
  setOpacity(slotRight, clamp((progress - 0.52) * 1.2, 0, 0.2));
  setOpacity(slotBottom, clamp((progress - 0.62) * 1.2, 0, 0.2));
  setOpacity(slotLeft, clamp((progress - 0.72) * 1.2, 0, 0.2));
}

function renderTransformation(progress) {
  const routeProgress = easeInOut(clamp(progress / 0.9, 0, 1));
  const position = pointOnWeave(routeProgress);

  setDot(position, 16, 96, 1, 0.22 + pulseWave(progress, 2.1) * 0.08);
  setOpacity(narrativeSpine, 0);
  setOpacity(warpField, lerp(0.5, 0.22, progress));

  setOpacity(weaveBase, lerp(0.08, 0.28, routeProgress));
  setPathWindow(weaveActive, WEAVE_LENGTH, WEAVE_LENGTH * routeProgress, 1);

  setOpacity(shedOutline, lerp(1, 0.06, progress));
  setOpacity(combTop, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(combBottom, clamp(1 - progress * 1.1, 0, 1));
  setOpacity(pressureHalo, clamp(0.44 - progress * 0.52, 0, 1));
  setGroupTransform(combTop, points.gate.x, lerp(390, 370, progress), 1, 0);
  setGroupTransform(combBottom, points.gate.x, lerp(510, 530, progress), 1, 0);

  [candidateA, candidateB, candidateC].forEach((element) => setOpacity(element, 0));
  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setOpacity(slotTop, slotState(routeProgress, 0.18));
  setOpacity(slotRight, slotState(routeProgress, 0.42));
  setOpacity(slotBottom, slotState(routeProgress, 0.64));
  setOpacity(slotLeft, slotState(routeProgress, 0.84));

  const topReveal = bandReveal(routeProgress, 0.18);
  const rightReveal = bandReveal(routeProgress, 0.42);
  const bottomReveal = bandReveal(routeProgress, 0.64);
  const leftReveal = bandReveal(routeProgress, 0.84);

  setGroupTransform(bandTop, weave.top.x, weave.top.y, lerp(0.88, 1, easeOut(topReveal)), 0);
  setGroupTransform(bandRight, weave.right.x, weave.right.y, lerp(0.88, 1, easeOut(rightReveal)), 0);
  setGroupTransform(bandBottom, weave.bottom.x, weave.bottom.y, lerp(0.88, 1, easeOut(bottomReveal)), 0);
  setGroupTransform(bandLeft, weave.left.x, weave.left.y, lerp(0.88, 1, easeOut(leftReveal)), 0);
  setOpacity(bandTop, topReveal);
  setOpacity(bandRight, rightReveal);
  setOpacity(bandBottom, bottomReveal);
  setOpacity(bandLeft, leftReveal);

  setOpacity(memorySeamTop, clamp((progress - 0.72) * 1.4, 0, 0.16));
  setOpacity(memorySeamBottom, clamp((progress - 0.78) * 1.4, 0, 0.16));
  setOpacity(resolutionFrame, clamp((progress - 0.7) * 1.4, 0, 0.22));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setDot(points.gate, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(warpField, lerp(0.16, 0.1, settle));

  [
    searchGuideA,
    searchGuideB,
    searchGuideC,
    candidateA,
    candidateB,
    candidateC,
    shedOutline,
    combTop,
    combBottom,
    pressureHalo,
    slotTop,
    slotRight,
    slotBottom,
    slotLeft,
  ].forEach((element) => setOpacity(element, 0));

  setOpacity(weaveBase, lerp(0.28, 0.36, settle));
  setPathWindow(weaveActive, WEAVE_LENGTH, WEAVE_LENGTH, lerp(1, 0.12, settle));

  setGroupTransform(
    bandTop,
    lerp(weave.top.x, weave.settleTop.x, settle),
    lerp(weave.top.y, weave.settleTop.y, settle),
    0.98,
    0,
  );
  setGroupTransform(
    bandRight,
    lerp(weave.right.x, weave.settleRight.x, settle),
    lerp(weave.right.y, weave.settleRight.y, settle),
    0.98,
    0,
  );
  setGroupTransform(
    bandBottom,
    lerp(weave.bottom.x, weave.settleBottom.x, settle),
    lerp(weave.bottom.y, weave.settleBottom.y, settle),
    0.98,
    0,
  );
  setGroupTransform(
    bandLeft,
    lerp(weave.left.x, weave.settleLeft.x, settle),
    lerp(weave.left.y, weave.settleLeft.y, settle),
    0.98,
    0,
  );
  [bandTop, bandRight, bandBottom, bandLeft].forEach((element) => setOpacity(element, 0.94));

  setOpacity(memorySeamTop, lerp(0.16, 0.22, settle));
  setOpacity(memorySeamBottom, lerp(0.16, 0.22, settle));
  setOpacity(resolutionFrame, lerp(0.22, 0.82, settle));
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
