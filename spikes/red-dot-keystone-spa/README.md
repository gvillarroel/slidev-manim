---
title: Red Dot Keystone SPA
status: active
date: 2026-05-02
---

# Red Dot Keystone SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point tests three possible pocket grammars, gets compressed inside a central receiving cavity, then traces a keystone-like lock structure that settles into a quieter centered emblem.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-keystone-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-keystone-spa/
```

Primary outputs:

```text
videos/red-dot-keystone-spa/red-dot-keystone-spa.webm
videos/red-dot-keystone-spa/poster-final.png
videos/red-dot-keystone-spa/screenshots/01-appearance.png
videos/red-dot-keystone-spa/screenshots/02-search.png
videos/red-dot-keystone-spa/screenshots/03-tension.png
videos/red-dot-keystone-spa/screenshots/04-transformation.png
videos/red-dot-keystone-spa/screenshots/05-resolution.png
videos/red-dot-keystone-spa/screenshots/mobile-resolution.png
videos/red-dot-keystone-spa/review-frames/frame-start.png
videos/red-dot-keystone-spa/review-frames/frame-middle.png
videos/red-dot-keystone-spa/review-frames/frame-final.png
videos/red-dot-keystone-spa/review/contact-sheet.png
videos/red-dot-keystone-spa/recording-summary.json
videos/red-dot-keystone-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-keystone-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the three pocket candidates in the middle composition band so the point reads as testing possible receivers instead of wandering through decorative traces.
- The tension beat assembles a visible receiving cavity around the point before the lock structure grows outward.
- The transformation beat lets the point trace the top and side anchors of the keystone system before the final hold retires the pocket scaffolds.
