---
title: Red Dot Circuit SPA
status: active
date: 2026-05-02
---

# Red Dot Circuit SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three connection grammars, gets compressed against an open gap, then resolves into a centered circuit-like device that holds without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-circuit-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-circuit-spa/
```

Primary outputs:

```text
videos/red-dot-circuit-spa/red-dot-circuit-spa.webm
videos/red-dot-circuit-spa/poster-final.png
videos/red-dot-circuit-spa/screenshots/01-appearance.png
videos/red-dot-circuit-spa/screenshots/02-search.png
videos/red-dot-circuit-spa/screenshots/03-tension.png
videos/red-dot-circuit-spa/screenshots/04-transformation.png
videos/red-dot-circuit-spa/screenshots/05-resolution.png
videos/red-dot-circuit-spa/screenshots/mobile-resolution.png
videos/red-dot-circuit-spa/review-frames/frame-start.png
videos/red-dot-circuit-spa/review-frames/frame-middle.png
videos/red-dot-circuit-spa/review-frames/frame-final.png
videos/red-dot-circuit-spa/review/contact-sheet.png
videos/red-dot-circuit-spa/recording-summary.json
videos/red-dot-circuit-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-circuit-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the candidate grammars in the middle composition band so the point feels like it is probing structure instead of jumping between decorative symbols.
- The tension beat uses a real open gap with opposing terminals and compression braces so the conflict reads as interrupted continuity rather than a generic pause.
- The transformation beat lets the point trace the chip perimeter before the pads settle inward, proving the connection path before the final centered hold simplifies into a calm device.
