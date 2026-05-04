---
title: Red Dot Ratchet SPA
status: active
date: 2026-05-03
---

# Red Dot Ratchet SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that pressure becomes direction only after it can lock into a ratchet grammar.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three tooth-like structures, gets pulled into a constrained pocket between a pawl and a toothed arc, then redraws that pressure into a compact ratchet emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-ratchet-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-ratchet-spa/
```

Primary outputs:

```text
videos/red-dot-ratchet-spa/red-dot-ratchet-spa.webm
videos/red-dot-ratchet-spa/poster-final.png
videos/red-dot-ratchet-spa/screenshots/01-appearance.png
videos/red-dot-ratchet-spa/screenshots/02-search.png
videos/red-dot-ratchet-spa/screenshots/03-tension.png
videos/red-dot-ratchet-spa/screenshots/04-transformation.png
videos/red-dot-ratchet-spa/screenshots/05-resolution.png
videos/red-dot-ratchet-spa/screenshots/mobile-resolution.png
videos/red-dot-ratchet-spa/review-frames/frame-start.png
videos/red-dot-ratchet-spa/review-frames/frame-middle.png
videos/red-dot-ratchet-spa/review-frames/frame-final.png
videos/red-dot-ratchet-spa/review/contact-sheet.png
videos/red-dot-ratchet-spa/recording-summary.json
videos/red-dot-ratchet-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-ratchet-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps all candidates inside one tooth-and-pawl family so the point feels like it is refining one mechanism instead of browsing unrelated symbols.
- The tension beat keeps the pocket, pawl, and toothed arc visible together so the conflict reads as stored directional pressure instead of a generic pause.
- The transformation beat traces the release along the ratchet route before the emblem settles into a centered final hold.
