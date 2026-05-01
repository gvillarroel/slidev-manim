---
title: Red Dot Bridge SPA
status: active
date: 2026-05-01
---

# Red Dot Bridge SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three bridge grammars, survives a compressed crossing, then turns that pressure into a calm three-part span that recenters around the red anchor.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-bridge-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-bridge-spa/
```

Primary outputs:

```text
videos/red-dot-bridge-spa/red-dot-bridge-spa.webm
videos/red-dot-bridge-spa/poster-final.png
videos/red-dot-bridge-spa/screenshots/01-appearance.png
videos/red-dot-bridge-spa/screenshots/02-search.png
videos/red-dot-bridge-spa/screenshots/03-tension.png
videos/red-dot-bridge-spa/screenshots/04-transformation.png
videos/red-dot-bridge-spa/screenshots/05-resolution.png
videos/red-dot-bridge-spa/screenshots/mobile-resolution.png
videos/red-dot-bridge-spa/review-frames/frame-start.png
videos/red-dot-bridge-spa/review-frames/frame-middle.png
videos/red-dot-bridge-spa/review-frames/frame-final.png
videos/red-dot-bridge-spa/review/contact-sheet.png
videos/red-dot-bridge-spa/recording-summary.json
videos/red-dot-bridge-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-bridge-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested bridge grammar visible as faint residue so the point feels like it is learning a structure instead of teleporting between decorations.
- The tension beat uses a compressed passage with visible upper and lower rails so the pressure reads as a real crossing, not as a generic stop.
- The resolved hold removes the passage hardware and recenters the three-part span around the red anchor so the ending feels settled instead of stranded in a left-to-right transfer.
