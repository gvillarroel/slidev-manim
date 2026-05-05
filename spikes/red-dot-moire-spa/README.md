---
title: Red Dot Moire SPA
status: active
date: 2026-05-05
---

# Red Dot Moire SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point teaches a field how to align.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters on a quiet lane, tests three line grammars, compresses between offset slat planes, then resolves that interference into a calm moire lens with the red core as the only strong accent.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-moire-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-moire-spa/
```

Primary outputs:

```text
videos/red-dot-moire-spa/red-dot-moire-spa.webm
videos/red-dot-moire-spa/poster-final.png
videos/red-dot-moire-spa/screenshots/01-appearance.png
videos/red-dot-moire-spa/screenshots/02-search.png
videos/red-dot-moire-spa/screenshots/03-tension.png
videos/red-dot-moire-spa/screenshots/04-transformation.png
videos/red-dot-moire-spa/screenshots/05-resolution.png
videos/red-dot-moire-spa/screenshots/mobile-resolution.png
videos/red-dot-moire-spa/review-frames/frame-start.png
videos/red-dot-moire-spa/review-frames/frame-middle.png
videos/red-dot-moire-spa/review-frames/frame-final.png
videos/red-dot-moire-spa/review-frames-0.3s/frames/
videos/red-dot-moire-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-moire-spa/review/contact-sheet.png
videos/red-dot-moire-spa/recording-summary.json
videos/red-dot-moire-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-moire-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- Add `?phase=appearance`, `?phase=search`, `?phase=tension`, `?phase=transformation`, or `?phase=resolution` to freeze the SPA on a stable review frame for that act.
- The opening frame keeps the future lens and corridor visible from frame zero so the first proof image reads as prepared intent, not as a drifting red dot.
- The search act tests three distinct line grammars: ascending slats, centered ovals, and descending slats.
- The tension beat uses opposing slat combs and a narrow interference corridor so the proof frame reads as visual pressure rather than a generic gate.
- The transformation beat turns the same slat energy into nested lens rings, which makes the resolution feel causal instead of swapped in.
