---
title: Red Dot Switchback SPA
status: active
date: 2026-05-03
---

# Red Dot Switchback SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how to guide attention by reversing direction without losing continuity.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three turning grammars from the same family, gets compressed inside a narrow elbow, then resolves into a centered switchback route that can hold without explanatory copy.

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
- The phase status remains screen-reader-only so proof frames stay visual-first.
- The search beat keeps every candidate in one turning grammar family, so the point reads as refining direction instead of browsing unrelated icons.
- The tension beat keeps the elbow corridor visible while the dot compresses at the pivot, so the conflict reads as constrained redirection instead of generic pressure.
- The transformation beat proves the switchback by tracing the route through the outer turn, the long return shelf, and the top recovery before the path settles back onto the center pivot.
- The runner also emits 0.3-second continuity review sheets, so cleanup between tension and transformation can be checked without rerunning ad hoc extraction commands.
