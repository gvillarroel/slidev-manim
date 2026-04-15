---
theme: default
title: Aspect Ratio Variants
info: Slidev + Manim integration spike for wide and tall asset framing.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import wideVideo from '../../videos/aspect-ratio-variants/aspect-ratio-variants-wide.webm'
import widePoster from '../../videos/aspect-ratio-variants/aspect-ratio-variants-wide.png'

const wideReady = ref(false)
</script>

<div class="h-full w-full bg-white px-12 py-10">
  <div class="grid h-full grid-cols-[0.9fr_1.1fr] gap-10">
    <section class="flex flex-col justify-center text-left">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
        Spike 4
      </p>
      <h1 class="mt-4 mb-5 text-5xl font-semibold leading-tight text-slate-950">
        Wide framing for the main slide
      </h1>
      <p class="m-0 text-lg leading-8 text-slate-700">
        This slide checks whether a wide Manim render can remain dominant while Slidev keeps
        the narrative minimal and clean beside it.
      </p>
      <ul class="mt-6 space-y-3 text-left text-lg leading-8 text-slate-800">
        <li>Use the wide asset when the slide can give the video most of the horizontal space.</li>
        <li>Keep the surrounding text short so the animation stays readable.</li>
        <li>The poster fallback remains useful while the video is loading or when reviewing screenshots.</li>
      </ul>
    </section>

    <section class="relative min-h-0">
      <div class="relative h-full overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
        <img
          v-show="!wideReady"
          :src="widePoster"
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
          :poster="widePoster"
          @loadeddata="wideReady = true"
        >
          <source :src="wideVideo" type="video/webm" />
        </video>
      </div>
    </section>
  </div>
</div>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import tallVideo from '../../videos/aspect-ratio-variants/aspect-ratio-variants-tall.webm'
import tallPoster from '../../videos/aspect-ratio-variants/aspect-ratio-variants-tall.png'

const tallReady = ref(false)
</script>

<div class="h-full w-full bg-white px-12 py-10">
  <div class="grid h-full grid-cols-[1fr_0.72fr] gap-10">
    <section class="flex flex-col justify-center">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
        Narrow layout
      </p>
      <h2 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
        Tall variant for a sidebar
      </h2>
      <p class="mt-6 mb-0 max-w-2xl text-xl leading-8 text-slate-700">
        The same idea can be rendered differently when the slide needs room for longer text or a more editorial composition.
      </p>
      <div class="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-6">
        <p class="m-0 text-lg leading-8 text-slate-700">
          This is the kind of asset that fits a narrow column, a stacked slide, or a vertical panel beside the explanation.
        </p>
      </div>
    </section>

    <section class="relative min-h-0">
      <div class="relative h-full overflow-hidden rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
        <img
          v-show="!tallReady"
          :src="tallPoster"
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
          :poster="tallPoster"
          @loadeddata="tallReady = true"
        >
          <source :src="tallVideo" type="video/webm" />
        </video>
      </div>
    </section>
  </div>
</div>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import wideCompareVideo from '../../videos/aspect-ratio-variants/aspect-ratio-variants-wide.webm'
import wideComparePoster from '../../videos/aspect-ratio-variants/aspect-ratio-variants-wide.png'
import tallCompareVideo from '../../videos/aspect-ratio-variants/aspect-ratio-variants-tall.webm'
import tallComparePoster from '../../videos/aspect-ratio-variants/aspect-ratio-variants-tall.png'

const wideCompareReady = ref(false)
const tallCompareReady = ref(false)
</script>

<div class="h-full w-full bg-white px-12 py-10">
  <div class="flex h-full flex-col">
    <div class="max-w-4xl">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
        Comparison view
      </p>
      <h2 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
        Same motion, different framing
      </h2>
      <p class="mt-5 mb-0 text-xl leading-8 text-slate-700">
        This slide confirms the two render variants stay coherent when shown side by side.
      </p>
    </div>

    <div class="mt-8 grid flex-1 min-h-0 grid-cols-2 gap-8">
      <section class="relative min-h-0 rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
        <img
          v-show="!wideCompareReady"
          :src="wideComparePoster"
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
          :poster="wideComparePoster"
          @loadeddata="wideCompareReady = true"
        >
          <source :src="wideCompareVideo" type="video/webm" />
        </video>
        <p class="absolute left-8 bottom-8 m-0 rounded-full bg-white/95 px-4 py-2 text-sm font-semibold text-slate-600 shadow">
          Wide
        </p>
      </section>

      <section class="relative min-h-0 rounded-[2rem] border border-slate-200 bg-slate-50 p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
        <img
          v-show="!tallCompareReady"
          :src="tallComparePoster"
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
          :poster="tallComparePoster"
          @loadeddata="tallCompareReady = true"
        >
          <source :src="tallCompareVideo" type="video/webm" />
        </video>
        <p class="absolute left-8 bottom-8 m-0 rounded-full bg-white/95 px-4 py-2 text-sm font-semibold text-slate-600 shadow">
          Tall
        </p>
      </section>
    </div>
  </div>
</div>
