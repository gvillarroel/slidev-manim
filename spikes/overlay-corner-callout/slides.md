---
theme: default
title: Overlay Corner Callout
info: Spike for a mostly normal slide with a small transparent Manim overlay.
background: white
class: text-left p-0 bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import overlayVideo from '../../videos/overlay-corner-callout/overlay-corner-callout.webm'
import overlayPoster from '../../videos/overlay-corner-callout/overlay-corner-callout.png'

const overlayReady = ref(false)
</script>

<section class="relative h-full w-full overflow-hidden bg-white px-12 py-10">
  <div class="max-w-3xl space-y-6">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
      Spike 1
    </p>
    <h1 class="m-0 text-5xl font-semibold leading-tight text-slate-900">
      Corner callout overlay
    </h1>
    <p class="m-0 text-2xl leading-relaxed text-slate-700">
      Keep the slide mostly normal and use a small transparent Manim animation as an accent in the corner.
    </p>
    <ul class="m-0 space-y-3 pl-6 text-xl leading-relaxed text-slate-700">
      <li>The text stays readable without needing the animation.</li>
      <li>The overlay video acts like a visual callout, not the main content.</li>
      <li>Small motion works best when the wrapper keeps a fixed placement.</li>
    </ul>
  </div>

  <div class="absolute right-8 bottom-8 w-[29%] min-w-[280px] max-w-[420px]">
    <img
      v-show="!overlayReady"
      :src="overlayPoster"
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
      :poster="overlayPoster"
      @loadeddata="overlayReady = true"
    >
      <source :src="overlayVideo" type="video/webm" />
    </video>
  </div>
</section>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import overlayVideoSide from '../../videos/overlay-corner-callout/overlay-corner-callout.webm'
import overlayPosterSide from '../../videos/overlay-corner-callout/overlay-corner-callout.png'

const overlayReadySide = ref(false)
</script>

<section class="relative h-full w-full overflow-hidden bg-white px-12 py-10">
  <div class="grid h-full grid-cols-[1.25fr_0.75fr] gap-10">
    <div class="flex flex-col justify-center">
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">
        Alternate placement
      </p>
      <h2 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-900">
        Side area composition
      </h2>
      <p class="mt-6 mb-0 text-2xl leading-relaxed text-slate-700">
        The same Manim asset can sit in a side panel when the slide needs more horizontal space for the explanation.
      </p>
      <div class="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-6">
        <p class="m-0 text-xl leading-relaxed text-slate-700">
          The only job of the overlay is to guide attention while the slide body stays clean and readable.
        </p>
      </div>
    </div>

    <div class="relative flex items-center justify-center">
      <div class="relative w-full max-w-[420px]">
        <img
          v-show="!overlayReadySide"
          :src="overlayPosterSide"
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
          :poster="overlayPosterSide"
          @loadeddata="overlayReadySide = true"
        >
          <source :src="overlayVideoSide" type="video/webm" />
        </video>
      </div>
    </div>
  </div>
</section>
