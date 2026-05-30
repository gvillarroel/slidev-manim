---
title: Red Dot Anchor SPA
status: active
date: 2026-05-04
---

# Red Dot Anchor SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn drift into hold.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three mooring grammars, gets pulled into a narrow anchor gate, then traces that pressure into a centered anchor-like emblem that holds the field in place.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-anchor-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, generates 0.3-second cadence sheets, and writes all generated artifacts to:

```text
videos/red-dot-anchor-spa/
```

Primary outputs:

```text
videos/red-dot-anchor-spa/red-dot-anchor-spa.webm
videos/red-dot-anchor-spa/poster-final.png
videos/red-dot-anchor-spa/screenshots/01-appearance.png
videos/red-dot-anchor-spa/screenshots/02-search.png
videos/red-dot-anchor-spa/screenshots/03-tension.png
videos/red-dot-anchor-spa/screenshots/04-transformation.png
videos/red-dot-anchor-spa/screenshots/05-resolution.png
videos/red-dot-anchor-spa/screenshots/mobile-resolution.png
videos/red-dot-anchor-spa/review-frames/frame-start.png
videos/red-dot-anchor-spa/review-frames/frame-middle.png
videos/red-dot-anchor-spa/review-frames/frame-final.png
videos/red-dot-anchor-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-anchor-spa/review/contact-sheet.png
videos/red-dot-anchor-spa/recording-summary.json
videos/red-dot-anchor-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-anchor-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the pending ring, shank, and fluke field so the first proof frame reads as prepared intent instead of decorative blank space.
- The search beat keeps each tested mooring grammar tied back to the same entry handoff so the dot still feels guided rather than erratic.
- The tension beat keeps the full anchor gate visible around the dot, so the proof frame reads as real hold pressure instead of a generic squeeze.
- The transformation beat traces the vertical shaft and both flukes before settling back into the ring, so the resolution feels causally built rather than swapped in.
