---
title: Red Dot Zipper SPA
status: active
date: 2026-05-03
---

# Red Dot Zipper SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that pressure can become closure.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three zipper-like closure grammars, gets compressed inside a slider throat, then redraws that pressure into a compact centered zipper emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-zipper-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-zipper-spa/
```

Primary outputs:

```text
videos/red-dot-zipper-spa/red-dot-zipper-spa.webm
videos/red-dot-zipper-spa/poster-final.png
videos/red-dot-zipper-spa/screenshots/01-appearance.png
videos/red-dot-zipper-spa/screenshots/02-search.png
videos/red-dot-zipper-spa/screenshots/03-tension.png
videos/red-dot-zipper-spa/screenshots/04-transformation.png
videos/red-dot-zipper-spa/screenshots/05-resolution.png
videos/red-dot-zipper-spa/screenshots/mobile-resolution.png
videos/red-dot-zipper-spa/review-frames/frame-start.png
videos/red-dot-zipper-spa/review-frames/frame-middle.png
videos/red-dot-zipper-spa/review-frames/frame-final.png
videos/red-dot-zipper-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-zipper-spa/review/contact-sheet.png
videos/red-dot-zipper-spa/recording-summary.json
videos/red-dot-zipper-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-zipper-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate inside one closure family, so the point reads as refining one mechanism instead of browsing unrelated icons.
- The tension beat keeps the zipper racks and slider throat visible together, so the conflict reads as a real pinch instead of a generic squeeze.
- The transformation beat lets the slider climb before the red seam fully calms down, proving how the closure is formed before the ending simplifies into a compact centered emblem.
- The runner emits 0.3-second continuity review sheets, so cleanup between tension and transformation can be checked without rerunning ad hoc extraction commands.
