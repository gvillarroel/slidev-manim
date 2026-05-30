---
title: Red Dot Mirror SPA
status: active
date: 2026-05-05
---

# Red Dot Mirror SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn reflection into alignment.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three mirror grammars, compresses against a narrow center seam, then unfolds that same seam into a calm symmetrical frame with the red point as the visual anchor.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-mirror-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-mirror-spa/
```

Primary outputs:

```text
videos/red-dot-mirror-spa/red-dot-mirror-spa.webm
videos/red-dot-mirror-spa/poster-final.png
videos/red-dot-mirror-spa/screenshots/01-appearance.png
videos/red-dot-mirror-spa/screenshots/02-search.png
videos/red-dot-mirror-spa/screenshots/03-tension.png
videos/red-dot-mirror-spa/screenshots/04-transformation.png
videos/red-dot-mirror-spa/screenshots/05-resolution.png
videos/red-dot-mirror-spa/screenshots/mobile-resolution.png
videos/red-dot-mirror-spa/review-frames/frame-start.png
videos/red-dot-mirror-spa/review-frames/frame-middle.png
videos/red-dot-mirror-spa/review-frames/frame-final.png
videos/red-dot-mirror-spa/review-frames-0.3s/frames/
videos/red-dot-mirror-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-mirror-spa/review/contact-sheet.png
videos/red-dot-mirror-spa/recording-summary.json
videos/red-dot-mirror-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-mirror-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the center seam and a faint future frame so the first proof frame reads as prepared intent instead of blank space.
- Search keeps three reflection candidates visible as neutral structures while the red point remains the only active accent.
- The tension beat makes the center seam physically tighten around the point before any resolved frame appears.
- Transformation turns the same seam into the settled frame grammar, so the resolution reads as a consequence of the conflict instead of a replacement icon.
- Portrait review uses phase-specific crops so the center seam, squeeze beat, and final symmetry remain legible on mobile.
