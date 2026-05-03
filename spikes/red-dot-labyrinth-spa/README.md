---
title: Red Dot Labyrinth SPA
status: active
date: 2026-05-02
---

# Red Dot Labyrinth SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that direction becomes meaning only after it can turn pressure into structure.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three corridor grammars, gets trapped inside a dead-end maze throat, then redraws the conflict into a centered labyrinth emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-labyrinth-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-labyrinth-spa/
```

Primary outputs:

```text
videos/red-dot-labyrinth-spa/red-dot-labyrinth-spa.webm
videos/red-dot-labyrinth-spa/poster-final.png
videos/red-dot-labyrinth-spa/screenshots/01-appearance.png
videos/red-dot-labyrinth-spa/screenshots/02-search.png
videos/red-dot-labyrinth-spa/screenshots/03-tension.png
videos/red-dot-labyrinth-spa/screenshots/04-transformation.png
videos/red-dot-labyrinth-spa/screenshots/05-resolution.png
videos/red-dot-labyrinth-spa/screenshots/mobile-resolution.png
videos/red-dot-labyrinth-spa/review-frames/frame-start.png
videos/red-dot-labyrinth-spa/review-frames/frame-middle.png
videos/red-dot-labyrinth-spa/review-frames/frame-final.png
videos/red-dot-labyrinth-spa/review/contact-sheet.png
videos/red-dot-labyrinth-spa/recording-summary.json
videos/red-dot-labyrinth-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-labyrinth-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps all candidates inside one maze language of corners, pockets, and stepped turns so the point feels like it is refining a route instead of browsing unrelated symbols.
- The tension beat uses a real dead-end throat with visible upper and lower walls plus a blocking cap, so the conflict reads as being cornered rather than simply paused.
- The transformation beat lets the point redraw the route as a square spiral before the conflict hardware disappears, proving how the final labyrinth is built before the ending simplifies into a calm centered seal.
