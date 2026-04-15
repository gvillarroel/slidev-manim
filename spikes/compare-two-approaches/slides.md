---
theme: default
title: Compare Two Approaches
info: Slidev comparison spike with two related Manim assets.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import approachAVideo from '../../videos/compare-two-approaches/compare-two-approaches-approach-a.webm'
import approachAPoster from '../../videos/compare-two-approaches/compare-two-approaches-approach-a.png'
import approachBVideo from '../../videos/compare-two-approaches/compare-two-approaches-approach-b.webm'
import approachBPoster from '../../videos/compare-two-approaches/compare-two-approaches-approach-b.png'

const approachAReady = ref(false)
const approachBReady = ref(false)
</script>

<div class="h-full w-full bg-white px-10 py-8 overflow-hidden">
  <header class="max-w-5xl text-left">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
      Spike 1
    </p>
    <h1 class="mt-3 mb-2 text-5xl font-semibold leading-tight text-slate-950">
      Compare Two Approaches
    </h1>
    <p class="m-0 text-lg leading-8 text-slate-700">
      The same motion is rendered two ways so the slide can compare presentation style, framing,
      and visual emphasis side by side.
    </p>
  </header>

  <section class="mt-7 grid h-[calc(100%-9.75rem)] grid-cols-2 gap-6">
    <article class="flex min-h-0 flex-col">
      <p class="mb-3 text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
        Approach A
      </p>
      <div class="relative min-h-0 grow overflow-hidden rounded-[1.75rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
        <img
          v-show="!approachAReady"
          :src="approachAPoster"
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
          :poster="approachAPoster"
          @loadeddata="approachAReady = true"
        >
          <source :src="approachAVideo" type="video/webm" />
        </video>
      </div>
    </article>

    <article class="flex min-h-0 flex-col">
      <p class="mb-3 text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
        Approach B
      </p>
      <div class="relative min-h-0 grow overflow-hidden rounded-[1.75rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.10)]">
        <img
          v-show="!approachBReady"
          :src="approachBPoster"
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
          :poster="approachBPoster"
          @loadeddata="approachBReady = true"
        >
          <source :src="approachBVideo" type="video/webm" />
        </video>
      </div>
    </article>
  </section>
</div>
