---
title: Indication Animation Gallery
status: active
date: 2026-05-01
---

# Indication Animation Gallery

## Purpose

Create a Slidev-ready Manim reference spike that exercises every class listed in the official `manim.animation.indication` reference page for Manim Community v0.20.1.

## Hypothesis

If the indication animations are shown in a calm 3 by 3 gallery with one target per cell, their behavioral differences will be easier to compare than in a single-object sequential demo.

## Included animations

- `ApplyWave`
- `Blink`
- `Circumscribe`
- `Flash`
- `FocusOn`
- `Indicate`
- `ShowPassingFlash`
- `ShowPassingFlashWithThinningStrokeWidth`
- `Wiggle`

## Run

From the repository root:

```bash
uv run --script spikes/indication-animation-gallery/main.py
```

This renders the video and poster to:

```text
videos/indication-animation-gallery/
```

The WebM is rendered with transparency for slide integration; the poster uses the project review background.
