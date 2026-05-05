const TOTAL_DURATION = 36_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 7_000 },
  { id: "tension", label: "tension", duration: 7_000 },
  { id: "transformation", label: "transformation", duration: 8_000 },
  { id: "resolution", label: "resolution", duration: 9_000 },
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
const candidateRack = document.getElementById("candidate-rack");
const candidatePawl = document.getElementById("candidate-pawl");
const candidateWheel = document.getElementById("candidate-wheel");

const throatArc = document.getElementById("throat-arc");
const pawlGuide = document.getElementById("pawl-guide");
const pressureHalo = document.getElementById("pressure-halo");
const toothBank = document.getElementById("tooth-bank");
const pawlClamp = document.getElementById("pawl-clamp");

const wheelBase = document.getElementById("wheel-base");
const wheelRing = document.getElementById("wheel-ring");
const wheelTrace = document.getElementById("wheel-trace");
const pawlTrace = document.getElementById("pawl-trace");
const toothOne = document.getElementById("tooth-one");
const toothTwo = document.getElementById("tooth-two");
const toothThree = document.getElementById("tooth-three");
const toothFour = document.getElementById("tooth-four");
const pawlFinal = document.getElementById("pawl-final");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const WHEEL_TRACE_LENGTH = wheelTrace.getTotalLength();
const PAWL_TRACE_LENGTH = pawlTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 296, y: 452 },
  entry: { x: 550, y: 452 },
  rack: { x: 656, y: 396 },
  pawl: { x: 822, y: 338 },
  wheel: { x: 992, y: 406 },
  throat: { x: 934, y: 452 },
  pocket: { x: 842, y: 452 },
  crest: { x: 840, y: 330 },
  center: { x: 820, y: 450 },
};

const toothOrigins = [
  { x: 930, y: 380, angle: -10 },
  { x: 948, y: 426, angle: 0 },
  { x: 948, y: 484, angle: 0 },
  { x: 930, y: 530, angle: 10 },
];

const toothTargets = [
  { x: 878, y: 356, angle: -58 },
  { x: 924, y: 410, angle: -18 },
  { x: 924, y: 490, angle: 18 },
  { x: 878, y: 544, angle: 58 },
];

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

function setCircleRadius(element, radius) {
  element.setAttribute("r", radius.toFixed(2));
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
    tension: 14,
    transformation: 6,
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
    appearance: { x: 118, y: 142, width: 1120, height: 644 },
    search: { x: 166, y: 126, width: 1130, height: 666 },
    tension: { x: 560, y: 90, width: 582, height: 784 },
    transformation: { x: 540, y: 74, width: 590, height: 804 },
    resolution: { x: 590, y: 98, width: 470, height: 706 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -10) translate(800 450) scale(1.055) translate(-800 -450)",
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

  setGroupTransform(candidateRack, points.rack.x, points.rack.y, 1, -2);
  setGroupTransform(candidatePawl, points.pawl.x, points.pawl.y, 1, -8);
  setGroupTransform(candidateWheel, points.wheel.x, points.wheel.y, 1, 16);
  [candidateRack, candidatePawl, candidateWheel].forEach((element) => setOpacity(element, 0));

  setOpacity(throatArc, 0);
  setOpacity(pawlGuide, 0);
  setCircleRadius(pressureHalo, 124);
  setOpacity(pressureHalo, 0);
  setGroupTransform(toothBank, 930, 452, 1, 0);
  setGroupTransform(pawlClamp, 756, 408, 1, 0);
  setOpacity(toothBank, 0);
  setOpacity(pawlClamp, 0);

  setCircleRadius(wheelBase, 110);
  setCircleRadius(wheelRing, 110);
  setCircleRadius(wheelTrace, 110);
  setOpacity(wheelBase, 0);
  setOpacity(wheelRing, 0);
  setPathWindow(wheelTrace, WHEEL_TRACE_LENGTH, 0, 0);
  setPathWindow(pawlTrace, PAWL_TRACE_LENGTH, 0, 0);

  const teeth = [toothOne, toothTwo, toothThree, toothFour];
  teeth.forEach((tooth, index) => {
    const origin = toothOrigins[index];
    setGroupTransform(tooth, origin.x, origin.y, 0.82, origin.angle);
    setOpacity(tooth, 0);
  });

  setGroupTransform(pawlFinal, 760, 512, 0.9, -4);
  setOpacity(pawlFinal, 0);
  setOpacity(anchorGrid, 0);
  setCircleRadius(resolutionHalo, 176);
  setOpacity(resolutionHalo, 0);
  setOpacity(resolutionFrame, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.entry, eased * 0.92);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(16, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.15) * 0.18,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.08) * 1.55, 0, 0.36));

  const preview = clamp((progress - 0.34) * 1.95, 0, 1);
  setOpacity(searchGuideA, preview * 0.18);
  setOpacity(searchGuideB, preview * 0.08);
  setOpacity(searchGuideC, preview * 0.04);
  setOpacity(candidateRack, preview * 0.16);
  setOpacity(candidatePawl, preview * 0.12);
  setOpacity(candidateWheel, preview * 0.1);
  setOpacity(throatArc, preview * 0.12);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.entry, to: points.rack },
    { start: 0.24, end: 0.54, from: points.rack, to: points.pawl },
    { start: 0.54, end: 0.82, from: points.pawl, to: points.wheel },
    { start: 0.82, end: 1, from: points.wheel, to: points.throat },
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

  setGroupTransform(candidateRack, points.rack.x, points.rack.y, lerp(0.9, activeA ? 1.06 : 0.97, revealA), -2);
  setGroupTransform(candidatePawl, points.pawl.x, points.pawl.y, lerp(0.9, activeB ? 1.05 : 0.97, revealB), -8);
  setGroupTransform(candidateWheel, points.wheel.x, points.wheel.y, lerp(0.88, activeC ? 1.05 : 0.97, revealC), 16);
  setOpacity(candidateRack, activeA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidatePawl, activeB ? 1 : revealB * 0.34 + 0.14);
  setOpacity(candidateWheel, activeC ? 1 : revealC * 0.34 + 0.12);
  setOpacity(throatArc, 0.14);
}

function renderTension(progress) {
  const ingress = easeInOut(clamp(progress / 0.28, 0, 1));
  const squeeze = clamp((progress - 0.22) / 0.34, 0, 1);
  const recoil = clamp((progress - 0.48) / 0.26, 0, 1);
  const position = mixPoint(points.throat, points.pocket, ingress);
  const recoilShift = lerp(0, 10, recoil);
  const dotPosition = { x: position.x - recoilShift, y: position.y };
  const bankShift = lerp(930, 910, easeInOut(squeeze));
  const clampShift = lerp(756, 782, easeInOut(squeeze));

  setDot(
    dotPosition,
    lerp(18, 16, progress),
    lerp(84, 110, progress),
    1,
    0.24 + pulseWave(progress, 2.0) * 0.1,
    lerp(1, 0.76, recoil),
    lerp(1, 1.18, recoil),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0.02, progress));

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide, index) => {
    guide.setAttribute("stroke", index === 2 ? COLORS.primaryRed : COLORS.lineGray);
    setOpacity(guide, lerp(index === 2 ? 0.18 : 0.12, 0, progress));
  });

  setGroupTransform(candidateRack, lerp(points.rack.x, 708, progress), lerp(points.rack.y, 424, progress), lerp(0.98, 0.78, progress), -12);
  setGroupTransform(candidatePawl, lerp(points.pawl.x, 820, progress), lerp(points.pawl.y, 384, progress), lerp(0.98, 0.72, progress), -6);
  setGroupTransform(candidateWheel, lerp(points.wheel.x, 934, progress), lerp(points.wheel.y, 434, progress), lerp(1, 0.8, progress), 8);
  setOpacity(candidateRack, lerp(0.28, 0.04, progress));
  setOpacity(candidatePawl, lerp(0.22, 0.04, progress));
  setOpacity(candidateWheel, lerp(0.78, 0.06, progress));

  setCircleRadius(pressureHalo, lerp(124, 140, progress));
  setOpacity(pressureHalo, clamp((progress - 0.02) * 1.5, 0, 0.24));
  setOpacity(throatArc, lerp(0.14, 0.28, progress));
  setOpacity(pawlGuide, clamp((progress - 0.08) * 1.8, 0, 0.26));
  setGroupTransform(toothBank, bankShift, 452, 1, 0);
  setGroupTransform(pawlClamp, clampShift, 408, 1, lerp(0, 7, squeeze));
  setOpacity(toothBank, clamp((progress - 0.04) * 1.8, 0, 1));
  setOpacity(pawlClamp, clamp((progress - 0.1) * 1.8, 0, 1));
}

function renderTransformation(progress) {
  const route = segmentedPoint(progress, [
    { start: 0, end: 0.42, from: points.pocket, to: points.crest },
    { start: 0.42, end: 1, from: points.crest, to: points.center },
  ]);
  const arcLift = Math.sin(clamp((progress - 0.42) / 0.58, 0, 1) * Math.PI) * 14;
  const position =
    progress <= 0.42
      ? route
      : {
          x: route.x,
          y: route.y - arcLift,
        };
  const shellReveal = easeInOut(clamp((progress - 0.1) / 0.72, 0, 1));
  const traceReveal = easeInOut(clamp((progress - 0.14) / 0.42, 0, 1));
  const pawlReveal = easeInOut(clamp((progress - 0.34) / 0.36, 0, 1));
  const teeth = [toothOne, toothTwo, toothThree, toothFour];

  setDot(
    position,
    16,
    100,
    1,
    0.22 + pulseWave(progress, 1.9) * 0.08,
    lerp(0.76, 1, shellReveal),
    lerp(1.18, 1, shellReveal),
  );
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);
  [searchGuideA, searchGuideB, searchGuideC, candidateRack, candidatePawl, candidateWheel].forEach((element) => setOpacity(element, 0));

  setOpacity(throatArc, clamp(0.28 - progress * 0.34, 0, 1));
  setOpacity(pawlGuide, lerp(0.26, 0.18, progress));
  setCircleRadius(pressureHalo, lerp(140, 126, progress));
  setOpacity(pressureHalo, lerp(0.24, 0.12, progress));
  setGroupTransform(toothBank, lerp(910, 924, progress), 452, 1, 0);
  setOpacity(toothBank, lerp(1, 0, clamp((progress - 0.18) * 1.45, 0, 1)));
  setGroupTransform(pawlClamp, lerp(782, 772, progress), lerp(408, 454, progress), lerp(1, 0.9, progress), lerp(7, -8, progress));
  setOpacity(pawlClamp, lerp(1, 0, clamp((progress - 0.2) * 1.45, 0, 1)));

  setOpacity(wheelBase, clamp((progress - 0.08) * 1.6, 0, 0.88));
  setOpacity(wheelRing, clamp(shellReveal * 1.08, 0, 0.94));
  setPathWindow(wheelTrace, WHEEL_TRACE_LENGTH, WHEEL_TRACE_LENGTH * traceReveal, traceReveal * 0.96);
  setPathWindow(pawlTrace, PAWL_TRACE_LENGTH, PAWL_TRACE_LENGTH * pawlReveal, pawlReveal * 0.94);

  teeth.forEach((tooth, index) => {
    const reveal = easeOut(clamp((progress - 0.18 - index * 0.08) / 0.22, 0, 1));
    const origin = toothOrigins[index];
    const target = toothTargets[index];
    setGroupTransform(
      tooth,
      lerp(origin.x, target.x, reveal),
      lerp(origin.y, target.y, reveal),
      lerp(0.82, 1, reveal),
      lerp(origin.angle, target.angle, reveal),
    );
    setOpacity(tooth, clamp(reveal * 1.15, 0, 0.94));
  });

  setGroupTransform(pawlFinal, lerp(772, 786, pawlReveal), lerp(512, 522, pawlReveal), lerp(0.9, 1, pawlReveal), lerp(-4, -10, pawlReveal));
  setOpacity(pawlFinal, clamp((progress - 0.34) * 1.5, 0, 0.94));
  setOpacity(anchorGrid, clamp((progress - 0.46) * 1.55, 0, 0.24));
  setOpacity(resolutionHalo, clamp((progress - 0.54) * 1.4, 0, 0.2));
  setOpacity(resolutionFrame, clamp((progress - 0.7) * 1.6, 0, 0.16));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.2) * 0.05;

  setDot(points.center, 16, 96, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(activeTrail, 0);
  setOpacity(throatArc, 0);
  setOpacity(pawlGuide, lerp(0.1, 0.04, settle));
  setOpacity(pressureHalo, 0);
  setOpacity(toothBank, 0);
  setOpacity(pawlClamp, 0);

  setCircleRadius(wheelBase, 110);
  setCircleRadius(wheelRing, 110);
  setOpacity(wheelBase, lerp(0.12, 0.05, settle));
  setOpacity(wheelRing, lerp(0.94, 0.88, settle));
  setPathWindow(wheelTrace, WHEEL_TRACE_LENGTH, WHEEL_TRACE_LENGTH, lerp(0.12, 0.03, settle));
  setPathWindow(pawlTrace, PAWL_TRACE_LENGTH, PAWL_TRACE_LENGTH, lerp(0.16, 0.04, settle));

  [toothOne, toothTwo, toothThree, toothFour].forEach((tooth, index) => {
    const target = toothTargets[index];
    setGroupTransform(tooth, target.x, target.y, 1, target.angle);
    setOpacity(tooth, lerp(0.94, 0.86, settle));
  });

  setGroupTransform(pawlFinal, 786, 522, 1, -10);
  setOpacity(pawlFinal, lerp(0.94, 0.86, settle));
  setOpacity(anchorGrid, lerp(0.16, 0.08, settle));
  setCircleRadius(resolutionHalo, lerp(172, 176, settle));
  setOpacity(resolutionHalo, lerp(0.2, 0.3, settle));
  setOpacity(resolutionFrame, lerp(0.18, 0.84, settle));
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
