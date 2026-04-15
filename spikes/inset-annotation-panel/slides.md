---
theme: default
title: Inset Annotation Panel
info: Slidev spike for inset Manim annotations and magnified detail views.
background: white
class: bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import insetMain from '../../videos/inset-annotation-panel/inset-annotation-panel-main.webm'
import insetMainPoster from '../../videos/inset-annotation-panel/inset-annotation-panel-main.png'
import insetZoom from '../../videos/inset-annotation-panel/inset-annotation-panel-zoom.webm'
import insetZoomPoster from '../../videos/inset-annotation-panel/inset-annotation-panel-zoom.png'
</script>

<div class="grid h-full w-full grid-cols-2 gap-8 bg-white px-12 py-10">
  <div class="flex flex-col justify-center gap-4 text-left">
    <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em] text-slate-500">Spike 1</p>
    <h1 class="m-0 text-5xl font-semibold leading-tight text-slate-950">Inset Annotation Panel</h1>
    <p class="m-0 text-lg leading-8 text-slate-700">
      This layout keeps the main slide readable while a second Manim asset acts as a zoomed annotation.
    </p>
    <div class="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4 text-lg leading-8 text-slate-800">
      Main content stays dominant and the inset remains a detail callout.
    </div>
    <div class="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4 text-lg leading-8 text-slate-800">
      Separate wide and square renders make the framing easier to control.
    </div>
  </div>

  <div class="relative overflow-hidden rounded-3xl border border-slate-200 bg-slate-50 p-4 shadow-xl">
    <img v-if="false" :src="insetMainPoster" alt="" />
    <video class="h-full w-full object-contain pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="insetMainPoster">
      <source :src="insetMain" type="video/webm" />
    </video>

    <div class="absolute right-6 top-6 w-56 overflow-hidden rounded-2xl border border-slate-200 bg-white p-3 shadow-lg">
      <img v-if="false" :src="insetZoomPoster" alt="" />
      <video class="aspect-square w-full object-contain pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="insetZoomPoster">
        <source :src="insetZoom" type="video/webm" />
      </video>
      <p class="mt-2 mb-0 text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Magnified detail</p>
    </div>
  </div>
</div>
