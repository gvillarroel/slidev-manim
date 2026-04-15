---
theme: default
title: Multi Video Grid
info: Slidev plus Manim multi-asset coexistence spike.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import orbitVideo from '../../videos/multi-video-grid/multi-video-grid-orbit.webm'
import orbitPoster from '../../videos/multi-video-grid/multi-video-grid-orbit.png'
import pulseVideo from '../../videos/multi-video-grid/multi-video-grid-pulse.webm'
import pulsePoster from '../../videos/multi-video-grid/multi-video-grid-pulse.png'
import sweepVideo from '../../videos/multi-video-grid/multi-video-grid-sweep.webm'
import sweepPoster from '../../videos/multi-video-grid/multi-video-grid-sweep.png'
import mergeVideo from '../../videos/multi-video-grid/multi-video-grid-merge.webm'
import mergePoster from '../../videos/multi-video-grid/multi-video-grid-merge.png'

const orbitReady = ref(false)
const pulseReady = ref(false)
const sweepReady = ref(false)
const mergeReady = ref(false)
</script>

<section class="flex h-full w-full flex-col gap-6 overflow-hidden bg-white px-10 py-8">
  <div class="flex items-end justify-between gap-6">
    <div class="text-left">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
        Spike 4
      </p>
      <h1 class="mt-3 mb-0 text-5xl font-semibold leading-tight text-slate-950">
        Multi Video Grid
      </h1>
    </div>
    <p class="m-0 max-w-3xl text-right text-lg leading-8 text-slate-700">
      Four independent Manim assets share the same slide so we can check alignment,
      autoplay, and visual balance before scaling the pattern.
    </p>
  </div>

  <div class="grid min-h-0 grow grid-cols-2 grid-rows-2 gap-5">
    <div class="relative min-h-0 overflow-hidden rounded-[1.85rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
      <img v-show="!orbitReady" :src="orbitPoster" alt="" class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain" />
      <video class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="orbitPoster" @loadeddata="orbitReady = true">
        <source :src="orbitVideo" type="video/webm">
      </video>
      <div class="absolute left-4 top-4 z-20 flex flex-col gap-1 text-left">
        <span class="inline-flex w-fit rounded-full bg-white/90 px-3 py-1 text-sm font-semibold uppercase tracking-[0.25em] text-slate-700 shadow-sm">Orbit</span>
        <span class="text-sm font-medium text-slate-500">Circular motion</span>
      </div>
    </div>

    <div class="relative min-h-0 overflow-hidden rounded-[1.85rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
      <img v-show="!pulseReady" :src="pulsePoster" alt="" class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain" />
      <video class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="pulsePoster" @loadeddata="pulseReady = true">
        <source :src="pulseVideo" type="video/webm">
      </video>
      <div class="absolute left-4 top-4 z-20 flex flex-col gap-1 text-left">
        <span class="inline-flex w-fit rounded-full bg-white/90 px-3 py-1 text-sm font-semibold uppercase tracking-[0.25em] text-slate-700 shadow-sm">Pulse</span>
        <span class="text-sm font-medium text-slate-500">Centered signal</span>
      </div>
    </div>

    <div class="relative min-h-0 overflow-hidden rounded-[1.85rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
      <img v-show="!sweepReady" :src="sweepPoster" alt="" class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain" />
      <video class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="sweepPoster" @loadeddata="sweepReady = true">
        <source :src="sweepVideo" type="video/webm">
      </video>
      <div class="absolute left-4 top-4 z-20 flex flex-col gap-1 text-left">
        <span class="inline-flex w-fit rounded-full bg-white/90 px-3 py-1 text-sm font-semibold uppercase tracking-[0.25em] text-slate-700 shadow-sm">Sweep</span>
        <span class="text-sm font-medium text-slate-500">Left to right pass</span>
      </div>
    </div>

    <div class="relative min-h-0 overflow-hidden rounded-[1.85rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
      <img v-show="!mergeReady" :src="mergePoster" alt="" class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain" />
      <video class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="mergePoster" @loadeddata="mergeReady = true">
        <source :src="mergeVideo" type="video/webm">
      </video>
      <div class="absolute left-4 top-4 z-20 flex flex-col gap-1 text-left">
        <span class="inline-flex w-fit rounded-full bg-white/90 px-3 py-1 text-sm font-semibold uppercase tracking-[0.25em] text-slate-700 shadow-sm">Merge</span>
        <span class="text-sm font-medium text-slate-500">Two inputs to one result</span>
      </div>
    </div>
  </div>
</section>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import orbitVideoLarge from '../../videos/multi-video-grid/multi-video-grid-orbit.webm'
import orbitPosterLarge from '../../videos/multi-video-grid/multi-video-grid-orbit.png'
import mergeVideoLarge from '../../videos/multi-video-grid/multi-video-grid-merge.webm'
import mergePosterLarge from '../../videos/multi-video-grid/multi-video-grid-merge.png'

const orbitLargeReady = ref(false)
const mergeLargeReady = ref(false)
</script>

<section class="flex h-full w-full flex-col bg-white px-12 py-10">
  <div class="flex items-end justify-between gap-8">
    <div class="max-w-3xl text-left">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
        Two-up panel
      </p>
      <h1 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
        Same assets, larger framing
      </h1>
    </div>
    <p class="m-0 max-w-xl text-right text-lg leading-8 text-slate-700">
      This second slide reuses the same assets to confirm they still read cleanly
      when the layout becomes more narrative and less grid-like.
    </p>
  </div>

  <div class="mt-8 grid min-h-0 grow grid-cols-[36%_64%] gap-6">
    <div class="flex flex-col justify-center gap-4 text-left text-lg leading-8 text-slate-700">
      <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">Independent video imports stay local to the spike.</div>
      <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">Each slot keeps its own readiness state and poster fallback.</div>
      <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">The same assets can support both dense grids and larger review panels.</div>
    </div>

    <div class="grid min-h-0 grid-cols-2 gap-5">
      <div class="relative min-h-0 overflow-hidden rounded-[1.85rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
        <img v-show="!orbitLargeReady" :src="orbitPosterLarge" alt="" class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain" />
        <video class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="orbitPosterLarge" @loadeddata="orbitLargeReady = true">
          <source :src="orbitVideoLarge" type="video/webm">
        </video>
      </div>

      <div class="relative min-h-0 overflow-hidden rounded-[1.85rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
        <img v-show="!mergeLargeReady" :src="mergePosterLarge" alt="" class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain" />
        <video class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="mergePosterLarge" @loadeddata="mergeLargeReady = true">
          <source :src="mergeVideoLarge" type="video/webm">
        </video>
      </div>
    </div>
  </div>
</section>
