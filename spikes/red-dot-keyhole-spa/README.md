---
title: Red Dot Keyhole SPA
status: active
date: 2026-05-03
---

# Red Dot Keyhole SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how to become an access mark instead of a loose accent.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three access grammars, compresses through a narrow slot, then redraws the stage into a compact keyhole-like emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-keyhole-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-keyhole-spa/
```

Primary outputs:

```text
videos/red-dot-keyhole-spa/red-dot-keyhole-spa.webm
videos/red-dot-keyhole-spa/poster-final.png
videos/red-dot-keyhole-spa/screenshots/01-appearance.png
videos/red-dot-keyhole-spa/screenshots/02-search.png
videos/red-dot-keyhole-spa/screenshots/03-tension.png
videos/red-dot-keyhole-spa/screenshots/04-transformation.png
videos/red-dot-keyhole-spa/screenshots/05-resolution.png
videos/red-dot-keyhole-spa/screenshots/mobile-resolution.png
videos/red-dot-keyhole-spa/review-frames/frame-start.png
videos/red-dot-keyhole-spa/review-frames/frame-middle.png
videos/red-dot-keyhole-spa/review-frames/frame-final.png
videos/red-dot-keyhole-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-keyhole-spa/review/contact-sheet.png
videos/red-dot-keyhole-spa/recording-summary.json
videos/red-dot-keyhole-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-keyhole-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate in the same access family, so the point reads as refining one structural idea instead of browsing unrelated icons.
- The tension beat keeps the destination chamber visible above the slot, so the conflict reads as needing access through a narrow stem instead of a generic squeeze.
- The transformation beat proves the slot first, then lets the point orbit the chamber before the final hold simplifies into a calm centered keyhole-like mark.
- The runner also emits 0.3-second continuity review sheets, so cleanup between tension and transformation can be checked without rerunning ad hoc extraction commands.
