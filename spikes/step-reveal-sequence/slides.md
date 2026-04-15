---
theme: default
title: Step Reveal Sequence
info: Slidev deck for the step-reveal sequence spike.
background: white
class: text-center p-0 bg-white
layout: full
drawings:
  persist: false
transition: fade-out
---

<script setup>
import { ref } from 'vue'
import introVideo from '../../videos/step-reveal-sequence/step-reveal-sequence-intro.webm'
import introPoster from '../../videos/step-reveal-sequence/step-reveal-sequence-intro.png'

const introReady = ref(false)
</script>

<div class="relative h-full w-full bg-white overflow-hidden">
  <img
    v-show="!introReady"
    :src="introPoster"
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
    :poster="introPoster"
    @loadeddata="introReady = true"
  >
    <source :src="introVideo" type="video/webm" />
  </video>
</div>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import contextVideo from '../../videos/step-reveal-sequence/step-reveal-sequence-context.webm'
import contextPoster from '../../videos/step-reveal-sequence/step-reveal-sequence-context.png'

const contextReady = ref(false)
</script>

<div class="h-full w-full bg-white px-12 pt-8 pb-6 flex flex-col">
  <h1 class="m-0 text-5xl leading-tight font-semibold text-black">
    Step 1: Add context
  </h1>
  <p class="mt-2 text-xl text-gray-600">
    The same motion now carries the explanation instead of standing alone.
  </p>

  <div class="relative mt-6 grow min-h-0 flex items-center justify-center">
    <img
      v-show="!contextReady"
      :src="contextPoster"
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
      :poster="contextPoster"
      @loadeddata="contextReady = true"
    >
      <source :src="contextVideo" type="video/webm" />
    </video>
  </div>
</div>

---
layout: full
class: bg-white
---

<script setup>
import { ref } from 'vue'
import wrapVideo from '../../videos/step-reveal-sequence/step-reveal-sequence-wrap.webm'
import wrapPoster from '../../videos/step-reveal-sequence/step-reveal-sequence-wrap.png'

const wrapReady = ref(false)
</script>

<div class="h-full w-full bg-white px-12 pt-8 pb-6 flex flex-col">
  <h1 class="m-0 text-5xl leading-tight font-semibold text-black">
    Step 2: Close the loop
  </h1>
  <p class="mt-2 text-xl text-gray-600">
    Reuse the same asset family, but move the emphasis toward the conclusion.
  </p>

  <div class="relative mt-6 grow min-h-0 flex items-center justify-center">
    <img
      v-show="!wrapReady"
      :src="wrapPoster"
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
      :poster="wrapPoster"
      @loadeddata="wrapReady = true"
    >
      <source :src="wrapVideo" type="video/webm" />
    </video>
  </div>
</div>
