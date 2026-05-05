---
title: Red Dot Domino SPA
status: active
date: 2026-05-05
---

# Red Dot Domino SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters on a quiet lane, tests three small domino grammars, wedges itself into a precarious sloped chain, then converts that stored pressure into a calm radial mark built from the fallen pieces.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-domino-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-domino-spa/
```

Primary outputs:

```text
videos/red-dot-domino-spa/red-dot-domino-spa.webm
videos/red-dot-domino-spa/poster-final.png
videos/red-dot-domino-spa/screenshots/01-appearance.png
videos/red-dot-domino-spa/screenshots/02-search.png
videos/red-dot-domino-spa/screenshots/03-tension.png
videos/red-dot-domino-spa/screenshots/04-transformation.png
videos/red-dot-domino-spa/screenshots/05-resolution.png
videos/red-dot-domino-spa/screenshots/mobile-resolution.png
videos/red-dot-domino-spa/review-frames/frame-start.png
videos/red-dot-domino-spa/review-frames/frame-middle.png
videos/red-dot-domino-spa/review-frames/frame-final.png
videos/red-dot-domino-spa/review-frames-0.3s/frames/
videos/red-dot-domino-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-domino-spa/review/contact-sheet.png
videos/red-dot-domino-spa/recording-summary.json
videos/red-dot-domino-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-domino-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- Add `?phase=appearance`, `?phase=search`, `?phase=tension`, `?phase=transformation`, or `?phase=resolution` to freeze the SPA on a stable review frame for that act.
- The first frame keeps the future radial receiver visible so the narrative reads as a prepared mechanism instead of an isolated moving dot.
- The conflict beat is built around a sloped chain of rigid bars, not another aperture or funnel, so the pressure frame reads as stored imbalance.
- The transformation beat retires the sloped corridor as the radial mark takes over, keeping the resolved hold calm instead of stranded in the old push lane.
