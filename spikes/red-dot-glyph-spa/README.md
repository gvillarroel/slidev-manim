---
title: Red Dot Glyph SPA
status: active
date: 2026-05-03
---

# Red Dot Glyph SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point does not discover a physical object so much as a visual language.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three related stroke grammars, gets compressed inside a narrow press, then rewrites that pressure into a centered glyph-like emblem that can hold attention with almost no text.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-glyph-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, generates `0.3s` cadence sheets, and writes all generated artifacts to:

```text
videos/red-dot-glyph-spa/
```

Primary outputs:

```text
videos/red-dot-glyph-spa/red-dot-glyph-spa.webm
videos/red-dot-glyph-spa/poster-final.png
videos/red-dot-glyph-spa/screenshots/01-appearance.png
videos/red-dot-glyph-spa/screenshots/02-search.png
videos/red-dot-glyph-spa/screenshots/03-tension.png
videos/red-dot-glyph-spa/screenshots/04-transformation.png
videos/red-dot-glyph-spa/screenshots/05-resolution.png
videos/red-dot-glyph-spa/screenshots/mobile-resolution.png
videos/red-dot-glyph-spa/review/contact-sheet.png
videos/red-dot-glyph-spa/review-frames/frame-start.png
videos/red-dot-glyph-spa/review-frames/frame-middle.png
videos/red-dot-glyph-spa/review-frames/frame-final.png
videos/red-dot-glyph-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-glyph-spa/recording-summary.json
videos/red-dot-glyph-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-glyph-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate in one evolving stroke family, so the point reads as refining one idea instead of browsing unrelated symbols.
- The tension beat uses a narrow press with visible inner rails, so the conflict reads as real compression rather than a generic stop.
- The transformation beat keeps the emergent glyph legible before the press fully clears, proving how the resolved emblem is being built rather than swapping one badge for another.
