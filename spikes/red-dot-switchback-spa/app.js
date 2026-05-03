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
const candidateShallow = document.getElementById("candidate-shallow");
const candidateSwitch = document.getElementById("candidate-switch");
const candidateTall = document.getElementById("candidate-tall");
const turnGuide = document.getElementById("turn-guide");
const gateGuide = document.getElementById("gate-guide");
const pressureHalo = document.getElementById("pressure-halo");
const gateShell = document.getElementById("gate-shell");
const gateLeft = document.getElementById("gate-left");
const gateVerticalA = document.getElementById("gate-vertical-a");
const gateMiddle = document.getElementById("gate-middle");
const gateVerticalB = document.getElementById("gate-vertical-b");
const gateTop = document.getElementById("gate-top");
const switchbackBase = document.getElementById("switchback-base");
const switchbackTrace = document.getElementById("switchback-trace");
const slotCenter = document.getElementById("slot-center");
const slotBottomRight = document.getElementById("slot-bottom-right");
const slotBottomLeft = document.getElementById("slot-bottom-left");
const slotTopLeft = document.getElementById("slot-top-left");
const slotTopCenter = document.getElementById("slot-top-center");
const slotTopRight = document.getElementById("slot-top-right");
const shelfBottom = document.getElementById("shelf-bottom");
const riserRight = document.getElementById("riser-right");
const shelfMiddle = document.getElementById("shelf-middle");
const riserLeft = document.getElementById("riser-left");
const shelfTop = document.getElementById("shelf-top");
const riserCenter = document.getElementById("riser-center");
const resolutionFrame = document.getElementById("resolution-frame");
const resolutionHalo = document.getElementById("resolution-halo");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const SWITCHBACK_TRACE_LENGTH = switchbackTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 520, y: 462 },
  ingress: { x: 720, y: 462 },
  candidateA: { x: 756, y: 392 },
  candidateB: { x: 908, y: 500 },
  candidateC: { x: 1052, y: 400 },
  center: { x: 820, y: 456 },
};

const candidateTransforms = {
  shallow: { x: 756, y: 392, rotate: -6 },
  switch: { x: 908, y: 500, rotate: 0 },
  tall: { x: 1052, y: 400, rotate: 6 },
};

const switchback = {
  center: { x: 820, y: 456 },
  rightMid: { x: 940, y: 456 },
  bottomRight: { x: 940, y: 548 },
  bottomLeft: { x: 700, y: 548 },
  topLeft: { x: 700, y: 364 },
  topCenter: { x: 820, y: 364 },
};

const gateWide = {
  center: { x: 820, y: 456 },
  rightMid: { x: 928, y: 456 },
  bottomRight: { x: 928, y: 536 },
  bottomLeft: { x: 718, y: 536 },
  topLeft: { x: 718, y: 372 },
  topCenter: { x: 820, y: 372 },
};

const gateTight = {
  center: { x: 820, y: 456 },
  rightMid: { x: 884, y: 456 },
  bottomRight: { x: 884, y: 500 },
  bottomLeft: { x: 758, y: 500 },
  topLeft: { x: 758, y: 404 },
  topCenter: { x: 820, y: 404 },
};

const slotPositions = {
  center: switchback.center,
  bottomRight: switchback.bottomRight,
  bottomLeft: switchback.bottomLeft,
  topLeft: switchback.topLeft,
  topCenter: switchback.topCenter,
  topRight: switchback.rightMid,
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

function mixNodes(a, b, amount) {
  return {
    center: mixPoint(a.center, b.center, amount),
    rightMid: mixPoint(a.rightMid, b.rightMid, amount),
    bottomRight: mixPoint(a.bottomRight, b.bottomRight, amount),
    bottomLeft: mixPoint(a.bottomLeft, b.bottomLeft, amount),
    topLeft: mixPoint(a.topLeft, b.topLeft, amount),
    topCenter: mixPoint(a.topCenter, b.topCenter, amount),
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

function beat(progress, center, width) {
  const distance = Math.abs(progress - center);
  return clamp(1 - distance / width, 0, 1);
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

function pathPoint(progress) {
  const length = clamp(progress, 0, 1) * SWITCHBACK_TRACE_LENGTH;
  const point = switchbackTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
}

function gatePath(nodes) {
  return [
    `M ${nodes.center.x.toFixed(2)} ${nodes.center.y.toFixed(2)}`,
    `H ${nodes.rightMid.x.toFixed(2)}`,
    `V ${nodes.bottomRight.y.toFixed(2)}`,
    `H ${nodes.bottomLeft.x.toFixed(2)}`,
    `V ${nodes.topLeft.y.toFixed(2)}`,
    `H ${nodes.topCenter.x.toFixed(2)}`,
    `V ${nodes.center.y.toFixed(2)}`,
  ].join(" ");
}

function setGateGeometry(amount) {
  const nodes = mixNodes(gateWide, gateTight, amount);
  gateShell.setAttribute("d", gatePath(nodes));
  gateLeft.setAttribute(
    "d",
    `M ${nodes.center.x.toFixed(2)} ${nodes.center.y.toFixed(2)} H ${nodes.rightMid.x.toFixed(2)}`,
  );
  gateVerticalA.setAttribute(
    "d",
    `M ${nodes.rightMid.x.toFixed(2)} ${nodes.rightMid.y.toFixed(2)} V ${nodes.bottomRight.y.toFixed(2)}`,
  );
  gateMiddle.setAttribute(
    "d",
    `M ${nodes.bottomRight.x.toFixed(2)} ${nodes.bottomRight.y.toFixed(2)} H ${nodes.bottomLeft.x.toFixed(2)}`,
  );
  gateVerticalB.setAttribute(
    "d",
    `M ${nodes.bottomLeft.x.toFixed(2)} ${nodes.bottomLeft.y.toFixed(2)} V ${nodes.topLeft.y.toFixed(2)}`,
  );
  gateTop.setAttribute(
    "d",
    `M ${nodes.topLeft.x.toFixed(2)} ${nodes.topLeft.y.toFixed(2)} H ${nodes.topCenter.x.toFixed(2)}`,
  );
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
    search: 26,
    tension: 8,
    transformation: 2,
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
    appearance: { x: 118, y: 146, width: 1088, height: 632 },
    search: { x: 146, y: 128, width: 1124, height: 668 },
    tension: { x: 342, y: 136, width: 912, height: 644 },
    transformation: { x: 278, y: 118, width: 1040, height: 688 },
    resolution: { x: 284, y: 122, width: 1028, height: 680 },
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
  setDot(points.start, 18, 74, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC].forEach((guide) => setOpacity(guide, 0));

  setGroupTransform(candidateShallow, candidateTransforms.shallow.x, candidateTransforms.shallow.y, 1, candidateTransforms.shallow.rotate);
  setGroupTransform(candidateSwitch, candidateTransforms.switch.x, candidateTransforms.switch.y, 1, candidateTransforms.switch.rotate);
  setGroupTransform(candidateTall, candidateTransforms.tall.x, candidateTransforms.tall.y, 1, candidateTransforms.tall.rotate);
  [candidateShallow, candidateSwitch, candidateTall].forEach((candidate) => setOpacity(candidate, 0));

  setOpacity(turnGuide, 0);
  setOpacity(gateGuide, 0);
  setOpacity(pressureHalo, 0);

  setGateGeometry(0);
  [gateShell, gateLeft, gateVerticalA, gateMiddle, gateVerticalB, gateTop].forEach((segment) => setOpacity(segment, 0));

  setOpacity(switchbackBase, 0);
  setPathWindow(switchbackTrace, SWITCHBACK_TRACE_LENGTH, 0, 0);

  setGroupTransform(slotCenter, slotPositions.center.x, slotPositions.center.y, 1, 0);
  setGroupTransform(slotBottomRight, slotPositions.bottomRight.x, slotPositions.bottomRight.y, 1, 0);
  setGroupTransform(slotBottomLeft, slotPositions.bottomLeft.x, slotPositions.bottomLeft.y, 1, 0);
  setGroupTransform(slotTopLeft, slotPositions.topLeft.x, slotPositions.topLeft.y, 1, 0);
  setGroupTransform(slotTopCenter, slotPositions.topCenter.x, slotPositions.topCenter.y, 1, 0);
  setGroupTransform(slotTopRight, slotPositions.topRight.x, slotPositions.topRight.y, 1, 0);
  [slotCenter, slotBottomRight, slotBottomLeft, slotTopLeft, slotTopCenter, slotTopRight].forEach((slot) => setOpacity(slot, 0));

  [shelfBottom, riserRight, shelfMiddle, riserLeft, shelfTop, riserCenter].forEach((segment) => setOpacity(segment, 0));
  setOpacity(resolutionFrame, 0);
  setOpacity(resolutionHalo, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const position = mixPoint(points.start, points.ingress, eased * 0.94);
  setOpacity(narrativeSpine, 0.18 + eased * 0.18);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * eased * 0.78, 0.18 + eased * 0.44);
  setDot(position, 18, 74, 0.36 + eased * 0.64, 0.14 + eased * 0.26);

  const hint = clamp((progress - 0.34) / 0.34, 0, 1);
  setGroupTransform(candidateShallow, candidateTransforms.shallow.x, candidateTransforms.shallow.y, 0.94 + hint * 0.04, candidateTransforms.shallow.rotate);
  setOpacity(candidateShallow, hint * 0.3);
  setOpacity(turnGuide, hint * 0.22);
  setOpacity(switchbackBase, hint * 0.12);
}

function renderSearch(progress) {
  const position = segmentedPoint(progress, [
    { start: 0, end: 0.26, from: points.ingress, to: points.candidateA },
    { start: 0.26, end: 0.58, from: points.candidateA, to: points.candidateB },
    { start: 0.58, end: 0.86, from: points.candidateB, to: points.candidateC },
    { start: 0.86, end: 1, from: points.candidateC, to: { x: 1000, y: 404 } },
  ]);

  setOpacity(narrativeSpine, 0.28);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, 0.18);
  setDot(position, 18, 72, 1, 0.28);

  const guideA = clamp(progress / 0.28, 0, 1);
  const guideB = clamp((progress - 0.18) / 0.32, 0, 1);
  const guideC = clamp((progress - 0.52) / 0.26, 0, 1);
  setOpacity(searchGuideA, 0.18 + guideA * 0.34);
  setOpacity(searchGuideB, 0.1 + guideB * 0.3);
  setOpacity(searchGuideC, 0.1 + guideC * 0.28);

  const shallowBeat = beat(progress, 0.17, 0.24);
  const switchBeat = beat(progress, 0.49, 0.26);
  const tallBeat = beat(progress, 0.78, 0.22);

  setGroupTransform(
    candidateShallow,
    candidateTransforms.shallow.x,
    candidateTransforms.shallow.y,
    0.96 + shallowBeat * 0.08,
    candidateTransforms.shallow.rotate - shallowBeat * 2,
  );
  setGroupTransform(
    candidateSwitch,
    candidateTransforms.switch.x,
    candidateTransforms.switch.y,
    0.94 + switchBeat * 0.1,
    candidateTransforms.switch.rotate,
  );
  setGroupTransform(
    candidateTall,
    candidateTransforms.tall.x,
    candidateTransforms.tall.y,
    0.94 + tallBeat * 0.08,
    candidateTransforms.tall.rotate + tallBeat * 2,
  );
  setOpacity(candidateShallow, 0.16 + shallowBeat * 0.58);
  setOpacity(candidateSwitch, 0.1 + switchBeat * 0.62);
  setOpacity(candidateTall, 0.1 + tallBeat * 0.56);
}

function renderTension(progress) {
  const moveIn = clamp(progress / 0.28, 0, 1);
  const position = mixPoint(points.candidateC, points.center, easeInOut(moveIn));
  const squeeze = clamp((progress - 0.2) / 0.46, 0, 1);
  const releasePrep = clamp((progress - 0.72) / 0.2, 0, 1);
  const squashedX = 1 + squeeze * 0.22 - releasePrep * 0.06;
  const squashedY = 1 - squeeze * 0.18 + releasePrep * 0.05;

  setOpacity(narrativeSpine, 0.14 * (1 - squeeze));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * (1 - squeeze * 0.7), 0.18 * (1 - squeeze));
  setDot(position, 18 - squeeze * 1.4, 72 + squeeze * 16, 1, 0.34 + squeeze * 0.08, squashedX, squashedY);

  const searchFade = clamp(1 - progress / 0.38, 0, 1);
  setOpacity(searchGuideA, 0.42 * searchFade);
  setOpacity(searchGuideB, 0.36 * searchFade);
  setOpacity(searchGuideC, 0.32 * searchFade);
  setOpacity(candidateShallow, 0.24 * searchFade);
  setOpacity(candidateSwitch, 0.24 * searchFade);
  setOpacity(candidateTall, 0.28 * searchFade);

  setOpacity(turnGuide, 0.12 + squeeze * 0.24);
  setOpacity(gateGuide, 0.12 + squeeze * 0.3);
  setOpacity(pressureHalo, 0.18 + pulseWave(progress, 1.5) * 0.28);
  setGateGeometry(easeInOut(squeeze));
  [gateShell, gateLeft, gateVerticalA, gateMiddle, gateVerticalB, gateTop].forEach((segment) => {
    setOpacity(segment, 0.24 + squeeze * 0.58);
  });
}

function renderTransformation(progress) {
  const gateFade = clamp(1 - progress / 0.26, 0, 1);
  const traceProgress = clamp((progress - 0.08) / 0.64, 0, 1);
  const slotReveal = clamp(progress / 0.2, 0, 1);
  const slotFade = clamp(1 - (progress - 0.42) / 0.18, 0, 1);
  const structure = clamp((progress - 0.24) / 0.34, 0, 1);
  const position = pathPoint(traceProgress);

  setDot(position, 17.2, 70, 1, 0.3 + pulseWave(progress, 1.25) * 0.12);
  setOpacity(turnGuide, 0.2 * gateFade);
  setOpacity(gateGuide, 0.28 * gateFade);
  setOpacity(pressureHalo, 0.16 * gateFade);
  setGateGeometry(1);
  [gateShell, gateLeft, gateVerticalA, gateMiddle, gateVerticalB, gateTop].forEach((segment) => {
    setOpacity(segment, 0.56 * gateFade);
  });

  setOpacity(switchbackBase, 0.22 + structure * 0.26);
  setPathWindow(switchbackTrace, SWITCHBACK_TRACE_LENGTH, SWITCHBACK_TRACE_LENGTH * traceProgress, 0.84);

  const slotOpacity = 0.46 * slotReveal * slotFade;
  [slotCenter, slotBottomRight, slotBottomLeft, slotTopLeft, slotTopCenter, slotTopRight].forEach((slot) => {
    setOpacity(slot, slotOpacity);
  });

  setOpacity(shelfMiddle, 0.26 + structure * 0.5);
  setOpacity(riserRight, structure * 0.72);
  setOpacity(shelfBottom, structure * 0.72);
  setOpacity(riserLeft, structure * 0.74);
  setOpacity(shelfTop, structure * 0.72);
  setOpacity(riserCenter, structure * 0.58);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const pulse = pulseWave(progress, 1.1);

  setDot(points.center, 18 + pulse * 1.6, 76 + pulse * 10, 1, 0.22 + pulse * 0.14);
  setOpacity(switchbackBase, 0.14 * (1 - settle));
  setPathWindow(switchbackTrace, SWITCHBACK_TRACE_LENGTH, SWITCHBACK_TRACE_LENGTH, 0.72 - settle * 0.12);

  setOpacity(shelfMiddle, 0.9);
  setOpacity(riserRight, 0.82);
  setOpacity(shelfBottom, 0.82);
  setOpacity(riserLeft, 0.84);
  setOpacity(shelfTop, 0.82);
  setOpacity(riserCenter, 0.66);

  setOpacity(resolutionFrame, 0.32 + settle * 0.44);
  setOpacity(resolutionHalo, 0.18 + settle * 0.18 + pulse * 0.06);
}

function renderScene(info) {
  resetScene();
  updatePhaseLabel(info);
  applySceneOffset(info.phase.id);
  applyFraming(info.phase.id);

  switch (info.phase.id) {
    case "appearance":
      renderAppearance(info.localProgress);
      break;
    case "search":
      renderSearch(info.localProgress);
      break;
    case "tension":
      renderTension(info.localProgress);
      break;
    case "transformation":
      renderTransformation(info.localProgress);
      break;
    case "resolution":
      renderResolution(info.localProgress);
      break;
    default:
      break;
  }
}

function setElapsed(elapsed) {
  state.currentElapsed = clamp(elapsed, 0, TOTAL_DURATION);
  renderScene(phaseForElapsed(state.currentElapsed));
}

function update(now) {
  if (state.playing) {
    const elapsed = now - state.startAt + state.elapsedBeforePause;
    if (elapsed >= TOTAL_DURATION) {
      if (state.looping) {
        state.startAt = now;
        state.elapsedBeforePause = 0;
        setElapsed(elapsed % TOTAL_DURATION);
      } else {
        state.playing = false;
        state.elapsedBeforePause = TOTAL_DURATION;
        setElapsed(TOTAL_DURATION);
      }
    } else {
      setElapsed(elapsed);
    }
  }
  window.requestAnimationFrame(update);
}

function play() {
  if (state.playing) return;
  state.playing = true;
  state.startAt = performance.now();
}

function pause() {
  if (!state.playing) return;
  state.playing = false;
  state.elapsedBeforePause = state.currentElapsed;
}

function toggle() {
  if (state.playing) {
    pause();
  } else {
    play();
  }
}

function reset() {
  state.elapsedBeforePause = 0;
  state.startAt = performance.now();
  state.playing = true;
  setElapsed(0);
}

function seek(ms) {
  state.elapsedBeforePause = clamp(ms, 0, TOTAL_DURATION);
  state.startAt = performance.now();
  if (!state.playing) {
    setElapsed(state.elapsedBeforePause);
  }
}

function setLooping(value) {
  state.looping = Boolean(value);
}

function getState() {
  return {
    playing: state.playing,
    elapsed: Math.round(state.currentElapsed),
    phase: phaseForElapsed(state.currentElapsed).phase.id,
    looping: state.looping,
  };
}

window.__RED_DOT_APP = {
  play,
  pause,
  toggle,
  reset,
  seek,
  setLooping,
  getState,
};

window.addEventListener("resize", () => {
  applyLayout();
  renderScene(phaseForElapsed(state.currentElapsed));
});

window.addEventListener("keydown", (event) => {
  if (event.code === "Space") {
    event.preventDefault();
    toggle();
  }
  if (event.key.toLowerCase() === "r") {
    event.preventDefault();
    reset();
  }
});

applyLayout();
setElapsed(0);
window.__RED_DOT_READY = true;
window.requestAnimationFrame(update);
