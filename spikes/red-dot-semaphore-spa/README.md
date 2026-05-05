---
title: Red Dot Semaphore SPA
status: active
date: 2026-05-05
---

# Red Dot Semaphore SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn loose gestures into a legible signal.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three signal-posture candidates around a faint mast, gets compressed into a tight central bundle, then redraws the stage into a calm semaphore-like emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-semaphore-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-semaphore-spa/
```

Primary outputs:

```text
videos/red-dot-semaphore-spa/red-dot-semaphore-spa.webm
videos/red-dot-semaphore-spa/poster-final.png
videos/red-dot-semaphore-spa/screenshots/01-appearance.png
videos/red-dot-semaphore-spa/screenshots/02-search.png
videos/red-dot-semaphore-spa/screenshots/03-tension.png
videos/red-dot-semaphore-spa/screenshots/04-transformation.png
videos/red-dot-semaphore-spa/screenshots/05-resolution.png
videos/red-dot-semaphore-spa/screenshots/mobile-resolution.png
videos/red-dot-semaphore-spa/review-frames/frame-start.png
videos/red-dot-semaphore-spa/review-frames/frame-middle.png
videos/red-dot-semaphore-spa/review-frames/frame-final.png
videos/red-dot-semaphore-spa/review/contact-sheet.png
videos/red-dot-semaphore-spa/recording-summary.json
videos/red-dot-semaphore-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-semaphore-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The appearance beat keeps a faint mast and hub visible from frame zero so the entering point does not feel stranded on an empty lane.
- The search beat stays in one signal grammar family: three postures around the same mast instead of three unrelated icons.
- The tension beat collapses the candidate posture into a tight central bundle so the conflict reads as a real loss of legibility, not just motion.
- The transformation beat lets the red point redraw the left arm, right arm, and mast in sequence before the final hold simplifies into one clear centered signal.
