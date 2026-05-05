---
title: Red Dot Hourglass SPA
status: active
date: 2026-05-05
---

# Red Dot Hourglass SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters along a quiet lane, tests three vessel grammars in the upper field, compresses through a narrow hourglass waist, then resolves into a calm centered hourglass emblem where the red point becomes the settled lower chamber core.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-hourglass-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-hourglass-spa/
```

Primary outputs:

```text
videos/red-dot-hourglass-spa/red-dot-hourglass-spa.webm
videos/red-dot-hourglass-spa/poster-final.png
videos/red-dot-hourglass-spa/screenshots/01-appearance.png
videos/red-dot-hourglass-spa/screenshots/02-search.png
videos/red-dot-hourglass-spa/screenshots/03-tension.png
videos/red-dot-hourglass-spa/screenshots/04-transformation.png
videos/red-dot-hourglass-spa/screenshots/05-resolution.png
videos/red-dot-hourglass-spa/screenshots/mobile-resolution.png
videos/red-dot-hourglass-spa/review-frames/frame-start.png
videos/red-dot-hourglass-spa/review-frames/frame-middle.png
videos/red-dot-hourglass-spa/review-frames/frame-final.png
videos/red-dot-hourglass-spa/review-frames-0.3s/frames/
videos/red-dot-hourglass-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-hourglass-spa/review/contact-sheet.png
videos/red-dot-hourglass-spa/recording-summary.json
videos/red-dot-hourglass-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-hourglass-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- Add `?phase=appearance`, `?phase=search`, `?phase=tension`, `?phase=transformation`, or `?phase=resolution` to freeze the SPA on a stable review frame for that act.
- The opening keeps the future hourglass silhouette, bowl slots, and waist guide visible from frame zero so the first proof frame reads as a prepared mechanism instead of an isolated dot in empty space.
- The search act stays in the upper chamber vocabulary long enough to make the later waist squeeze feel like a failed attempt to choose shape, not just a route change.
- The resolution is intentionally calmer than the transformation proof: the red trace residue falls away, the waist pressure disappears, and the full vertical silhouette holds cleanly for review.
