---
title: Red Dot Crank SPA
status: active
date: 2026-05-05
---

# Red Dot Crank SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn a straight arrival into rotational agency.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters along a quiet lane, tests three crank-like joint grammars, gets pinned inside a narrow mechanical throat, then resolves into a calm crank emblem where the red point becomes the active pin that connects the motion.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-crank-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-crank-spa/
```

Primary outputs:

```text
videos/red-dot-crank-spa/red-dot-crank-spa.webm
videos/red-dot-crank-spa/poster-final.png
videos/red-dot-crank-spa/screenshots/01-appearance.png
videos/red-dot-crank-spa/screenshots/02-search.png
videos/red-dot-crank-spa/screenshots/03-tension.png
videos/red-dot-crank-spa/screenshots/04-transformation.png
videos/red-dot-crank-spa/screenshots/05-resolution.png
videos/red-dot-crank-spa/screenshots/mobile-resolution.png
videos/red-dot-crank-spa/review-frames/frame-start.png
videos/red-dot-crank-spa/review-frames/frame-middle.png
videos/red-dot-crank-spa/review-frames/frame-final.png
videos/red-dot-crank-spa/review-frames-0.3s/frames/
videos/red-dot-crank-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-crank-spa/review/contact-sheet.png
videos/red-dot-crank-spa/recording-summary.json
videos/red-dot-crank-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-crank-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- Add `?phase=appearance`, `?phase=search`, `?phase=tension`, `?phase=transformation`, or `?phase=resolution` to freeze the SPA on a stable review frame for that act.
- The opening keeps the future hub, axle, and jaw hints visible from frame zero so the proof image reads as a prepared mechanism rather than a drifting red dot.
- The search beat keeps all three candidate joints in one family, so the point feels like it is refining one mechanical idea instead of browsing unrelated icons.
- The tension beat uses opposing jaws, a visible collar, and a narrowed slot so the conflict reads as a real pinching mechanism rather than a generic gate.
- The transformation beat converts that pressure into a rotating arm, then retires the active red traces so the final hold reads as one calm crank device with the red pin as the narrative center.
