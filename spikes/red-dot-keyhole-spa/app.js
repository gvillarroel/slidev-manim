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
const candidateRing = document.getElementById("candidate-ring");
const candidateSlot = document.getElementById("candidate-slot");
const candidateKeyhole = document.getElementById("candidate-keyhole");
const chamberGuide = document.getElementById("chamber-guide");
const slotGuide = document.getElementById("slot-guide");
const pressureHalo = document.getElementById("pressure-halo");
const slotLeftWall = document.getElementById("slot-left-wall");
const slotRightWall = document.getElementById("slot-right-wall");
const chamberShell = document.getElementById("chamber-shell");
const chamberBase = document.getElementById("chamber-base");
const chamberTrace = document.getElementById("chamber-trace");
const slotShell = document.getElementById("slot-shell");
const slotBase = document.getElementById("slot-base");
const slotTrace = document.getElementById("slot-trace");
const anchorGrid = document.getElementById("anchor-grid");
const resolutionHalo = document.getElementById("resolution-halo");
const resolutionFrame = document.getElementById("resolution-frame");
const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const CHAMBER_TRACE_LENGTH = chamberTrace.getTotalLength();
const SLOT_TRACE_LENGTH = slotTrace.getTotalLength();
const FULL_VIEWBOX = "0 0 1600 900";

const points = {
  start: { x: 424, y: 450 },
  ingress: { x: 642, y: 450 },
  ringCandidate: { x: 726, y: 394 },
  slotCandidate: { x: 856, y: 338 },
  keyholeCandidate: { x: 964, y: 394 },
  thresholdApproach: { x: 912, y: 470 },
  threshold: { x: 820, y: 502 },
  slotRelease: { x: 820, y: 432 },
  chamberCenter: { x: 820, y: 364 },
};

const keyhole = {
  leftWall: { x: 784, y: 492 },
  rightWall: { x: 856, y: 492 },
  squeezeLeftWall: { x: 804, y: 490 },
  squeezeRightWall: { x: 836, y: 490 },
  releaseLeftWall: { x: 790, y: 492 },
  releaseRightWall: { x: 850, y: 492 },
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

function windowedFade(progress, start, peak, end, maxOpacity = 1) {
  if (progress <= start || progress >= end) {
    return 0;
  }
  if (progress <= peak) {
    return clamp((progress - start) / Math.max(peak - start, 0.001), 0, 1) * maxOpacity;
  }
  return clamp(1 - (progress - peak) / Math.max(end - peak, 0.001), 0, 1) * maxOpacity;
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

function pointOnChamber(progress) {
  const length = clamp(progress, 0, 1) * CHAMBER_TRACE_LENGTH;
  const point = chamberTrace.getPointAtLength(length);
  return { x: point.x, y: point.y };
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
    appearance: { x: 18, y: 12 },
    search: { x: 0, y: 24 },
    tension: { x: 0, y: 8 },
    transformation: { x: 0, y: -4 },
    resolution: { x: 0, y: -2 },
  };
  const offset = offsets[phaseId] ?? { x: 0, y: 0 };
  sceneRoot.setAttribute("transform", `translate(${offset.x} ${offset.y})`);
}

function applyFraming(phaseId) {
  if (svg.dataset.layout !== "portrait") {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
    return;
  }

  const frames = {
    appearance: { x: 126, y: 142, width: 1092, height: 642 },
    search: { x: 136, y: 110, width: 1140, height: 674 },
    tension: { x: 342, y: 132, width: 956, height: 650 },
    transformation: { x: 354, y: 94, width: 936, height: 684 },
    resolution: { x: 392, y: 118, width: 872, height: 664 },
  };
  const frame = frames[phaseId] ?? { x: 0, y: 0, width: 1600, height: 900 };
  svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
}

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    layoutRoot.setAttribute(
      "transform",
      "translate(0 -16) translate(800 450) scale(1.04) translate(-800 -450)",
    );
    svg.dataset.layout = "portrait";
    svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
  } else {
    layoutRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  }
}

function resetScene() {
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);
  [searchGuideA, searchGuideB, searchGuideC].forEach((element) => setOpacity(element, 0));
  [candidateRing, candidateSlot, candidateKeyhole].forEach((element) => setOpacity(element, 0));
  [chamberGuide, slotGuide, pressureHalo].forEach((element) => setOpacity(element, 0));
  [slotLeftWall, slotRightWall, chamberShell, chamberBase, chamberTrace, slotShell, slotBase, slotTrace].forEach(
    (element) => setOpacity(element, 0),
  );
  [anchorGrid, resolutionHalo, resolutionFrame].forEach((element) => setOpacity(element, 0));

  setGroupTransform(candidateRing, points.ringCandidate.x, points.ringCandidate.y, 1, -10);
  setGroupTransform(candidateSlot, points.slotCandidate.x, points.slotCandidate.y, 1, 0);
  setGroupTransform(candidateKeyhole, points.keyholeCandidate.x, points.keyholeCandidate.y, 1, 10);
  setGroupTransform(slotLeftWall, keyhole.leftWall.x, keyhole.leftWall.y, 1, 0);
  setGroupTransform(slotRightWall, keyhole.rightWall.x, keyhole.rightWall.y, 1, 0);

  setPathWindow(chamberTrace, CHAMBER_TRACE_LENGTH, 0, 0);
  setPathWindow(slotTrace, SLOT_TRACE_LENGTH, 0, 0);
  setDot(points.start, 14, 72, 0, 0);
}

function renderAppearance(progress) {
  const placement = easeInOut(progress);
  const dotPosition = mixPoint(points.start, points.ingress, placement);

  setOpacity(narrativeSpine, lerp(0.12, 0.22, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * (0.58 * placement), 0.74);
  setDot(dotPosition, lerp(11, 16, progress), lerp(44, 88, progress), 1, lerp(0.1, 0.18, progress));

  setOpacity(chamberGuide, lerp(0.08, 0.14, progress));
  setOpacity(slotGuide, lerp(0.06, 0.12, progress));
  setOpacity(chamberShell, lerp(0.08, 0.16, progress));
  setOpacity(slotBase, lerp(0.08, 0.14, progress));
}

function renderSearch(progress) {
  const dotPosition = segmentedPoint(progress, [
    { start: 0, end: 0.26, from: points.ingress, to: points.ringCandidate },
    { start: 0.26, end: 0.58, from: points.ringCandidate, to: points.slotCandidate },
    { start: 0.58, end: 0.82, from: points.slotCandidate, to: points.keyholeCandidate },
    { start: 0.82, end: 1, from: points.keyholeCandidate, to: points.thresholdApproach },
  ]);

  setOpacity(narrativeSpine, 0.18);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * lerp(0.56, 1, progress), 0.72);
  setDot(dotPosition, 16, 90, 1, 0.18 + pulseWave(progress, 1.4) * 0.05);

  setOpacity(searchGuideA, windowedFade(progress, 0.02, 0.16, 0.42, 0.32));
  setOpacity(searchGuideB, windowedFade(progress, 0.22, 0.44, 0.74, 0.32));
  setOpacity(searchGuideC, windowedFade(progress, 0.48, 0.72, 0.98, 0.32));

  const ringOpacity = windowedFade(progress, 0.05, 0.18, 0.42, 0.96);
  const slotOpacity = windowedFade(progress, 0.24, 0.46, 0.72, 0.96);
  const keyholeOpacity = windowedFade(progress, 0.54, 0.72, 0.96, 0.98);
  setOpacity(candidateRing, ringOpacity);
  setOpacity(candidateSlot, slotOpacity);
  setOpacity(candidateKeyhole, keyholeOpacity);

  setGroupTransform(
    candidateRing,
    lerp(points.ringCandidate.x - 4, points.ringCandidate.x + 4, pulseWave(progress, 0.8)),
    lerp(points.ringCandidate.y + 8, points.ringCandidate.y - 4, easeOut(clamp(progress / 0.36, 0, 1))),
    lerp(0.92, 1, clamp(progress / 0.32, 0, 1)),
    lerp(-12, -4, clamp(progress / 0.28, 0, 1)),
  );
  setGroupTransform(
    candidateSlot,
    points.slotCandidate.x,
    lerp(points.slotCandidate.y + 10, points.slotCandidate.y - 6, easeOut(clamp((progress - 0.2) / 0.34, 0, 1))),
    lerp(0.9, 1, clamp((progress - 0.2) / 0.34, 0, 1)),
    0,
  );
  setGroupTransform(
    candidateKeyhole,
    lerp(points.keyholeCandidate.x + 6, points.keyholeCandidate.x - 4, easeOut(clamp((progress - 0.5) / 0.34, 0, 1))),
    lerp(points.keyholeCandidate.y + 10, points.keyholeCandidate.y - 2, easeOut(clamp((progress - 0.5) / 0.34, 0, 1))),
    lerp(0.9, 1, clamp((progress - 0.5) / 0.34, 0, 1)),
    lerp(10, 2, clamp((progress - 0.5) / 0.34, 0, 1)),
  );

  setOpacity(chamberGuide, lerp(0.1, 0.18, clamp((progress - 0.34) / 0.66, 0, 1)));
  setOpacity(slotGuide, lerp(0.08, 0.2, clamp((progress - 0.38) / 0.62, 0, 1)));
  setOpacity(chamberShell, lerp(0.08, 0.14, clamp((progress - 0.42) / 0.58, 0, 1)));
  setOpacity(slotBase, lerp(0.08, 0.16, clamp((progress - 0.48) / 0.52, 0, 1)));
}

function renderTension(progress) {
  const squeeze = easeInOut(clamp(progress / 0.58, 0, 1));
  const trailOpacity = clamp(0.14 - progress * 0.42, 0, 0.14);
  const dotPosition = {
    x: points.threshold.x,
    y: lerp(points.threshold.y, 486, squeeze),
  };

  setOpacity(narrativeSpine, lerp(0.12, 0.02, progress));
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH * lerp(1, 0.8, clamp(progress / 0.32, 0, 1)), trailOpacity);
  setDot(
    dotPosition,
    lerp(16, 18, progress),
    lerp(92, 122, progress),
    1,
    0.22 + pulseWave(progress, 1.1) * 0.12,
    lerp(1, 0.58, squeeze),
    lerp(1, 1.24, squeeze),
  );

  [searchGuideA, searchGuideB, searchGuideC].forEach((element) => setOpacity(element, clamp((0.18 - progress) * 1.5, 0, 0.18)));
  setOpacity(candidateRing, clamp((0.14 - progress) * 4.8, 0, 0.42));
  setOpacity(candidateSlot, clamp((0.18 - progress) * 4.2, 0, 0.48));
  setOpacity(candidateKeyhole, clamp((0.22 - progress) * 3.8, 0, 0.54));

  setOpacity(chamberGuide, lerp(0.16, 0.24, progress));
  setOpacity(slotGuide, lerp(0.22, 0.34, progress));
  setOpacity(pressureHalo, lerp(0.12, 0.3, progress));

  setGroupTransform(
    slotLeftWall,
    lerp(keyhole.leftWall.x, keyhole.squeezeLeftWall.x, squeeze),
    lerp(keyhole.leftWall.y, keyhole.squeezeLeftWall.y, squeeze),
    1.02,
    0,
  );
  setGroupTransform(
    slotRightWall,
    lerp(keyhole.rightWall.x, keyhole.squeezeRightWall.x, squeeze),
    lerp(keyhole.rightWall.y, keyhole.squeezeRightWall.y, squeeze),
    1.02,
    0,
  );
  setOpacity(slotLeftWall, 0.92);
  setOpacity(slotRightWall, 0.92);

  setOpacity(chamberShell, clamp((progress - 0.12) * 1.3, 0, 0.48));
  setOpacity(chamberBase, clamp((progress - 0.04) * 1.1, 0, 0.26));
  setOpacity(slotShell, clamp((progress - 0.08) * 1.6, 0, 0.74));
  setOpacity(slotBase, clamp((progress - 0.02) * 1.1, 0, 0.22));
}

function renderTransformation(progress) {
  const release = easeOut(clamp(progress / 0.24, 0, 1));
  const ringProgress = clamp((progress - 0.24) / 0.54, 0, 1);
  const settle = easeOut(clamp((progress - 0.82) / 0.18, 0, 1));

  let dotPosition = mixPoint({ x: 820, y: 486 }, points.slotRelease, release);
  if (progress > 0.24 && progress <= 0.82) {
    dotPosition = pointOnChamber(ringProgress);
  } else if (progress > 0.82) {
    dotPosition = mixPoint(pointOnChamber(1), points.chamberCenter, settle);
  }

  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, ACTIVE_TRAIL_LENGTH, clamp(0.08 - progress * 0.2, 0, 0.08));
  setDot(
    dotPosition,
    16,
    lerp(108, 96, settle),
    1,
    lerp(0.24, 0.18, settle) + pulseWave(progress, 1.2) * 0.06,
    lerp(0.58, 1, release),
    lerp(1.24, 1, release),
  );

  [searchGuideA, searchGuideB, searchGuideC, candidateRing, candidateSlot, candidateKeyhole].forEach((element) => setOpacity(element, 0));
  setOpacity(chamberGuide, clamp(1 - progress / 0.48, 0, 1) * 0.18);
  setOpacity(slotGuide, clamp(1 - progress / 0.42, 0, 1) * 0.24);
  setOpacity(pressureHalo, clamp(1 - progress / 0.46, 0, 1) * 0.26);

  setGroupTransform(
    slotLeftWall,
    lerp(keyhole.squeezeLeftWall.x, keyhole.releaseLeftWall.x, easeOut(clamp(progress / 0.5, 0, 1))),
    keyhole.releaseLeftWall.y,
    1,
    0,
  );
  setGroupTransform(
    slotRightWall,
    lerp(keyhole.squeezeRightWall.x, keyhole.releaseRightWall.x, easeOut(clamp(progress / 0.5, 0, 1))),
    keyhole.releaseRightWall.y,
    1,
    0,
  );
  setOpacity(slotLeftWall, clamp(0.9 - progress * 1.2, 0, 0.9));
  setOpacity(slotRightWall, clamp(0.9 - progress * 1.2, 0, 0.9));

  setOpacity(chamberShell, lerp(0.46, 0.96, easeOut(progress)));
  setOpacity(chamberBase, lerp(0.18, 0.28, easeOut(progress)));
  setOpacity(slotShell, lerp(0.74, 0.94, easeOut(progress)));
  setOpacity(slotBase, lerp(0.22, 0.32, easeOut(progress)));

  const slotTraceProgress = clamp(progress / 0.38, 0, 1);
  const chamberTraceOpacity = ringProgress > 0 ? lerp(0.36, 0.94, ringProgress) : 0;
  setPathWindow(slotTrace, SLOT_TRACE_LENGTH, SLOT_TRACE_LENGTH * slotTraceProgress, lerp(0.32, 0.86, slotTraceProgress));
  setPathWindow(
    chamberTrace,
    CHAMBER_TRACE_LENGTH,
    CHAMBER_TRACE_LENGTH * ringProgress,
    ringProgress > 0 ? chamberTraceOpacity : 0,
  );

  setOpacity(anchorGrid, clamp((progress - 0.72) * 1.4, 0, 0.12));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.3, 0, 0.18));
  setOpacity(resolutionFrame, clamp((progress - 0.8) * 1.5, 0, 0.28));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  const holdPulse = 0.16 + pulseWave(progress, 1.3) * 0.05;

  setOpacity(narrativeSpine, 0);
  setDot(points.chamberCenter, 16, 96, 1, holdPulse);

  [searchGuideA, searchGuideB, searchGuideC, candidateRing, candidateSlot, candidateKeyhole, chamberGuide, slotGuide, pressureHalo].forEach(
    (element) => setOpacity(element, 0),
  );
  setOpacity(slotLeftWall, 0);
  setOpacity(slotRightWall, 0);

  setOpacity(chamberShell, lerp(0.96, 0.92, settle));
  setOpacity(chamberBase, lerp(0.28, 0.22, settle));
  setOpacity(slotShell, lerp(0.94, 0.9, settle));
  setOpacity(slotBase, lerp(0.32, 0.24, settle));
  setPathWindow(chamberTrace, CHAMBER_TRACE_LENGTH, CHAMBER_TRACE_LENGTH, lerp(0.32, 0.14, settle));
  setPathWindow(slotTrace, SLOT_TRACE_LENGTH, SLOT_TRACE_LENGTH, lerp(0.26, 0.1, settle));

  setOpacity(anchorGrid, lerp(0.12, 0.16, settle));
  setOpacity(resolutionHalo, lerp(0.18, 0.28, settle));
  setOpacity(resolutionFrame, lerp(0.28, 0.66, settle));
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
