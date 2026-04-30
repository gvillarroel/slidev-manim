---
theme: default
title: Mermaid Sequence Boundary
info: Slidev spike for a Mermaid sequence diagram plus a transparent Manim explanation video.
background: '#f7f7f7'
class: text-slate-900
layout: two-cols
drawings:
  persist: false
transition: fade-out
---

<script setup>
import spikeVideo from '../../videos/mermaid-sequence-boundary/mermaid-sequence-boundary.webm'
import spikePoster from '../../videos/mermaid-sequence-boundary/mermaid-sequence-boundary.png'
</script>

# Boundary request and response

The boundary participant starts the interaction. Bob processes it and sends the response back.

<div class="mt-2 flex flex-wrap gap-2">
  <div class="rounded-full border px-3 py-1 text-xs font-semibold" style="border-color:#45842A;background:#DBFFCC;color:#333E48;">Boundary</div>
  <div class="rounded-full border px-3 py-1 text-xs font-semibold" style="border-color:#007298;background:#CDF3FF;color:#333E48;">Service</div>
  <div class="rounded-full border px-3 py-1 text-xs font-semibold" style="border-color:#E77204;background:#FFE5CC;color:#333E48;">Request</div>
  <div class="rounded-full border px-3 py-1 text-xs font-semibold" style="border-color:#9E1B32;background:#FFCCD5;color:#333E48;">Response</div>
</div>

::left::

<div class="rounded-3xl border p-4 shadow-xl" style="border-color:#9c9c9c;background:#ffffff;">

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "fontFamily": "Open Sans, Arial, sans-serif",
    "background": "#FFFFFF",
    "mainBkg": "#FFFFFF",
    "primaryColor": "#DBFFCC",
    "primaryTextColor": "#333E48",
    "primaryBorderColor": "#45842A",
    "secondaryColor": "#CDF3FF",
    "secondaryTextColor": "#333E48",
    "secondaryBorderColor": "#007298",
    "tertiaryColor": "#FFE5CC",
    "lineColor": "#007298",
    "signalColor": "#007298",
    "signalTextColor": "#333E48",
    "labelBoxBkgColor": "#FFFFFF",
    "labelBoxBorderColor": "#9C9C9C",
    "labelTextColor": "#333E48",
    "actorBorder": "#007298",
    "actorBkg": "#CDF3FF",
    "actorTextColor": "#333E48",
    "actorLineColor": "#9C9C9C",
    "activationBkgColor": "#FFE5CC",
    "activationBorderColor": "#E77204",
    "sequenceNumberColor": "#FFFFFF"
  }
}}%%
sequenceDiagram
    box #DBFFCC Boundary
    participant Alice@{ "type" : "boundary" }
    end
    box #CDF3FF Service
    participant Bob
    end
    Alice->>Bob: Request from boundary
    Bob->>Alice: Response to boundary
```

</div>

<div class="mt-3 grid grid-cols-2 gap-2">
  <div class="rounded-3xl border p-3 text-sm leading-6 shadow-sm" style="border-color:#45842A;background:#DBFFCC;color:#333E48;">
    Alice is the boundary entry point.
  </div>
  <div class="rounded-3xl border p-3 text-sm leading-6 shadow-sm" style="border-color:#007298;background:#CDF3FF;color:#333E48;">
    Bob is the collaborating actor that receives the request and returns the response.
  </div>
  <div class="rounded-3xl border p-3 text-sm leading-6 shadow-sm" style="border-color:#E77204;background:#FFE5CC;color:#333E48;">
    Request goes from the boundary to the service.
  </div>
  <div class="rounded-3xl border p-3 text-sm leading-6 shadow-sm" style="border-color:#9E1B32;background:#FFCCD5;color:#333E48;">
    Response returns from the service to the boundary.
  </div>
</div>

::right::

<div class="flex h-full min-h-[430px] flex-col rounded-3xl border p-4 shadow-xl" style="border-color:#004d66;background:linear-gradient(180deg,#ffffff 0%, #e5f4fa 100%);">
  <div class="mb-2 flex gap-2">
    <div class="rounded-full border px-3 py-1 text-xs font-semibold" style="border-color:#E77204;background:#FFE5CC;color:#333E48;">Request animation</div>
    <div class="rounded-full border px-3 py-1 text-xs font-semibold" style="border-color:#9E1B32;background:#FFCCD5;color:#333E48;">Response animation</div>
  </div>
  <div class="flex min-h-0 flex-1 items-center justify-center">
  <video class="h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="spikePoster">
    <source :src="spikeVideo" type="video/webm" />
  </video>
  </div>
</div>
