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
const candidateSling = document.getElementById("candidate-sling");
const candidateHook = document.getElementById("candidate-hook");
const candidateCup = document.getElementById("candidate-cup");

const tensionHalo = document.getElementById("tension-halo");
const topLatch = document.getElementById("top-latch");
const suspensionLine = document.getElementById("suspension-line");
const bowlGuide = document.getElementById("bowl-guide");
const leftPad = document.getElementById("left-pad");
const rightPad = document.getElementById("right-pad");

const leftArm = document.getElementById("left-arm");
const baseArc = document.getElementById("base-arc");
const rightArm = document.getElementById("right-arm");
const activeLeft = document.getElementById("active-left");
const activeBase = document.getElementById("active-base");
const activeRight = document.getElementById("active-right");
const activeLeftPath = document.getElementById("active-left-path");
const activeBasePath = document.getElementById("active-base-path");
const activeRightPath = document.getElementById("active-right-path");

const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ACTIVE_LEFT_LENGTH = activeLeftPath.getTotalLength();
const ACTIVE_BASE_LENGTH = activeBasePath.getTotalLength();
const ACTIVE_RIGHT_LENGTH = activeRightPath.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 302, y: 454 },
  entry: { x: 558, y: 454 },
  sling: { x: 688, y: 392 },
  hook: { x: 846, y: 360 },
  cup: { x: 992, y: 432 },
  mouth: { x: 886, y: 408 },
  tether: { x: 846, y: 422 },
  release: { x: 846, y: 438 },
  center: { x: 846, y: 468 },
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

function rangedProgress(progress, start, end) {
  return clamp((progress - start) / (end - start), 0, 1);
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

function setGroupTransform(element, x, y, scale = 1, rotate = 0, scaleY = scale) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${rotate.toFixed(2)}) scale(${scale.toFixed(3)} ${scaleY.toFixed(3)})`,
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
    appearance: 8,
    search: 18,
    tension: 14,
    transformation: 8,
    resolution: 0,
  };
  sceneRoot.setAttribute("transform", `translate(0 ${offsets[phaseId] ?? 0})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 120, y: 142, width: 1118, height: 644 },
    search: { x: 170, y: 128, width: 1134, height: 662 },
    tension: { x: 586, y: 114, width: 520, height: 736 },
    transformation: { x: 572, y: 96, width: 548, height: 772 },
    resolution: { x: 618, y: 104, width: 456, height: 756 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -12) translate(800 450) scale(1.05) translate(-800 -450)",
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

  setGroupTransform(candidateSling, points.sling.x, points.sling.y, 1, 0);
  setGroupTransform(candidateHook, points.hook.x, points.hook.y, 1, 0);
  setGroupTransform(candidateCup, points.cup.x, points.cup.y, 1, 0);
  [candidateSling, candidateHook, candidateCup].forEach((candidate) => setOpacity(candidate, 0));

  setEllipseRadius(tensionHalo, 156, 118);
  setGroupTransform(topLatch, points.center.x, points.center.y, 1, 0);
  setGroupTransform(suspensionLine, points.center.x, points.center.y, 1, 0);
  setGroupTransform(bowlGuide, points.center.x, points.center.y, 0.78, 0, 0.82);
  setGroupTransform(leftPad, points.center.x, points.center.y, 0.76, 0);
  setGroupTransform(rightPad, points.center.x, points.center.y, 0.76, 0);
  [tensionHalo, topLatch, suspensionLine, bowlGuide, leftPad, rightPad].forEach((element) => setOpacity(element, 0));

  setGroupTransform(leftArm, points.center.x, points.center.y, 0.78, 0);
  setGroupTransform(baseArc, points.center.x, points.center.y, 0.78, 0, 0.82);
  setGroupTransform(rightArm, points.center.x, points.center.y, 0.78, 0);
  setGroupTransform(activeLeft, points.center.x, points.center.y, 0.78, 0);
  setGroupTransform(activeBase, points.center.x, points.center.y, 0.78, 0, 0.82);
  setGroupTransform(activeRight, points.center.x, points.center.y, 0.78, 0);
  [leftArm, baseArc, rightArm, activeLeft, activeBase, activeRight].forEach((element) => setOpacity(element, 0));
  setPathWindow(activeLeftPath, ACTIVE_LEFT_LENGTH, 0, 0);
  setPathWindow(activeBasePath, ACTIVE_BASE_LENGTH, 0, 0);
  setPathWindow(activeRightPath, ACTIVE_RIGHT_LENGTH, 0, 0);

  setEllipseRadius(resolutionHalo, 154, 158);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionRing, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.entry, eased * 0.92);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(16, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.2) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.06) * 1.6, 0, 0.42));

  const preview = clamp((progress - 0.34) * 1.9, 0, 1);
  setOpacity(searchGuideA, preview * 0.2);
  setOpacity(candidateSling, preview * 0.22);
  setOpacity(candidateHook, preview * 0.14);
  setOpacity(candidateCup, preview * 0.12);
  setOpacity(bowlGuide, preview * 0.1);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.entry, to: points.sling },
    { start: 0.24, end: 0.52, from: points.sling, to: points.hook },
    { start: 0.52, end: 0.82, from: points.hook, to: points.cup },
    { start: 0.82, end: 1, from: points.cup, to: points.mouth },
  ]);

  setDot(position, 18, 84, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.3, 0.14, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.24, 0.1, progress));

  const revealA = clamp(progress / 0.22, 0, 1);
  const revealB = clamp((progress - 0.22) / 0.22, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.22, 0, 1);

  searchGuideA.setAttribute("stroke", progress < 0.28 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideB.setAttribute("stroke", progress >= 0.28 && progress < 0.6 ? COLORS.primaryRed : COLORS.lineGray);
  searchGuideC.setAttribute("stroke", progress >= 0.6 ? COLORS.primaryRed : COLORS.lineGray);
  setOpacity(searchGuideA, 0.2 + revealA * 0.22);
  setOpacity(searchGuideB, 0.12 + revealB * 0.22);
  setOpacity(searchGuideC, 0.1 + revealC * 0.24);

  const activeA = progress < 0.28 ? 1 : 0;
  const activeB = progress >= 0.28 && progress < 0.6 ? 1 : 0;
  const activeC = progress >= 0.6 ? 1 : 0;

  setGroupTransform(candidateSling, points.sling.x, points.sling.y, lerp(0.9, activeA ? 1.06 : 0.98, revealA), -2);
  setGroupTransform(candidateHook, points.hook.x, points.hook.y, lerp(0.9, activeB ? 1.05 : 0.98, revealB), 0);
  setGroupTransform(candidateCup, points.cup.x, points.cup.y, lerp(0.9, activeC ? 1.05 : 0.98, revealC), 4);
  setOpacity(candidateSling, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateHook, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateCup, activeC ? 1 : revealC * 0.34 + 0.12);

  setOpacity(bowlGuide, 0.08);
  setOpacity(suspensionLine, 0.06);
}

function renderTension(progress) {
  const ingress = easeInOut(clamp(progress / 0.26, 0, 1));
  const compression = clamp((progress - 0.34) / 0.26, 0, 1);
  const position = mixPoint(points.mouth, points.tether, ingress);
  const supportScale = lerp(0.76, 1, easeInOut(clamp((progress - 0.12) / 0.34, 0, 1)));

  setDot(
    position,
    lerp(18, 17, progress),
    lerp(84, 108, progress),
    1,
    0.24 + pulseWave(progress, 2) * 0.1,
    lerp(1, 0.74, compression),
    lerp(1, 1.18, compression),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.1, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.18 : 0.12, 0, progress));
  });

  setGroupTransform(candidateSling, lerp(points.sling.x, 730, progress), lerp(points.sling.y, 438, progress), lerp(0.98, 0.76, progress), -8);
  setGroupTransform(candidateHook, lerp(points.hook.x, 846, progress), lerp(points.hook.y, 360, progress), lerp(0.98, 0.74, progress), 0);
  setGroupTransform(candidateCup, lerp(points.cup.x, 962, progress), lerp(points.cup.y, 458, progress), lerp(1, 0.78, progress), 8);
  setOpacity(candidateSling, lerp(0.26, 0.04, progress));
  setOpacity(candidateHook, lerp(0.22, 0.04, progress));
  setOpacity(candidateCup, lerp(0.74, 0.06, progress));

  setEllipseRadius(tensionHalo, lerp(156, 166, progress), lerp(118, 130, progress));
  setOpacity(tensionHalo, clamp((progress - 0.02) * 1.6, 0, 0.24));
  setGroupTransform(topLatch, points.center.x, points.center.y, 1, 0);
  setGroupTransform(suspensionLine, points.center.x, points.center.y, 1, 0);
  setGroupTransform(bowlGuide, points.center.x, points.center.y, supportScale, 0, lerp(0.82, 1, progress));
  setGroupTransform(leftPad, points.center.x, points.center.y, supportScale, 0);
  setGroupTransform(rightPad, points.center.x, points.center.y, supportScale, 0);
  setOpacity(topLatch, clamp((progress - 0.08) * 1.8, 0, 0.9));
  setOpacity(suspensionLine, clamp((progress - 0.02) * 1.8, 0, 0.82));
  setOpacity(bowlGuide, clamp((progress - 0.12) * 1.8, 0, 0.82));
  setOpacity(leftPad, clamp((progress - 0.18) * 1.8, 0, 0.96));
  setOpacity(rightPad, clamp((progress - 0.18) * 1.8, 0, 0.96));
}

function renderTransformation(progress) {
  const hold = rangedProgress(progress, 0, 0.3);
  const release = rangedProgress(progress, 0.3, 1);
  const leftReveal = easeInOut(rangedProgress(progress, 0.08, 0.34));
  const baseReveal = easeInOut(rangedProgress(progress, 0.28, 0.62));
  const rightReveal = easeInOut(rangedProgress(progress, 0.5, 0.84));
  const activeLeftReveal = easeInOut(rangedProgress(progress, 0.1, 0.32));
  const activeBaseReveal = easeInOut(rangedProgress(progress, 0.3, 0.58));
  const activeRightReveal = easeInOut(rangedProgress(progress, 0.54, 0.8));

  const route =
    progress <= 0.3
      ? mixPoint(points.tether, points.release, easeInOut(hold))
      : mixPoint(points.release, points.center, easeInOut(release));

  setDot(
    route,
    17,
    100,
    1,
    0.22 + pulseWave(progress, 1.8) * 0.08,
    lerp(0.76, 1, release || leftReveal),
    lerp(1.16, 1, release || leftReveal),
  );
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);
  [searchGuideA, searchGuideB, searchGuideC, candidateSling, candidateHook, candidateCup].forEach((element) => setOpacity(element, 0));

  setEllipseRadius(tensionHalo, lerp(166, 154, progress), lerp(130, 150, progress));
  setOpacity(tensionHalo, lerp(0.24, 0.12, progress));
  setOpacity(topLatch, lerp(0.9, 0, clamp((progress - 0.16) * 1.5, 0, 1)));
  setOpacity(suspensionLine, lerp(0.82, 0, clamp((progress - 0.2) * 1.6, 0, 1)));
  setGroupTransform(bowlGuide, points.center.x, points.center.y, lerp(1, 0.9, progress), 0, lerp(1, 0.94, progress));
  setOpacity(bowlGuide, lerp(0.82, 0.12, progress));
  setGroupTransform(leftPad, points.center.x, points.center.y, lerp(1, 0.84, progress), 0);
  setGroupTransform(rightPad, points.center.x, points.center.y, lerp(1, 0.84, progress), 0);
  setOpacity(leftPad, lerp(0.96, 0, clamp((progress - 0.14) * 1.5, 0, 1)));
  setOpacity(rightPad, lerp(0.96, 0, clamp((progress - 0.14) * 1.5, 0, 1)));

  setGroupTransform(leftArm, points.center.x, points.center.y, lerp(0.78, 1, leftReveal), 0);
  setGroupTransform(baseArc, points.center.x, points.center.y, lerp(0.78, 1, baseReveal), 0, lerp(0.82, 1, baseReveal));
  setGroupTransform(rightArm, points.center.x, points.center.y, lerp(0.78, 1, rightReveal), 0);
  setGroupTransform(activeLeft, points.center.x, points.center.y, lerp(0.78, 1, leftReveal), 0);
  setGroupTransform(activeBase, points.center.x, points.center.y, lerp(0.78, 1, baseReveal), 0, lerp(0.82, 1, baseReveal));
  setGroupTransform(activeRight, points.center.x, points.center.y, lerp(0.78, 1, rightReveal), 0);

  setOpacity(leftArm, clamp(leftReveal * 1.1, 0, 0.92));
  setOpacity(baseArc, clamp(baseReveal * 1.1, 0, 0.92));
  setOpacity(rightArm, clamp(rightReveal * 1.1, 0, 0.92));
  setOpacity(activeLeft, 1);
  setOpacity(activeBase, 1);
  setOpacity(activeRight, 1);
  setPathWindow(activeLeftPath, ACTIVE_LEFT_LENGTH, ACTIVE_LEFT_LENGTH * activeLeftReveal, activeLeftReveal * 0.96);
  setPathWindow(activeBasePath, ACTIVE_BASE_LENGTH, ACTIVE_BASE_LENGTH * activeBaseReveal, activeBaseReveal * 0.96);
  setPathWindow(activeRightPath, ACTIVE_RIGHT_LENGTH, ACTIVE_RIGHT_LENGTH * activeRightReveal, activeRightReveal * 0.94);

  setOpacity(resolutionHalo, clamp((progress - 0.46) * 1.5, 0, 0.24));
  setOpacity(resolutionRing, clamp((progress - 0.66) * 1.4, 0, 0.18));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.center, 17, 92, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(tensionHalo, 0);
  setOpacity(topLatch, 0);
  setOpacity(suspensionLine, 0);
  setOpacity(bowlGuide, 0);
  setOpacity(leftPad, 0);
  setOpacity(rightPad, 0);

  setGroupTransform(leftArm, points.center.x, points.center.y, lerp(1, 0.94, settle), 0);
  setGroupTransform(baseArc, points.center.x, points.center.y, lerp(1, 0.95, settle), 0, lerp(1, 0.94, settle));
  setGroupTransform(rightArm, points.center.x, points.center.y, lerp(1, 0.94, settle), 0);
  [leftArm, baseArc, rightArm].forEach((element) => setOpacity(element, lerp(0.92, 0.84, settle)));

  setGroupTransform(activeLeft, points.center.x, points.center.y, 0.94, 0);
  setGroupTransform(activeBase, points.center.x, points.center.y, 0.95, 0, 0.94);
  setGroupTransform(activeRight, points.center.x, points.center.y, 0.94, 0);
  setPathWindow(activeLeftPath, ACTIVE_LEFT_LENGTH, ACTIVE_LEFT_LENGTH, lerp(0.16, 0.04, settle));
  setPathWindow(activeBasePath, ACTIVE_BASE_LENGTH, ACTIVE_BASE_LENGTH, lerp(0.14, 0.03, settle));
  setPathWindow(activeRightPath, ACTIVE_RIGHT_LENGTH, ACTIVE_RIGHT_LENGTH, lerp(0.14, 0.03, settle));

  setEllipseRadius(resolutionHalo, 154, 158);
  setOpacity(resolutionHalo, lerp(0.24, 0.34, settle));
  setOpacity(resolutionRing, lerp(0.18, 0.86, settle));
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
