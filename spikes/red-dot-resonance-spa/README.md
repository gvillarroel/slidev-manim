---
title: Red Dot Resonance SPA
status: active
date: 2026-05-01
---

# Red Dot Resonance SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point does not explain itself with copy. It tests three candidate forms, survives a narrow pressure slot, then activates a quiet field that recenters into one resolved system.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-resonance-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-resonance-spa/
```

Primary outputs:

```text
videos/red-dot-resonance-spa/red-dot-resonance-spa.webm
videos/red-dot-resonance-spa/poster-final.png
videos/red-dot-resonance-spa/screenshots/01-appearance.png
videos/red-dot-resonance-spa/screenshots/02-search.png
videos/red-dot-resonance-spa/screenshots/03-tension.png
videos/red-dot-resonance-spa/screenshots/04-transformation.png
videos/red-dot-resonance-spa/screenshots/05-resolution.png
videos/red-dot-resonance-spa/screenshots/mobile-resolution.png
videos/red-dot-resonance-spa/review-frames/frame-start.png
videos/red-dot-resonance-spa/review-frames/frame-middle.png
videos/red-dot-resonance-spa/review-frames/frame-final.png
videos/red-dot-resonance-spa/review/contact-sheet.png
videos/red-dot-resonance-spa/recording-summary.json
videos/red-dot-resonance-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-resonance-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The three search candidates stay visible as faint residue until the pressure beat takes over, so the search feels cumulative instead of decorative.
- The activated field is built as pending slots first, then red force-lines, then a calmer centered system for the resolved hold.
- On narrow screens the stage scales upward while preserving the full 16:9 story field, keeping the final network legible without cropping the earlier beats.
