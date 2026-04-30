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
import browserVideo from '../../videos/device-frame-embed/device-frame-embed-browser.webm'
import browserPoster from '../../videos/device-frame-embed/device-frame-embed-browser.png'
import deviceVideo from '../../videos/device-frame-embed/device-frame-embed-device.webm'
import devicePoster from '../../videos/device-frame-embed/device-frame-embed-device.png'
</script>

<section class="grid h-full w-full gap-10 bg-slate-50 px-12 py-10 text-slate-900" style="grid-template-columns: 0.95fr 1.05fr;">
  <div class="flex flex-col justify-center gap-5 text-left">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">Browser frame</p>
    <h1 class="m-0 text-5xl font-semibold leading-tight text-slate-950">Embed the video inside a product-style frame.</h1>
    <p class="m-0 text-lg leading-8 text-slate-700">The slide keeps the browser chrome in Slidev and leaves the Manim asset transparent so it behaves like live UI content.</p>
  </div>

  <div class="flex min-h-0 items-center justify-center">
    <div class="w-full max-w-5xl overflow-hidden rounded-3xl border border-slate-200 bg-white p-4 shadow-xl">
      <div class="flex items-center gap-3 border-b border-slate-200 px-2 pb-3">
        <div class="flex gap-2">
          <span class="h-3 w-3 rounded-full bg-red-400"></span>
          <span class="h-3 w-3 rounded-full bg-amber-400"></span>
          <span class="h-3 w-3 rounded-full bg-emerald-400"></span>
        </div>
        <div class="flex-1 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-500">demo.app / product preview</div>
      </div>
      <div class="relative mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <video
          class="h-full w-full object-contain bg-transparent pointer-events-none"
          autoplay
          loop
          muted
          playsinline
          preload="auto"
          :poster="browserPoster"
          :src="browserVideo"
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

<section class="grid h-full w-full gap-10 bg-slate-50 px-12 py-10 text-slate-900" style="grid-template-columns: 1fr 0.9fr;">
  <div class="flex flex-col justify-center gap-5 text-left">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">Device frame</p>
    <h1 class="m-0 text-5xl font-semibold leading-tight text-slate-950">The same idea also works in a taller device shell.</h1>
    <p class="m-0 text-lg leading-8 text-slate-700">This slide checks whether the motion stays legible when the frame becomes closer to a phone or app mockup.</p>
  </div>

  <div class="flex min-h-0 items-center justify-center">
    <div class="relative w-[440px] rounded-[2.5rem] border border-slate-200 bg-white p-4 shadow-xl">
      <div class="mx-auto mb-3 h-1.5 w-24 rounded-full bg-slate-200"></div>
      <div class="relative overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 p-4">
        <video
          class="h-full w-full object-contain bg-transparent pointer-events-none"
          autoplay
          loop
          muted
          playsinline
          preload="auto"
          :poster="devicePoster"
          :src="deviceVideo"
        ></video>
      </div>
      <div class="mx-auto mt-3 h-1.5 w-32 rounded-full bg-slate-200"></div>
    </div>
  </div>
</section>
