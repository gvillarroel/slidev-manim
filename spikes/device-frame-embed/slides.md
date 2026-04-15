---
theme: default
title: Device Frame Embed
info: Slidev plus Manim spike for browser and device framing.
background: '#f8fafc'
class: bg-slate-50 text-slate-900
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import browserVideo from '../../videos/device-frame-embed/device-frame-embed-browser.webm'
import browserPoster from '../../videos/device-frame-embed/device-frame-embed-browser.png'
import deviceVideo from '../../videos/device-frame-embed/device-frame-embed-device.webm'
import devicePoster from '../../videos/device-frame-embed/device-frame-embed-device.png'

const browserReady = ref(false)
const deviceReady = ref(false)
</script>

<section class="grid h-full w-full gap-10 bg-slate-50 px-12 py-10 text-slate-900" style="grid-template-columns: 0.9fr 1.1fr;">
  <div class="flex flex-col justify-center gap-5 text-left">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">Browser frame</p>
    <h1 class="m-0 text-5xl font-semibold leading-tight text-slate-950">Embed the video inside a product-style frame.</h1>
    <p class="m-0 text-lg leading-8 text-slate-700">This composition keeps the chrome in Slidev and uses the Manim asset as the moving content inside the viewport.</p>
    <div class="space-y-4 text-lg leading-8 text-slate-700">
      <div class="rounded-3xl border border-slate-200 bg-white px-5 py-4 shadow-sm">The browser shell stays readable even when the animation is subtle.</div>
      <div class="rounded-3xl border border-slate-200 bg-white px-5 py-4 shadow-sm">A transparent WebM and a white poster keep the review path practical.</div>
    </div>
  </div>

  <div class="flex min-h-0 items-center justify-center">
    <div class="w-full max-w-6xl overflow-hidden rounded-3xl border border-slate-200 bg-white p-4 shadow-xl">
      <div class="flex items-center gap-3 border-b border-slate-200 px-2 pb-3">
        <div class="flex gap-2">
          <span class="h-3 w-3 rounded-full bg-red-400"></span>
          <span class="h-3 w-3 rounded-full bg-amber-400"></span>
          <span class="h-3 w-3 rounded-full bg-emerald-400"></span>
        </div>
        <div class="flex-1 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-500">
          demo.app / product preview
        </div>
      </div>

      <div class="relative mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-5">
        <img
          v-show="!browserReady"
          :src="browserPoster"
          alt=""
          class="absolute inset-0 h-full w-full object-contain p-5"
        />
        <video
          class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none"
          autoplay
          loop
          muted
          playsinline
          preload="auto"
          :poster="browserPoster"
          :src="browserVideo"
          @loadeddata="browserReady = true"
        ></video>
      </div>
    </div>
  </div>
</section>

---
theme: default
title: Device Frame Embed
info: Slidev plus Manim spike for phone-style framing.
background: '#f8fafc'
class: bg-slate-50 text-slate-900
layout: full
drawings:
  persist: false
transition: fade-out
---

<section class="grid h-full w-full gap-10 bg-slate-50 px-12 py-10 text-slate-900" style="grid-template-columns: 1.05fr 0.95fr;">
  <div class="flex flex-col justify-center gap-5 text-left">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">Device frame</p>
    <h1 class="m-0 text-5xl font-semibold leading-tight text-slate-950">The same idea also works in a taller device shell.</h1>
    <p class="m-0 text-lg leading-8 text-slate-700">This slide checks whether the motion stays legible when the frame becomes closer to a phone or app mockup.</p>
    <div class="space-y-4 text-lg leading-8 text-slate-700">
      <div class="rounded-3xl border border-slate-200 bg-white px-5 py-4 shadow-sm">Use the device frame for product demo narration or UI explanation slides.</div>
      <div class="rounded-3xl border border-slate-200 bg-white px-5 py-4 shadow-sm">The frame reads cleanly because the Manim video does not contain its own chrome.</div>
    </div>
  </div>

  <div class="flex min-h-0 items-center justify-center">
    <div class="relative w-[440px] rounded-[2.5rem] border border-slate-200 bg-white p-4 shadow-xl">
      <div class="mx-auto mb-3 h-1.5 w-24 rounded-full bg-slate-200"></div>
      <div class="relative overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 p-4">
        <img
          v-show="!deviceReady"
          :src="devicePoster"
          alt=""
          class="absolute inset-0 h-full w-full object-contain p-4"
        />
        <video
          class="relative z-10 h-full w-full object-contain bg-transparent pointer-events-none"
          autoplay
          loop
          muted
          playsinline
          preload="auto"
          :poster="devicePoster"
          :src="deviceVideo"
          @loadeddata="deviceReady = true"
        ></video>
      </div>
      <div class="mx-auto mt-3 h-1.5 w-32 rounded-full bg-slate-200"></div>
    </div>
  </div>
</section>
