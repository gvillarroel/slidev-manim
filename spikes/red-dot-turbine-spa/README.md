---
title: Red Dot Turbine SPA
status: active
date: 2026-05-05
---

# Red Dot Turbine SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters along a quiet lane, tests three vane candidates, compresses through a rotational throat, then resolves into a calm turbine-like hub that keeps the red core as the only strong accent.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-turbine-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-turbine-spa/
```

Primary outputs:

```text
videos/red-dot-turbine-spa/red-dot-turbine-spa.webm
videos/red-dot-turbine-spa/poster-final.png
videos/red-dot-turbine-spa/screenshots/01-appearance.png
videos/red-dot-turbine-spa/screenshots/02-search.png
videos/red-dot-turbine-spa/screenshots/03-tension.png
videos/red-dot-turbine-spa/screenshots/04-transformation.png
videos/red-dot-turbine-spa/screenshots/05-resolution.png
videos/red-dot-turbine-spa/screenshots/mobile-resolution.png
videos/red-dot-turbine-spa/review-frames/frame-start.png
videos/red-dot-turbine-spa/review-frames/frame-middle.png
videos/red-dot-turbine-spa/review-frames/frame-final.png
videos/red-dot-turbine-spa/review-frames-0.3s/frames/
videos/red-dot-turbine-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-turbine-spa/review/contact-sheet.png
videos/red-dot-turbine-spa/recording-summary.json
videos/red-dot-turbine-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-turbine-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- Add `?phase=appearance`, `?phase=search`, `?phase=tension`, `?phase=transformation`, or `?phase=resolution` to freeze the SPA on a stable review frame for that act.
- The opening keeps the destination hub and blade hints visible from frame zero so the first proof image reads as a prepared mechanism instead of a drifting red dot.
- The tension beat uses opposing diagonal vanes and a narrow spindle throat so the pressure frame reads as rotational conflict rather than a generic gate.
- The transformation beat traces the turbine geometry before the final hold retires the active route, leaving a calmer centered device for the ending.
