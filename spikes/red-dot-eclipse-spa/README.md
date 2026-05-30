---
title: Red Dot Eclipse SPA
status: active
date: 2026-05-03
---

# Red Dot Eclipse SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to hold a field through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet stage, tests three eclipse-like grammars, gets compressed between two offset occluding bodies, then redraws that pressure into a calm centered eclipse system.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-eclipse-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts boundary continuity frames, and writes all generated artifacts to:

```text
videos/red-dot-eclipse-spa/
```

Primary outputs:

```text
videos/red-dot-eclipse-spa/red-dot-eclipse-spa.webm
videos/red-dot-eclipse-spa/poster-final.png
videos/red-dot-eclipse-spa/screenshots/01-appearance.png
videos/red-dot-eclipse-spa/screenshots/02-search.png
videos/red-dot-eclipse-spa/screenshots/03-tension.png
videos/red-dot-eclipse-spa/screenshots/04-transformation.png
videos/red-dot-eclipse-spa/screenshots/05-resolution.png
videos/red-dot-eclipse-spa/screenshots/mobile-resolution.png
videos/red-dot-eclipse-spa/review-frames/frame-start.png
videos/red-dot-eclipse-spa/review-frames/frame-middle.png
videos/red-dot-eclipse-spa/review-frames/frame-final.png
videos/red-dot-eclipse-spa/review/contact-sheet.png
videos/red-dot-eclipse-spa/continuity-review/continuity-contact-sheet.png
videos/red-dot-eclipse-spa/recording-summary.json
videos/red-dot-eclipse-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-eclipse-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps three incomplete eclipse grammars visible on the middle band so the red point feels like it is testing possible occlusions instead of jumping between icons.
- The tension beat uses two large offset bodies that stay visible long enough to prove the compression before the orbit system starts to form.
- The resolved hold retires those heavy bodies and keeps only a compact ring, side crescents, and the centered red core so the ending feels quieter than the conflict.
