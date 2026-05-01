---
title: Broadcast Limits Lab
status: active
date: 2026-05-01
---

# Broadcast Limits Lab

## Purpose

Create a Slidev-ready Manim spike that probes the practical limits of `manim.animation.specialized.Broadcast` in Manim Community v0.20.1.

## Source

The official reference describes `Broadcast` as a `LaggedStart` animation that emits copies of a mobject from `focal_point`, beginning at `initial_width` and restoring to the mobject's actual size.

Reference: <https://docs.manim.community/en/stable/reference/manim.animation.specialized.Broadcast.html>

## Hypothesis

If the same visual shell is tested across density, starting width, fill opacity, focal placement, and cleanup behavior, the API's useful boundaries will be visible without needing a long code walkthrough.

## Cases

- `stroke shell`: default stroke-only pulse behavior.
- `dense shell`: high `n_mobs` and tiny `lag_ratio` approximate a continuous ripple, but can become visually heavy.
- `wide start`: nonzero `initial_width` removes the pin-point origin flash.
- `filled body`: mobjects with `fill_opacity > 0` fade as filled sheets, not only as outlines.
- `offset focal`: `focal_point` controls the broadcast center; the original mobject position only contributes size and style.
- `residue hold`: `remover=False` with a nonzero `final_opacity` leaves expanded copies in the scene.

## Run

From the repository root:

```bash
uv run --script spikes/broadcast-limits-lab/main.py
```

This renders the video and poster to:

```text
videos/broadcast-limits-lab/
```

The WebM is rendered with transparency for slide integration; the poster uses the project review background.
