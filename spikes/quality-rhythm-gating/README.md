---
title: Quality Rhythm Gating
status: active
date: 2026-04-15
---

# Quality Rhythm Gating

## Hypothesis

If motion is revealed in timed beats rather than as one continuous transform, the video will feel more deliberate and more premium.

## Purpose

This spike tests whether staggered rhythm gates can create a stronger sense of choreography while keeping text at zero.

## Run the render

From the repository root:

```bash
uv run --script spikes/quality-rhythm-gating/main.py
```

This writes the rendered assets to:

```text
videos/quality-rhythm-gating/
```

The runner writes the promoted transparent WebM, poster PNG, and dense review frames:

```text
videos/quality-rhythm-gating/quality-rhythm-gating.webm
videos/quality-rhythm-gating/quality-rhythm-gating.png
videos/quality-rhythm-gating/review-frames-0.3s/
```

## Current validation

- Duration: 31.021 seconds at 30 fps.
- Transparency: decoded VP9 alpha range is `0..255`.
- Review: 103 white-background cadence frames were extracted at 0.3-second cadence.
- Audits: composition and frame-crowding audits sampled 104 frames with zero blocking frames; resting-mobject audit reported zero blocking snapshots across 10 rest states.
