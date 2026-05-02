---
title: Red Dot Cradle SPA
status: active
date: 2026-05-02
---

# Red Dot Cradle SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to be held, not just how to move.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three support grammars, hangs in a caught moment between a top tether and lower supports, then resolves into a compact open cradle that holds calmly at the center.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-cradle-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-cradle-spa/
```

Primary outputs:

```text
videos/red-dot-cradle-spa/red-dot-cradle-spa.webm
videos/red-dot-cradle-spa/poster-final.png
videos/red-dot-cradle-spa/screenshots/01-appearance.png
videos/red-dot-cradle-spa/screenshots/02-search.png
videos/red-dot-cradle-spa/screenshots/03-tension.png
videos/red-dot-cradle-spa/screenshots/04-transformation.png
videos/red-dot-cradle-spa/screenshots/05-resolution.png
videos/red-dot-cradle-spa/screenshots/mobile-resolution.png
videos/red-dot-cradle-spa/review-frames/frame-start.png
videos/red-dot-cradle-spa/review-frames/frame-middle.png
videos/red-dot-cradle-spa/review-frames/frame-final.png
videos/red-dot-cradle-spa/review/contact-sheet.png
videos/red-dot-cradle-spa/continuity-review/continuity-contact-sheet.png
videos/red-dot-cradle-spa/recording-summary.json
videos/red-dot-cradle-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-cradle-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat stays in the middle composition band while the dot tests three support grammars so the stage reads as guided exploration instead of a decorative sweep.
- The tension beat keeps the top tether visible long enough to prove the caught moment before the lower supports turn into the new structure.
- The resolution opens the cradle upward and retires the tether so the final frame reads as support, not confinement, on both desktop and mobile review.
- The runner also exports continuity-review stills around each phase boundary so transition polish can be checked without a manual video scrub.
