---
title: Red Dot Knot SPA
status: active
date: 2026-05-01
---

# Red Dot Knot SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three route grammars, survives a compressed crossing, then turns that pressure into a centered knot with three calm anchors.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-knot-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-knot-spa/
```

Primary outputs:

```text
videos/red-dot-knot-spa/red-dot-knot-spa.webm
videos/red-dot-knot-spa/poster-final.png
videos/red-dot-knot-spa/screenshots/01-appearance.png
videos/red-dot-knot-spa/screenshots/02-search.png
videos/red-dot-knot-spa/screenshots/03-tension.png
videos/red-dot-knot-spa/screenshots/04-transformation.png
videos/red-dot-knot-spa/screenshots/05-resolution.png
videos/red-dot-knot-spa/screenshots/mobile-resolution.png
videos/red-dot-knot-spa/review-frames/frame-start.png
videos/red-dot-knot-spa/review-frames/frame-middle.png
videos/red-dot-knot-spa/review-frames/frame-final.png
videos/red-dot-knot-spa/review/contact-sheet.png
videos/red-dot-knot-spa/recording-summary.json
videos/red-dot-knot-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-knot-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested route visible as faint residue so the point feels like it is learning a crossing grammar instead of teleporting.
- The tension beat uses a narrow crossing gate with visible upper and lower rails so the conflict reads as compression inside a passage, not as a generic stop.
- The transformation beat draws a continuous knot route through three prepared anchors before the final hold quiets the helper slots and recenters the composition around the red core.
