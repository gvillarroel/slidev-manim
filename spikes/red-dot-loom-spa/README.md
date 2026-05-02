---
title: Red Dot Loom SPA
status: active
date: 2026-05-02
---

# Red Dot Loom SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three loom-like passage grammars, gets pressed through a narrow woven gate, then resolves into a calm centered weave with the red point held at its core.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-loom-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-loom-spa/
```

Primary outputs:

```text
videos/red-dot-loom-spa/red-dot-loom-spa.webm
videos/red-dot-loom-spa/poster-final.png
videos/red-dot-loom-spa/screenshots/01-appearance.png
videos/red-dot-loom-spa/screenshots/02-search.png
videos/red-dot-loom-spa/screenshots/03-tension.png
videos/red-dot-loom-spa/screenshots/04-transformation.png
videos/red-dot-loom-spa/screenshots/05-resolution.png
videos/red-dot-loom-spa/screenshots/mobile-resolution.png
videos/red-dot-loom-spa/review-frames/frame-start.png
videos/red-dot-loom-spa/review-frames/frame-middle.png
videos/red-dot-loom-spa/review-frames/frame-final.png
videos/red-dot-loom-spa/review/contact-sheet.png
videos/red-dot-loom-spa/recording-summary.json
videos/red-dot-loom-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-loom-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the three tested passage grammars inside the middle composition band so the point reads as learning the weave instead of wandering.
- The tension beat uses visible comb pressure from above and below so the conflict reads as a real woven gate rather than a generic stop.
- The transformation beat turns that pressure into a woven four-side frame, then the final hold retires the gate helpers and recenters the red point inside the resolved weave.
