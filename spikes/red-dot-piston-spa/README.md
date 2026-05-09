---
title: Red Dot Piston SPA
status: active
date: 2026-05-05
---

# Red Dot Piston SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how pressure can become structure.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three piston-and-chamber grammars, gets compressed inside a narrowing head and side walls, then redraws that pressure into a calm centered piston emblem without relying on explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-piston-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-piston-spa/
```

Primary outputs:

```text
videos/red-dot-piston-spa/red-dot-piston-spa.webm
videos/red-dot-piston-spa/poster-final.png
videos/red-dot-piston-spa/screenshots/01-appearance.png
videos/red-dot-piston-spa/screenshots/02-search.png
videos/red-dot-piston-spa/screenshots/03-tension.png
videos/red-dot-piston-spa/screenshots/04-transformation.png
videos/red-dot-piston-spa/screenshots/05-resolution.png
videos/red-dot-piston-spa/screenshots/mobile-resolution.png
videos/red-dot-piston-spa/review-frames/frame-start.png
videos/red-dot-piston-spa/review-frames/frame-middle.png
videos/red-dot-piston-spa/review-frames/frame-final.png
videos/red-dot-piston-spa/review-frames-0.3s/frames/
videos/red-dot-piston-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-piston-spa/review/contact-sheet.png
videos/red-dot-piston-spa/recording-summary.json
videos/red-dot-piston-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-piston-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the pending chamber scaffold so the red point never appears stranded in blank space.
- The search act stays within one piston family, using related chamber-head variations instead of unrelated symbols.
- The tension beat keeps the side walls and descending head visible together so the pressure reads as a real mechanism.
- The transformation beat traces the final frame from the compressed center outward, proving how the resolved emblem comes from the same chamber geometry.
- Portrait review uses a tighter phase-specific crop so the chamber remains legible on mobile without shrinking into a small center icon.
