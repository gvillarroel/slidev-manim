---
title: Quality Scale Hierarchy
status: active
date: 2026-04-15
---

# Quality Scale Hierarchy

## Hypothesis

If one shape clearly owns the composition by scale and the rest behave as supporting forms, the video will feel clearer and more premium than a composition where everything competes at similar sizes.

## Purpose

This spike tests whether aggressive size hierarchy creates a stronger final frame without relying on text.

## Run the render

From the repository root:

```bash
uv run --script spikes/quality-scale-hierarchy/main.py
```

This writes the rendered assets to:

```text
videos/quality-scale-hierarchy/
```

## Current quality pass

- Promoted video: `videos/quality-scale-hierarchy/quality-scale-hierarchy.webm`
- Poster: `videos/quality-scale-hierarchy/quality-scale-hierarchy.png`
- Review frames: `videos/quality-scale-hierarchy/review-final-0.3s/`
- Validation reports:
  - `videos/quality-scale-hierarchy/composition-audit/report.md`
  - `videos/quality-scale-hierarchy/crowding-audit/report.md`
  - `videos/quality-scale-hierarchy/resting-mobject-audit/report.md`

The current render is a transparent 27.49 second slide-integration asset with a visible opening scaffold, a staged size-hierarchy handoff, a held dominant-form proof, cleanup, and a centered final hold.
