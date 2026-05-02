---
title: Red Dot Orbit SPA
status: active
date: 2026-05-02
---

# Red Dot Orbit SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that motion becomes meaning only after it commits to an orbit.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three orbit grammars, gets captured inside a compressed gravitational lane, then redraws the stage into a centered orbital emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-orbit-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-orbit-spa/
```

Primary outputs:

```text
videos/red-dot-orbit-spa/red-dot-orbit-spa.webm
videos/red-dot-orbit-spa/poster-final.png
videos/red-dot-orbit-spa/screenshots/01-appearance.png
videos/red-dot-orbit-spa/screenshots/02-search.png
videos/red-dot-orbit-spa/screenshots/03-tension.png
videos/red-dot-orbit-spa/screenshots/04-transformation.png
videos/red-dot-orbit-spa/screenshots/05-resolution.png
videos/red-dot-orbit-spa/screenshots/mobile-resolution.png
videos/red-dot-orbit-spa/review-frames/frame-start.png
videos/red-dot-orbit-spa/review-frames/frame-middle.png
videos/red-dot-orbit-spa/review-frames/frame-final.png
videos/red-dot-orbit-spa/review/contact-sheet.png
videos/red-dot-orbit-spa/recording-summary.json
videos/red-dot-orbit-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-orbit-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps all candidates inside one orbital family, so the point looks like it is refining one idea instead of browsing unrelated symbols.
- The tension beat uses a visible capture lane with opposing fins and a central core, so the conflict reads as gravitational capture rather than a generic squeeze.
- The transformation beat traces the orbit before the satellites finish settling, proving how the final emblem is built before the ending simplifies into a calm center-weighted mark.
