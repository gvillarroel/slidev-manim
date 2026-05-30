---
title: Red Dot Caliper SPA
status: active
date: 2026-05-05
---

# Red Dot Caliper SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point turns loose measurement gestures into a precise caliper-like form.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three measuring-head grammars, gets pinched inside a narrow gauge, then redraws the stage into a calm caliper emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-caliper-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts dense review frames, and writes all generated artifacts to:

```text
videos/red-dot-caliper-spa/
```

Primary outputs:

```text
videos/red-dot-caliper-spa/red-dot-caliper-spa.webm
videos/red-dot-caliper-spa/poster-final.png
videos/red-dot-caliper-spa/screenshots/01-appearance.png
videos/red-dot-caliper-spa/screenshots/02-search.png
videos/red-dot-caliper-spa/screenshots/03-tension.png
videos/red-dot-caliper-spa/screenshots/04-transformation.png
videos/red-dot-caliper-spa/screenshots/05-resolution.png
videos/red-dot-caliper-spa/screenshots/mobile-resolution.png
videos/red-dot-caliper-spa/review-frames/frame-start.png
videos/red-dot-caliper-spa/review-frames/frame-middle.png
videos/red-dot-caliper-spa/review-frames/frame-final.png
videos/red-dot-caliper-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-caliper-spa/review/contact-sheet.png
videos/red-dot-caliper-spa/recording-summary.json
videos/red-dot-caliper-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-caliper-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM stays on the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame keeps a faint beam, legs, and lower rail visible so the red point enters into a prepared measurement family instead of an empty field.
- The search beat stays inside one caliper grammar family rather than swapping across unrelated icons.
- The tension beat narrows four jaws around the point so the conflict reads as real gauge pressure, not a generic clamp.
- The transformation beat traces the beam, outer legs, lower rail, and center stem before the hold simplifies into one clear centered emblem.
