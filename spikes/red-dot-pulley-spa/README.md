---
title: Red Dot Pulley SPA
status: active
date: 2026-05-05
---

# Red Dot Pulley SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters on a quiet lane, tests three pulley-like grammars, gets pulled into a narrow hanging channel, then releases that stored tension into a centered twin-wheel pulley emblem.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-pulley-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-pulley-spa/
```

Primary outputs:

```text
videos/red-dot-pulley-spa/red-dot-pulley-spa.webm
videos/red-dot-pulley-spa/poster-final.png
videos/red-dot-pulley-spa/screenshots/01-appearance.png
videos/red-dot-pulley-spa/screenshots/02-search.png
videos/red-dot-pulley-spa/screenshots/03-tension.png
videos/red-dot-pulley-spa/screenshots/04-transformation.png
videos/red-dot-pulley-spa/screenshots/05-resolution.png
videos/red-dot-pulley-spa/screenshots/mobile-resolution.png
videos/red-dot-pulley-spa/review-frames/frame-start.png
videos/red-dot-pulley-spa/review-frames/frame-middle.png
videos/red-dot-pulley-spa/review-frames/frame-final.png
videos/red-dot-pulley-spa/review-frames-0.3s/frames/
videos/red-dot-pulley-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-pulley-spa/review/contact-sheet.png
videos/red-dot-pulley-spa/recording-summary.json
videos/red-dot-pulley-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-pulley-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- Add `?phase=appearance`, `?phase=search`, `?phase=tension`, `?phase=transformation`, or `?phase=resolution` to freeze the SPA on a stable review frame for that act.
- The opening frame keeps the future beam, wheels, and lower knot slot visible so the narrative reads as a prepared mechanism instead of an isolated moving dot.
- The promoted recording trims the browser recorder's startup blank so 0.3-second review begins on the first meaningful composition.
- The conflict beat is a hanging compression channel, not another funnel or hinge, so the visual tension reads as suspended load.
- The transformation beat traces the release path over the wheels before the structure settles into the final emblem, keeping the resolution causal instead of decorative.
- Portrait review uses phase-specific scaling so the wide opening still reads while the final wheel-and-knot emblem stays legible on mobile.
