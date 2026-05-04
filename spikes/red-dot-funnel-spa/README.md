---
title: Red Dot Funnel SPA
status: active
date: 2026-05-04
---

# Red Dot Funnel SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three converging route grammars, gets compressed inside a visible merge throat, then turns that pressure into a centered funnel-like merge mark with a calm terminal hold.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-funnel-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, generates 0.3-second cadence sheets, and writes all generated artifacts to:

```text
videos/red-dot-funnel-spa/
```

Primary outputs:

```text
videos/red-dot-funnel-spa/red-dot-funnel-spa.webm
videos/red-dot-funnel-spa/poster-final.png
videos/red-dot-funnel-spa/screenshots/01-appearance.png
videos/red-dot-funnel-spa/screenshots/02-search.png
videos/red-dot-funnel-spa/screenshots/03-tension.png
videos/red-dot-funnel-spa/screenshots/04-transformation.png
videos/red-dot-funnel-spa/screenshots/05-resolution.png
videos/red-dot-funnel-spa/screenshots/mobile-resolution.png
videos/red-dot-funnel-spa/review-frames/frame-start.png
videos/red-dot-funnel-spa/review-frames/frame-middle.png
videos/red-dot-funnel-spa/review-frames/frame-final.png
videos/red-dot-funnel-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-funnel-spa/review/contact-sheet.png
videos/red-dot-funnel-spa/recording-summary.json
videos/red-dot-funnel-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-funnel-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested merge lane visible long enough to read as exploration instead of a random jump.
- The tension beat keeps the funnel walls and narrow throat visible around the dot so the conflict reads as compression into a chosen path.
- The transformation beat traces a single continuous merge outline that starts and ends at the same throat, so the resolved hold feels causally built rather than swapped in.
