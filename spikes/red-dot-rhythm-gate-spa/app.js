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
const centerGuide = document.getElementById("center-guide");
const candidateA = document.getElementById("candidate-a");
const candidateB = document.getElementById("candidate-b");
const candidateC = document.getElementById("candidate-c");
const echoA = document.getElementById("echo-a");
const echoB = document.getElementById("echo-b");
const echoC = document.getElementById("echo-c");

const compressionHalo = document.getElementById("compression-halo");
const pressureLeft = document.getElementById("pressure-left");
const pressureRight = document.getElementById("pressure-right");
const pressureTop = document.getElementById("pressure-top");
const pressureBottom = document.getElementById("pressure-bottom");

const meterLeft = document.getElementById("meter-left");
const meterRight = document.getElementById("meter-right");
const meterTop = document.getElementById("meter-top");
const meterBottom = document.getElementById("meter-bottom");
const activeTopPath = document.getElementById("active-top-path");
const activeBottomPath = document.getElementById("active-bottom-path");
const meterBeats = document.getElementById("meter-beats");
const resolutionHalo = document.getElementById("resolution-halo");
const terminalCorners = document.getElementById("terminal-corners");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const ACTIVE_TOP_LENGTH = activeTopPath.getTotalLength();
const ACTIVE_BOTTOM_LENGTH = activeBottomPath.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const COLORS = {
  primaryRed: "#9e1b32",
  lineGray: "#cfcfcf",
  lineDark: "#4f4f4f",
};

const points = {
  start: { x: 294, y: 450 },
  entry: { x: 520, y: 450 },
  gateA: { x: 690, y: 426 },
  gateB: { x: 846, y: 450 },
  gateC: { x: 1008, y: 414 },
  mouth: { x: 846, y: 450 },
  channel: { x: 846, y: 450 },
  center: { x: 846, y: 450 },
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

function setCandidateColor(element, active) {
  element.style.color = active ? COLORS.primaryRed : COLORS.lineDark;
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
    search: 12,
    tension: 8,
    transformation: 2,
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
    appearance: { x: 120, y: 144, width: 1120, height: 642 },
    search: { x: 164, y: 126, width: 1128, height: 668 },
    tension: { x: 580, y: 110, width: 532, height: 744 },
    transformation: { x: 560, y: 96, width: 576, height: 772 },
    resolution: { x: 594, y: 98, width: 504, height: 760 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -8) translate(800 450) scale(1.05) translate(-800 -450)",
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
  setOpacity(centerGuide, 0);

  setGroupTransform(candidateA, points.gateA.x, points.gateA.y, 0.96, 0);
  setGroupTransform(candidateB, points.gateB.x, points.gateB.y, 0.96, 0);
  setGroupTransform(candidateC, points.gateC.x, points.gateC.y, 0.96, 0);
  [candidateA, candidateB, candidateC].forEach((candidate) => {
    setOpacity(candidate, 0);
    setCandidateColor(candidate, false);
  });
  [echoA, echoB, echoC].forEach((echo) => setOpacity(echo, 0));

  setEllipseRadius(compressionHalo, 176, 138);
  setOpacity(compressionHalo, 0);
  setGroupTransform(pressureLeft, points.center.x, points.center.y, 1, 0);
  setGroupTransform(pressureRight, points.center.x, points.center.y, 1, 0);
  setGroupTransform(pressureTop, points.center.x, points.center.y, 1, 0);
  setGroupTransform(pressureBottom, points.center.x, points.center.y, 1, 0);
  [pressureLeft, pressureRight, pressureTop, pressureBottom].forEach((element) => setOpacity(element, 0));

  setGroupTransform(meterLeft, points.center.x, points.center.y, 0.9, 0);
  setGroupTransform(meterRight, points.center.x, points.center.y, 0.9, 0);
  setGroupTransform(meterTop, points.center.x, points.center.y, 0.9, 0);
  setGroupTransform(meterBottom, points.center.x, points.center.y, 0.9, 0);
  [meterLeft, meterRight, meterTop, meterBottom, meterBeats, terminalCorners].forEach((element) => setOpacity(element, 0));
  setPathWindow(activeTopPath, ACTIVE_TOP_LENGTH, 0, 0);
  setPathWindow(activeBottomPath, ACTIVE_BOTTOM_LENGTH, 0, 0);
  setEllipseRadius(resolutionHalo, 168, 146);
  setOpacity(resolutionHalo, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.entry, eased);

  setDot(
    position,
    lerp(4, 18, eased),
    lerp(16, 82, eased),
    clamp(progress * 1.8, 0, 1),
    0.2 + pulseWave(progress, 1.2) * 0.16,
  );
  setOpacity(narrativeSpine, clamp((progress - 0.06) * 1.7, 0, 0.42));
  setOpacity(centerGuide, clamp((progress - 0.28) * 1.7, 0, 0.14));

  const preview = clamp((progress - 0.22) * 1.4, 0, 1);
  setGroupTransform(candidateA, points.gateA.x, points.gateA.y, lerp(0.9, 0.98, preview), 0);
  setGroupTransform(candidateB, points.gateB.x, points.gateB.y, lerp(0.9, 0.98, preview), 0);
  setGroupTransform(candidateC, points.gateC.x, points.gateC.y, lerp(0.9, 0.98, preview), 0);
  setOpacity(candidateA, preview * 0.24);
  setOpacity(candidateB, preview * 0.32);
  setOpacity(candidateC, preview * 0.22);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.24, from: points.entry, to: points.gateA },
    { start: 0.24, end: 0.54, from: points.gateA, to: points.gateB },
    { start: 0.54, end: 0.82, from: points.gateB, to: points.gateC },
    { start: 0.82, end: 1, from: points.gateC, to: points.mouth },
  ]);

  const trailProgress = clamp(progress / 0.92, 0, 1);
  const highlightA = progress < 0.28;
  const highlightB = progress >= 0.28 && progress < 0.62;
  const highlightC = progress >= 0.62 && progress < 0.86;

  setDot(position, 18, 84, 1, 0.22 + pulseWave(progress, 1.8) * 0.1);
  setOpacity(narrativeSpine, lerp(0.34, 0.12, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * trailProgress, lerp(0.26, 0.12, progress));
  setOpacity(centerGuide, lerp(0.16, 0.22, progress));

  const revealA = clamp(progress / 0.2, 0, 1);
  const revealB = clamp((progress - 0.18) / 0.24, 0, 1);
  const revealC = clamp((progress - 0.5) / 0.24, 0, 1);

  setGroupTransform(candidateA, points.gateA.x, points.gateA.y, lerp(0.94, highlightA ? 1.08 : 0.98, revealA), 0);
  setGroupTransform(candidateB, points.gateB.x, points.gateB.y, lerp(0.94, highlightB ? 1.08 : 1, revealB), 0);
  setGroupTransform(candidateC, points.gateC.x, points.gateC.y, lerp(0.94, highlightC ? 1.08 : 0.98, revealC), 0);
  setOpacity(candidateA, highlightA ? 1 : revealA * 0.34 + 0.14);
  setOpacity(candidateB, highlightB ? 1 : revealB * 0.38 + 0.16);
  setOpacity(candidateC, highlightC ? 1 : revealC * 0.34 + 0.12);
  setCandidateColor(candidateA, highlightA);
  setCandidateColor(candidateB, highlightB);
  setCandidateColor(candidateC, highlightC);

  setOpacity(echoA, progress > 0.3 ? clamp((progress - 0.3) * 1.4, 0, 0.18) : 0);
  setOpacity(echoB, progress > 0.64 ? clamp((progress - 0.64) * 1.4, 0, 0.18) : 0);
  setOpacity(echoC, 0);
}

function renderTension(progress) {
  const ingress = easeInOut(clamp(progress / 0.32, 0, 1));
  const squeeze = easeInOut(clamp((progress - 0.18) / 0.46, 0, 1));
  const exitFade = clamp((progress - 0.74) / 0.18, 0, 1);
  const position = mixPoint(points.mouth, points.channel, ingress);
  const leftStart = 120;
  const leftEnd = 44;
  const topScale = lerp(1, 0.92, squeeze);

  setDot(
    position,
    lerp(18, 16, progress),
    lerp(84, 112, progress),
    1,
    0.24 + pulseWave(progress, 2) * 0.1,
    lerp(1, 0.72, squeeze),
    lerp(1, 1.22, squeeze),
  );
  setOpacity(narrativeSpine, lerp(0.12, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, lerp(0.12, 0, progress));
  setOpacity(centerGuide, lerp(0.22, 0.28, progress));

  setGroupTransform(candidateA, lerp(points.gateA.x, 760, progress), lerp(points.gateA.y, 428, progress), lerp(0.98, 0.76, progress), 0);
  setGroupTransform(candidateB, points.gateB.x, lerp(points.gateB.y, 446, progress), lerp(1, 0.74, progress), 0);
  setGroupTransform(candidateC, lerp(points.gateC.x, 932, progress), lerp(points.gateC.y, 420, progress), lerp(0.98, 0.76, progress), 0);
  setOpacity(candidateA, lerp(0.28, 0.04, progress));
  setOpacity(candidateB, lerp(0.38, 0.06, progress));
  setOpacity(candidateC, lerp(0.24, 0.04, progress));
  setCandidateColor(candidateA, false);
  setCandidateColor(candidateB, progress < 0.56);
  setCandidateColor(candidateC, false);
  setOpacity(echoA, lerp(0.18, 0, progress));
  setOpacity(echoB, lerp(0.18, 0, progress));
  setOpacity(echoC, clamp((progress - 0.58) * 1.2, 0, 0.16) * (1 - exitFade));

  setEllipseRadius(compressionHalo, lerp(176, 166, progress), lerp(138, 128, progress));
  setOpacity(compressionHalo, clamp((progress - 0.04) * 1.6, 0, 0.28));
  setGroupTransform(pressureLeft, points.center.x, points.center.y, 1, 0);
  setGroupTransform(pressureRight, points.center.x, points.center.y, 1, 0);
  pressureLeft.setAttribute("transform", `translate(${(points.center.x - lerp(leftStart, leftEnd, squeeze)).toFixed(2)} ${points.center.y.toFixed(2)})`);
  pressureRight.setAttribute("transform", `translate(${(points.center.x + lerp(leftStart, leftEnd, squeeze)).toFixed(2)} ${points.center.y.toFixed(2)})`);
  setGroupTransform(pressureTop, points.center.x, points.center.y, topScale, 0);
  setGroupTransform(pressureBottom, points.center.x, points.center.y, topScale, 0);
  setOpacity(pressureLeft, clamp((progress - 0.1) * 1.8, 0, 1));
  setOpacity(pressureRight, clamp((progress - 0.1) * 1.8, 0, 1));
  setOpacity(pressureTop, clamp((progress - 0.2) * 1.8, 0, 0.92));
  setOpacity(pressureBottom, clamp((progress - 0.26) * 1.8, 0, 0.92));
}

function renderTransformation(progress) {
  const release = rangedProgress(progress, 0, 0.28);
  const frameBuild = rangedProgress(progress, 0.2, 0.72);
  const routeTop = rangedProgress(progress, 0.28, 0.54);
  const routeBottom = rangedProgress(progress, 0.46, 0.76);
  const settle = rangedProgress(progress, 0.68, 1);

  setDot(
    points.center,
    16,
    104,
    1,
    0.22 + pulseWave(progress, 1.7) * 0.08,
    lerp(0.72, 1, release || frameBuild),
    lerp(1.22, 1, release || frameBuild),
  );
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0);
  setOpacity(centerGuide, lerp(0.28, 0.08, progress));
  [candidateA, candidateB, candidateC, echoA, echoB, echoC].forEach((element) => setOpacity(element, 0));

  setEllipseRadius(compressionHalo, lerp(166, 168, progress), lerp(128, 146, progress));
  setOpacity(compressionHalo, lerp(0.28, 0.08, progress));
  pressureLeft.setAttribute("transform", `translate(${lerp(points.center.x - 44, points.center.x - 96, easeInOut(frameBuild)).toFixed(2)} ${points.center.y.toFixed(2)})`);
  pressureRight.setAttribute("transform", `translate(${lerp(points.center.x + 44, points.center.x + 96, easeInOut(frameBuild)).toFixed(2)} ${points.center.y.toFixed(2)})`);
  setOpacity(pressureLeft, lerp(1, 0, clamp((progress - 0.24) * 1.6, 0, 1)));
  setOpacity(pressureRight, lerp(1, 0, clamp((progress - 0.24) * 1.6, 0, 1)));
  setOpacity(pressureTop, lerp(0.92, 0, clamp((progress - 0.14) * 1.5, 0, 1)));
  setOpacity(pressureBottom, lerp(0.92, 0, clamp((progress - 0.18) * 1.5, 0, 1)));

  setGroupTransform(meterLeft, points.center.x, points.center.y, lerp(0.82, 1, frameBuild), 0);
  setGroupTransform(meterRight, points.center.x, points.center.y, lerp(0.82, 1, frameBuild), 0);
  setGroupTransform(meterTop, points.center.x, points.center.y, lerp(0.82, 1, frameBuild), 0);
  setGroupTransform(meterBottom, points.center.x, points.center.y, lerp(0.82, 1, frameBuild), 0);
  setOpacity(meterLeft, clamp((progress - 0.18) * 1.5, 0, 0.92));
  setOpacity(meterRight, clamp((progress - 0.18) * 1.5, 0, 0.92));
  setOpacity(meterTop, clamp((progress - 0.28) * 1.5, 0, 0.92));
  setOpacity(meterBottom, clamp((progress - 0.4) * 1.5, 0, 0.92));
  setPathWindow(activeTopPath, ACTIVE_TOP_LENGTH, ACTIVE_TOP_LENGTH * easeInOut(routeTop), clamp((progress - 0.28) * 1.6, 0, 0.96));
  setPathWindow(activeBottomPath, ACTIVE_BOTTOM_LENGTH, ACTIVE_BOTTOM_LENGTH * easeInOut(routeBottom), clamp((progress - 0.46) * 1.6, 0, 0.94));
  setOpacity(meterBeats, clamp((progress - 0.56) * 1.6, 0, 0.9));
  setOpacity(resolutionHalo, clamp((progress - 0.44) * 1.5, 0, 0.26));
  setOpacity(terminalCorners, clamp((progress - 0.7) * 1.5, 0, 0.7));

  if (settle > 0) {
    setEllipseRadius(resolutionHalo, lerp(168, 162, settle), lerp(146, 142, settle));
  }
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.2) * 0.05;

  setDot(points.center, 16, 94, 1, holdPulse);
  setOpacity(narrativeSpine, 0);
  setOpacity(centerGuide, 0.06);
  setOpacity(compressionHalo, 0);

  [meterLeft, meterRight, meterTop, meterBottom].forEach((element) => setOpacity(element, lerp(0.92, 0.84, settle)));
  setGroupTransform(meterLeft, points.center.x, points.center.y, lerp(1, 0.96, settle), 0);
  setGroupTransform(meterRight, points.center.x, points.center.y, lerp(1, 0.96, settle), 0);
  setGroupTransform(meterTop, points.center.x, points.center.y, lerp(1, 0.96, settle), 0);
  setGroupTransform(meterBottom, points.center.x, points.center.y, lerp(1, 0.96, settle), 0);

  setPathWindow(activeTopPath, ACTIVE_TOP_LENGTH, ACTIVE_TOP_LENGTH, lerp(0.16, 0.05, settle));
  setPathWindow(activeBottomPath, ACTIVE_BOTTOM_LENGTH, ACTIVE_BOTTOM_LENGTH, lerp(0.14, 0.04, settle));
  setOpacity(meterBeats, lerp(0.9, 0.3, settle));
  setOpacity(resolutionHalo, lerp(0.26, 0.32, settle));
  setOpacity(terminalCorners, lerp(0.7, 0.54, settle));
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
