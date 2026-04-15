---
theme: default
title: Timeline Stack
info: Slidev + Manim spike for stacked timeline-style compositions.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import timelineWide from '../../videos/timeline-stack/timeline-stack-wide.webm'
import timelineWidePoster from '../../videos/timeline-stack/timeline-stack-wide.png'

const timelineWideReady = ref(false)
</script>

<div class="flex h-full w-full items-center justify-center bg-white px-8 py-8">
  <div class="relative h-full w-full overflow-hidden bg-white">
    <img
      v-show="!timelineWideReady"
      :src="timelineWidePoster"
      alt=""
      class="absolute inset-0 h-full w-full object-contain"
    />
    <video
      class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none"
      autoplay
      loop
      muted
      playsinline
      preload="auto"
      :poster="timelineWidePoster"
      @loadeddata="timelineWideReady = true"
    >
      <source :src="timelineWide" type="video/webm" />
    </video>
  </div>
</div>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import timelineWideReplay from '../../videos/timeline-stack/timeline-stack-wide.webm'
import timelineWidePosterReplay from '../../videos/timeline-stack/timeline-stack-wide.png'

const timelineWideReplayReady = ref(false)
</script>

<div class="grid h-full w-full grid-cols-[0.88fr_1.12fr] gap-10 bg-white px-12 py-10">
  <section class="flex h-full flex-col justify-center">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
      Sequence review
    </p>
    <h1 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
      Stacked sections, one narrative lane
    </h1>
    <div class="mt-8 space-y-4">
      <article class="rounded-3xl border border-slate-200 bg-slate-50 p-5 shadow-[0_16px_48px_rgba(15,23,42,0.08)]">
        <p class="m-0 text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">01</p>
        <p class="mt-2 mb-0 text-xl leading-8 text-slate-700">Open with the first section so the sequence has a clear starting point.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-slate-50 p-5 shadow-[0_16px_48px_rgba(15,23,42,0.08)]">
        <p class="m-0 text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">02</p>
        <p class="mt-2 mb-0 text-xl leading-8 text-slate-700">Keep the middle section visually stable so the progression is easy to read.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-slate-50 p-5 shadow-[0_16px_48px_rgba(15,23,42,0.08)]">
        <p class="m-0 text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">03</p>
        <p class="mt-2 mb-0 text-xl leading-8 text-slate-700">Close by letting the final card feel like the conclusion of the timeline.</p>
      </article>
    </div>
  </section>

  <section class="min-h-0">
    <div class="relative h-full overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
      <img
        v-show="!timelineWideReplayReady"
        :src="timelineWidePosterReplay"
        alt=""
        class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain"
      />
      <video
        class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none"
        autoplay
        loop
        muted
        playsinline
        preload="auto"
        :poster="timelineWidePosterReplay"
        @loadeddata="timelineWideReplayReady = true"
      >
        <source :src="timelineWideReplay" type="video/webm" />
      </video>
    </div>
  </section>
</div>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import timelinePortrait from '../../videos/timeline-stack/timeline-stack-portrait.webm'
import timelinePortraitPoster from '../../videos/timeline-stack/timeline-stack-portrait.png'

const timelinePortraitReady = ref(false)
</script>

<div class="grid h-full w-full grid-cols-[1fr_0.86fr] gap-10 bg-white px-12 py-10">
  <section class="flex h-full flex-col justify-center">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
      Vertical variant
    </p>
    <h2 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
      Taller framing for a tighter narrative lane
    </h2>
    <div class="mt-8 space-y-4">
      <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
        <p class="m-0 text-xl leading-8 text-slate-700">Use the tall render when the slide needs more room for surrounding copy.</p>
      </div>
      <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
        <p class="m-0 text-xl leading-8 text-slate-700">The same stacked motion still reads as a timeline, even when the panel becomes narrow.</p>
      </div>
      <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
        <p class="m-0 text-xl leading-8 text-slate-700">This is the best shape for a vertical narrative block with strong progression.</p>
      </div>
    </div>
  </section>

  <section class="flex min-h-0 items-center justify-center">
    <div class="relative h-full w-full max-w-[430px] overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
      <img
        v-show="!timelinePortraitReady"
        :src="timelinePortraitPoster"
        alt=""
        class="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] object-contain"
      />
      <video
        class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none"
        autoplay
        loop
        muted
        playsinline
        preload="auto"
        :poster="timelinePortraitPoster"
        @loadeddata="timelinePortraitReady = true"
      >
        <source :src="timelinePortrait" type="video/webm" />
      </video>
    </div>
  </section>
</div>
