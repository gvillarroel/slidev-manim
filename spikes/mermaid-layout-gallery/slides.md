---
theme: default
title: Mermaid Layout Gallery
info: Gallery of repository layout families using Mermaid diagrams plus transparent Manim videos.
background: '#f7f7f7'
class: text-slate-900
layout: cover
drawings:
  persist: false
transition: fade-out
---

<script setup>
import bgVideo from '../../videos/mermaid-layout-gallery/background-loop.webm'
import bgPoster from '../../videos/mermaid-layout-gallery/background-loop.png'
import calloutVideo from '../../videos/mermaid-layout-gallery/corner-callout.webm'
import calloutPoster from '../../videos/mermaid-layout-gallery/corner-callout.png'
import sideVideo from '../../videos/mermaid-layout-gallery/side-by-side.webm'
import sidePoster from '../../videos/mermaid-layout-gallery/side-by-side.png'
import insetMain from '../../videos/mermaid-layout-gallery/inset-main.webm'
import insetMainPoster from '../../videos/mermaid-layout-gallery/inset-main.png'
import insetDetail from '../../videos/mermaid-layout-gallery/inset-detail.webm'
import insetDetailPoster from '../../videos/mermaid-layout-gallery/inset-detail.png'
import compareLeft from '../../videos/mermaid-layout-gallery/compare-left.webm'
import compareLeftPoster from '../../videos/mermaid-layout-gallery/compare-left.png'
import compareRight from '../../videos/mermaid-layout-gallery/compare-right.webm'
import compareRightPoster from '../../videos/mermaid-layout-gallery/compare-right.png'
import timelineVideo from '../../videos/mermaid-layout-gallery/timeline.webm'
import timelinePoster from '../../videos/mermaid-layout-gallery/timeline.png'
import gridJourney from '../../videos/mermaid-layout-gallery/grid-journey.webm'
import gridJourneyPoster from '../../videos/mermaid-layout-gallery/grid-journey.png'
import gridPie from '../../videos/mermaid-layout-gallery/grid-pie.webm'
import gridPiePoster from '../../videos/mermaid-layout-gallery/grid-pie.png'
import gridGit from '../../videos/mermaid-layout-gallery/grid-git.webm'
import gridGitPoster from '../../videos/mermaid-layout-gallery/grid-git.png'
import gridFlow from '../../videos/mermaid-layout-gallery/grid-flow.webm'
import gridFlowPoster from '../../videos/mermaid-layout-gallery/grid-flow.png'
import heroMain from '../../videos/mermaid-layout-gallery/hero-main.webm'
import heroMainPoster from '../../videos/mermaid-layout-gallery/hero-main.png'
import heroSupport from '../../videos/mermaid-layout-gallery/hero-support.webm'
import heroSupportPoster from '../../videos/mermaid-layout-gallery/hero-support.png'
import deviceFrame from '../../videos/mermaid-layout-gallery/device-frame.webm'
import deviceFramePoster from '../../videos/mermaid-layout-gallery/device-frame.png'
</script>

# Mermaid Layout Gallery

Every established slide pattern in this repository, now paired with a distinct Mermaid diagram and a transparent Manim video.

<div class="mt-6 flex flex-wrap gap-3">
  <div class="rounded-full border px-3 py-1 text-sm font-semibold" style="border-color:#45842A;background:#DBFFCC;color:#333E48;">Primary green</div>
  <div class="rounded-full border px-3 py-1 text-sm font-semibold" style="border-color:#007298;background:#CDF3FF;color:#333E48;">Primary blue</div>
  <div class="rounded-full border px-3 py-1 text-sm font-semibold" style="border-color:#E77204;background:#FFE5CC;color:#333E48;">Primary orange</div>
  <div class="rounded-full border px-3 py-1 text-sm font-semibold" style="border-color:#9E1B32;background:#FFCCD5;color:#333E48;">Primary red</div>
  <div class="rounded-full border px-3 py-1 text-sm font-semibold" style="border-color:#652F6C;background:#F9CCFF;color:#333E48;">Primary purple</div>
</div>

---
layout: full
---

<div class="pointer-events-none absolute inset-0">
  <video class="h-full w-full object-cover" autoplay loop muted playsinline preload="auto" :poster="bgPoster">
    <source :src="bgVideo" type="video/webm" />
  </video>
</div>

<div class="relative z-10 mx-auto max-w-5xl px-12 py-12">
  <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em]" style="color:#007298;">Background loop layer</p>
  <h1 class="mt-4 text-4xl font-semibold leading-tight" style="color:#333E48;">Ambient motion behind a Mermaid sequence.</h1>
</div>

<div class="mx-auto max-w-3xl rounded-[2rem] border bg-white/92 px-8 py-6 shadow-xl" style="border-color:#007298;">

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#CDF3FF","primaryTextColor":"#333E48","primaryBorderColor":"#007298","secondaryColor":"#DBFFCC","secondaryBorderColor":"#45842A","lineColor":"#007298","actorBkg":"#CDF3FF","actorBorder":"#007298","actorTextColor":"#333E48"}}}%%
sequenceDiagram
    participant Browser
    participant API
    Browser->>API: Fetch dashboard
    API->>Browser: Return view model
```

</div>

---
layout: full
---

<div class="px-12 pt-10">
  <p class="m-0 text-sm font-semibold uppercase tracking-[0.35em]" style="color:#45842A;">Corner callout</p>
  <h1 class="mt-4 max-w-4xl text-4xl font-semibold leading-tight" style="color:#333E48;">Main diagram plus a small motion accent.</h1>
</div>

<div class="ml-12 mt-6 max-w-[720px] rounded-[2rem] border bg-white px-8 py-5 shadow-xl" style="border-color:#45842A;">

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#DBFFCC","primaryTextColor":"#333E48","primaryBorderColor":"#45842A","secondaryColor":"#FFE5CC","secondaryBorderColor":"#E77204","tertiaryColor":"#FFCCD5","lineColor":"#007298"}}}%%
flowchart LR
    A[Collect] --> B[Review]
    B --> C[Ship]
```

</div>

<div class="pointer-events-none absolute right-12 top-48 w-[240px] rounded-3xl border bg-white p-4 shadow-xl" style="border-color:#007298;">
  <video class="h-full w-full object-contain bg-transparent" autoplay loop muted playsinline preload="auto" :poster="calloutPoster">
    <source :src="calloutVideo" type="video/webm" />
  </video>
</div>

---
layout: two-cols
---

# Side by side

Diagram and animation split the slide evenly.

::left::

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#DBFFCC","primaryBorderColor":"#45842A","secondaryColor":"#CDF3FF","secondaryBorderColor":"#007298","lineColor":"#007298","signalColor":"#E77204","signalTextColor":"#333E48","actorBkg":"#CDF3FF","actorBorder":"#007298","actorTextColor":"#333E48"}}}%%
sequenceDiagram
    participant Boundary
    participant Service
    Boundary->>Service: Validate request
    Service->>Boundary: Return result
```

::right::

<div class="mx-auto mt-8 flex h-[280px] max-w-[460px] items-center justify-center rounded-3xl border p-5 shadow-xl" style="border-color:#007298;background:#ffffff;">
  <video class="h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="sidePoster">
    <source :src="sideVideo" type="video/webm" />
  </video>
</div>

---
layout: two-cols
---

# Inset annotation

The main video explains the state change while the inset isolates one detail.

::left::

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#CDF3FF","primaryBorderColor":"#007298","secondaryColor":"#FFE5CC","secondaryBorderColor":"#E77204","tertiaryColor":"#DBFFCC","lineColor":"#007298"}}}%%
stateDiagram-v2
    [*] --> Idle
    Idle --> Running
    Running --> Done
```

::right::

<div class="relative mx-auto mt-6 flex h-[290px] max-w-[460px] items-center justify-center rounded-3xl border p-4 shadow-xl" style="border-color:#9c9c9c;background:#ffffff;">
  <video class="h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="insetMainPoster">
    <source :src="insetMain" type="video/webm" />
  </video>
  <div class="absolute right-4 top-4 w-[150px] rounded-2xl border p-3 shadow-lg" style="border-color:#E77204;background:#ffffff;">
    <video class="aspect-square w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="insetDetailPoster">
      <source :src="insetDetail" type="video/webm" />
    </video>
  </div>
</div>

---
layout: two-cols
---

# Compare two approaches

Two related diagrams stay readable when each side owns its own panel and motion.

::left::

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#DBFFCC","primaryBorderColor":"#45842A","secondaryColor":"#CDF3FF","secondaryBorderColor":"#007298","lineColor":"#007298"}}}%%
classDiagram
    Customer "1" --> "*" Order : places
    Order "1" --> "*" Item : contains
```

<div class="mt-4 rounded-3xl border p-4 shadow-xl" style="border-color:#45842A;background:#ffffff;">
  <video class="h-[140px] w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="compareLeftPoster">
    <source :src="compareLeft" type="video/webm" />
  </video>
</div>

::right::

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#F9CCFF","primaryBorderColor":"#652F6C","secondaryColor":"#DBFFCC","secondaryBorderColor":"#45842A","lineColor":"#9E1B32"}}}%%
flowchart LR
    Read --> Model
    Model --> Write
```

<div class="mt-4 rounded-3xl border p-4 shadow-xl" style="border-color:#652F6C;background:#ffffff;">
  <video class="h-[140px] w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="compareRightPoster">
    <source :src="compareRight" type="video/webm" />
  </video>
</div>

---
layout: two-cols
---

# Timeline stack

The vertical lane carries the narrative while Mermaid supplies the milestones.

::left::

```mermaid
timeline
    title Delivery path
    Start : Intake
          : Design
    Middle : Build
           : Review
    End : Launch
```

::right::

<div class="mx-auto mt-12 flex h-[300px] max-w-[280px] items-center justify-center rounded-3xl border p-4 shadow-xl" style="border-color:#007298;background:#ffffff;">
  <video class="h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="timelinePoster">
    <source :src="timelineVideo" type="video/webm" />
  </video>
</div>

---
layout: full
---

# Multi-video grid

Several diagram stories can coexist when each tile owns its own transparent loop.

<div class="mt-4 grid grid-cols-2 gap-3">
  <div class="rounded-3xl border p-4 shadow-xl" style="border-color:#45842A;background:#ffffff;">
    <p class="mb-3 text-sm font-semibold uppercase tracking-[0.25em]" style="color:#45842A;">Journey</p>
    <video class="h-[70px] w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="gridJourneyPoster">
      <source :src="gridJourney" type="video/webm" />
    </video>
  </div>
  <div class="rounded-3xl border p-4 shadow-xl" style="border-color:#E77204;background:#ffffff;">
    <p class="mb-3 text-sm font-semibold uppercase tracking-[0.25em]" style="color:#E77204;">Pie</p>
    <video class="h-[70px] w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="gridPiePoster">
      <source :src="gridPie" type="video/webm" />
    </video>
  </div>
  <div class="rounded-3xl border p-4 shadow-xl" style="border-color:#007298;background:#ffffff;">
    <p class="mb-3 text-sm font-semibold uppercase tracking-[0.25em]" style="color:#007298;">Git</p>
    <video class="h-[70px] w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="gridGitPoster">
      <source :src="gridGit" type="video/webm" />
    </video>
  </div>
  <div class="rounded-3xl border p-4 shadow-xl" style="border-color:#652F6C;background:#ffffff;">
    <p class="mb-3 text-sm font-semibold uppercase tracking-[0.25em]" style="color:#652F6C;">Flow</p>
    <video class="h-[70px] w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="gridFlowPoster">
      <source :src="gridFlow" type="video/webm" />
    </video>
  </div>
</div>

<div class="mt-3 rounded-[1.75rem] border bg-white px-6 py-3 shadow-xl" style="border-color:#652F6C;">

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#DBFFCC","primaryBorderColor":"#45842A","secondaryColor":"#CDF3FF","secondaryBorderColor":"#007298","tertiaryColor":"#FFE5CC","lineColor":"#652F6C"}}}%%
flowchart LR
    Journey --> Pie
    Pie --> Git
    Git --> Flow
```

</div>

---
layout: two-cols
---

# Hero plus support

One hero diagram owns the slide while a smaller loop reinforces the same vocabulary.

::left::

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Open Sans, Arial, sans-serif","primaryColor":"#DBFFCC","primaryBorderColor":"#45842A","secondaryColor":"#CDF3FF","secondaryBorderColor":"#007298","tertiaryColor":"#F9CCFF","lineColor":"#9E1B32"}}}%%
flowchart TB
    Client --> Gateway
    Gateway --> Services
```

::right::

<div class="flex min-h-0 flex-col gap-5">
  <div class="mx-auto mt-4 h-[190px] w-full max-w-[500px] rounded-3xl border p-4 shadow-xl" style="border-color:#9E1B32;background:#ffffff;">
    <video class="h-full w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="heroMainPoster">
      <source :src="heroMain" type="video/webm" />
    </video>
  </div>
  <div class="grid grid-cols-[130px_1fr] gap-4 rounded-3xl border p-4 shadow-lg" style="border-color:#E77204;background:#ffffff;">
    <video class="aspect-square w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="heroSupportPoster">
      <source :src="heroSupport" type="video/webm" />
    </video>
    <div class="flex items-center pr-2 text-sm leading-6" style="color:#333E48;">The support loop keeps the same motion language without competing with the main diagram.</div>
  </div>
</div>

---
layout: two-cols
---

# Device frame embed

UI framing helps when the Manim explanation belongs inside an application surface.

::left::

```mermaid
journey
    title Checkout journey
    section Search
      Find item: 4: User
    section Buy
      Review cart: 3: User
      Confirm payment: 5: User
```

::right::

<div class="mx-auto mt-6 w-full max-w-[520px] overflow-hidden rounded-3xl border p-4 shadow-xl" style="border-color:#007298;background:#ffffff;">
  <div class="mb-4 flex items-center gap-3 border-b pb-3" style="border-color:#cfcfcf;">
    <div class="flex gap-2">
      <div class="h-3 w-3 rounded-full" style="background:#9E1B32;"></div>
      <div class="h-3 w-3 rounded-full" style="background:#E77204;"></div>
      <div class="h-3 w-3 rounded-full" style="background:#45842A;"></div>
    </div>
    <div class="flex-1 rounded-full px-4 py-2 text-sm" style="border:1px solid #cfcfcf;background:#f7f7f7;color:#333E48;">app.example / checkout</div>
  </div>
  <div class="rounded-3xl border p-4" style="border-color:#cfcfcf;background:#ffffff;">
    <video class="h-[200px] w-full object-contain bg-transparent pointer-events-none" autoplay loop muted playsinline preload="auto" :poster="deviceFramePoster">
      <source :src="deviceFrame" type="video/webm" />
    </video>
  </div>
</div>
