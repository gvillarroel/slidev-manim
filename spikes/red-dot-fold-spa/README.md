---
title: Red Dot Fold SPA
status: active
date: 2026-05-01
---

# Red Dot Fold SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three fold grammars, gets compressed inside a crease pinch, then resolves into a centered origami-like fold system that holds without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-fold-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-fold-spa/
```

Primary outputs:

```text
videos/red-dot-fold-spa/red-dot-fold-spa.webm
videos/red-dot-fold-spa/poster-final.png
videos/red-dot-fold-spa/screenshots/01-appearance.png
videos/red-dot-fold-spa/screenshots/02-search.png
videos/red-dot-fold-spa/screenshots/03-tension.png
videos/red-dot-fold-spa/screenshots/04-transformation.png
videos/red-dot-fold-spa/screenshots/05-resolution.png
videos/red-dot-fold-spa/screenshots/mobile-resolution.png
videos/red-dot-fold-spa/review-frames/frame-start.png
videos/red-dot-fold-spa/review-frames/frame-middle.png
videos/red-dot-fold-spa/review-frames/frame-final.png
videos/red-dot-fold-spa/review/contact-sheet.png
videos/red-dot-fold-spa/recording-summary.json
videos/red-dot-fold-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-fold-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested fold grammar visible as faint residue so the point feels like it is learning a structure instead of teleporting between ornaments.
- The tension beat uses converging fold planes and a visible crease spine so the conflict reads as a forced flattening, not as a generic stop or shutter.
- The transformation beat turns the compressed point into a four-facet fold system with prepared slots, then the resolved hold retires those helpers and recenters the final origami-like form around the red core.
