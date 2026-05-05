---
title: Red Dot Membrane SPA
status: active
date: 2026-05-05
---

# Red Dot Membrane SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how pressure can become a membrane.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, probes three membrane grammars, gets compressed inside an elastic waist, then opens that same pressure into a calm suspended structure.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-membrane-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-membrane-spa/
```

Primary outputs:

```text
videos/red-dot-membrane-spa/red-dot-membrane-spa.webm
videos/red-dot-membrane-spa/poster-final.png
videos/red-dot-membrane-spa/screenshots/01-appearance.png
videos/red-dot-membrane-spa/screenshots/02-search.png
videos/red-dot-membrane-spa/screenshots/03-tension.png
videos/red-dot-membrane-spa/screenshots/04-transformation.png
videos/red-dot-membrane-spa/screenshots/05-resolution.png
videos/red-dot-membrane-spa/screenshots/mobile-resolution.png
videos/red-dot-membrane-spa/review-frames/frame-start.png
videos/red-dot-membrane-spa/review-frames/frame-middle.png
videos/red-dot-membrane-spa/review-frames/frame-final.png
videos/red-dot-membrane-spa/review-frames-0.3s/frames/
videos/red-dot-membrane-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-membrane-spa/review/contact-sheet.png
videos/red-dot-membrane-spa/recording-summary.json
videos/red-dot-membrane-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-membrane-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the suspended target scaffold and a faint red receiving seam so the first proof frame reads as prepared intent.
- Search candidates stay in the middle composition band and use distinct membrane shapes instead of acting like generic menu items.
- The tension beat keeps the anchors and the elastic waist visible together, so the still frame reads as actual surface pressure.
- The transformation beat opens the same waist into the final structure instead of swapping to a new symbol.
- Portrait review uses phase-specific crops and phase-specific whole-scene scaling so the final membrane still reads as a full structure on mobile.
