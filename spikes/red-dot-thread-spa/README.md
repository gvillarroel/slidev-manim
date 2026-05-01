---
title: Red Dot Thread SPA
status: active
date: 2026-05-01
---

# Red Dot Thread SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three candidate identities, survives a throat-gate compression, then becomes a thread that stitches three calm structures into one resolved woven system.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-thread-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-thread-spa/
```

Primary outputs:

```text
videos/red-dot-thread-spa/red-dot-thread-spa.webm
videos/red-dot-thread-spa/poster-final.png
videos/red-dot-thread-spa/screenshots/01-appearance.png
videos/red-dot-thread-spa/screenshots/02-search.png
videos/red-dot-thread-spa/screenshots/03-tension.png
videos/red-dot-thread-spa/screenshots/04-transformation.png
videos/red-dot-thread-spa/screenshots/05-resolution.png
videos/red-dot-thread-spa/screenshots/mobile-resolution.png
videos/red-dot-thread-spa/review-frames/frame-start.png
videos/red-dot-thread-spa/review-frames/frame-middle.png
videos/red-dot-thread-spa/review-frames/frame-final.png
videos/red-dot-thread-spa/review/contact-sheet.png
videos/red-dot-thread-spa/recording-summary.json
videos/red-dot-thread-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-thread-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat leaves each tested form visible as faint residue so the point feels like it is learning instead of teleporting between unrelated ornaments.
- The tension beat collapses those candidate identities into a narrow throat gate, making the conflict read as compression rather than as an arbitrary cut.
- The transformation beat turns the point into a stitching head that draws one continuous route through three prepared slots before the final hold simplifies the system again.
