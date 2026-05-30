---
title: Red Dot Ramp SPA
status: active
date: 2026-05-03
---

# Red Dot Ramp SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that rise only feels meaningful once pressure turns into support.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three incline grammars, gets pinned at the crest of a lifting ramp, then redraws that conflict into a calm centered lift emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-ramp-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, builds 0.3-second cadence sheets, and writes all generated artifacts to:

```text
videos/red-dot-ramp-spa/
```

Primary outputs:

```text
videos/red-dot-ramp-spa/red-dot-ramp-spa.webm
videos/red-dot-ramp-spa/poster-final.png
videos/red-dot-ramp-spa/screenshots/01-appearance.png
videos/red-dot-ramp-spa/screenshots/02-search.png
videos/red-dot-ramp-spa/screenshots/03-tension.png
videos/red-dot-ramp-spa/screenshots/04-transformation.png
videos/red-dot-ramp-spa/screenshots/05-resolution.png
videos/red-dot-ramp-spa/screenshots/mobile-resolution.png
videos/red-dot-ramp-spa/review-frames/frame-start.png
videos/red-dot-ramp-spa/review-frames/frame-middle.png
videos/red-dot-ramp-spa/review-frames/frame-final.png
videos/red-dot-ramp-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-ramp-spa/review/contact-sheet.png
videos/red-dot-ramp-spa/recording-summary.json
videos/red-dot-ramp-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-ramp-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The appearance beat previews only the nearest incline candidate plus the future ramp system, so the opening frame stays centered instead of reading like a full search board too early.
- The search beat keeps every candidate inside one ramp-and-landing family, so the point reads as refining one lift grammar instead of browsing unrelated icons.
- The tension beat keeps the ramp, base supports, and blocker visible together, so the proof frame reads as an authored lift pocket rather than a generic squeeze.
- The transformation beat opens the blocker into a calmer crest while support blocks arrive underneath, proving how the resolved emblem grows out of the conflict before the final hold retires the route.
