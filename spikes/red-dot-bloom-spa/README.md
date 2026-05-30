---
title: Red Dot Bloom SPA
status: active
date: 2026-05-05
---

# Red Dot Bloom SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point arrives on a quiet lane, tests three petal slots, compresses inside a closing bud, then resolves into a calm geometric bloom that keeps the red core as the only strong accent.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-bloom-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-bloom-spa/
```

Primary outputs:

```text
videos/red-dot-bloom-spa/red-dot-bloom-spa.webm
videos/red-dot-bloom-spa/poster-final.png
videos/red-dot-bloom-spa/screenshots/01-appearance.png
videos/red-dot-bloom-spa/screenshots/02-search.png
videos/red-dot-bloom-spa/screenshots/03-tension.png
videos/red-dot-bloom-spa/screenshots/04-transformation.png
videos/red-dot-bloom-spa/screenshots/05-resolution.png
videos/red-dot-bloom-spa/screenshots/mobile-resolution.png
videos/red-dot-bloom-spa/review-frames/frame-start.png
videos/red-dot-bloom-spa/review-frames/frame-middle.png
videos/red-dot-bloom-spa/review-frames/frame-final.png
videos/red-dot-bloom-spa/review-frames-0.3s/frames/
videos/red-dot-bloom-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-bloom-spa/review/contact-sheet.png
videos/red-dot-bloom-spa/recording-summary.json
videos/red-dot-bloom-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-bloom-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- Add `?phase=appearance`, `?phase=search`, `?phase=tension`, `?phase=transformation`, or `?phase=resolution` to freeze the SPA on a stable review frame for that act.
- The opening keeps the future bud silhouette and a faint bloom scaffold visible from frame zero so the first proof frame reads as a prepared destination instead of an isolated moving dot.
- The tension beat uses four closing bud leaves, not only a left-right gate, so the pressure frame reads as enclosure rather than a generic corridor squeeze.
- The transformation beat lets the dot trace the bloom axes before the final hold retires the active routes and leaves a calmer centered emblem.
