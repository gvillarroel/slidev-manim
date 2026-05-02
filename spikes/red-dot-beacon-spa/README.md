---
title: Red Dot Beacon SPA
status: active
date: 2026-05-02
---

# Red Dot Beacon SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three signal grammars, compresses through a narrow aperture, then resolves into a centered beacon-like mark that holds without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-beacon-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-beacon-spa/
```

Primary outputs:

```text
videos/red-dot-beacon-spa/red-dot-beacon-spa.webm
videos/red-dot-beacon-spa/poster-final.png
videos/red-dot-beacon-spa/screenshots/01-appearance.png
videos/red-dot-beacon-spa/screenshots/02-search.png
videos/red-dot-beacon-spa/screenshots/03-tension.png
videos/red-dot-beacon-spa/screenshots/04-transformation.png
videos/red-dot-beacon-spa/screenshots/05-resolution.png
videos/red-dot-beacon-spa/screenshots/mobile-resolution.png
videos/red-dot-beacon-spa/review-frames/frame-start.png
videos/red-dot-beacon-spa/review-frames/frame-middle.png
videos/red-dot-beacon-spa/review-frames/frame-final.png
videos/red-dot-beacon-spa/review/contact-sheet.png
videos/red-dot-beacon-spa/recording-summary.json
videos/red-dot-beacon-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-beacon-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the candidate signal grammars in the middle composition band so the red point feels like it is probing structure rather than decorating the top edge.
- The tension beat uses a real aperture with opposing shutters and compression braces so the conflict reads as a constrained passage instead of a generic pause.
- The transformation beat lets the point trace the beacon route before the surrounding markers settle inward, proving the structure before the final centered hold simplifies into a calm device.
