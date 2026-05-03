---
title: Red Dot Pendulum SPA
status: active
date: 2026-05-02
---

# Red Dot Pendulum SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three possible hanging grammars, gets held in a taut off-center pendulum state, then swings through a wider arc before settling into a calm centered pendulum emblem.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-pendulum-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-pendulum-spa/
```

Primary outputs:

```text
videos/red-dot-pendulum-spa/red-dot-pendulum-spa.webm
videos/red-dot-pendulum-spa/poster-final.png
videos/red-dot-pendulum-spa/screenshots/01-appearance.png
videos/red-dot-pendulum-spa/screenshots/02-search.png
videos/red-dot-pendulum-spa/screenshots/03-tension.png
videos/red-dot-pendulum-spa/screenshots/04-transformation.png
videos/red-dot-pendulum-spa/screenshots/05-resolution.png
videos/red-dot-pendulum-spa/screenshots/mobile-resolution.png
videos/red-dot-pendulum-spa/review-frames/frame-start.png
videos/red-dot-pendulum-spa/review-frames/frame-middle.png
videos/red-dot-pendulum-spa/review-frames/frame-final.png
videos/red-dot-pendulum-spa/review/contact-sheet.png
videos/red-dot-pendulum-spa/recording-summary.json
videos/red-dot-pendulum-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-pendulum-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the candidate hanging grammars in the middle composition band so the point reads as testing anchors rather than wandering.
- The tension beat keeps the top pivot and the holding bracket visible together so the off-center bob reads as stored force, not drift.
- The transformation beat proves the release with a large pendulum arc before the final hold compacts back to a centered calm structure.
