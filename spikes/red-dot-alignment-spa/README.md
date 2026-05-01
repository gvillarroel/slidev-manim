---
title: Red Dot Alignment SPA
status: active
date: 2026-05-01
---

# Red Dot Alignment SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to align a field through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three incomplete alignment grammars, gets compressed inside a sheared interference pocket, then rebuilds the scene into a calm precision cross centered on the red anchor.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-alignment-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-alignment-spa/
```

Primary outputs:

```text
videos/red-dot-alignment-spa/red-dot-alignment-spa.webm
videos/red-dot-alignment-spa/poster-final.png
videos/red-dot-alignment-spa/screenshots/01-appearance.png
videos/red-dot-alignment-spa/screenshots/02-search.png
videos/red-dot-alignment-spa/screenshots/03-tension.png
videos/red-dot-alignment-spa/screenshots/04-transformation.png
videos/red-dot-alignment-spa/screenshots/05-resolution.png
videos/red-dot-alignment-spa/screenshots/mobile-resolution.png
videos/red-dot-alignment-spa/review-frames/frame-start.png
videos/red-dot-alignment-spa/review-frames/frame-middle.png
videos/red-dot-alignment-spa/review-frames/frame-final.png
videos/red-dot-alignment-spa/review/contact-sheet.png
videos/red-dot-alignment-spa/recording-summary.json
videos/red-dot-alignment-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-alignment-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested alignment grammar visible as faint residue so the point feels like it is calibrating the field instead of teleporting through icons.
- The tension beat uses four sheared panels that pull inward on separate lanes so the conflict reads as interference, not as a generic stop.
- The resolved hold removes the interference hardware and recenters the surviving beams around the red point so the ending feels precise instead of mechanical.
