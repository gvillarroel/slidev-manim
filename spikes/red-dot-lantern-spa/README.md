---
title: Red Dot Lantern SPA
status: active
date: 2026-05-02
---

# Red Dot Lantern SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three shelter grammars, gets compressed inside a narrow lantern throat, then resolves into a calm centered lantern where the red core becomes the light source instead of the trapped object.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-lantern-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-lantern-spa/
```

Primary outputs:

```text
videos/red-dot-lantern-spa/red-dot-lantern-spa.webm
videos/red-dot-lantern-spa/poster-final.png
videos/red-dot-lantern-spa/screenshots/01-appearance.png
videos/red-dot-lantern-spa/screenshots/02-search.png
videos/red-dot-lantern-spa/screenshots/03-tension.png
videos/red-dot-lantern-spa/screenshots/04-transformation.png
videos/red-dot-lantern-spa/screenshots/05-resolution.png
videos/red-dot-lantern-spa/screenshots/mobile-resolution.png
videos/red-dot-lantern-spa/review-frames/frame-start.png
videos/red-dot-lantern-spa/review-frames/frame-middle.png
videos/red-dot-lantern-spa/review-frames/frame-final.png
videos/red-dot-lantern-spa/review/contact-sheet.png
videos/red-dot-lantern-spa/recording-summary.json
videos/red-dot-lantern-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-lantern-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the three shelter candidates in the middle composition band so the point reads as testing possible housings rather than wandering between decorations.
- The tension beat keeps the lantern throat visibly prepared before the shutters close, so the conflict reads as containment instead of a generic squeeze.
- The transformation beat turns the compression pocket into a centered lantern shell, then retires the shutters so the resolved hold feels lit and calm.
