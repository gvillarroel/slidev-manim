---
title: Red Dot Harbor SPA
status: active
date: 2026-05-03
---

# Red Dot Harbor SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to arrive, dock, and become structure instead of motion.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three docking grammars, compresses through a narrow harbor channel, then redraws the stage into a calm centered basin with three piers and a stable red core.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-harbor-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-harbor-spa/
```

Primary outputs:

```text
videos/red-dot-harbor-spa/red-dot-harbor-spa.webm
videos/red-dot-harbor-spa/poster-final.png
videos/red-dot-harbor-spa/screenshots/01-appearance.png
videos/red-dot-harbor-spa/screenshots/02-search.png
videos/red-dot-harbor-spa/screenshots/03-tension.png
videos/red-dot-harbor-spa/screenshots/04-transformation.png
videos/red-dot-harbor-spa/screenshots/05-resolution.png
videos/red-dot-harbor-spa/screenshots/mobile-resolution.png
videos/red-dot-harbor-spa/review-frames/frame-start.png
videos/red-dot-harbor-spa/review-frames/frame-middle.png
videos/red-dot-harbor-spa/review-frames/frame-final.png
videos/red-dot-harbor-spa/review/contact-sheet.png
videos/red-dot-harbor-spa/review/dense-contact-sheet.png
videos/red-dot-harbor-spa/recording-summary.json
videos/red-dot-harbor-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-harbor-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps all three docking candidates on one horizontal approach band so the point feels like it is testing related landing grammars instead of browsing unrelated symbols.
- The tension beat leaves the channel walls and basin scaffold visible together, so the proof frame reads as constrained arrival rather than a generic squeeze.
- The transformation beat traces the basin perimeter first, then grows the interior piers, so the final hold feels like a calm harbor system instead of a frozen route sketch.
- The portrait framing compacts the basin and terminal corner marks so the mobile proof frame still reads as one centered harbor rather than a wide shell with detached side residue.
