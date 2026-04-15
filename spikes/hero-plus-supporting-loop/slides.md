---
theme: default
title: Hero Plus Supporting Loop
info: Slidev plus Manim spike for a dominant hero animation and a smaller reinforcing loop.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import heroVideo from '../../videos/hero-plus-supporting-loop/hero-plus-supporting-loop-hero.webm'
import heroPoster from '../../videos/hero-plus-supporting-loop/hero-plus-supporting-loop-hero.png'

const heroReady = ref(false)
</script>

<section class="relative flex h-full w-full items-center justify-center overflow-hidden bg-white px-8 py-8">
  <div class="relative h-full w-full max-w-[1700px] overflow-hidden rounded-[2.2rem] border border-slate-200 bg-white shadow-[0_24px_90px_rgba(15,23,42,0.1)]">
    <img
      :src="heroPoster"
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
      :poster="heroPoster"
      @loadeddata="heroReady = true"
    >
      <source :src="heroVideo" type="video/webm" />
    </video>
  </div>
</section>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import heroVideo from '../../videos/hero-plus-supporting-loop/hero-plus-supporting-loop-hero.webm'
import heroPoster from '../../videos/hero-plus-supporting-loop/hero-plus-supporting-loop-hero.png'
import supportVideo from '../../videos/hero-plus-supporting-loop/hero-plus-supporting-loop-support.webm'
import supportPoster from '../../videos/hero-plus-supporting-loop/hero-plus-supporting-loop-support.png'

const heroReady = ref(false)
const supportReady = ref(false)
</script>

<section class="grid h-full w-full grid-cols-[0.9fr_1.1fr] gap-10 bg-white px-12 py-10">
<div class="flex h-full flex-col justify-center">
  <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
    Advanced spike
  </p>
  <h1 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
    Hero first, support second
  </h1>
  <p class="mt-6 mb-0 text-2xl leading-relaxed text-slate-700">
    The hero video owns the composition while the smaller loop reinforces the same motion language without competing for attention.
  </p>
  <div class="mt-8 space-y-4">
    <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
      <p class="m-0 text-xl leading-8 text-slate-700">
        Use the hero asset as the main visual anchor when the slide needs a dominant motion block.
      </p>
    </div>
    <div class="rounded-3xl border border-slate-200 bg-slate-50 p-5">
      <p class="m-0 text-xl leading-8 text-slate-700">
        Keep the support loop smaller and simpler so it reads as reinforcement instead of a second focal point.
      </p>
    </div>
  </div>
</div>

<div class="flex min-h-0 flex-col gap-6">
  <div class="relative min-h-0 flex-1 overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
    <img
      v-show="!heroReady"
      :src="heroPoster"
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
      :poster="heroPoster"
      @loadeddata="heroReady = true"
    >
      <source :src="heroVideo" type="video/webm" />
    </video>
    <div class="absolute right-6 bottom-6 w-[260px] rounded-[1.4rem] border border-slate-200 bg-white/92 p-3 shadow-[0_16px_50px_rgba(15,23,42,0.15)] backdrop-blur">
      <div class="relative aspect-square overflow-hidden rounded-[1.1rem] bg-white">
        <img
          :src="supportPoster"
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
          :poster="supportPoster"
          @loadeddata="supportReady = true"
        >
          <source :src="supportVideo" type="video/webm" />
        </video>
      </div>
      <p class="mt-3 mb-0 text-sm font-semibold uppercase tracking-[0.32em] text-slate-500">
        Support loop
      </p>
      <p class="mt-2 mb-0 text-lg leading-7 text-slate-700">
        A smaller repeating motion keeps the slide alive while the hero remains the primary visual.
      </p>
    </div>
  </div>
</div>
</section>
