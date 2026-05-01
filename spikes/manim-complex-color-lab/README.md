---
title: Manim Complex Color Lab
status: active
date: 2026-04-30
---

# Manim Complex Color Lab

## Hypothesis

If advanced Manim features are staged as adjacent visual systems with explicit color roles, the result can read as a polished slide asset instead of a technical feature dump.

## Purpose

This spike tests three complex Manim capabilities in one composition:

- a `ThreeDScene` surface with height-based color mapping,
- a vector-field panel using `ArrowVectorField` and `StreamLines`,
- an updater-driven parametric trace using `ValueTracker`, `always_redraw`, and `TracedPath`.

The scene uses the project palette as semantic roles: blue and purple for mathematical systems, green and orange for flow, red for active focus, and gray for structure.

## Run the render

From the repository root:

```bash
uv run --script spikes/manim-complex-color-lab/main.py
```

This writes the rendered assets to:

```text
videos/manim-complex-color-lab/
```
