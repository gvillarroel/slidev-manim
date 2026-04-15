---
theme: default
title: Slide Step Handshake
info: Slidev plus Manim spike for reusing one asset across consecutive slides.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import handshakeVideo from '../../videos/slide-step-handshake/slide-step-handshake.webm'
import handshakePoster from '../../videos/slide-step-handshake/slide-step-handshake.png'

const handshakeReady = ref(false)
</script>

<section class="relative flex h-full w-full items-center justify-center overflow-hidden bg-white px-8 py-8">
  <div class="relative h-full w-full max-w-[1700px] overflow-hidden rounded-[2.2rem] border border-slate-200 bg-white shadow-[0_24px_90px_rgba(15,23,42,0.1)]">
    <img
      v-show="!handshakeReady"
      :src="handshakePoster"
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
      :poster="handshakePoster"
      @loadeddata="handshakeReady = true"
    >
      <source :src="handshakeVideo" type="video/webm" />
    </video>
  </div>
</section>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import handshakeVideo from '../../videos/slide-step-handshake/slide-step-handshake.webm'
import handshakePoster from '../../videos/slide-step-handshake/slide-step-handshake.png'

const handshakeReady = ref(false)
</script>

<section class="grid h-full w-full grid-rows-[auto_1fr] gap-6 bg-white px-12 py-10">
  <header class="flex items-end justify-between gap-6 border-b border-slate-200 pb-4">
    <div>
      <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">
        Step-based narration
      </p>
      <h1 class="mt-4 mb-0 text-5xl font-semibold leading-tight text-slate-950">
        Same motion, next slide
      </h1>
    </div>
    <p class="m-0 max-w-[32rem] text-xl leading-relaxed text-slate-700">
      This slide reuses the exact same Manim asset so the visual language stays stable while the narrative advances.
    </p>
  </header>

  <div class="flex h-full min-h-0 items-center">
    <div class="relative h-full min-h-0 w-full overflow-hidden rounded-[2rem] border border-slate-200 bg-white p-4 shadow-[0_24px_80px_rgba(15,23,42,0.12)]">
      <img
        v-show="!handshakeReady"
        :src="handshakePoster"
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
        :poster="handshakePoster"
        @loadeddata="handshakeReady = true"
      >
        <source :src="handshakeVideo" type="video/webm" />
      </video>
    </div>
  </div>
</section>
