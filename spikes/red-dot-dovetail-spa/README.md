---
title: Red Dot Dovetail SPA
status: active
date: 2026-05-03
---

# Red Dot Dovetail SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how to become an interlocking join instead of a loose moving accent.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three join grammars, compresses inside a narrow dovetail throat, then redraws the stage into a compact centered interlock that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-dovetail-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-dovetail-spa/
```

Primary outputs:

```text
videos/red-dot-dovetail-spa/red-dot-dovetail-spa.webm
videos/red-dot-dovetail-spa/poster-final.png
videos/red-dot-dovetail-spa/screenshots/01-appearance.png
videos/red-dot-dovetail-spa/screenshots/02-search.png
videos/red-dot-dovetail-spa/screenshots/03-tension.png
videos/red-dot-dovetail-spa/screenshots/04-transformation.png
videos/red-dot-dovetail-spa/screenshots/05-resolution.png
videos/red-dot-dovetail-spa/screenshots/mobile-resolution.png
videos/red-dot-dovetail-spa/review-frames/frame-start.png
videos/red-dot-dovetail-spa/review-frames/frame-middle.png
videos/red-dot-dovetail-spa/review-frames/frame-final.png
videos/red-dot-dovetail-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-dovetail-spa/review/contact-sheet.png
videos/red-dot-dovetail-spa/recording-summary.json
videos/red-dot-dovetail-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-dovetail-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate in the same interlock family, so the point reads as refining one join logic instead of shopping between unrelated icons.
- The tension beat keeps both opposing jaws visible while the center gap narrows, so the conflict reads as an interlock throat instead of a generic squeeze.
- The transformation beat proves the join by tracing the full taper route before the seam and supporting slot marks settle into a calmer centered hold.
- The runner also emits 0.3-second continuity review sheets, so cleanup between tension and transformation can be checked without rerunning ad hoc extraction commands.
