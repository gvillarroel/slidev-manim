---
title: Red Dot Balance SPA
status: active
date: 2026-05-02
---

# Red Dot Balance SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three support grammars, tips a balance into visible instability, then resolves into a centered calm mobile where the red core becomes the balancing pivot.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-balance-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-balance-spa/
```

Primary outputs:

```text
videos/red-dot-balance-spa/red-dot-balance-spa.webm
videos/red-dot-balance-spa/poster-final.png
videos/red-dot-balance-spa/screenshots/01-appearance.png
videos/red-dot-balance-spa/screenshots/02-search.png
videos/red-dot-balance-spa/screenshots/03-tension.png
videos/red-dot-balance-spa/screenshots/04-transformation.png
videos/red-dot-balance-spa/screenshots/05-resolution.png
videos/red-dot-balance-spa/screenshots/mobile-resolution.png
videos/red-dot-balance-spa/review-frames/frame-start.png
videos/red-dot-balance-spa/review-frames/frame-middle.png
videos/red-dot-balance-spa/review-frames/frame-final.png
videos/red-dot-balance-spa/review/contact-sheet.png
videos/red-dot-balance-spa/recording-summary.json
videos/red-dot-balance-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-balance-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested support grammar in the middle composition band so the point feels like it is testing places to rest, not wandering between decorations.
- The tension beat uses a visibly tilted beam, a prepared receiver on the loaded side, and a counterweight drop on the opposite side so the conflict reads as imbalance rather than generic compression.
- The transformation beat straightens the beam while the dot climbs toward the pivot and the missing support weight appears, then the resolved hold retires the receiver and leaves one calm balanced mobile.
