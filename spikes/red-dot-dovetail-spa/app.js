const TOTAL_DURATION = 35_000;
const PHASES = [
  { id: "appearance", label: "appearance", duration: 6_000 },
  { id: "search", label: "search for form", duration: 7_500 },
  { id: "tension", label: "tension", duration: 6_000 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 8_500 },
];

const svg = document.getElementById("stage");
const sceneRoot = document.getElementById("scene-root");
const phaseLabel = document.getElementById("phase-label");

const dotCore = document.getElementById("dot-core");
const dotHalo = document.getElementById("dot-halo");
const futureGhost = document.getElementById("future-ghost");
const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");

const searchGroup = document.getElementById("search-group");
const candidateLeft = document.getElementById("candidate-left");
const candidateTop = document.getElementById("candidate-top");
const candidateRight = document.getElementById("candidate-right");
const candidateLeftAccent = document.getElementById("candidate-left-accent");
const candidateTopAccent = document.getElementById("candidate-top-accent");
const candidateRightAccent = document.getElementById("candidate-right-accent");

const tensionGroup = document.getElementById("tension-group");
const leftHalf = document.getElementById("left-half");
const rightHalf = document.getElementById("right-half");
const leftHalfRed = document.getElementById("left-half-red");
const rightHalfRed = document.getElementById("right-half-red");
const centerGuide = document.getElementById("center-guide");
const cornerBrackets = document.getElementById("corner-brackets");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c36b7d",
  gray: "#a6a6a6",
  lineGray: "#d2d2d2",
};

const points = {
  start: { x: 468, y: 468 },
  searchLeft: { x: 610, y: 425 },
  searchTop: { x: 836, y: 368 },
  searchRight: { x: 1008, y: 416 },
  pressure: { x: 820, y: 468 },
  final: { x: 820, y: 450 },
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

function setStroke(element, color) {
  element.setAttribute("stroke", color);
}

function setCircleCenter(element, point) {
  element.setAttribute("cx", point.x.toFixed(2));
  element.setAttribute("cy", point.y.toFixed(2));
}

function setTransform(element, point, scaleX = 1, scaleY = 1) {
  element.setAttribute(
    "transform",
    `translate(${point.x} ${point.y}) scale(${scaleX} ${scaleY}) translate(${-point.x} ${-point.y})`,
  );
}

function setTranslate(element, x, y) {
  element.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
}

function setTrailSegment(startFraction, endFraction, opacity) {
  const start = clamp(startFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const end = clamp(endFraction, 0, 1) * ACTIVE_TRAIL_LENGTH;
  const visible = Math.max(0, end - start);
  activeTrail.style.strokeDasharray = `${visible.toFixed(2)} ${(ACTIVE_TRAIL_LENGTH + visible + 120).toFixed(2)}`;
  activeTrail.style.strokeDashoffset = `${(-start).toFixed(2)}`;
  setOpacity(activeTrail, opacity);
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

function applyLayout() {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 1.02) {
    const intensity = clamp((1.02 - viewportRatio) / 0.56, 0, 1);
    const scale = lerp(1.18, 1.56, intensity);
    sceneRoot.setAttribute(
      "transform",
      `translate(800 450) scale(${scale.toFixed(3)}) translate(-800 -450)`,
    );
    svg.dataset.layout = "portrait";
  } else {
    sceneRoot.setAttribute("transform", "");
    svg.dataset.layout = "landscape";
  }
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

function setCandidateAccent(activeId) {
  setStroke(candidateLeftAccent, activeId === "left" ? COLORS.primaryRed : activeId === "past-left" ? COLORS.mutedRed : COLORS.lineGray);
  setStroke(candidateTopAccent, activeId === "top" ? COLORS.primaryRed : activeId === "past-top" ? COLORS.mutedRed : COLORS.lineGray);
  setStroke(candidateRightAccent, activeId === "right" ? COLORS.primaryRed : COLORS.lineGray);
}

function resetScene() {
  applyDot(points.start, 18, 74, 0, 0);
  setOpacity(futureGhost, 0);
  setOpacity(narrativeSpine, 0);
  setTrailSegment(0, 0, 0);

  setOpacity(searchGroup, 0);
  setOpacity(candidateLeft, 0);
  setOpacity(candidateTop, 0);
  setOpacity(candidateRight, 0);
  setCandidateAccent("");

  setOpacity(tensionGroup, 0);
  setTranslate(leftHalf, -74, 0);
  setTranslate(rightHalf, 74, 0);
  setOpacity(leftHalfRed, 0);
  setOpacity(rightHalfRed, 0);
  setOpacity(centerGuide, 0);
  setOpacity(cornerBrackets, 0);
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  const ghostOpacity = clamp((progress - 0.12) * 0.28, 0, 0.18);

  applyDot(points.start, lerp(4, 18, eased), lerp(16, 74, eased), clamp(progress * 1.8, 0, 1), 0.16 + pulseWave(progress, 1.2) * 0.14);
  setOpacity(futureGhost, ghostOpacity);
  setOpacity(narrativeSpine, clamp((progress - 0.10) * 0.44, 0, 0.24));
  setTrailSegment(0, 0, 0);

  setOpacity(searchGroup, clamp((progress - 0.28) * 0.28, 0, 0.16));
  setOpacity(candidateLeft, clamp((progress - 0.34) * 0.3, 0, 0.16));
  setOpacity(candidateTop, clamp((progress - 0.48) * 0.26, 0, 0.14));
  setOpacity(candidateRight, clamp((progress - 0.60) * 0.24, 0, 0.12));
}

function renderSearch(progress) {
  let position = points.searchLeft;
  let scaleX = 1;
  let scaleY = 1;
  let active = "left";
  let trailEnd = 0.18;

  if (progress < 0.34) {
    const t = easeInOut(progress / 0.34);
    position = mixPoint(points.start, points.searchLeft, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.08, t);
    active = "left";
    trailEnd = lerp(0, 0.26, t);
  } else if (progress < 0.68) {
    const t = easeInOut((progress - 0.34) / 0.34);
    position = mixPoint(points.searchLeft, points.searchTop, t);
    scaleX = lerp(0.92, 1.06, t);
    scaleY = lerp(1.08, 0.94, t);
    active = t < 0.54 ? "past-left" : "top";
    trailEnd = lerp(0.26, 0.62, t);
  } else if (progress < 0.92) {
    const t = easeInOut((progress - 0.68) / 0.24);
    position = mixPoint(points.searchTop, points.searchRight, t);
    scaleX = lerp(1.06, 1.12, t);
    scaleY = lerp(0.94, 0.92, t);
    active = t < 0.42 ? "past-top" : "right";
    trailEnd = lerp(0.62, 0.82, t);
  } else {
    const t = easeInOut((progress - 0.92) / 0.08);
    position = mixPoint(points.searchRight, points.pressure, t);
    scaleX = lerp(1.12, 0.98, t);
    scaleY = lerp(0.92, 1.06, t);
    active = "right";
    trailEnd = lerp(0.82, 1, t);
  }

  applyDot(position, 18.5, 84, 1, 0.3 + pulseWave(progress, 2.2) * 0.14, scaleX, scaleY);
  setOpacity(futureGhost, 0.18);
  setOpacity(narrativeSpine, 0.22);
  setTrailSegment(0, trailEnd, 0.7);

  setOpacity(searchGroup, 1);
  setOpacity(candidateLeft, 0.82);
  setOpacity(candidateTop, 0.78);
  setOpacity(candidateRight, 0.86);
  setCandidateAccent(active);
}

function renderTension(progress) {
  const moveIn = progress < 0.34 ? easeOut(progress / 0.34) : 1;
  const release = progress > 0.82 ? easeInOut((progress - 0.82) / 0.18) : 0;
  const leftOffset = lerp(-74, -10, moveIn) + release * 10;
  const rightOffset = lerp(74, 10, moveIn) - release * 10;
  const squeeze = progress < 0.42 ? easeOut(progress / 0.42) : progress < 0.76 ? 1 : 1 - easeInOut((progress - 0.76) / 0.24);
  const guideOpacity = 0.22 + squeeze * 0.34;

  applyDot(
    points.pressure,
    18,
    lerp(92, 118, squeeze),
    1,
    0.28 + squeeze * 0.12,
    lerp(1.02, 1.58, squeeze),
    lerp(0.98, 0.72, squeeze),
  );
  setOpacity(futureGhost, 0.12);
  setOpacity(searchGroup, clamp(0.24 - progress * 0.28, 0, 1));
  setOpacity(narrativeSpine, 0.16);
  setTrailSegment(0.32, 1, 0.24);

  setOpacity(tensionGroup, 1);
  setTranslate(leftHalf, leftOffset, 0);
  setTranslate(rightHalf, rightOffset, 0);
  setOpacity(leftHalfRed, clamp((progress - 0.60) * 0.9, 0, 0.4));
  setOpacity(rightHalfRed, clamp((progress - 0.60) * 0.9, 0, 0.4));
  setOpacity(centerGuide, guideOpacity);
  setOpacity(cornerBrackets, clamp((progress - 0.72) * 0.8, 0, 0.2));
}

function renderTransformation(progress) {
  const settle = easeOut(progress);
  const sideSettle = progress < 0.34 ? 1 - easeInOut(progress / 0.34) * 0.2 : 0.8;
  const guideFade = clamp(1 - Math.max(0, progress - 0.42) / 0.58, 0.16, 1);

  applyDot(
    mixPoint(points.pressure, points.final, settle),
    lerp(18, 18.5, progress),
    lerp(118, 106, progress),
    1,
    0.22 + pulseWave(progress, 2.1) * 0.1,
  );
  setOpacity(futureGhost, 0.08);
  setOpacity(searchGroup, 0);
  setOpacity(narrativeSpine, 0);
  setTrailSegment(0, 0, 0);

  setOpacity(tensionGroup, 1);
  setTranslate(leftHalf, lerp(-10, 0, settle * sideSettle), 0);
  setTranslate(rightHalf, lerp(10, 0, settle * sideSettle), 0);
  setOpacity(leftHalfRed, 0.42 + progress * 0.28);
  setOpacity(rightHalfRed, 0.42 + progress * 0.28);
  setOpacity(centerGuide, 0.46 * guideFade);
  setOpacity(cornerBrackets, clamp((progress - 0.18) * 1.1, 0, 0.9));
}

function renderResolution(progress) {
  const hold = easeInOut(progress);

  applyDot(points.final, 18.5, lerp(104, 86, progress), 1, 0.18 + pulseWave(progress, 1.6) * 0.06);
  setOpacity(futureGhost, 0);
  setOpacity(searchGroup, 0);
  setOpacity(narrativeSpine, 0);
  setTrailSegment(0, 0, 0);

  setOpacity(tensionGroup, 1);
  setTranslate(leftHalf, 0, 0);
  setTranslate(rightHalf, 0, 0);
  setOpacity(leftHalfRed, lerp(0.74, 0.62, hold));
  setOpacity(rightHalfRed, lerp(0.74, 0.62, hold));
  setOpacity(centerGuide, lerp(0.34, 0.26, hold));
  setOpacity(cornerBrackets, lerp(0.82, 0.7, hold));
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
  phaseLabel.textContent = info.phase.label;
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

function computeElapsed(now) {
  if (!state.playing) {
    return state.elapsedBeforePause;
  }

  const raw = state.elapsedBeforePause + (now - state.startAt);
  if (state.looping) {
    return raw % TOTAL_DURATION;
  }
  return Math.min(raw, TOTAL_DURATION - 1);
}

function tick(now) {
  const elapsed = computeElapsed(now);

  if (state.playing) {
    state.currentElapsed = elapsed;
    if (!state.looping && elapsed >= TOTAL_DURATION - 1) {
      state.elapsedBeforePause = TOTAL_DURATION - 1;
      state.currentElapsed = TOTAL_DURATION - 1;
      state.playing = false;
    }
  }

  render(state.currentElapsed);
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
    const nextElapsed = clamp(milliseconds, 0, TOTAL_DURATION - 1);
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
