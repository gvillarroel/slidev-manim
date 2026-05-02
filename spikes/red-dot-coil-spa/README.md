---
title: Red Dot Coil SPA
status: active
date: 2026-05-02
---

# Red Dot Coil SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how to become tension, release, and structure at once.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three related curl grammars, gets compressed between opposing shutters, then uncoils into a compact centered emblem that holds without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-coil-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-coil-spa/
```

Primary outputs:

```text
videos/red-dot-coil-spa/red-dot-coil-spa.webm
videos/red-dot-coil-spa/poster-final.png
videos/red-dot-coil-spa/screenshots/01-appearance.png
videos/red-dot-coil-spa/screenshots/02-search.png
videos/red-dot-coil-spa/screenshots/03-tension.png
videos/red-dot-coil-spa/screenshots/04-transformation.png
videos/red-dot-coil-spa/screenshots/05-resolution.png
videos/red-dot-coil-spa/screenshots/mobile-resolution.png
videos/red-dot-coil-spa/review-frames/frame-start.png
videos/red-dot-coil-spa/review-frames/frame-middle.png
videos/red-dot-coil-spa/review-frames/frame-final.png
videos/red-dot-coil-spa/review/contact-sheet.png
videos/red-dot-coil-spa/recording-summary.json
videos/red-dot-coil-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-coil-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat stays inside one curl-to-coil family so the point feels like it is refining a single idea instead of browsing unrelated symbols.
- The tension beat uses opposing vertical shutters and a visible central throat so the conflict reads as compression before release, not as generic motion.
- The transformation beat traces the coil from the constrained core outward, then the resolution recenters the red point so the final hold feels like a stable stored force rather than a path that simply ended.
