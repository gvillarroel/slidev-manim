const TOTAL_DURATION = 35_400;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_400 },
  { id: "search", label: "search for form", duration: 6_600 },
  { id: "tension", label: "tension", duration: 7_200 },
  { id: "transformation", label: "transformation", duration: 7_200 },
  { id: "resolution", label: "resolution", duration: 9_000 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");
const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const searchOrbit = document.getElementById("search-orbit");
const searchZigzag = document.getElementById("search-zigzag");
const searchWave = document.getElementById("search-wave");
const searchEchoTop = document.getElementById("search-echo-top");
const searchEchoMid = document.getElementById("search-echo-mid");
const searchEchoBottom = document.getElementById("search-echo-bottom");
const searchArcTop = document.getElementById("search-arc-top");
const searchArcMid = document.getElementById("search-arc-mid");
const searchArcBottom = document.getElementById("search-arc-bottom");

const tensionGroup = document.getElementById("tension-group");
const pressTop = document.getElementById("press-top");
const pressBottom = document.getElementById("press-bottom");
const guideLane = document.getElementById("guide-lane");
const compressionSlot = document.getElementById("compression-slot");
const energyBandTop = document.getElementById("energy-band-top");
const energyBandMid = document.getElementById("energy-band-mid");
const energyBandBottom = document.getElementById("energy-band-bottom");
const pressureRing = document.getElementById("pressure-ring");

const transformRig = document.getElementById("transform-rig");
const futureGroup = document.getElementById("future-group");
const slotTop = document.getElementById("slot-top");
const slotBottom = document.getElementById("slot-bottom");
const springGuideTop = document.getElementById("spring-guide-top");
const springGuideBottom = document.getElementById("spring-guide-bottom");

const transformGroup = document.getElementById("transform-group");
const anchorTop = document.getElementById("anchor-top");
const anchorBottom = document.getElementById("anchor-bottom");
const braceLeft = document.getElementById("brace-left");
const braceRight = document.getElementById("brace-right");
const springTop = document.getElementById("spring-top");
const springBottom = document.getElementById("spring-bottom");
const springAura = document.getElementById("spring-aura");
const springCenterRing = document.getElementById("spring-center-ring");

const resolutionGroup = document.getElementById("resolution-group");
const resolutionTopCap = document.getElementById("resolution-top-cap");
const resolutionBottomCap = document.getElementById("resolution-bottom-cap");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const SPRING_TOP_LENGTH = springTop.getTotalLength();
const SPRING_BOTTOM_LENGTH = springBottom.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  highlightRed: "#ffccd5",
  passiveGray: "#b5b5b5",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 344, y: 450 },
  searchTop: { x: 520, y: 302 },
  searchMid: { x: 668, y: 424 },
  searchBottom: { x: 584, y: 610 },
  clampEntry: { x: 760, y: 468 },
  clampCenter: { x: 860, y: 468 },
  clampExit: { x: 968, y: 468 },
  springHub: { x: 1100, y: 450 },
  finalCenter: { x: 820, y: 450 },
};

const state = {
  playing: true,
  looping: true,
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

function setOpacity(element, value) {
  element.setAttribute("opacity", clamp(value, 0, 1).toFixed(3));
}

function setCircleCenter(element, { x, y }) {
  element.setAttribute("cx", x.toFixed(2));
  element.setAttribute("cy", y.toFixed(2));
}

function setTransform(element, { x, y }, scaleX = 1, scaleY = 1) {
  element.setAttribute(
    "transform",
    `translate(${x} ${y}) scale(${scaleX} ${scaleY}) translate(${-x} ${-y})`,
  );
}

function setRectY(element, y, height) {
  element.setAttribute("y", y.toFixed(2));
  element.setAttribute("height", height.toFixed(2));
}

function setRectX(element, x, width) {
  element.setAttribute("x", x.toFixed(2));
  element.setAttribute("width", width.toFixed(2));
}

function setLineSpan(element, centerX, halfWidth) {
  element.setAttribute("x1", (centerX - halfWidth).toFixed(2));
  element.setAttribute("x2", (centerX + halfWidth).toFixed(2));
}

function setStrokeColor(element, color) {
  element.setAttribute("stroke", color);
}

function revealPath(element, length, progress, opacity) {
  const clamped = clamp(progress, 0, 1);
  element.style.strokeDasharray = `${length.toFixed(2)}`;
  element.style.strokeDashoffset = `${((1 - clamped) * length).toFixed(2)}`;
  setOpacity(element, opacity);
}

function setTrailSegment(startFraction, endFraction, opacity) {
  const start = clamp(startFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const end = clamp(endFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const visible = Math.max(0, end - start);
  activeTrail.style.strokeDasharray = `${visible.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + visible + 120).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = `${(-start).toFixed(2)}`;
  setOpacity(activeTrail, opacity);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    const intensity = clamp((0.9 - viewportRatio) / 0.44, 0, 1);
    const scale = lerp(1.2, 1.96, intensity);
    const shiftY = lerp(-6, -22, intensity);
    svg.setAttribute("viewBox", "80 0 1440 900");
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    sceneRoot.setAttribute(
      "transform",
      `translate(800 450) scale(${scale.toFixed(3)}) translate(-800 -450) translate(0 ${shiftY.toFixed(2)})`,
    );
    svg.dataset.layout = "portrait";
  } else {
    svg.setAttribute("viewBox", "0 0 1600 900");
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
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
  dotCore.setAttribute("r", radius.toFixed(2));
  dotHalo.setAttribute("r", haloRadius.toFixed(2));
  setOpacity(dotCore, opacity);
  setOpacity(dotHalo, haloOpacity);
  setTransform(dotCore, position, scaleX, scaleY);
  setTransform(dotHalo, position, scaleX, scaleY);
}

function setSearchPalette(activeIndex) {
  setStrokeColor(
    searchOrbit,
    activeIndex === 0 ? COLORS.primaryRed : activeIndex > 0 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  setStrokeColor(
    searchZigzag,
    activeIndex === 1 ? COLORS.primaryRed : activeIndex > 1 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  setStrokeColor(
    searchWave,
    activeIndex === 2 ? COLORS.primaryRed : activeIndex > 2 ? COLORS.mutedRed : COLORS.passiveGray,
  );
  setStrokeColor(
    searchArcTop,
    activeIndex === 0 ? COLORS.primaryRed : activeIndex > 0 ? COLORS.mutedRed : COLORS.lineGray,
  );
  setStrokeColor(
    searchArcMid,
    activeIndex === 1 ? COLORS.primaryRed : activeIndex > 1 ? COLORS.mutedRed : COLORS.lineGray,
  );
  setStrokeColor(searchArcBottom, activeIndex >= 2 ? COLORS.primaryRed : COLORS.lineGray);
}

function resetScene() {
  applyDot(points.start, 18, 76, 0, 0);
  setOpacity(narrativeSpine, 0);
  setTrailSegment(0, 0, 0);

  [
    searchOrbit,
    searchZigzag,
    searchWave,
    searchEchoTop,
    searchEchoMid,
    searchEchoBottom,
    searchArcTop,
    searchArcMid,
    searchArcBottom,
    tensionGroup,
    futureGroup,
    transformGroup,
    resolutionGroup,
  ].forEach((element) => setOpacity(element, 0));

  setStrokeColor(searchOrbit, COLORS.passiveGray);
  setStrokeColor(searchZigzag, COLORS.passiveGray);
  setStrokeColor(searchWave, COLORS.passiveGray);
  setStrokeColor(searchArcTop, COLORS.lineGray);
  setStrokeColor(searchArcMid, COLORS.lineGray);
  setStrokeColor(searchArcBottom, COLORS.lineGray);

  setRectY(pressTop, 224, 162);
  setRectY(pressBottom, 550, 162);
  setRectX(compressionSlot, 814, 92);
  setLineSpan(energyBandTop, 860, 34);
  setLineSpan(energyBandMid, 860, 38);
  setLineSpan(energyBandBottom, 860, 34);
  pressureRing.setAttribute("r", "34");

  transformRig.setAttribute("transform", "");
  setOpacity(slotTop, 0);
  setOpacity(slotBottom, 0);
  setOpacity(springGuideTop, 0);
  setOpacity(springGuideBottom, 0);
  setOpacity(anchorTop, 0);
  setOpacity(anchorBottom, 0);
  setOpacity(braceLeft, 0);
  setOpacity(braceRight, 0);
  revealPath(springTop, SPRING_TOP_LENGTH, 0, 0);
  revealPath(springBottom, SPRING_BOTTOM_LENGTH, 0, 0);
  springAura.setAttribute("r", "104");
  springCenterRing.setAttribute("r", "62");
  setOpacity(springAura, 0);
  setOpacity(springCenterRing, 0);
  setTransform(anchorTop, { x: 1100, y: 279 }, 0.9, 0.9);
  setTransform(anchorBottom, { x: 1100, y: 621 }, 0.9, 0.9);

  setOpacity(resolutionTopCap, 0);
  setOpacity(resolutionBottomCap, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const dotOpacity = clamp(progress * 1.8, 0, 1);
  const haloPulse = 0.22 + pulseWave(progress, 1.2) * 0.16;

  applyDot(points.start, lerp(4, 19, eased), lerp(20, 84, eased), dotOpacity, dotOpacity * haloPulse);
  setOpacity(narrativeSpine, clamp((progress - 0.08) * 0.42, 0, 0.22));
  setTrailSegment(0, 0, 0);

  setOpacity(searchOrbit, clamp((progress - 0.18) * 0.62, 0, 0.24));
  setOpacity(searchZigzag, clamp((progress - 0.30) * 0.58, 0, 0.2));
  setOpacity(searchWave, clamp((progress - 0.42) * 0.54, 0, 0.18));
  setOpacity(searchArcTop, clamp((progress - 0.22) * 0.44, 0, 0.16));
  setOpacity(searchArcMid, clamp((progress - 0.36) * 0.4, 0, 0.13));
  setOpacity(searchArcBottom, clamp((progress - 0.48) * 0.36, 0, 0.1));

  setOpacity(futureGroup, clamp((progress - 0.18) * 0.18, 0, 0.09));
  setOpacity(slotTop, 0.05 + progress * 0.03);
  setOpacity(slotBottom, 0.05 + progress * 0.03);
  setOpacity(springGuideTop, clamp((progress - 0.24) * 0.12, 0, 0.06));
  setOpacity(springGuideBottom, clamp((progress - 0.24) * 0.12, 0, 0.06));
}

function renderSearch(progress) {
  let position = points.searchTop;
  let stretchX = 1;
  let stretchY = 1;
  let activeIndex = 0;

  if (progress < 0.28) {
    const t = easeInOut(progress / 0.28);
    position = mixPoint(points.start, points.searchTop, t);
    stretchX = lerp(1, 0.9, t);
    stretchY = lerp(1, 1.1, t);
    activeIndex = 0;
  } else if (progress < 0.58) {
    const t = easeInOut((progress - 0.28) / 0.3);
    position = mixPoint(points.searchTop, points.searchMid, t);
    stretchX = lerp(0.92, 1.12, t);
    stretchY = lerp(1.08, 0.9, t);
    activeIndex = 1;
  } else if (progress < 0.84) {
    const t = easeInOut((progress - 0.58) / 0.26);
    position = mixPoint(points.searchMid, points.searchBottom, t);
    stretchX = lerp(1.1, 0.92, t);
    stretchY = lerp(0.9, 1.12, t);
    activeIndex = 2;
  } else {
    const t = easeInOut((progress - 0.84) / 0.16);
    position = mixPoint(points.searchBottom, points.clampEntry, t);
    stretchX = lerp(0.92, 1.08, t);
    stretchY = lerp(1.12, 0.94, t);
    activeIndex = 3;
  }

  applyDot(position, 19, 86, 1, 0.34 + pulseWave(progress, 2.1) * 0.16, stretchX, stretchY);
  setOpacity(narrativeSpine, 0.26);
  setTrailSegment(0, 0.54 * progress, 0.82);

  setOpacity(searchOrbit, 0.7);
  setOpacity(searchZigzag, 0.66);
  setOpacity(searchWave, 0.62);
  setOpacity(searchArcTop, 0.58);
  setOpacity(searchArcMid, 0.56);
  setOpacity(searchArcBottom, 0.54);
  setSearchPalette(activeIndex);

  setOpacity(searchEchoTop, progress >= 0.24 ? 0.42 : 0);
  setOpacity(searchEchoMid, progress >= 0.52 ? 0.38 : 0);
  setOpacity(searchEchoBottom, progress >= 0.78 ? 0.34 : 0);

  setOpacity(futureGroup, 0.12);
  setOpacity(slotTop, 0.12);
  setOpacity(slotBottom, 0.12);
  setOpacity(springGuideTop, 0.08);
  setOpacity(springGuideBottom, 0.08);
}

function renderTension(progress) {
  const travel = progress < 0.22
    ? mixPoint(points.clampEntry, points.clampCenter, easeInOut(progress / 0.22))
    : progress < 0.76
      ? points.clampCenter
      : mixPoint(points.clampCenter, points.clampExit, easeInOut((progress - 0.76) / 0.24));

  const squeezeStrength = progress < 0.28
    ? easeOut(progress / 0.28)
    : progress < 0.74
      ? 1
      : 1 - easeInOut((progress - 0.74) / 0.26);
  const pressurePulse = progress > 0.28 && progress < 0.74
    ? (pulseWave((progress - 0.28) / 0.46, 2.8) - 0.5) * 10
    : 0;

  const gap = lerp(238, 82, squeezeStrength) + pressurePulse;
  const topY = 468 - gap / 2 - 162;
  const bottomY = 468 + gap / 2;
  const slotWidth = lerp(92, 66, squeezeStrength) - pressurePulse * 0.22;
  const bandHalf = lerp(36, 18, squeezeStrength) + pressurePulse * 0.4;

  applyDot(
    travel,
    19,
    lerp(88, 112, squeezeStrength),
    1,
    0.38 + squeezeStrength * 0.1,
    lerp(1.02, 1.78, squeezeStrength),
    lerp(0.98, 0.62, squeezeStrength),
  );
  setOpacity(narrativeSpine, 0.16);
  setTrailSegment(0.34, lerp(0.54, 0.76, progress), 0.78);

  setOpacity(searchOrbit, 0.14);
  setOpacity(searchZigzag, 0.14);
  setOpacity(searchWave, 0.12);
  setOpacity(searchEchoTop, 0.14);
  setOpacity(searchEchoMid, 0.12);
  setOpacity(searchEchoBottom, 0.1);
  setOpacity(searchArcTop, 0.12);
  setOpacity(searchArcMid, 0.1);
  setOpacity(searchArcBottom, 0.1);

  setOpacity(tensionGroup, 1);
  setRectY(pressTop, topY, 162);
  setRectY(pressBottom, bottomY, 162);
  setRectX(compressionSlot, 860 - slotWidth / 2, slotWidth);
  setLineSpan(energyBandTop, 860, bandHalf);
  setLineSpan(energyBandMid, 860, bandHalf + 4);
  setLineSpan(energyBandBottom, 860, bandHalf);
  setOpacity(energyBandTop, 0.18 + squeezeStrength * 0.18);
  setOpacity(energyBandMid, 0.24 + squeezeStrength * 0.26);
  setOpacity(energyBandBottom, 0.18 + squeezeStrength * 0.18);
  pressureRing.setAttribute("r", lerp(30, 44, squeezeStrength).toFixed(2));
  setOpacity(pressureRing, 0.22 + squeezeStrength * 0.22);
  setOpacity(guideLane, 0.42 + squeezeStrength * 0.1);

  setOpacity(futureGroup, 0.14);
  setOpacity(slotTop, 0.14);
  setOpacity(slotBottom, 0.14);
  setOpacity(springGuideTop, 0.1);
  setOpacity(springGuideBottom, 0.1);
}

function renderTransformation(progress) {
  const entryMove = progress < 0.22
    ? mixPoint(points.clampExit, points.springHub, easeOut(progress / 0.22))
    : points.springHub;
  const slotReveal = clamp((progress - 0.04) / 0.24, 0, 1);
  const springGrow = clamp((progress - 0.16) / 0.48, 0, 1);
  const anchorGrow = clamp((progress - 0.28) / 0.36, 0, 1);
  const braceGrow = clamp((progress - 0.42) / 0.26, 0, 1);

  applyDot(
    entryMove,
    lerp(19, 16.5, progress),
    lerp(96, 126, springGrow),
    1,
    0.28 + pulseWave(progress, 2.4) * 0.12,
  );
  setOpacity(narrativeSpine, 0.05);
  setTrailSegment(0.54, lerp(0.76, 0.92, progress), 0.22 + (1 - springGrow) * 0.06);

  setOpacity(searchOrbit, 0);
  setOpacity(searchZigzag, 0);
  setOpacity(searchWave, 0);
  setOpacity(searchEchoTop, 0);
  setOpacity(searchEchoMid, 0);
  setOpacity(searchEchoBottom, 0);
  setOpacity(searchArcTop, 0);
  setOpacity(searchArcMid, 0);
  setOpacity(searchArcBottom, 0);
  setOpacity(tensionGroup, 0.18 + (1 - progress) * 0.08);

  setOpacity(futureGroup, 0.14 + slotReveal * 0.34);
  setOpacity(slotTop, clamp(0.12 + slotReveal * 0.24 - anchorGrow * 0.14, 0, 0.34));
  setOpacity(slotBottom, clamp(0.12 + slotReveal * 0.24 - anchorGrow * 0.14, 0, 0.34));
  setOpacity(springGuideTop, 0.12 + slotReveal * 0.18);
  setOpacity(springGuideBottom, 0.12 + slotReveal * 0.18);

  setOpacity(transformGroup, 1);
  setOpacity(anchorTop, anchorGrow);
  setOpacity(anchorBottom, anchorGrow);
  setTransform(anchorTop, { x: 1100, y: 279 }, lerp(0.9, 1, easeOut(anchorGrow)), lerp(0.9, 1, easeOut(anchorGrow)));
  setTransform(anchorBottom, { x: 1100, y: 621 }, lerp(0.9, 1, easeOut(anchorGrow)), lerp(0.9, 1, easeOut(anchorGrow)));
  revealPath(springTop, SPRING_TOP_LENGTH, springGrow, 0.94);
  revealPath(springBottom, SPRING_BOTTOM_LENGTH, springGrow, 0.94);
  setOpacity(braceLeft, braceGrow * 0.86);
  setOpacity(braceRight, braceGrow * 0.86);
  springAura.setAttribute("r", lerp(72, 118, easeOut(springGrow)).toFixed(2));
  springCenterRing.setAttribute("r", lerp(42, 70, easeOut(springGrow)).toFixed(2));
  setOpacity(springAura, springGrow * 0.54);
  setOpacity(springCenterRing, 0.12 + springGrow * 0.2);
}

function renderResolution(progress) {
  const settle = easeInOut(progress);
  const shift = lerp(0, points.finalCenter.x - points.springHub.x, settle);
  const center = { x: points.springHub.x + shift, y: points.finalCenter.y };
  const haloPulse = 0.2 + pulseWave(progress, 1.6) * 0.08;

  applyDot(center, 16.5, lerp(118, 88, progress), 1, haloPulse);
  setOpacity(narrativeSpine, 0);
  setTrailSegment(0, 0, 0);

  setOpacity(tensionGroup, clamp(0.16 - easeOut(progress) * 0.22, 0, 1));
  transformRig.setAttribute("transform", `translate(${shift.toFixed(2)} 0)`);
  setOpacity(futureGroup, 0.18 - progress * 0.18);
  setOpacity(slotTop, clamp(0.12 - progress * 0.16, 0, 1));
  setOpacity(slotBottom, clamp(0.12 - progress * 0.16, 0, 1));
  setOpacity(springGuideTop, clamp(0.16 - progress * 0.2, 0, 1));
  setOpacity(springGuideBottom, clamp(0.16 - progress * 0.2, 0, 1));

  setOpacity(transformGroup, 1);
  setOpacity(anchorTop, 1);
  setOpacity(anchorBottom, 1);
  revealPath(springTop, SPRING_TOP_LENGTH, 1, 0.94);
  revealPath(springBottom, SPRING_BOTTOM_LENGTH, 1, 0.94);
  setOpacity(braceLeft, clamp(0.48 - progress * 0.18, 0.22, 1));
  setOpacity(braceRight, clamp(0.48 - progress * 0.18, 0.22, 1));
  springAura.setAttribute("r", lerp(118, 104, progress).toFixed(2));
  springCenterRing.setAttribute("r", lerp(70, 60, progress).toFixed(2));
  setOpacity(springAura, 0.22 + (1 - settle) * 0.16);
  setOpacity(springCenterRing, 0.18);

  setOpacity(resolutionGroup, 1);
  setOpacity(resolutionTopCap, 0.22 + settle * 0.12);
  setOpacity(resolutionBottomCap, 0.22 + settle * 0.12);
  resolutionTopCap.setAttribute("x1", (center.x - 52).toFixed(2));
  resolutionTopCap.setAttribute("x2", (center.x + 52).toFixed(2));
  resolutionBottomCap.setAttribute("x1", (center.x - 52).toFixed(2));
  resolutionBottomCap.setAttribute("x2", (center.x + 52).toFixed(2));
  resolutionTopCap.setAttribute("y1", "294");
  resolutionTopCap.setAttribute("y2", "294");
  resolutionBottomCap.setAttribute("y1", "606");
  resolutionBottomCap.setAttribute("y2", "606");
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

function currentElapsed(now) {
  const rawElapsed = state.playing
    ? state.elapsedBeforePause + (now - state.startAt)
    : state.elapsedBeforePause;

  if (state.looping) {
    return rawElapsed % TOTAL_DURATION;
  }

  return clamp(rawElapsed, 0, TOTAL_DURATION);
}

function tick(now) {
  const elapsed = currentElapsed(now);
  render(elapsed);

  if (!state.looping && state.playing && elapsed >= TOTAL_DURATION) {
    state.elapsedBeforePause = TOTAL_DURATION;
    state.currentElapsed = TOTAL_DURATION;
    state.playing = false;
  }

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
    const nextElapsed = clamp(milliseconds, 0, TOTAL_DURATION);
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
    if (!state.looping) {
      state.elapsedBeforePause = clamp(state.currentElapsed, 0, TOTAL_DURATION);
    }
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
