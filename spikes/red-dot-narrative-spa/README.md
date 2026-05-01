---
title: Red Dot Narrative SPA
status: active
date: 2026-05-01
---

# Red Dot Narrative SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The experience is intentionally sparse. The motion, spacing, and hierarchy should explain the sequence without leaning on explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-narrative-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-narrative-spa/
```

Primary outputs:

```text
videos/red-dot-narrative-spa/red-dot-narrative-spa.webm
videos/red-dot-narrative-spa/poster-final.png
videos/red-dot-narrative-spa/screenshots/01-appearance.png
videos/red-dot-narrative-spa/screenshots/02-search.png
videos/red-dot-narrative-spa/screenshots/03-tension.png
videos/red-dot-narrative-spa/screenshots/04-transformation.png
videos/red-dot-narrative-spa/screenshots/05-resolution.png
videos/red-dot-narrative-spa/screenshots/mobile-resolution.png
videos/red-dot-narrative-spa/review-frames/frame-start.png
videos/red-dot-narrative-spa/review-frames/frame-middle.png
videos/red-dot-narrative-spa/review-frames/frame-final.png
videos/red-dot-narrative-spa/review/contact-sheet.png
videos/red-dot-narrative-spa/recording-summary.json
videos/red-dot-narrative-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-narrative-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The narrative now keeps the phase chip, progress rail, and utility controls off-stage until hover or keyboard focus so the red point remains the primary subject in proof frames.
- On narrow screens the stage scales the active scene upward and nudges it higher while preserving the full 16:9 story field, keeping the resolution cluster legible without cropping the earlier left-to-right beats.
- The final composition recenters after the earlier search and tension devices retire so the resolved hold stays calm and legible.
