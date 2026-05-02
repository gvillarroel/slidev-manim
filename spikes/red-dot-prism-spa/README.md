---
title: Red Dot Prism SPA
status: active
date: 2026-05-02
---

# Red Dot Prism SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to become structure instead of decoration.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three facet grammars, compresses through a narrow prism throat, then redraws the stage into a compact prism-like emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-prism-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-prism-spa/
```

Primary outputs:

```text
videos/red-dot-prism-spa/red-dot-prism-spa.webm
videos/red-dot-prism-spa/poster-final.png
videos/red-dot-prism-spa/screenshots/01-appearance.png
videos/red-dot-prism-spa/screenshots/02-search.png
videos/red-dot-prism-spa/screenshots/03-tension.png
videos/red-dot-prism-spa/screenshots/04-transformation.png
videos/red-dot-prism-spa/screenshots/05-resolution.png
videos/red-dot-prism-spa/screenshots/mobile-resolution.png
videos/red-dot-prism-spa/review-frames/frame-start.png
videos/red-dot-prism-spa/review-frames/frame-middle.png
videos/red-dot-prism-spa/review-frames/frame-final.png
videos/red-dot-prism-spa/review/contact-sheet.png
videos/red-dot-prism-spa/recording-summary.json
videos/red-dot-prism-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-prism-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the candidate tests on one diagonal-to-horizontal faceting grammar, so the point feels like it is discovering one family of structure rather than browsing unrelated symbols.
- The tension beat uses visible opposing prism clamps and a narrow throat, so the conflict reads as compression through a device instead of a generic squeeze.
- The transformation beat traces the prism perimeter before the central axis settles, proving how the resolved emblem is built before the final hold simplifies into a calm center-weighted mark.
