---
title: Red Dot Hinge SPA
status: active
date: 2026-05-02
---

# Red Dot Hinge SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries a five-act hinge story:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three hinge grammars, gets compressed between opposing shutters, then resolves into a centered open hinge where the red core reads as the pin that keeps the whole structure aligned.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-hinge-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-hinge-spa/
```

Primary outputs:

```text
videos/red-dot-hinge-spa/red-dot-hinge-spa.webm
videos/red-dot-hinge-spa/poster-final.png
videos/red-dot-hinge-spa/screenshots/01-appearance.png
videos/red-dot-hinge-spa/screenshots/02-search.png
videos/red-dot-hinge-spa/screenshots/03-tension.png
videos/red-dot-hinge-spa/screenshots/04-transformation.png
videos/red-dot-hinge-spa/screenshots/05-resolution.png
videos/red-dot-hinge-spa/screenshots/mobile-resolution.png
videos/red-dot-hinge-spa/review-frames/frame-start.png
videos/red-dot-hinge-spa/review-frames/frame-middle.png
videos/red-dot-hinge-spa/review-frames/frame-final.png
videos/red-dot-hinge-spa/review/contact-sheet.png
videos/red-dot-hinge-spa/recording-summary.json
videos/red-dot-hinge-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-hinge-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the three hinge candidates in the middle composition band so the point reads as testing possible joints rather than wandering between ornaments.
- The tension beat keeps the axis pin and lower slot visible before the shutters close, so the conflict reads as a hinge under pressure instead of a generic clamp.
- The transformation beat opens the shutters into four calmer wings and retires the conflict-only guides before the final hold, so the resolution reads as a stable object instead of a trapped core.
