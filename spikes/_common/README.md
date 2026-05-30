---
id: common-spike-library
title: Common spike library
status: active
---

# Common Spike Library

This folder contains reusable Manim helpers extracted from repeated spike
patterns. It is not a standalone spike. Import it from spike entrypoints by
adding `spikes/` to `sys.path` and importing `_common`.

Use this library for shared visual tokens, mechanism components, and render
helpers. Keep experiment-specific timing and narrative decisions in the spike
that owns the render.

