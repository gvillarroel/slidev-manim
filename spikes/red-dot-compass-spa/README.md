---
title: Red Dot Compass SPA
status: active
date: 2026-05-02
---

# Red Dot Compass SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to orient the stage with almost no copy.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three direction grammars, gets trapped between competing vertical and horizontal cues, then redraws the stage into a compact compass-like emblem that holds calmly at the center.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-compass-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-compass-spa/
```

Primary outputs:

```text
videos/red-dot-compass-spa/red-dot-compass-spa.webm
videos/red-dot-compass-spa/poster-final.png
videos/red-dot-compass-spa/screenshots/01-appearance.png
videos/red-dot-compass-spa/screenshots/02-search.png
videos/red-dot-compass-spa/screenshots/03-tension.png
videos/red-dot-compass-spa/screenshots/04-transformation.png
videos/red-dot-compass-spa/screenshots/05-resolution.png
videos/red-dot-compass-spa/screenshots/mobile-resolution.png
videos/red-dot-compass-spa/review-frames/frame-start.png
videos/red-dot-compass-spa/review-frames/frame-middle.png
videos/red-dot-compass-spa/review-frames/frame-final.png
videos/red-dot-compass-spa/review/contact-sheet.png
videos/red-dot-compass-spa/recording-summary.json
videos/red-dot-compass-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-compass-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps a faint ingress trail active so the candidate tests still feel anchored to the original entry vector.
- The tension beat uses visible north and south brackets plus a restrained horizon axis so the conflict reads as competing orientation cues, not just a generic squeeze.
- The transformation beat traces the route into a compass rose before the final hold collapses into a compact center-weighted emblem that remains legible on mobile review.
