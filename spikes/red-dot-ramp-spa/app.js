const TOTAL_DURATION = 36_000;
const CAPTURE_MODE = new URLSearchParams(window.location.search).get("capture") === "1";
const FULL_VIEWBOX = "0 0 1600 900";
const PHASES = [
  { id: "appearance", label: "appearance", duration: 5_200 },
  { id: "search", label: "search for form", duration: 6_500 },
  { id: "tension", label: "tension", duration: 6_200 },
  { id: "transformation", label: "transformation", duration: 7_000 },
  { id: "resolution", label: "resolution", duration: 11_100 },
];
const PORTRAIT_VIEWBOXES = {
  appearance: { x: 150, y: 148, width: 1220, height: 740 },
  search: { x: 250, y: 142, width: 1120, height: 760 },
  tension: { x: 454, y: 130, width: 760, height: 720 },
  transformation: { x: 446, y: 118, width: 760, height: 720 },
  resolution: { x: 430, y: 110, width: 772, height: 720 },
};

const svg = document.getElementById("stage");
const phaseLabel = document.getElementById("phase-label");

const narrativeSpine = document.getElementById("narrative-spine");
const activeTrail = document.getElementById("active-trail");
const searchGuideA = document.getElementById("search-guide-a");
const searchGuideB = document.getElementById("search-guide-b");
const searchGuideC = document.getElementById("search-guide-c");

const candidateGentle = document.getElementById("candidate-gentle");
const candidateStep = document.getElementById("candidate-step");
const candidateSteep = document.getElementById("candidate-steep");
const accentGentle = document.getElementById("accent-gentle");
const accentStep = document.getElementById("accent-step");
const accentSteep = document.getElementById("accent-steep");
const echoGentle = document.getElementById("echo-gentle");
const echoStep = document.getElementById("echo-step");
const echoSteep = document.getElementById("echo-steep");
const entryBracket = document.getElementById("entry-bracket");

const pressureHalo = document.getElementById("pressure-halo");
const rampAssembly = document.getElementById("ramp-assembly");
const rampGuide = document.getElementById("ramp-guide");
const rampRailLower = document.getElementById("ramp-rail-lower");
const rampRailUpper = document.getElementById("ramp-rail-upper");
const deck = document.getElementById("deck");
const baseLeft = document.getElementById("base-left");
const baseMid = document.getElementById("base-mid");
const supportRight = document.getElementById("support-right");
const stopper = document.getElementById("stopper");

const crestRouteBase = document.getElementById("crest-route-base");
const crestRouteActive = document.getElementById("crest-route-active");
const finalCorners = document.getElementById("final-corners");
const crosshair = document.getElementById("crosshair");
const resolutionHalo = document.getElementById("resolution-halo");

const dotHalo = document.getElementById("dot-halo");
const dotCore = document.getElementById("dot-core");

const ACTIVE_TRAIL_LENGTH = activeTrail.getTotalLength();
const CREST_ROUTE_LENGTH = crestRouteBase.getTotalLength();

const COLORS = {
  primaryRed: "#9e1b32",
  mutedRed: "#c97a89",
  lineGray: "#cfcfcf",
};

const points = {
  start: { x: 404, y: 500 },
  gentle: { x: 690, y: 412 },
  step: { x: 820, y: 450 },
  steep: { x: 1008, y: 506 },
  entry: { x: 736, y: 536 },
  rampMid: { x: 794, y: 480 },
  blocked: { x: 874, y: 402 },
  final: { x: 824, y: 396 },
};

const rampLayouts = {
  preview: { x: 972, y: 468, scale: 0.9 },
  search: { x: 964, y: 466, scale: 0.92 },
  tension: { x: 816, y: 452, scale: 1 },
  resolution: { x: 804, y: 448, scale: 0.92 },
};

const state = {
  playing: true,
  looping: !CAPTURE_MODE,
  startAt: performance.now(),
  elapsedBeforePause: 0,
  currentElapsed: 0,
};

let currentPhaseId = "appearance";

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

function setCircleCenter(element, point) {
  element.setAttribute("cx", point.x.toFixed(2));
  element.setAttribute("cy", point.y.toFixed(2));
}

function setTransform(element, point, scaleX = 1, scaleY = 1) {
  element.setAttribute(
    "transform",
    `translate(${point.x.toFixed(2)} ${point.y.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)}) translate(${-point.x.toFixed(2)} ${-point.y.toFixed(2)})`,
  );
}

function setTranslate(element, x, y) {
  element.setAttribute("transform", `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
}

function setGroupTransform(element, x, y, scaleX = 1, scaleY = scaleX) {
  element.setAttribute(
    "transform",
    `translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${scaleX.toFixed(3)} ${scaleY.toFixed(3)})`,
  );
}

function setPathWindow(element, totalLength, visibleLength, opacity) {
  const clampedLength = clamp(visibleLength, 0, totalLength);
  element.style.strokeDasharray = `${clampedLength.toFixed(2)} ${(totalLength + 240).toFixed(2)}`;
  element.style.strokeDashoffset = "0";
  setOpacity(element, opacity);
}

function pointOnPath(path, totalLength, progress) {
  const point = path.getPointAtLength(clamp(progress, 0, 1) * totalLength);
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

function applyLayout(phaseId = currentPhaseId) {
  const viewportRatio = window.innerWidth / window.innerHeight;
  if (viewportRatio < 0.9) {
    const frame = PORTRAIT_VIEWBOXES[phaseId] ?? PORTRAIT_VIEWBOXES.appearance;
    svg.setAttribute("viewBox", `${frame.x} ${frame.y} ${frame.width} ${frame.height}`);
  } else {
    svg.setAttribute("viewBox", FULL_VIEWBOX);
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

function setCandidateState(group, point, scale, opacity) {
  setGroupTransform(group, point.x, point.y, scale, scale);
  setOpacity(group, opacity);
}

function resetScene() {
  applyDot(points.start, 18, 78, 0, 0);
  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);

  [searchGuideA, searchGuideB, searchGuideC, echoGentle, echoStep, echoSteep, entryBracket].forEach((element) => {
    setOpacity(element, 0);
  });

  setCandidateState(candidateGentle, points.gentle, 1, 0);
  setCandidateState(candidateStep, points.step, 1, 0);
  setCandidateState(candidateSteep, points.steep, 1, 0);
  setOpacity(accentGentle, 0);
  setOpacity(accentStep, 0);
  setOpacity(accentSteep, 0);

  setCircleCenter(pressureHalo, points.blocked);
  pressureHalo.setAttribute("r", "136");
  setOpacity(pressureHalo, 0);

  setGroupTransform(rampAssembly, rampLayouts.preview.x, rampLayouts.preview.y, rampLayouts.preview.scale);
  [rampGuide, rampRailLower, rampRailUpper, deck, baseLeft, baseMid, supportRight, stopper].forEach((element) => {
    setOpacity(element, 0);
    setTranslate(element, 0, 0);
  });

  setOpacity(crestRouteBase, 0);
  setPathWindow(crestRouteActive, CREST_ROUTE_LENGTH, 0, 0);
  setOpacity(finalCorners, 0);
  setOpacity(crosshair, 0);
  setOpacity(resolutionHalo, 0);
  setCircleCenter(resolutionHalo, { x: 824, y: 430 });
}

function renderAppearance(progress) {
  const eased = easeOut(progress);
  applyDot(points.start, lerp(14, 20, eased), lerp(54, 82, eased), 0.74 + progress * 0.26, 0.18 + pulseWave(progress, 1.2) * 0.18);
  setOpacity(narrativeSpine, 0.18 + progress * 0.12);

  setCandidateState(candidateGentle, points.gentle, lerp(0.94, 1, eased), 0.18 + progress * 0.16);
  setOpacity(accentGentle, 0.26 + progress * 0.32);

  setGroupTransform(rampAssembly, rampLayouts.preview.x, rampLayouts.preview.y, rampLayouts.preview.scale);
  setOpacity(rampGuide, 0.12 + progress * 0.08);
  setOpacity(rampRailLower, 0.06 + progress * 0.05);
  setOpacity(rampRailUpper, 0.05 + progress * 0.04);
  setOpacity(deck, 0.06 + progress * 0.04);
  setOpacity(baseLeft, 0.05 + progress * 0.04);
  setOpacity(baseMid, 0.04 + progress * 0.04);
  setOpacity(entryBracket, 0.04 + progress * 0.06);
}

function renderSearch(progress) {
  let position = points.gentle;
  let scaleX = 1;
  let scaleY = 1;

  if (progress < 0.28) {
    const t = easeInOut(progress / 0.28);
    position = mixPoint(points.start, points.gentle, t);
    scaleX = lerp(1, 0.92, t);
    scaleY = lerp(1, 1.08, t);
  } else if (progress < 0.56) {
    const t = easeInOut((progress - 0.28) / 0.28);
    position = mixPoint(points.gentle, points.step, t);
    scaleX = lerp(0.92, 1.06, t);
    scaleY = lerp(1.08, 0.94, t);
  } else if (progress < 0.84) {
    const t = easeInOut((progress - 0.56) / 0.28);
    position = mixPoint(points.step, points.steep, t);
    scaleX = lerp(1.06, 0.96, t);
    scaleY = lerp(0.94, 1.1, t);
  } else {
    const t = easeInOut((progress - 0.84) / 0.16);
    position = mixPoint(points.steep, points.entry, t);
    scaleX = lerp(0.96, 1.08, t);
    scaleY = lerp(1.1, 0.92, t);
  }

  applyDot(position, 19, 70, 1, 0.28 + pulseWave(progress, 2.2) * 0.14, scaleX, scaleY);
  setOpacity(narrativeSpine, 0.28);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 160 + progress * 250, 0.78);

  const activeA = progress < 0.34;
  const activeB = progress >= 0.34 && progress < 0.66;
  const activeC = progress >= 0.66 && progress < 0.88;

  setCandidateState(candidateGentle, points.gentle, activeA ? 1.06 : 0.98, 0.7);
  setCandidateState(candidateStep, points.step, activeB ? 1.06 : 0.98, progress >= 0.24 ? 0.68 : 0.14);
  setCandidateState(candidateSteep, points.steep, activeC ? 1.06 : 0.98, progress >= 0.52 ? 0.68 : 0.14);

  setOpacity(accentGentle, activeA ? 1 : 0.38);
  setOpacity(accentStep, activeB ? 1 : progress >= 0.34 ? 0.38 : 0);
  setOpacity(accentSteep, activeC ? 1 : progress >= 0.66 ? 0.38 : 0);

  setOpacity(searchGuideA, 0.62);
  setOpacity(searchGuideB, progress >= 0.28 ? 0.58 : 0.1);
  setOpacity(searchGuideC, progress >= 0.56 ? 0.56 : 0.08);
  setOpacity(echoGentle, progress >= 0.3 ? 0.42 : 0);
  setOpacity(echoStep, progress >= 0.58 ? 0.38 : 0);
  setOpacity(echoSteep, progress >= 0.84 ? 0.34 : 0);

  setGroupTransform(rampAssembly, rampLayouts.search.x, rampLayouts.search.y, rampLayouts.search.scale);
  setOpacity(rampGuide, 0.16);
  setOpacity(rampRailLower, 0.08);
  setOpacity(rampRailUpper, 0.06);
  setOpacity(deck, 0.08);
  setOpacity(baseLeft, 0.07);
  setOpacity(baseMid, 0.06);
  setOpacity(entryBracket, 0.12 + clamp((progress - 0.78) * 1.4, 0, 0.24));
}

function renderTension(progress) {
  const rampProgress = easeOut(clamp(progress / 0.34, 0, 1));
  const rampX = lerp(rampLayouts.search.x, rampLayouts.tension.x, rampProgress);
  const rampY = lerp(rampLayouts.search.y, rampLayouts.tension.y, rampProgress);
  const rampScale = lerp(rampLayouts.search.scale, rampLayouts.tension.scale, rampProgress);
  setGroupTransform(rampAssembly, rampX, rampY, rampScale);

  let position = points.blocked;
  if (progress < 0.3) {
    position = mixPoint(points.entry, points.rampMid, easeInOut(progress / 0.3));
  } else if (progress < 0.62) {
    position = mixPoint(points.rampMid, points.blocked, easeInOut((progress - 0.3) / 0.32));
  } else {
    const pulse = (pulseWave((progress - 0.62) / 0.38, 2.2) - 0.5) * 7;
    position = {
      x: points.blocked.x + pulse * 0.35,
      y: points.blocked.y - Math.abs(pulse) * 0.18,
    };
  }

  const squeezeStrength = progress < 0.62 ? easeOut(progress / 0.62) : 1;
  applyDot(
    position,
    19,
    lerp(78, 108, squeezeStrength),
    1,
    0.34 + squeezeStrength * 0.12,
    lerp(1.02, 1.8, squeezeStrength),
    lerp(0.98, 0.7, squeezeStrength),
  );

  const residue = 1 - easeOut(clamp(progress / 0.34, 0, 1));
  setOpacity(narrativeSpine, 0.14 * residue);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 360 + progress * 120, 0.58 * residue);

  setCandidateState(candidateGentle, points.gentle, 0.96, 0.14 * residue);
  setCandidateState(candidateStep, points.step, 0.96, 0.12 * residue);
  setCandidateState(candidateSteep, points.steep, 0.96, 0.12 * residue);
  setOpacity(accentGentle, 0.14 * residue);
  setOpacity(accentStep, 0.12 * residue);
  setOpacity(accentSteep, 0.12 * residue);
  setOpacity(searchGuideA, 0.16 * residue);
  setOpacity(searchGuideB, 0.16 * residue);
  setOpacity(searchGuideC, 0.14 * residue);
  setOpacity(echoGentle, 0.16 * residue);
  setOpacity(echoStep, 0.14 * residue);
  setOpacity(echoSteep, 0.12 * residue);
  setOpacity(entryBracket, 0.22 * (1 - easeOut(clamp(progress / 0.18, 0, 1))));

  setOpacity(rampGuide, 0.56);
  setOpacity(rampRailLower, 1);
  setOpacity(rampRailUpper, 0.94);
  setOpacity(deck, 0.54);
  setOpacity(baseLeft, 0.82);
  setOpacity(baseMid, 0.8);
  setOpacity(supportRight, 0.08);
  setOpacity(stopper, 1);
  setTranslate(stopper, 0, lerp(0, 6, squeezeStrength));

  setCircleCenter(pressureHalo, points.blocked);
  pressureHalo.setAttribute("r", lerp(112, 144, squeezeStrength).toFixed(2));
  setOpacity(pressureHalo, 0.18 + squeezeStrength * 0.22);
}

function renderTransformation(progress) {
  const rampShift = easeOut(progress);
  const rampX = lerp(rampLayouts.tension.x, rampLayouts.resolution.x, rampShift);
  const rampY = lerp(rampLayouts.tension.y, rampLayouts.resolution.y, rampShift);
  const rampScale = lerp(rampLayouts.tension.scale, rampLayouts.resolution.scale, rampShift);
  setGroupTransform(rampAssembly, rampX, rampY, rampScale);

  const routeProgress = clamp((progress - 0.16) / 0.66, 0, 1);
  const pathPosition = pointOnPath(crestRouteBase, CREST_ROUTE_LENGTH, routeProgress);
  const settle = clamp((progress - 0.82) / 0.18, 0, 1);
  const position = progress < 0.16
    ? points.blocked
    : mixPoint(pathPosition, points.final, easeOut(settle));

  applyDot(
    position,
    lerp(19, 17, easeOut(progress)),
    lerp(108, 118, easeOut(progress)),
    1,
    0.3 + pulseWave(progress, 1.8) * 0.1,
  );

  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 160, 0);

  setOpacity(rampGuide, lerp(0.56, 0.12, easeOut(progress)));
  setOpacity(rampRailLower, 1);
  setOpacity(rampRailUpper, 0.94);
  setOpacity(deck, lerp(0.54, 0.92, easeOut(progress)));
  setOpacity(baseLeft, 0.84);
  setOpacity(baseMid, 0.84);
  setOpacity(supportRight, clamp((progress - 0.22) * 1.8, 0, 0.92));
  setTranslate(supportRight, 0, lerp(18, 0, easeOut(clamp((progress - 0.22) / 0.36, 0, 1))));
  setOpacity(stopper, clamp(1 - progress * 3.2, 0, 1));
  setTranslate(stopper, 0, lerp(0, -24, easeOut(clamp(progress / 0.3, 0, 1))));

  setOpacity(pressureHalo, clamp(0.4 - progress * 0.7, 0, 1));

  setOpacity(crestRouteBase, clamp((progress - 0.08) * 1.6, 0, 0.44));
  setPathWindow(crestRouteActive, CREST_ROUTE_LENGTH, CREST_ROUTE_LENGTH * routeProgress, clamp((progress - 0.12) * 1.8, 0, 0.94));
  setOpacity(finalCorners, clamp((progress - 0.7) * 1.5, 0, 0.44));
  setOpacity(crosshair, clamp((progress - 0.64) * 1.4, 0, 0.18));
  setOpacity(resolutionHalo, clamp((progress - 0.68) * 1.4, 0, 0.16));
}

function renderResolution(progress) {
  const settle = easeOut(progress);
  setGroupTransform(rampAssembly, rampLayouts.resolution.x, rampLayouts.resolution.y, rampLayouts.resolution.scale);

  applyDot(
    points.final,
    17,
    lerp(92, 82, settle),
    1,
    0.18 + pulseWave(progress, 1.2) * 0.08,
    1 + pulseWave(progress, 1.2) * 0.03,
    1 + pulseWave(progress, 1.2) * 0.03,
  );

  setOpacity(narrativeSpine, 0);
  setPathWindow(activeTrail, ACTIVE_TRAIL_LENGTH, 0, 0);
  setOpacity(pressureHalo, 0);

  setOpacity(rampGuide, 0);
  setOpacity(rampRailLower, 1);
  setOpacity(rampRailUpper, 0.94);
  setOpacity(deck, 0.92);
  setOpacity(baseLeft, 0.88);
  setOpacity(baseMid, 0.88);
  setOpacity(supportRight, 0.92);
  setOpacity(stopper, 0);
  setTranslate(baseLeft, lerp(0, -8, settle), 0);
  setTranslate(baseMid, lerp(0, 4, settle), 0);
  setTranslate(supportRight, lerp(0, 4, settle), 0);

  setOpacity(crestRouteBase, lerp(0.18, 0, settle));
  setPathWindow(crestRouteActive, CREST_ROUTE_LENGTH, CREST_ROUTE_LENGTH, lerp(0.24, 0, settle));
  setOpacity(finalCorners, lerp(0.5, 0.88, settle));
  setOpacity(crosshair, lerp(0.2, 0.26, settle));
  setOpacity(resolutionHalo, lerp(0.18, 0.26, settle));
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

  currentPhaseId = info.phase.id;
  svg.dataset.phase = info.phase.id;
  phaseLabel.textContent = info.phase.label;
  applyLayout(info.phase.id);
  state.currentElapsed = elapsed;
}

function setPlaying(nextPlaying) {
  if (state.playing === nextPlaying) return;
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
  const rawElapsed = state.playing
    ? state.elapsedBeforePause + (now - state.startAt)
    : state.elapsedBeforePause;

  let elapsed;
  if (state.looping) {
    elapsed = rawElapsed % TOTAL_DURATION;
  } else {
    elapsed = Math.min(rawElapsed, TOTAL_DURATION - 1);
    if (rawElapsed >= TOTAL_DURATION) {
      state.playing = false;
      state.elapsedBeforePause = TOTAL_DURATION - 1;
    }
  }

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
      setPlaying(false);
    } else {
      state.startAt = performance.now();
      setPlaying(true);
    }
  } else if (event.key.toLowerCase() === "r") {
    resetTimeline();
    if (!state.playing) {
      state.startAt = performance.now();
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
    setPlaying(false);
  },
  play() {
    state.startAt = performance.now();
    setPlaying(true);
  },
  setLooping(looping) {
    state.looping = looping;
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
window.addEventListener("resize", () => applyLayout());
resetScene();
render(0);
window.__RED_DOT_READY = true;
requestAnimationFrame(tick);
