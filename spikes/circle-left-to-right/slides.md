---
theme: default
title: Circle Left To Right
info: Minimal Slidev deck for the circle-left-to-right spike.
background: white
class: text-center p-0 bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import fullVideo from '../../videos/circle-left-to-right/circle-left-to-right-full.webm'
import contentVideo from '../../videos/circle-left-to-right/circle-left-to-right-content.webm'
import fullPoster from '../../videos/circle-left-to-right/circle-left-to-right-full.png'
import contentPoster from '../../videos/circle-left-to-right/circle-left-to-right-content.png'

const fullVideoReady = ref(false)
const contentVideoReady = ref(false)
</script>

<div class="relative h-full w-full bg-white overflow-hidden">
  <img
    v-show="!fullVideoReady"
    :src="fullPoster"
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
    :poster="fullPoster"
    @loadeddata="fullVideoReady = true"
  >
    <source :src="fullVideo" type="video/webm" />
  </video>
</div>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import contentVideoSlide from '../../videos/circle-left-to-right/circle-left-to-right-content.webm'
import contentPosterSlide from '../../videos/circle-left-to-right/circle-left-to-right-content.png'

const contentVideoSlideReady = ref(false)
</script>

<div class="h-full w-full bg-white px-12 pt-8 pb-6 flex flex-col">
  <h1 class="m-0 text-5xl leading-tight font-semibold text-black">
    Circle Left To Right
  </h1>

  <div class="relative mt-6 grow min-h-0 flex items-center justify-center">
    <img
      v-show="!contentVideoSlideReady"
      :src="contentPosterSlide"
      alt=""
      class="absolute inset-0 m-auto h-[88%] w-full object-contain"
    />
    <video
      class="relative z-10 h-[88%] w-full object-contain bg-transparent pointer-events-none"
      autoplay
      loop
      muted
      playsinline
      preload="auto"
      :poster="contentPosterSlide"
      @loadeddata="contentVideoSlideReady = true"
    >
      <source :src="contentVideoSlide" type="video/webm" />
    </video>
  </div>
</div>
