---
title: Red Dot Rosette SPA
status: active
date: 2026-05-04
---

# Red Dot Rosette SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers a four-petal rosette by testing one curved grammar, forcing its way through a vertical pinch, and then drawing the resolved emblem into place.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The experience stays sparse on purpose. The story should read from timing, pressure, alignment, and the way the point connects separate parts into one centered mark.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-rosette-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-rosette-spa/
```

Primary outputs:

```text
videos/red-dot-rosette-spa/red-dot-rosette-spa.webm
videos/red-dot-rosette-spa/poster-final.png
videos/red-dot-rosette-spa/screenshots/01-appearance.png
videos/red-dot-rosette-spa/screenshots/02-search.png
videos/red-dot-rosette-spa/screenshots/03-tension.png
videos/red-dot-rosette-spa/screenshots/04-transformation.png
videos/red-dot-rosette-spa/screenshots/05-resolution.png
videos/red-dot-rosette-spa/screenshots/mobile-resolution.png
videos/red-dot-rosette-spa/review-frames/frame-start.png
videos/red-dot-rosette-spa/review-frames/frame-middle.png
videos/red-dot-rosette-spa/review-frames/frame-final.png
videos/red-dot-rosette-spa/review-frames-0.3s/frames/
videos/red-dot-rosette-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-rosette-spa/review/contact-sheet.png
videos/red-dot-rosette-spa/recording-summary.json
videos/red-dot-rosette-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-rosette-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in interactive mode.
- Recorded validation disables looping and holds on the resolved rosette.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat uses one petal family throughout so the point feels like it is refining one idea instead of browsing unrelated symbols.
- The tension beat keeps a visible vertical pinch around the point before the rosette appears, so the transformation reads as pressure becoming structure.
- The transformation beat traces the rosette route before the final petals settle inward, proving how the final emblem is assembled instead of swapping directly into a badge.

