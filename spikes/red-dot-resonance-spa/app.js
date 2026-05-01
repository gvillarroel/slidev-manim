const TOTAL_DURATION = 32_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_000 },
  { id: "search", label: "search for form", duration: 6_500 },
  { id: "tension", label: "tension", duration: 6_500 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 7_000 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");
const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const searchRing = document.getElementById("search-ring");
const searchFrame = document.getElementById("search-frame");
const searchArch = document.getElementById("search-arch");
const searchEchoA = document.getElementById("search-echo-a");
const searchEchoB = document.getElementById("search-echo-b");
const searchEchoC = document.getElementById("search-echo-c");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");

const tensionGroup = document.getElementById("tension-group");
const shutterTop = document.getElementById("shutter-top");
const shutterBottom = document.getElementById("shutter-bottom");
const apertureFrame = document.getElementById("aperture-frame");
const compressionField = document.getElementById("compression-field");
const pullLeft = document.getElementById("pull-left");
const pullRight = document.getElementById("pull-right");

const systemRig = document.getElementById("system-rig");
const futureGroup = document.getElementById("future-group");
const transformGroup = document.getElementById("transform-group");
const hubRing = document.getElementById("hub-ring");
const weaveRing = document.getElementById("weave-ring");

const resolutionGroup = document.getElementById("resolution-group");
const finalShell = document.getElementById("final-shell");
const finalCoreRing = document.getElementById("final-core-ring");
const finalOrbit = document.getElementById("final-orbit");

const network = [
  {
    slot: document.getElementById("slot-top"),
    baseLine: document.getElementById("base-line-top"),
    activeLine: document.getElementById("active-line-top"),
    node: document.getElementById("node-top"),
    pulse: document.getElementById("pulse-top"),
    center: { x: 1060, y: 286 },
    start: 0.18,
    end: 0.34,
  },
  {
    slot: document.getElementById("slot-right"),
    baseLine: document.getElementById("base-line-right"),
    activeLine: document.getElementById("active-line-right"),
    node: document.getElementById("node-right"),
    pulse: document.getElementById("pulse-right"),
    center: { x: 1236, y: 450 },
    start: 0.34,
    end: 0.50,
  },
  {
    slot: document.getElementById("slot-bottom"),
    baseLine: document.getElementById("base-line-bottom"),
    activeLine: document.getElementById("active-line-bottom"),
    node: document.getElementById("node-bottom"),
    pulse: document.getElementById("pulse-bottom"),
    center: { x: 1060, y: 614 },
    start: 0.50,
    end: 0.66,
  },
  {
    slot: document.getElementById("slot-left"),
    baseLine: document.getElementById("base-line-left"),
    activeLine: document.getElementById("active-line-left"),
    node: document.getElementById("node-left"),
    pulse: document.getElementById("pulse-left"),
    center: { x: 890, y: 450 },
    start: 0.66,
    end: 0.82,
  },
];

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const FINAL_ORBIT_LENGTH = finalOrbit.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  highlightRed: "#ffccd5",
  passiveGray: "#b5b5b5",
  lineGray: "#cfcfcf",
  darkGray: "#4f4f4f",
};

const points = {
  start: { x: 340, y: 450 },
  searchA: { x: 510, y: 292 },
  searchB: { x: 664, y: 430 },
  searchC: { x: 544, y: 606 },
  gateEntry: { x: 760, y: 470 },
  gateCenter: { x: 860, y: 470 },
  gateExit: { x: 958, y: 470 },
  hub: { x: 1060, y: 450 },
  top: { x: 1060, y: 286 },
  right: { x: 1236, y: 450 },
  bottom: { x: 1060, y: 614 },
  left: { x: 890, y: 450 },
  finalCenter: { x: 820, y: 426 },
};

const travelSegments = [
  { from: points.hub, to: points.top },
  { from: points.top, to: points.right },
  { from: points.right, to: points.bottom },
  { from: points.bottom, to: points.left },
  { from: points.left, to: points.hub },
];

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

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 1.05) {
    const intensity = clamp((1.05 - viewportRatio) / 0.58, 0, 1);
    const scale = lerp(1.06, 1.30, intensity);
    const shiftY = lerp(-18, -70, intensity);
    sceneRoot.setAttribute(
      "transform",
      `translate(800 450) scale(${scale.toFixed(3)}) translate(-800 -450) translate(0 ${shiftY.toFixed(2)})`,
    );
    svg.dataset.layout = "portrait";
  } else {
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
}

function setOpacity(element, value) {
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
}

function setTransform(element, { x, y }, scaleX = 1, scaleY = 1) {
  element.setAttribute(
    "transform",
    `translate(${x} ${y}) scale(${scaleX} ${scaleY}) translate(${-x} ${-y})`,
  );
}

function setCircleCenter(element, { x, y }) {
  element.setAttribute("cx", x.toFixed(2));
  element.setAttribute("cy", y.toFixed(2));
}

function setCircleRadius(element, radius) {
  element.setAttribute("r", radius.toFixed(2));
}

function setRectY(element, y, height) {
  element.setAttribute("y", y.toFixed(2));
  element.setAttribute("height", height.toFixed(2));
}

function setRectX(element, x, width) {
  element.setAttribute("x", x.toFixed(2));
  element.setAttribute("width", width.toFixed(2));
}

function setStrokeColor(element, color) {
  element.setAttribute("stroke", color);
}

function setLineEnd(element, from, to, amount) {
  const point = mixPoint(from, to, clamp(amount, 0, 1));
  element.setAttribute("x1", from.x.toFixed(2));
  element.setAttribute("y1", from.y.toFixed(2));
  element.setAttribute("x2", point.x.toFixed(2));
  element.setAttribute("y2", point.y.toFixed(2));
}

function setTrailSegment(startFraction, endFraction, opacity) {
  const start = clamp(startFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const end = clamp(endFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const visible = Math.max(0, end - start);
  activeTrail.style.strokeDasharray = `${visible.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + visible + 120).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = `${(-start).toFixed(2)}`;
  setOpacity(activeTrail, opacity);
}

function setOrbitProgress(fraction, opacity) {
  const visible = clamp(fraction, 0, 1) * FINAL_ORBIT_LENGTH;
  finalOrbit.style.strokeDasharray = `${visible.toFixed(2)} ${(FINAL_ORBIT_LENGTH + 64).toFixed(2)}`;
  finalOrbit.style.strokeDashoffset = "0";
  setOpacity(finalOrbit, opacity);
}

function setGroupTranslation(group, xOffset, yOffset = 0) {
  group.setAttribute("transform", `translate(${xOffset.toFixed(2)} ${yOffset.toFixed(2)})`);
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

function updateStatus(info) {
  phaseLabel.textContent = info.phase.label;
}

function applyDot(position, radius, haloRadius, opacity, haloOpacity, scaleX = 1, scaleY = 1) {
  setCircleCenter(dotCore, position);
  setCircleCenter(dotHalo, position);
  setCircleRadius(dotCore, radius);
  setCircleRadius(dotHalo, haloRadius);
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  setTransform(dotCore, position, scaleX, scaleY);
  setTransform(dotHalo, position, scaleX, scaleY);
}

function setSearchPalette(activeIndex) {
  setStrokeColor(
    searchRing,
    activeIndex === 0 ? COLORS.primaryRed : activeIndex > 0 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  setStrokeColor(
    searchFrame,
    activeIndex === 1 ? COLORS.primaryRed : activeIndex > 1 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  setStrokeColor(
    searchArch,
    activeIndex === 2 ? COLORS.primaryRed : activeIndex > 2 ? COLORS.mutedRed : COLORS.passiveGray,
  );

  setStrokeColor(
    searchGuideA,
    activeIndex === 0 ? COLORS.primaryRed : activeIndex > 0 ? COLORS.mutedRed : COLORS.lineGray,
  );
  setStrokeColor(
    searchGuideB,
    activeIndex === 1 ? COLORS.primaryRed : activeIndex > 1 ? COLORS.mutedRed : COLORS.lineGray,
  );
  setStrokeColor(searchGuideC, activeIndex >= 2 ? COLORS.primaryRed : COLORS.lineGray);
}

function segmentProgress(progress, start, end) {
  return clamp((progress - start) / (end - start), 0, 1);
}

function travelPoint(progress) {
  const timeline = clamp((progress - 0.16) / 0.68, 0, 1) * travelSegments.length;
  const index = Math.min(Math.floor(timeline), travelSegments.length - 1);
  const local = clamp(timeline - index, 0, 1);
  const segment = travelSegments[index];
  return mixPoint(segment.from, segment.to, easeInOut(local));
}

function resetScene() {
  applyDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setTrailSegment(0, 0, 0);
  setOrbitProgress(0, 0);

  [
    searchRing,
    searchFrame,
    searchArch,
    searchEchoA,
    searchEchoB,
    searchEchoC,
    searchGuideA,
    searchGuideB,
    searchGuideC,
    tensionGroup,
    futureGroup,
    transformGroup,
    resolutionGroup,
  ].forEach((element) => setOpacity(element, 0));

  setStrokeColor(searchRing, COLORS.passiveGray);
  setStrokeColor(searchFrame, COLORS.passiveGray);
  setStrokeColor(searchArch, COLORS.passiveGray);
  setStrokeColor(searchGuideA, COLORS.lineGray);
  setStrokeColor(searchGuideB, COLORS.lineGray);
  setStrokeColor(searchGuideC, COLORS.lineGray);

  setRectY(shutterTop, 216, 156);
  setRectY(shutterBottom, 568, 156);
  setRectX(apertureFrame, 812, 96);
  compressionField.setAttribute("rx", "46");
  compressionField.setAttribute("ry", "28");
  setOpacity(compressionField, 0.22);
  setOpacity(pullLeft, 0.64);
  setOpacity(pullRight, 0.64);

  setGroupTranslation(systemRig, 0, 0);
  setCircleRadius(hubRing, 36);
  setCircleRadius(weaveRing, 92);
  setOpacity(weaveRing, 0);

  network.forEach(({ slot, baseLine, activeLine, node, pulse, center }) => {
    setOpacity(slot, 0);
    setOpacity(baseLine, 0);
    setOpacity(activeLine, 0);
    setOpacity(node, 0);
    setOpacity(pulse, 0);
    setLineEnd(activeLine, points.hub, center, 0);
    setCircleRadius(pulse, 16);
    setStrokeColor(slot, COLORS.passiveGray);
    setStrokeColor(baseLine, COLORS.lineGray);
    setStrokeColor(node, COLORS.darkGray);
  });

  setOpacity(finalShell, 0);
  setOpacity(finalCoreRing, 0);
  setCircleRadius(finalShell, 142);
  setCircleRadius(finalCoreRing, 74);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const dotOpacity = clamp(progress * 1.9, 0, 1);
  const haloPulse = 0.22 + pulseWave(progress, 1.3) * 0.18;

  applyDot(points.start, lerp(4, 18.5, eased), lerp(18, 82, eased), dotOpacity, haloPulse * dotOpacity);
  setOpacity(narrativeSpine, clamp((progress - 0.08) * 0.44, 0, 0.2));
  setTrailSegment(0, 0, 0);

  setOpacity(searchRing, clamp((progress - 0.18) * 0.62, 0, 0.24));
  setOpacity(searchFrame, clamp((progress - 0.32) * 0.54, 0, 0.2));
  setOpacity(searchArch, clamp((progress - 0.46) * 0.5, 0, 0.18));
  setOpacity(searchGuideA, clamp((progress - 0.24) * 0.42, 0, 0.14));
  setOpacity(searchGuideB, clamp((progress - 0.38) * 0.42, 0, 0.12));
  setOpacity(searchGuideC, clamp((progress - 0.52) * 0.38, 0, 0.1));

  setOpacity(futureGroup, clamp((progress - 0.24) * 0.18, 0, 0.08));
  network.forEach(({ slot, baseLine }) => {
    setOpacity(slot, 0.03 + progress * 0.02);
    setOpacity(baseLine, 0.02 + progress * 0.02);
  });
}

function renderSearch(progress) {
  let position = points.searchA;
  let stretchX = 1;
  let stretchY = 1;
  let activeIndex = 0;

  if (progress < 0.26) {
    const t = easeInOut(progress / 0.26);
    position = mixPoint(points.start, points.searchA, t);
    stretchX = lerp(1, 0.9, t);
    stretchY = lerp(1, 1.12, t);
    activeIndex = 0;
  } else if (progress < 0.56) {
    const t = easeInOut((progress - 0.26) / 0.3);
    position = mixPoint(points.searchA, points.searchB, t);
    stretchX = lerp(0.9, 1.1, t);
    stretchY = lerp(1.12, 0.9, t);
    activeIndex = 1;
  } else if (progress < 0.82) {
    const t = easeInOut((progress - 0.56) / 0.26);
    position = mixPoint(points.searchB, points.searchC, t);
    stretchX = lerp(1.1, 0.92, t);
    stretchY = lerp(0.9, 1.14, t);
    activeIndex = 2;
  } else {
    const t = easeInOut((progress - 0.82) / 0.18);
    position = mixPoint(points.searchC, points.gateEntry, t);
    stretchX = lerp(0.92, 1.08, t);
    stretchY = lerp(1.14, 0.92, t);
    activeIndex = 3;
  }

  applyDot(position, 19, 84, 1, 0.34 + pulseWave(progress, 2.2) * 0.16, stretchX, stretchY);
  setOpacity(narrativeSpine, 0.24);
  setTrailSegment(0, 0.34 + progress * 0.2, 0.8);

  setOpacity(searchRing, 0.72);
  setOpacity(searchFrame, 0.64);
  setOpacity(searchArch, 0.58);
  setOpacity(searchGuideA, 0.54);
  setOpacity(searchGuideB, 0.54);
  setOpacity(searchGuideC, 0.54);
  setSearchPalette(activeIndex);

  setOpacity(searchEchoA, progress >= 0.22 ? 0.42 : 0);
  setOpacity(searchEchoB, progress >= 0.54 ? 0.38 : 0);
  setOpacity(searchEchoC, progress >= 0.8 ? 0.34 : 0);

  setOpacity(futureGroup, 0.1);
  network.forEach(({ slot, baseLine }) => {
    setOpacity(slot, 0.08);
    setOpacity(baseLine, 0.06);
  });
}

function renderTension(progress) {
  const travel = progress < 0.24
    ? mixPoint(points.gateEntry, points.gateCenter, easeInOut(progress / 0.24))
    : progress < 0.74
      ? points.gateCenter
      : mixPoint(points.gateCenter, points.gateExit, easeInOut((progress - 0.74) / 0.26));

  const squeezeStrength = progress < 0.32
    ? easeOut(progress / 0.32)
    : progress < 0.72
      ? 1
      : 1 - easeInOut((progress - 0.72) / 0.28);
  const pressurePulse = progress > 0.32 && progress < 0.72
    ? (pulseWave((progress - 0.32) / 0.4, 2.6) - 0.5) * 12
    : 0;

  const gap = lerp(234, 76, squeezeStrength) + pressurePulse;
  const topY = 470 - gap / 2 - 156;
  const bottomY = 470 + gap / 2;
  const gateWidth = lerp(96, 58, squeezeStrength) - pressurePulse * 0.32;

  applyDot(
    travel,
    19,
    lerp(84, 106, squeezeStrength),
    1,
    0.38 + squeezeStrength * 0.1,
    lerp(1.02, 1.86, squeezeStrength),
    lerp(0.98, 0.62, squeezeStrength),
  );
  setOpacity(narrativeSpine, 0.16);
  setTrailSegment(0.36, lerp(0.44, 0.49, progress), 0.8);

  setOpacity(searchRing, 0.14);
  setOpacity(searchFrame, 0.12);
  setOpacity(searchArch, 0.06);
  setOpacity(searchEchoA, 0.14);
  setOpacity(searchEchoB, 0.12);
  setOpacity(searchEchoC, 0.04);
  setOpacity(searchGuideA, 0.1);
  setOpacity(searchGuideB, 0.1);
  setOpacity(searchGuideC, 0.04);

  setOpacity(tensionGroup, 1);
  setRectY(shutterTop, topY, 156);
  setRectY(shutterBottom, bottomY, 156);
  setRectX(apertureFrame, 860 - gateWidth / 2, gateWidth);
  compressionField.setAttribute("rx", lerp(46, 58, squeezeStrength).toFixed(2));
  compressionField.setAttribute("ry", lerp(28, 20, squeezeStrength).toFixed(2));
  setOpacity(compressionField, 0.2 + squeezeStrength * 0.24);
  setOpacity(pullLeft, 0.36 + squeezeStrength * 0.28);
  setOpacity(pullRight, 0.36 + squeezeStrength * 0.28);

  setOpacity(futureGroup, 0.08);
  network.forEach(({ slot, baseLine }) => {
    setOpacity(slot, 0.06);
    setOpacity(baseLine, 0.05);
  });
}

function renderTransformation(progress) {
  const entryToHub = clamp(progress / 0.16, 0, 1);
  const position = progress < 0.16 ? mixPoint(points.gateExit, points.hub, easeOut(entryToHub)) : travelPoint(progress);
  const ringGrow = clamp((progress - 0.08) / 0.18, 0, 1);
  const slotReveal = clamp((progress - 0.02) / 0.2, 0, 1);

  applyDot(
    position,
    lerp(18.5, 16.5, clamp(progress / 0.24, 0, 1)),
    lerp(92, 126, ringGrow),
    1,
    0.28 + pulseWave(progress, 2.4) * 0.12,
  );
  setOpacity(narrativeSpine, 0.06);
  setTrailSegment(0.48, lerp(0.68, 0.9, progress), 0.24 + (1 - ringGrow) * 0.08);

  setOpacity(searchRing, 0);
  setOpacity(searchFrame, 0);
  setOpacity(searchArch, 0);
  setOpacity(searchEchoA, 0);
  setOpacity(searchEchoB, 0);
  setOpacity(searchEchoC, 0);
  setOpacity(searchGuideA, 0);
  setOpacity(searchGuideB, 0);
  setOpacity(searchGuideC, 0);
  setOpacity(tensionGroup, 0.18 + (1 - progress) * 0.08);

  setOpacity(futureGroup, 0.18 + slotReveal * 0.34);
  setOpacity(transformGroup, 1);
  setCircleRadius(hubRing, lerp(36, 28, clamp((progress - 0.18) / 0.64, 0, 1)));
  setCircleRadius(weaveRing, lerp(64, 92, easeOut(ringGrow)));
  setOpacity(weaveRing, ringGrow * 0.56);

  network.forEach(({ slot, baseLine, activeLine, node, pulse, center, start, end }) => {
    const lineProgress = segmentProgress(progress, start, end);
    const nodeProgress = clamp(lineProgress * 1.35, 0, 1);
    const currentPulse = clamp(1 - Math.abs(progress - (start + end) / 2) / 0.1, 0, 1);

    setOpacity(slot, clamp(0.18 + slotReveal * 0.18 - nodeProgress * 0.14, 0, 0.36));
    setOpacity(baseLine, 0.2 + slotReveal * 0.22);
    setOpacity(activeLine, lineProgress > 0 ? 0.9 : 0);
    setOpacity(node, nodeProgress);
    setOpacity(pulse, currentPulse * 0.8);
    setLineEnd(activeLine, points.hub, center, easeOut(lineProgress));
    setCircleRadius(pulse, lerp(16, 28, currentPulse));
  });
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shiftX = lerp(0, points.finalCenter.x - points.hub.x, settle);
  const shiftY = lerp(0, points.finalCenter.y - points.hub.y, settle);
  const center = { x: points.hub.x + shiftX, y: points.finalCenter.y };
  const haloPulse = 0.2 + pulseWave(progress, 1.7) * 0.08;

  applyDot(center, 16, lerp(112, 86, progress), 1, haloPulse);
  setOpacity(narrativeSpine, 0);
  setTrailSegment(0, 0, 0);

  setOpacity(tensionGroup, clamp(0.12 - easeOut(progress) * 0.18, 0, 1));
  setGroupTranslation(systemRig, shiftX, shiftY);
  setOpacity(futureGroup, 0.42 - progress * 0.18);
  setOpacity(transformGroup, 1);
  setCircleRadius(hubRing, lerp(28, 26, settle));
  setCircleRadius(weaveRing, lerp(92, 74, settle));
  setOpacity(weaveRing, 0.14 + (1 - settle) * 0.14);

  network.forEach(({ slot, baseLine, activeLine, node, pulse, center: nodeCenter }) => {
    setOpacity(slot, clamp(0.18 - progress * 0.18, 0, 1));
    setOpacity(baseLine, 0.34 + settle * 0.18);
    setOpacity(activeLine, 0.56 - progress * 0.28);
    setOpacity(node, 1);
    setOpacity(pulse, 0);
    setLineEnd(activeLine, points.hub, nodeCenter, 1);
  });

  setOpacity(resolutionGroup, 1);
  setOpacity(finalShell, 0.28);
  setOpacity(finalCoreRing, 0.16);
  setCircleCenter(finalShell, center);
  setCircleCenter(finalCoreRing, center);
  setCircleRadius(finalShell, lerp(148, 138, progress));
  setCircleRadius(finalCoreRing, lerp(86, 72, progress));
  setOrbitProgress(0.24 + settle * 0.76, 0.32);
}

function render(elapsed) {
  resetScene();
  const info = phaseForElapsed(elapsed);

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
  updateStatus(info);
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
