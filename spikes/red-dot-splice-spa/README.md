---
title: Red Dot Splice SPA
status: active
date: 2026-05-03
---

# Red Dot Splice SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point tests three joining grammars, compresses inside a broken seam, then traces a splice that resolves the gap into a quieter centered connected emblem.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-splice-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-splice-spa/
```

Primary outputs:

```text
videos/red-dot-splice-spa/red-dot-splice-spa.webm
videos/red-dot-splice-spa/poster-final.png
videos/red-dot-splice-spa/screenshots/01-appearance.png
videos/red-dot-splice-spa/screenshots/02-search.png
videos/red-dot-splice-spa/screenshots/03-tension.png
videos/red-dot-splice-spa/screenshots/04-transformation.png
videos/red-dot-splice-spa/screenshots/05-resolution.png
videos/red-dot-splice-spa/screenshots/mobile-resolution.png
videos/red-dot-splice-spa/review-frames/frame-start.png
videos/red-dot-splice-spa/review-frames/frame-middle.png
videos/red-dot-splice-spa/review-frames/frame-final.png
videos/red-dot-splice-spa/review/contact-sheet.png
videos/red-dot-splice-spa/recording-summary.json
videos/red-dot-splice-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-splice-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the three splice candidates inside the middle composition band so the point reads as testing join grammars instead of wandering through decoration.
- The tension beat preserves the broken seam while the clamp closes so the conflict stays legible before the splice route appears.
- The transformation beat makes the point return to center after tracing the splice loop so the final hold reads as a resolved connection rather than an unfinished route.
