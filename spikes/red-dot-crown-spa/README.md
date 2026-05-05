---
title: Red Dot Crown SPA
status: active
date: 2026-05-05
---

# Red Dot Crown SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn pressure into a crown-like passage.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three related crown grammars above one faint doorway, gets compressed beneath a narrowing crest, then redraws that pressure into a calm centered crown-and-doorway emblem.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-crown-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-crown-spa/
```

Primary outputs:

```text
videos/red-dot-crown-spa/red-dot-crown-spa.webm
videos/red-dot-crown-spa/poster-final.png
videos/red-dot-crown-spa/screenshots/01-appearance.png
videos/red-dot-crown-spa/screenshots/02-search.png
videos/red-dot-crown-spa/screenshots/03-tension.png
videos/red-dot-crown-spa/screenshots/04-transformation.png
videos/red-dot-crown-spa/screenshots/05-resolution.png
videos/red-dot-crown-spa/screenshots/mobile-resolution.png
videos/red-dot-crown-spa/review-frames/frame-start.png
videos/red-dot-crown-spa/review-frames/frame-middle.png
videos/red-dot-crown-spa/review-frames/frame-final.png
videos/red-dot-crown-spa/review-frames-0.3s/frames/
videos/red-dot-crown-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-crown-spa/review/contact-sheet.png
videos/red-dot-crown-spa/recording-summary.json
videos/red-dot-crown-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-crown-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the pending doorway and crown slot so the point never feels stranded on an empty lane.
- The search act stays in one crown family: each candidate shares the same passage baseline instead of switching to unrelated icons.
- The tension beat keeps the doorway visible under the descending crest so the conflict reads as real passage pressure instead of a generic clamp.
- The transformation beat redraws the crown from the constricted center outward, then returns the point to the doorway center for the resolved hold.
- Portrait review uses phase-specific crops and scene scaling so the crown peaks and doorway stay readable on mobile.
