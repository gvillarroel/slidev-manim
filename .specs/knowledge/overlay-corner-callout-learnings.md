---
id: KNOW-0003
title: Overlay corner callout spike learnings
status: active
date: 2026-04-14
---

# Summary

Small Manim overlays work best when the slide owns the composition and the video only supplies the motion accent.

# Learned Patterns

1. Anchor the overlay with an absolutely positioned wrapper so the slide layout stays stable.
2. Keep the Manim artwork simple, high-contrast, and readable at a small size.
3. A transparent `.webm` is the delivery artifact, while a white-background PNG is a useful review fallback.
4. Reusing the same overlay asset across corner and side placements is viable when the wrapper controls the framing.
5. Slide-local assets should be imported through Vite from inside the spike, not referenced as raw filesystem paths.
6. A `loadeddata` gate prevents the fallback image from overlapping the video once playback starts.

# Practical Rule

- For corner-callout spikes, make the slide feel normal first, then add the overlay video as a controlled accent.
