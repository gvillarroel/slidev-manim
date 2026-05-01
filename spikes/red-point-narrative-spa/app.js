const phases = [
  { id: "appearance", duration: 3400 },
  { id: "search", duration: 5200 },
  { id: "tension", duration: 5200 },
  { id: "transform", duration: 6000 },
  { id: "resolution", duration: 6400 },
];

const phaseIds = phases.map((phase) => phase.id);
const root = document.querySelector(".app");
const phaseDots = Array.from(document.querySelectorAll(".phase-dot"));
const controlButtons = Array.from(document.querySelectorAll("[data-action]"));

let phaseIndex = 0;
let autoplay = true;
let timerId = 0;

function phaseFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const requested = params.get("phase");
  if (!requested) {
    return null;
  }
  const normalized = requested.trim().toLowerCase();
  return phaseIds.includes(normalized) ? normalized : null;
}

function updateActiveDots(activePhase) {
  for (const dot of phaseDots) {
    dot.classList.toggle("is-active", dot.dataset.phaseTarget === activePhase);
  }
}

function setPhase(nextIndex, options = {}) {
  const { silent = false } = options;
  phaseIndex = ((nextIndex % phases.length) + phases.length) % phases.length;
  const activePhase = phases[phaseIndex].id;
  root.dataset.phase = activePhase;
  root.dataset.index = String(phaseIndex);
  updateActiveDots(activePhase);
  if (!silent) {
    window.dispatchEvent(
      new CustomEvent("red-point-phase-change", {
        detail: { phase: activePhase, index: phaseIndex },
      }),
    );
  }
}

function clearTimer() {
  window.clearTimeout(timerId);
  timerId = 0;
}

function scheduleNextPhase() {
  clearTimer();
  if (!autoplay) {
    return;
  }
  const duration = phases[phaseIndex].duration;
  timerId = window.setTimeout(() => {
    const isLastPhase = phaseIndex === phases.length - 1;
    if (isLastPhase) {
      autoplay = false;
      return;
    }
    setPhase(phaseIndex + 1);
    scheduleNextPhase();
  }, duration);
}

function replay() {
  autoplay = true;
  setPhase(0);
  scheduleNextPhase();
}

function move(step) {
  autoplay = false;
  clearTimer();
  setPhase(phaseIndex + step);
}

function bindControls() {
  for (const button of controlButtons) {
    button.addEventListener("click", () => {
      const action = button.dataset.action;
      if (action === "replay") {
        replay();
      } else if (action === "next") {
        move(1);
      } else if (action === "previous") {
        move(-1);
      }
    });
  }

  for (const dot of phaseDots) {
    dot.addEventListener("click", () => {
      autoplay = false;
      clearTimer();
      const target = dot.dataset.phaseTarget;
      const nextIndex = phaseIds.indexOf(target);
      if (nextIndex >= 0) {
        setPhase(nextIndex);
      }
    });
  }

  window.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") {
      move(1);
    } else if (event.key === "ArrowLeft") {
      move(-1);
    } else if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      replay();
    }
  });
}

function exposeDebugApi() {
  window.redPointNarrative = {
    get phase() {
      return phases[phaseIndex].id;
    },
    get index() {
      return phaseIndex;
    },
    phases: [...phaseIds],
    setPhase(target) {
      const nextIndex =
        typeof target === "number" ? target : phaseIds.indexOf(String(target));
      if (nextIndex >= 0) {
        autoplay = false;
        clearTimer();
        setPhase(nextIndex);
      }
    },
    replay,
  };
}

function init() {
  bindControls();
  exposeDebugApi();

  const frozenPhase = phaseFromQuery();
  if (frozenPhase) {
    autoplay = false;
    setPhase(phaseIds.indexOf(frozenPhase), { silent: true });
    return;
  }

  setPhase(0, { silent: true });
  scheduleNextPhase();
}

init();
