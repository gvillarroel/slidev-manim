---
theme: default
title: Split Screen Sync
info: Slidev + Manim split-screen integration spike.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import splitScreenVideo from '../../videos/split-screen-sync/split-screen-sync.webm'
import splitScreenPoster from '../../videos/split-screen-sync/split-screen-sync.png'

const splitScreenReady = ref(false)
</script>

<div class="h-full w-full grid grid-cols-[38%_62%] gap-10 px-12 py-10 bg-white overflow-hidden">
  <section class="flex h-full flex-col justify-center text-left">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
      Spike 2
    </p>
    <h1 class="mt-4 mb-5 text-5xl font-semibold leading-tight text-slate-950">
      Split Screen Sync
    </h1>
    <p class="m-0 text-lg leading-8 text-slate-700">
      This slide checks whether a Manim animation can stay readable while Slidev carries
      the explanatory context beside it.
    </p>
    <ul class="mt-6 space-y-3 text-left text-lg leading-8 text-slate-800">
      <li>Left side: framing, explanation, and slide narrative.</li>
      <li>Right side: a larger Manim panel that can stay visually dominant.</li>
      <li>Shared asset: the same video can be reused in different slide layouts.</li>
    </ul>
  </section>

  <section class="min-h-0">
    <div class="relative h-full overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
      <img
        v-show="!splitScreenReady"
        :src="splitScreenPoster"
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
        :poster="splitScreenPoster"
        @loadeddata="splitScreenReady = true"
      >
        <source :src="splitScreenVideo" type="video/webm" />
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
import splitScreenVideoReplay from '../../videos/split-screen-sync/split-screen-sync.webm'
import splitScreenPosterReplay from '../../videos/split-screen-sync/split-screen-sync.png'

const splitScreenReplayReady = ref(false)
</script>

<div class="h-full w-full flex flex-col bg-white px-12 py-10">
  <div class="flex items-end justify-between gap-6">
    <div class="max-w-3xl text-left">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
        Review layout
      </p>
      <h1 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
        Same asset, different framing
      </h1>
    </div>
    <p class="m-0 max-w-xl text-right text-lg leading-8 text-slate-700">
      This second slide reuses the same animation to confirm the video still feels balanced
      when the surrounding layout changes.
    </p>
  </div>

  <div class="relative mt-8 grow min-h-0 overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
    <img
      v-show="!splitScreenReplayReady"
      :src="splitScreenPosterReplay"
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
      :poster="splitScreenPosterReplay"
      @loadeddata="splitScreenReplayReady = true"
    >
      <source :src="splitScreenVideoReplay" type="video/webm" />
    </video>
  </div>
</div>
