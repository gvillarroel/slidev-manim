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
const candidateSlot = document.getElementById("candidate-slot");
const candidateFork = document.getElementById("candidate-fork");
const candidateLoop = document.getElementById("candidate-loop");

const tensionHalo = document.getElementById("tension-halo");
const throatGuide = document.getElementById("throat-guide");
const relayLeftBracket = document.getElementById("relay-left-bracket");
const relayRightBracket = document.getElementById("relay-right-bracket");
const relayTopRail = document.getElementById("relay-top-rail");
const relayBottomRail = document.getElementById("relay-bottom-rail");
const triangleLeft = document.getElementById("triangle-left");
const triangleBase = document.getElementById("triangle-base");
const triangleRight = document.getElementById("triangle-right");
const activeTriangleLeft = document.getElementById("active-triangle-left");
const activeTriangleBase = document.getElementById("active-triangle-base");
const activeTriangleRight = document.getElementById("active-triangle-right");
const hubSpokeTop = document.getElementById("hub-spoke-top");
const hubSpokeLeft = document.getElementById("hub-spoke-left");
const hubSpokeRight = document.getElementById("hub-spoke-right");
const hubNodeTop = document.getElementById("hub-node-top");
const hubNodeLeft = document.getElementById("hub-node-left");
const hubNodeRight = document.getElementById("hub-node-right");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionRing = document.getElementById("resolution-ring");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ACTIVE_TRIANGLE_LEFT_LENGTH = activeTriangleLeft.getTotalLength();
const ACTIVE_TRIANGLE_BASE_LENGTH = activeTriangleBase.getTotalLength();
const ACTIVE_TRIANGLE_RIGHT_LENGTH = activeTriangleRight.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 302, y: 454 },
  entry: { x: 556, y: 454 },
  slot: { x: 676, y: 392 },
  fork: { x: 846, y: 338 },
  loop: { x: 1000, y: 410 },
  mouth: { x: 932, y: 454 },
  pocket: { x: 846, y: 454 },
  topNode: { x: 846, y: 338 },
  leftNode: { x: 760, y: 530 },
  rightNode: { x: 932, y: 530 },
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
    search: 18,
    tension: 16,
    transformation: 10,
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
    appearance: { x: 120, y: 146, width: 1120, height: 646 },
    search: { x: 168, y: 130, width: 1126, height: 662 },
    tension: { x: 560, y: 102, width: 572, height: 760 },
    transformation: { x: 542, y: 104, width: 604, height: 760 },
    resolution: { x: 590, y: 108, width: 520, height: 760 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -10) translate(800 450) scale(1.06) translate(-800 -450)",
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

  setGroupTransform(candidateSlot, points.slot.x, points.slot.y, 1, 0);
  setGroupTransform(candidateFork, points.fork.x, points.fork.y, 1, 0);
  setGroupTransform(candidateLoop, points.loop.x, points.loop.y, 1, 0);
  [candidateSlot, candidateFork, candidateLoop].forEach((element) => setOpacity(element, 0));

  setEllipseRadius(tensionHalo, 150, 118);
  setOpacity(tensionHalo, 0);
  setOpacity(throatGuide, 0);
  setGroupTransform(relayLeftBracket, points.pocket.x - 122, points.pocket.y, 1, 0);
  setGroupTransform(relayRightBracket, points.pocket.x + 122, points.pocket.y, 1, 0);
  setGroupTransform(relayTopRail, points.pocket.x, points.pocket.y - 88, 1, 0);
  setGroupTransform(relayBottomRail, points.pocket.x, points.pocket.y + 88, 1, 0);
  [relayLeftBracket, relayRightBracket, relayTopRail, relayBottomRail].forEach((element) => setOpacity(element, 0));
  [triangleLeft, triangleBase, triangleRight, hubSpokeTop, hubSpokeLeft, hubSpokeRight].forEach((element) => setOpacity(element, 0));
  [hubNodeTop, hubNodeLeft, hubNodeRight].forEach((element) => setOpacity(element, 0));
  setPathWindow(activeTriangleLeft, ACTIVE_TRIANGLE_LEFT_LENGTH, 0, 0);
  setPathWindow(activeTriangleBase, ACTIVE_TRIANGLE_BASE_LENGTH, 0, 0);
  setPathWindow(activeTriangleRight, ACTIVE_TRIANGLE_RIGHT_LENGTH, 0, 0);
  setEllipseRadius(resolutionHalo, 134, 146);
  setEllipseRadius(resolutionRing, 78, 78);
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
  setOpacity(candidateSlot, preview * 0.12);
  setOpacity(candidateFork, preview * 0.08);
  setOpacity(candidateLoop, preview * 0.06);
  setOpacity(throatGuide, preview * 0.08);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.entry, to: points.slot },
    { start: 0.24, end: 0.54, from: points.slot, to: points.fork },
    { start: 0.54, end: 0.82, from: points.fork, to: points.loop },
    { start: 0.82, end: 1, from: points.loop, to: points.mouth },
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

  setGroupTransform(candidateSlot, points.slot.x, points.slot.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), 0);
  setGroupTransform(candidateFork, points.fork.x, points.fork.y, lerp(0.9, activeB ? 1.05 : 0.97, revealB), 0);
  setGroupTransform(candidateLoop, points.loop.x, points.loop.y, lerp(0.88, activeC ? 1.05 : 0.97, revealC), 4);
  setOpacity(candidateSlot, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateFork, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateLoop, activeC ? 1 : revealC * 0.34 + 0.12);
  setOpacity(throatGuide, 0.12);
}

function renderTension(progress) {
  const ingress = easeInOut(clamp(progress / 0.28, 0, 1));
  const squeeze = clamp((progress - 0.22) / 0.34, 0, 1);
  const position = mixPoint(points.mouth, points.pocket, ingress);
  const bracketOffset = lerp(122, 54, easeInOut(squeeze));
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

  setGroupTransform(candidateSlot, lerp(points.slot.x, 724, progress), lerp(points.slot.y, 428, progress), lerp(0.98, 0.8, progress), -8);
  setGroupTransform(candidateFork, lerp(points.fork.x, 846, progress), lerp(points.fork.y, 390, progress), lerp(0.98, 0.72, progress), 0);
  setGroupTransform(candidateLoop, lerp(points.loop.x, 968, progress), lerp(points.loop.y, 434, progress), lerp(1, 0.8, progress), 8);
  setOpacity(candidateSlot, lerp(0.28, 0.04, progress));
  setOpacity(candidateFork, lerp(0.22, 0.04, progress));
  setOpacity(candidateLoop, lerp(0.78, 0.06, progress));

  setEllipseRadius(tensionHalo, lerp(150, 170, progress), lerp(118, 132, progress));
  setOpacity(tensionHalo, clamp((progress - 0.02) * 1.5, 0, 0.22));
  setOpacity(throatGuide, lerp(0.12, 0.28, progress));
  setGroupTransform(relayLeftBracket, points.pocket.x - bracketOffset, points.pocket.y, 1, 0);
  setGroupTransform(relayRightBracket, points.pocket.x + bracketOffset, points.pocket.y, 1, 0);
  setGroupTransform(relayTopRail, points.pocket.x, lerp(points.pocket.y - 112, points.pocket.y - 88, progress), 1, 0);
  setGroupTransform(relayBottomRail, points.pocket.x, lerp(points.pocket.y + 112, points.pocket.y + 88, progress), 1, 0);
  setOpacity(relayLeftBracket, clamp((progress - 0.04) * 1.8, 0, 1));
  setOpacity(relayRightBracket, clamp((progress - 0.04) * 1.8, 0, 1));
  setOpacity(relayTopRail, clamp((progress - 0.12) * 1.8, 0, 0.92));
  setOpacity(relayBottomRail, clamp((progress - 0.12) * 1.8, 0, 0.92));
}

function renderTransformation(progress) {
  const route = segmentedPoint(progress, [
    { start: 0, end: 0.26, from: points.pocket, to: points.topNode },
    { start: 0.26, end: 0.56, from: points.topNode, to: points.leftNode },
    { start: 0.56, end: 0.82, from: points.leftNode, to: points.rightNode },
    { start: 0.82, end: 1, from: points.rightNode, to: points.center },
  ]);
  const arcLift = Math.sin(clamp((progress - 0.26) / 0.56, 0, 1) * Math.PI) * 12;
  const position = progress <= 0.26 ? route : { x: route.x, y: route.y - arcLift };
  const triangleReveal = easeInOut(clamp((progress - 0.08) / 0.74, 0, 1));
  const spokeReveal = easeInOut(clamp((progress - 0.54) / 0.34, 0, 1));
  const leftTrace = easeInOut(clamp((progress - 0.12) / 0.2, 0, 1));
  const baseTrace = easeInOut(clamp((progress - 0.38) / 0.18, 0, 1));
  const rightTrace = easeInOut(clamp((progress - 0.58) / 0.18, 0, 1));

  setDot(
    position,
    16,
    100,
    1,
    0.22 + pulseWave(progress, 1.9) * 0.08,
    lerp(0.78, 1, triangleReveal),
    lerp(1.18, 1, triangleReveal),
  );
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);

  [searchGuideA, searchGuideB, searchGuideC, candidateSlot, candidateFork, candidateLoop].forEach((element) => setOpacity(element, 0));
  setOpacity(throatGuide, clamp(0.28 - progress * 0.34, 0, 1));
  setEllipseRadius(tensionHalo, lerp(170, 140, progress), lerp(132, 144, progress));
  setOpacity(tensionHalo, lerp(0.22, 0.12, progress));
  setGroupTransform(relayLeftBracket, points.pocket.x - lerp(54, 134, progress), points.pocket.y, 1, 0);
  setGroupTransform(relayRightBracket, points.pocket.x + lerp(54, 134, progress), points.pocket.y, 1, 0);
  setGroupTransform(relayTopRail, points.pocket.x, lerp(points.pocket.y - 88, points.pocket.y - 116, progress), 1, 0);
  setGroupTransform(relayBottomRail, points.pocket.x, lerp(points.pocket.y + 88, points.pocket.y + 116, progress), 1, 0);
  setOpacity(relayLeftBracket, lerp(1, 0, clamp((progress - 0.18) * 1.4, 0, 1)));
  setOpacity(relayRightBracket, lerp(1, 0, clamp((progress - 0.18) * 1.4, 0, 1)));
  setOpacity(relayTopRail, lerp(0.92, 0.04, clamp((progress - 0.24) * 1.45, 0, 1)));
  setOpacity(relayBottomRail, lerp(0.92, 0.04, clamp((progress - 0.24) * 1.45, 0, 1)));

  [triangleLeft, triangleBase, triangleRight].forEach((element) => setOpacity(element, clamp(triangleReveal * 1.1, 0, 0.9)));
  [hubSpokeTop, hubSpokeLeft, hubSpokeRight, hubNodeTop, hubNodeLeft, hubNodeRight].forEach((element) =>
    setOpacity(element, clamp(spokeReveal * 1.12, 0, 0.9)),
  );
  setPathWindow(activeTriangleLeft, ACTIVE_TRIANGLE_LEFT_LENGTH, ACTIVE_TRIANGLE_LEFT_LENGTH * leftTrace, leftTrace * 0.96);
  setPathWindow(activeTriangleBase, ACTIVE_TRIANGLE_BASE_LENGTH, ACTIVE_TRIANGLE_BASE_LENGTH * baseTrace, baseTrace * 0.96);
  setPathWindow(activeTriangleRight, ACTIVE_TRIANGLE_RIGHT_LENGTH, ACTIVE_TRIANGLE_RIGHT_LENGTH * rightTrace, rightTrace * 0.96);
  setOpacity(resolutionHalo, clamp((progress - 0.44) * 1.5, 0, 0.24));
  setOpacity(resolutionRing, clamp((progress - 0.66) * 1.5, 0, 0.18));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.25) * 0.05;

  setDot(points.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(throatGuide, 0);
  setOpacity(tensionHalo, 0);
  [relayLeftBracket, relayRightBracket, relayTopRail, relayBottomRail].forEach((element) => setOpacity(element, 0));

  setOpacity(triangleLeft, lerp(0.18, 0.06, settle));
  setOpacity(triangleBase, lerp(0.18, 0.06, settle));
  setOpacity(triangleRight, lerp(0.18, 0.06, settle));
  setOpacity(hubSpokeTop, lerp(0.84, 0.78, settle));
  setOpacity(hubSpokeLeft, lerp(0.84, 0.78, settle));
  setOpacity(hubSpokeRight, lerp(0.84, 0.78, settle));
  setOpacity(hubNodeTop, lerp(0.88, 0.8, settle));
  setOpacity(hubNodeLeft, lerp(0.88, 0.8, settle));
  setOpacity(hubNodeRight, lerp(0.88, 0.8, settle));
  setPathWindow(activeTriangleLeft, ACTIVE_TRIANGLE_LEFT_LENGTH, ACTIVE_TRIANGLE_LEFT_LENGTH, lerp(0.12, 0.03, settle));
  setPathWindow(activeTriangleBase, ACTIVE_TRIANGLE_BASE_LENGTH, ACTIVE_TRIANGLE_BASE_LENGTH, lerp(0.14, 0.03, settle));
  setPathWindow(activeTriangleRight, ACTIVE_TRIANGLE_RIGHT_LENGTH, ACTIVE_TRIANGLE_RIGHT_LENGTH, lerp(0.1, 0.02, settle));
  setEllipseRadius(resolutionHalo, 134, 146);
  setEllipseRadius(resolutionRing, lerp(74, 78, settle), lerp(74, 78, settle));
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
