---
title: Red Dot Bumper SPA
status: active
date: 2026-05-04
---

# Red Dot Bumper SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how impact can become direction.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three deflection grammars, compresses into a slanted bumper, then traces that collision into a calm elbow-like chamber that keeps the point centered in the final hold.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-bumper-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-bumper-spa/
```

Primary outputs:

```text
videos/red-dot-bumper-spa/red-dot-bumper-spa.webm
videos/red-dot-bumper-spa/poster-final.png
videos/red-dot-bumper-spa/screenshots/01-appearance.png
videos/red-dot-bumper-spa/screenshots/02-search.png
videos/red-dot-bumper-spa/screenshots/03-tension.png
videos/red-dot-bumper-spa/screenshots/04-transformation.png
videos/red-dot-bumper-spa/screenshots/05-resolution.png
videos/red-dot-bumper-spa/screenshots/mobile-resolution.png
videos/red-dot-bumper-spa/review-frames/frame-start.png
videos/red-dot-bumper-spa/review-frames/frame-middle.png
videos/red-dot-bumper-spa/review-frames/frame-final.png
videos/red-dot-bumper-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-bumper-spa/review/contact-sheet.png
videos/red-dot-bumper-spa/recording-summary.json
videos/red-dot-bumper-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-bumper-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame keeps the future chamber faintly visible so the viewer reads the incoming collision as purposeful, not decorative.
- The tension beat keeps the bumper, keeper, and narrowing guides visible together so the compression frame reads as a real deflection problem.
- The transformation beat traces the full elbow route before the final hold, so the resolution feels caused by impact instead of swapped in.
