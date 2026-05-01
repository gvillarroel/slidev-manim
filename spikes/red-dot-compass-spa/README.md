---
title: Red Dot Compass SPA
status: active
date: 2026-05-01
---

# Red Dot Compass SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three possible orientation grammars, compresses inside a central hinge, then resolves into a calm compass-like system that holds attention without relying on explanatory text.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-compass-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-compass-spa/
```

Primary outputs:

```text
videos/red-dot-compass-spa/red-dot-compass-spa.webm
videos/red-dot-compass-spa/poster-final.png
videos/red-dot-compass-spa/screenshots/01-appearance.png
videos/red-dot-compass-spa/screenshots/02-search.png
videos/red-dot-compass-spa/screenshots/03-tension.png
videos/red-dot-compass-spa/screenshots/04-transformation.png
videos/red-dot-compass-spa/screenshots/05-resolution.png
videos/red-dot-compass-spa/screenshots/mobile-resolution.png
videos/red-dot-compass-spa/review-frames/frame-start.png
videos/red-dot-compass-spa/review-frames/frame-middle.png
videos/red-dot-compass-spa/review-frames/frame-final.png
videos/red-dot-compass-spa/review/contact-sheet.png
videos/red-dot-compass-spa/recording-summary.json
videos/red-dot-compass-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-compass-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps three distinct trial grammars visible long enough to read as tested orientations instead of decorative traces.
- The tension beat uses a top-and-bottom hinge so the red point looks visibly compressed before the compass grammar opens.
- The transformation beat lets the point author the cardinal spokes directly, then retires the slots and hinge so the final hold feels centered and calm.
