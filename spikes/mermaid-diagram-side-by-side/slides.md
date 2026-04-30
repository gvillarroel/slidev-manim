---
theme: default
title: Mermaid Diagram Side By Side
info: Slidev spike for Mermaid markdown plus Manim video.
background: '#22c55e'
class: bg-green-500 text-slate-900
layout: two-cols
drawings:
  persist: false
transition: fade-out
---

<script setup>
import spikeVideo from '../../videos/mermaid-diagram-side-by-side/mermaid-diagram-side-by-side.webm'
import spikePoster from '../../videos/mermaid-diagram-side-by-side/mermaid-diagram-side-by-side.png'
</script>

# Mermaid plus motion

The diagram states the flow. The Manim video reinforces it with movement.

::left::

<div class="rounded-3xl border border-green-700/20 bg-white/92 p-5 shadow-xl">

```mermaid
flowchart LR
    A[Source] --> B[Transform]
    B --> C[Output]
```

</div>

::right::

<div class="flex h-full min-h-[420px] items-center justify-center rounded-3xl border border-green-900/15 bg-white/18 p-5 shadow-xl backdrop-blur-[1px]">
  <video class="h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="spikePoster">
    <source :src="spikeVideo" type="video/webm" />
  </video>
</div>
