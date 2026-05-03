---
title: Red Dot Dovetail SPA
status: active
date: 2026-05-03
---

# Red Dot Dovetail SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers a dovetail-like joining grammar through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The experience stays almost text-free. The story is carried by pressure, alignment, and the moment where two mirrored halves learn how to lock around the active red point.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-dovetail-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, runs the composition audit, and writes generated artifacts to:

```text
videos/red-dot-dovetail-spa/
```

Primary outputs:

```text
videos/red-dot-dovetail-spa/red-dot-dovetail-spa.webm
videos/red-dot-dovetail-spa/poster-final.png
videos/red-dot-dovetail-spa/screenshots/01-appearance.png
videos/red-dot-dovetail-spa/screenshots/02-search.png
videos/red-dot-dovetail-spa/screenshots/03-tension.png
videos/red-dot-dovetail-spa/screenshots/04-transformation.png
videos/red-dot-dovetail-spa/screenshots/05-resolution.png
videos/red-dot-dovetail-spa/screenshots/mobile-resolution.png
videos/red-dot-dovetail-spa/review-frames/frame-start.png
videos/red-dot-dovetail-spa/review-frames/frame-middle.png
videos/red-dot-dovetail-spa/review-frames/frame-final.png
videos/red-dot-dovetail-spa/review/contact-sheet.png
videos/red-dot-dovetail-spa/review-frames-0.3s/sheets/
videos/red-dot-dovetail-spa/recording-summary.json
videos/red-dot-dovetail-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-dovetail-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The interactive version loops by default after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The phase label remains screen-reader-only so proof frames stay visual-first.
- Faint future geometry appears early to keep the opening balanced while preserving a sparse stage.
- The search beat tests multiple incompatible notch grammars before the narrative commits to a mirrored dovetail join.
