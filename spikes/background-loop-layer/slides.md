---
theme: default
title: Background Loop Layer
info: Slidev + Manim ambient background spike.
background: '#0b1120'
class: bg-slate-950 text-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import backgroundLoopLayerVideo from '../../videos/background-loop-layer/background-loop-layer.webm'
import backgroundLoopLayerPoster from '../../videos/background-loop-layer/background-loop-layer.png'
</script>

<div class="relative h-full w-full overflow-hidden bg-slate-950 text-white">
  <video
    class="absolute inset-0 h-full w-full object-cover pointer-events-none"
    autoplay
    loop
    muted
    playsinline
    preload="auto"
    :poster="backgroundLoopLayerPoster"
  >
    <source :src="backgroundLoopLayerVideo" type="video/webm" />
  </video>

  <div
    class="absolute inset-0"
    style="background:
      radial-gradient(circle at 22% 20%, rgba(96, 165, 250, 0.16), transparent 34%),
      radial-gradient(circle at 78% 18%, rgba(14, 165, 233, 0.12), transparent 28%),
      linear-gradient(135deg, rgba(2, 6, 23, 0.12), rgba(2, 6, 23, 0.46));"
  ></div>

  <div class="relative z-10 flex h-full items-center justify-center px-12">
    <div class="max-w-4xl rounded-[2rem] border border-white/15 bg-slate-950/78 p-10 shadow-[0_30px_90px_rgba(2,6,23,0.45)] backdrop-blur">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-sky-200/80">
        Ambient layer
      </p>
      <h1 class="mt-4 mb-4 text-5xl font-semibold leading-tight text-white">
        A Manim loop can sit behind the slide without taking over it.
      </h1>
      <p class="m-0 text-lg leading-8 text-slate-200">
        This spike keeps the motion low-contrast and loopable so the foreground message stays
        readable while the background adds texture and energy.
      </p>
    </div>
  </div>
</div>

---
layout: full
background: '#0b1120'
class: bg-slate-950 text-white
---

<script setup>
import backgroundLoopLayerDetailVideo from '../../videos/background-loop-layer/background-loop-layer.webm'
import backgroundLoopLayerDetailPoster from '../../videos/background-loop-layer/background-loop-layer.png'
</script>

<div class="relative h-full w-full overflow-hidden bg-slate-950 text-white px-12 py-8">
  <video
    class="absolute inset-0 h-full w-full object-cover pointer-events-none"
    autoplay
    loop
    muted
    playsinline
    preload="auto"
    :poster="backgroundLoopLayerDetailPoster"
  >
    <source :src="backgroundLoopLayerDetailVideo" type="video/webm" />
  </video>

  <div
    class="absolute inset-0"
    style="background:
      linear-gradient(135deg, rgba(15, 23, 42, 0.18), rgba(15, 23, 42, 0.55)),
      radial-gradient(circle at 20% 18%, rgba(56, 189, 248, 0.10), transparent 28%),
      radial-gradient(circle at 84% 76%, rgba(148, 163, 184, 0.10), transparent 26%);"
  ></div>

  <div class="relative z-10 flex h-full flex-col">
    <div class="flex items-end justify-between gap-8">
      <div class="max-w-2xl text-left">
        <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-sky-200/80">Near-full-slide review</p>
        <h1 class="mt-3 mb-0 text-4xl font-semibold leading-tight text-white">The same loop still works when the content gets denser.</h1>
      </div>
      <p class="m-0 max-w-xl text-right text-base leading-7 text-slate-200">This slide checks whether the background stays useful when the foreground switches to a larger content block with a more structured layout.</p>
    </div>
    <div class="mt-6 grid min-h-0 flex-1 grid-cols-[1.1fr_0.9fr] gap-6">
      <div class="rounded-[1.8rem] border border-white/15 bg-white/88 p-6 text-slate-900 shadow-[0_24px_80px_rgba(2,6,23,0.24)] backdrop-blur">
        <h2 class="mt-0 mb-4 text-xl font-semibold text-slate-950">What this spike is checking</h2>
        <ul class="m-0 space-y-3 pl-5 text-base leading-7 text-slate-700">
          <li>The background stays subtle enough to support text instead of competing with it.</li>
          <li>The loop remains readable on a full-slide hero and on a denser content layout.</li>
        </ul>
      </div>
      <div class="flex h-full flex-col justify-between rounded-[1.8rem] border border-white/15 bg-slate-950/58 p-6 text-white shadow-[0_24px_80px_rgba(2,6,23,0.34)] backdrop-blur">
        <div>
          <h2 class="mt-0 mb-4 text-xl font-semibold text-white">Why it works</h2>
          <p class="m-0 text-base leading-7 text-slate-200">The slide owns the backdrop color, while Manim supplies only the ambient motion. That separation makes the animation feel like texture rather than content.</p>
        </div>
        <div class="rounded-[1.25rem] border border-sky-200/15 bg-sky-300/10 p-4 text-sky-100">
          <p class="m-0 text-sm font-semibold uppercase tracking-[0.3em] text-sky-200/80">Spike outcome</p>
          <p class="mt-2 mb-0 text-sm leading-6">Use the transparent WebM as the live layer and keep the poster for review and fallback validation.</p>
        </div>
      </div>
    </div>
  </div>
</div>
