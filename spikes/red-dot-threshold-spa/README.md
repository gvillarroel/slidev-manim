---
title: Red Dot Threshold SPA
status: active
date: 2026-05-04
---

# Red Dot Threshold SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn pressure into passage.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three threshold grammars, compresses inside a narrow slit, then unfolds that same threshold into a calm open chamber with the red point as the central anchor.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-threshold-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-threshold-spa/
```

Primary outputs:

```text
videos/red-dot-threshold-spa/red-dot-threshold-spa.webm
videos/red-dot-threshold-spa/poster-final.png
videos/red-dot-threshold-spa/screenshots/01-appearance.png
videos/red-dot-threshold-spa/screenshots/02-search.png
videos/red-dot-threshold-spa/screenshots/03-tension.png
videos/red-dot-threshold-spa/screenshots/04-transformation.png
videos/red-dot-threshold-spa/screenshots/05-resolution.png
videos/red-dot-threshold-spa/screenshots/mobile-resolution.png
videos/red-dot-threshold-spa/review-frames/frame-start.png
videos/red-dot-threshold-spa/review-frames/frame-middle.png
videos/red-dot-threshold-spa/review-frames/frame-final.png
videos/red-dot-threshold-spa/review-frames-0.3s/frames/
videos/red-dot-threshold-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-threshold-spa/review/contact-sheet.png
videos/red-dot-threshold-spa/recording-summary.json
videos/red-dot-threshold-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-threshold-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the pending chamber and threshold family so the first proof frame reads as prepared intent, not decorative blank space.
- The tension beat keeps the slit and the pending chamber visible together, so the proof frame reads as real passage pressure instead of a generic clamp.
- The transformation beat converts the same shutters into the final frame grammar, so the resolution feels causal rather than swapped in.
