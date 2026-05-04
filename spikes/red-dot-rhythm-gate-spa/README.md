---
title: Red Dot Rhythm Gate SPA
status: active
date: 2026-05-04
---

# Red Dot Rhythm Gate SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries a five-act rhythm-gate story:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three cadence gate grammars along a shared rail, gets compressed inside a narrow central channel, then resolves into a centered rhythm frame where the point reads as the pulse that organizes the whole system.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-rhythm-gate-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-rhythm-gate-spa/
```

Primary outputs:

```text
videos/red-dot-rhythm-gate-spa/red-dot-rhythm-gate-spa.webm
videos/red-dot-rhythm-gate-spa/poster-final.png
videos/red-dot-rhythm-gate-spa/screenshots/01-appearance.png
videos/red-dot-rhythm-gate-spa/screenshots/02-search.png
videos/red-dot-rhythm-gate-spa/screenshots/03-tension.png
videos/red-dot-rhythm-gate-spa/screenshots/04-transformation.png
videos/red-dot-rhythm-gate-spa/screenshots/05-resolution.png
videos/red-dot-rhythm-gate-spa/screenshots/mobile-resolution.png
videos/red-dot-rhythm-gate-spa/review-frames/frame-start.png
videos/red-dot-rhythm-gate-spa/review-frames/frame-middle.png
videos/red-dot-rhythm-gate-spa/review-frames/frame-final.png
videos/red-dot-rhythm-gate-spa/review-frames-0.3s/frames/
videos/red-dot-rhythm-gate-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-rhythm-gate-spa/review/contact-sheet.png
videos/red-dot-rhythm-gate-spa/recording-summary.json
videos/red-dot-rhythm-gate-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-rhythm-gate-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search act keeps all candidate gates inside the middle composition band so the point reads as testing cadence rather than wandering between decorations.
- The tension act keeps the channel visibly open around the compressed point before release, so the proof frame reads as a gate under pressure instead of a generic squeeze.
- The transformation act removes the pressure-only rails before the hold and promotes the new top and bottom rhythm traces into the resolved frame, so the ending reads as a stable cadence device rather than leftover scaffolding.
