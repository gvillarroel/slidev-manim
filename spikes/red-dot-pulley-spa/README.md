---
title: Red Dot Pulley SPA
status: active
date: 2026-05-05
---

# Red Dot Pulley SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn hanging tension into a calm pulley-like system.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three related hanging-route grammars under one overhead beam, gets squeezed between two tightening sheaves, then redraws that pressure into a centered pulley emblem.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-pulley-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-pulley-spa/
```

Primary outputs:

```text
videos/red-dot-pulley-spa/red-dot-pulley-spa.webm
videos/red-dot-pulley-spa/poster-final.png
videos/red-dot-pulley-spa/screenshots/01-appearance.png
videos/red-dot-pulley-spa/screenshots/02-search.png
videos/red-dot-pulley-spa/screenshots/03-tension.png
videos/red-dot-pulley-spa/screenshots/04-transformation.png
videos/red-dot-pulley-spa/screenshots/05-resolution.png
videos/red-dot-pulley-spa/screenshots/mobile-resolution.png
videos/red-dot-pulley-spa/review-frames/frame-start.png
videos/red-dot-pulley-spa/review-frames/frame-middle.png
videos/red-dot-pulley-spa/review-frames/frame-final.png
videos/red-dot-pulley-spa/review-frames-0.3s/frames/
videos/red-dot-pulley-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-pulley-spa/review/contact-sheet.png
videos/red-dot-pulley-spa/recording-summary.json
videos/red-dot-pulley-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-pulley-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the overhead beam, the hanging lane, and the faint wheel pockets so the point never enters an empty field.
- The search act stays in one family of hanging routes instead of switching to unrelated icons.
- The tension beat keeps the beam and both sheaves visible while the lane narrows around the point.
- The transformation beat redraws the route from the compressed center upward and outward before the point settles back into the calm hanging line.
- Portrait review uses phase-specific crops so the beam, wheels, and final suspended point stay legible on mobile.
