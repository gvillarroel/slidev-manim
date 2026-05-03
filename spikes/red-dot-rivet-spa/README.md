---
title: Red Dot Rivet SPA
status: active
date: 2026-05-03
---

# Red Dot Rivet SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point stops behaving like a loose accent and becomes the structural fastener that holds a composition together.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three fastening grammars, gets compressed inside a four-piece joint, then redraws that conflict into a calm rivet-like emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-rivet-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-rivet-spa/
```

Primary outputs:

```text
videos/red-dot-rivet-spa/red-dot-rivet-spa.webm
videos/red-dot-rivet-spa/poster-final.png
videos/red-dot-rivet-spa/screenshots/01-appearance.png
videos/red-dot-rivet-spa/screenshots/02-search.png
videos/red-dot-rivet-spa/screenshots/03-tension.png
videos/red-dot-rivet-spa/screenshots/04-transformation.png
videos/red-dot-rivet-spa/screenshots/05-resolution.png
videos/red-dot-rivet-spa/screenshots/mobile-resolution.png
videos/red-dot-rivet-spa/review-frames/frame-start.png
videos/red-dot-rivet-spa/review-frames/frame-middle.png
videos/red-dot-rivet-spa/review-frames/frame-final.png
videos/red-dot-rivet-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-rivet-spa/review/contact-sheet.png
videos/red-dot-rivet-spa/recording-summary.json
videos/red-dot-rivet-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-rivet-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate in the same family of joining grammars, so the point reads as refining one structural role instead of browsing unrelated icons.
- The tension beat uses four separate joint pieces instead of one enclosing frame, so the conflict reads as pressure around a fastening socket rather than as a generic crop.
- The transformation beat sends the point through a lock route that returns to center, so the proof frame shows the point actively authoring the joint before the final hold simplifies into a calm fastener mark.
- The runner also emits 0.3-second continuity review sheets, so cleanup between tension and transformation can be checked without rerunning ad hoc extraction commands.
