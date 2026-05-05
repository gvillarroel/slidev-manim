---
title: Red Dot Spring SPA
status: active
date: 2026-05-05
---

# Red Dot Spring SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns that pressure can become structure instead of just obstruction.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests orbit, zigzag, and wave grammars, gets compressed between a top and bottom press, then releases that stored energy into a centered spring-like system that holds attention with almost no text.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-spring-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, generates `0.3s` cadence sheets, and writes all generated artifacts to:

```text
videos/red-dot-spring-spa/
```

Primary outputs:

```text
videos/red-dot-spring-spa/red-dot-spring-spa.webm
videos/red-dot-spring-spa/poster-final.png
videos/red-dot-spring-spa/screenshots/01-appearance.png
videos/red-dot-spring-spa/screenshots/02-search.png
videos/red-dot-spring-spa/screenshots/03-tension.png
videos/red-dot-spring-spa/screenshots/04-transformation.png
videos/red-dot-spring-spa/screenshots/05-resolution.png
videos/red-dot-spring-spa/screenshots/mobile-resolution.png
videos/red-dot-spring-spa/review/contact-sheet.png
videos/red-dot-spring-spa/review-frames/frame-start.png
videos/red-dot-spring-spa/review-frames/frame-middle.png
videos/red-dot-spring-spa/review-frames/frame-final.png
videos/red-dot-spring-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-spring-spa/recording-summary.json
videos/red-dot-spring-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-spring-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate inside one energy-storage family, so the point reads as refining one idea instead of browsing unrelated symbols.
- The tension beat uses a visible top-and-bottom press with interior charge bars, so the conflict reads as stored compression rather than a generic stop.
- The transformation beat grows the spring from the red core outward before the helper slots disappear, proving how the final emblem is built instead of swapping in a decorative badge.
