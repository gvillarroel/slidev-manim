---
title: Red Dot Iris SPA
status: active
date: 2026-05-01
---

# Red Dot Iris SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three aperture grammars, gets compressed inside a narrowing iris throat, then resolves into a centered iris-like system that holds without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-iris-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-iris-spa/
```

Primary outputs:

```text
videos/red-dot-iris-spa/red-dot-iris-spa.webm
videos/red-dot-iris-spa/poster-final.png
videos/red-dot-iris-spa/screenshots/01-appearance.png
videos/red-dot-iris-spa/screenshots/02-search.png
videos/red-dot-iris-spa/screenshots/03-tension.png
videos/red-dot-iris-spa/screenshots/04-transformation.png
videos/red-dot-iris-spa/screenshots/05-resolution.png
videos/red-dot-iris-spa/screenshots/mobile-resolution.png
videos/red-dot-iris-spa/review-frames/frame-start.png
videos/red-dot-iris-spa/review-frames/frame-middle.png
videos/red-dot-iris-spa/review-frames/frame-final.png
videos/red-dot-iris-spa/review/contact-sheet.png
videos/red-dot-iris-spa/recording-summary.json
videos/red-dot-iris-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-iris-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested aperture grammar visible as faint residue so the point feels like it is learning an opening, not teleporting between ornaments.
- The tension beat uses a visible slit guide and opposing shutter blades so the conflict reads as pressure inside a real throat rather than a generic stop.
- The transformation beat turns that throat into a balanced four-blade iris with prepared landing slots, then the resolved hold retires those helpers and recenters the final form around the red core.
