---
title: Red Dot Dovetail SPA
status: active
date: 2026-05-05
---

# Red Dot Dovetail SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how to become an interlock instead of a loose accent.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three related join grammars, compresses through a narrow dovetail throat, then redraws the stage into a compact interlocked emblem that can hold without explanatory copy.

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
- The search beat keeps every candidate in the same join family, so the point reads as refining one interlock idea instead of browsing unrelated icons.
- The tension beat keeps the body outlines, top and bottom throat rules, and compression plates visible together, so the conflict reads as a constrained joint instead of a generic pause.
- The transformation beat proves the join by tracing the outer interlock route first, then settling the quieter end anchors and seam markers before the final hold simplifies into a calm centered mark.
- The runner also emits 0.3-second continuity review sheets, so cleanup between tension and transformation can be checked without rerunning ad hoc extraction commands.
