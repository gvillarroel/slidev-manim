---
title: Red Dot Switchback SPA
status: active
date: 2026-05-03
---

# Red Dot Switchback SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how to turn pressure into direction instead of staying a loose accent.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three turn grammars, gets compressed inside a narrow switchback pocket, then redraws the stage into a compact centered route that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-switchback-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-switchback-spa/
```

Primary outputs:

```text
videos/red-dot-switchback-spa/red-dot-switchback-spa.webm
videos/red-dot-switchback-spa/poster-final.png
videos/red-dot-switchback-spa/screenshots/01-appearance.png
videos/red-dot-switchback-spa/screenshots/02-search.png
videos/red-dot-switchback-spa/screenshots/03-tension.png
videos/red-dot-switchback-spa/screenshots/04-transformation.png
videos/red-dot-switchback-spa/screenshots/05-resolution.png
videos/red-dot-switchback-spa/screenshots/mobile-resolution.png
videos/red-dot-switchback-spa/review-frames/frame-start.png
videos/red-dot-switchback-spa/review-frames/frame-middle.png
videos/red-dot-switchback-spa/review-frames/frame-final.png
videos/red-dot-switchback-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-switchback-spa/review/contact-sheet.png
videos/red-dot-switchback-spa/recording-summary.json
videos/red-dot-switchback-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-switchback-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate in one turn-and-corridor family, so the point reads as refining one directional idea instead of browsing unrelated icons.
- The tension beat keeps the turn pocket and the next outbound lane visible together, so the conflict reads as needing to survive a tight change in direction instead of a generic squeeze.
- The transformation beat lets the red point prove the tight turn first, then traces the wider switchback route before the final hold compacts into a calmer centered emblem.
- The runner emits 0.3-second cadence review sheets so cleanup between tension, transformation, and resolution can be checked without ad hoc extraction.
