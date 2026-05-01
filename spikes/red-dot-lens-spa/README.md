---
title: Red Dot Lens SPA
status: active
date: 2026-05-01
---

# Red Dot Lens SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point appears in a quiet field, tests three candidate identities, survives a narrowing lens, then resolves into one centered system with the earlier search compressed into memory.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-lens-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-lens-spa/
```

Primary outputs:

```text
videos/red-dot-lens-spa/red-dot-lens-spa.webm
videos/red-dot-lens-spa/poster-final.png
videos/red-dot-lens-spa/screenshots/01-appearance.png
videos/red-dot-lens-spa/screenshots/02-search.png
videos/red-dot-lens-spa/screenshots/03-tension.png
videos/red-dot-lens-spa/screenshots/04-transformation.png
videos/red-dot-lens-spa/screenshots/05-resolution.png
videos/red-dot-lens-spa/screenshots/mobile-resolution.png
videos/red-dot-lens-spa/review-frames/frame-start.png
videos/red-dot-lens-spa/review-frames/frame-middle.png
videos/red-dot-lens-spa/review-frames/frame-final.png
videos/red-dot-lens-spa/review/contact-sheet.png
videos/red-dot-lens-spa/recording-summary.json
videos/red-dot-lens-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-lens-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat leaves each tried identity behind as muted residue so the point feels like it is learning instead of teleporting between unrelated ornaments.
- The tension beat uses lateral shutters instead of a top-and-bottom aperture, making the conflict read as a forced narrowing rather than a vertical crop.
- The resolved hold recenters the activated system so the ending reads as a calm conclusion instead of a leftover right-side target.
