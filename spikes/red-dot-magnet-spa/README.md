---
title: Red Dot Magnet SPA
status: active
date: 2026-05-02
---

# Red Dot Magnet SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point tests three magnetic receiver grammars, gets compressed between opposing poles, then traces a calmer open field that settles into a centered magnetic emblem.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-magnet-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-magnet-spa/
```

Primary outputs:

```text
videos/red-dot-magnet-spa/red-dot-magnet-spa.webm
videos/red-dot-magnet-spa/poster-final.png
videos/red-dot-magnet-spa/screenshots/01-appearance.png
videos/red-dot-magnet-spa/screenshots/02-search.png
videos/red-dot-magnet-spa/screenshots/03-tension.png
videos/red-dot-magnet-spa/screenshots/04-transformation.png
videos/red-dot-magnet-spa/screenshots/05-resolution.png
videos/red-dot-magnet-spa/screenshots/mobile-resolution.png
videos/red-dot-magnet-spa/review-frames/frame-start.png
videos/red-dot-magnet-spa/review-frames/frame-middle.png
videos/red-dot-magnet-spa/review-frames/frame-final.png
videos/red-dot-magnet-spa/review/contact-sheet.png
videos/red-dot-magnet-spa/recording-summary.json
videos/red-dot-magnet-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-magnet-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the three receiver candidates inside the middle composition band so the point reads as testing magnetic grammars instead of wandering through decoration.
- The tension beat compresses the point between opposing poles while the receiving field remains visibly prepared around it.
- The transformation beat uses the moving point to draw the open field memory before the final hold retires the tight capture geometry.
