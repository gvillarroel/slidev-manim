---
title: Red Dot Clamp SPA
status: active
date: 2026-05-04
---

# Red Dot Clamp SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three grip grammars, gets compressed inside a visible side clamp, then resolves into a calm centered clamp emblem with the pressure mechanism retired.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-clamp-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, builds 0.3-second cadence sheets, and writes all generated artifacts to:

```text
videos/red-dot-clamp-spa/
```

Primary outputs:

```text
videos/red-dot-clamp-spa/red-dot-clamp-spa.webm
videos/red-dot-clamp-spa/poster-final.png
videos/red-dot-clamp-spa/screenshots/01-appearance.png
videos/red-dot-clamp-spa/screenshots/02-search.png
videos/red-dot-clamp-spa/screenshots/03-tension.png
videos/red-dot-clamp-spa/screenshots/04-transformation.png
videos/red-dot-clamp-spa/screenshots/05-resolution.png
videos/red-dot-clamp-spa/screenshots/mobile-resolution.png
videos/red-dot-clamp-spa/review-frames/frame-start.png
videos/red-dot-clamp-spa/review-frames/frame-middle.png
videos/red-dot-clamp-spa/review-frames/frame-final.png
videos/red-dot-clamp-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-clamp-spa/review/contact-sheet.png
videos/red-dot-clamp-spa/recording-summary.json
videos/red-dot-clamp-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-clamp-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps all candidate grip grammars inside the middle composition band so the point reads as probing for a usable clamp instead of drifting.
- The tension beat uses visible side-pressure jaws and quiet top and bottom balancing rails so the proof frame reads as a real squeeze.
- The transformation beat converts that squeeze into a calmer centered clamp emblem and removes the pressure bars before the final hold.
