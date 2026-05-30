---
title: Red Dot Kite SPA
status: active
date: 2026-05-05
---

# Red Dot Kite SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn pull and drift into a stable kite grammar.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three related kite-frame candidates, gets pulled into a crossed tension point, then redraws that same pressure system into a calm centered kite emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-kite-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-kite-spa/
```

Primary outputs:

```text
videos/red-dot-kite-spa/red-dot-kite-spa.webm
videos/red-dot-kite-spa/poster-final.png
videos/red-dot-kite-spa/screenshots/01-appearance.png
videos/red-dot-kite-spa/screenshots/02-search.png
videos/red-dot-kite-spa/screenshots/03-tension.png
videos/red-dot-kite-spa/screenshots/04-transformation.png
videos/red-dot-kite-spa/screenshots/05-resolution.png
videos/red-dot-kite-spa/screenshots/mobile-resolution.png
videos/red-dot-kite-spa/review-frames/frame-start.png
videos/red-dot-kite-spa/review-frames/frame-middle.png
videos/red-dot-kite-spa/review-frames/frame-final.png
videos/red-dot-kite-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-kite-spa/review/contact-sheet.png
videos/red-dot-kite-spa/recording-summary.json
videos/red-dot-kite-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-kite-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the pending kite scaffold, so the point feels guided toward a destination instead of wandering through empty space.
- The search beat keeps every candidate in the same kite family, so the point reads as refining one structural idea instead of browsing unrelated symbols.
- The tension beat keeps the crossed tethers, pressure diamond, and center point visible together, so the conflict reads as pull and restraint rather than a generic squeeze.
- The transformation beat traces the kite shell first, then settles the spar, braces, and tail details so the resolution feels causally built from the same pressure system.
