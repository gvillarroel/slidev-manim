---
title: Red Dot Shear SPA
status: active
date: 2026-05-04
---

# Red Dot Shear SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn shear pressure into alignment.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three offset step grammars, compresses inside a shearing gap, then resolves that same pressure into a calm aligned aperture.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-shear-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-shear-spa/
```

Primary outputs:

```text
videos/red-dot-shear-spa/red-dot-shear-spa.webm
videos/red-dot-shear-spa/poster-final.png
videos/red-dot-shear-spa/screenshots/01-appearance.png
videos/red-dot-shear-spa/screenshots/02-search.png
videos/red-dot-shear-spa/screenshots/03-tension.png
videos/red-dot-shear-spa/screenshots/04-transformation.png
videos/red-dot-shear-spa/screenshots/05-resolution.png
videos/red-dot-shear-spa/screenshots/mobile-resolution.png
videos/red-dot-shear-spa/review-frames/frame-start.png
videos/red-dot-shear-spa/review-frames/frame-middle.png
videos/red-dot-shear-spa/review-frames/frame-final.png
videos/red-dot-shear-spa/review-frames-0.3s/frames/
videos/red-dot-shear-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-shear-spa/review/contact-sheet.png
videos/red-dot-shear-spa/recording-summary.json
videos/red-dot-shear-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-shear-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the pending aligned aperture so the point does not read stranded on an empty lane.
- The search beat keeps the candidate slots in the middle band and moves the visited echoes outside each slot perimeter.
- The tension beat preserves both the shearing slabs and the pending aperture grammar so the squeeze reads as causally connected to the final structure.
- The final hold keeps the brackets open and the braces quiet, so the resolution reads as alignment instead of a cage.
- Portrait review uses phase-specific crops plus phase-centered scene scaling, so the mobile proof frame stays on the shear gap and final aperture instead of shrinking the desktop composition into a tall white field.
