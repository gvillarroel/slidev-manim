---
title: Red Dot Weave SPA
status: active
date: 2026-05-02
---

# Red Dot Weave SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that pressure becomes meaning only after it can be rewoven into structure.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three orthogonal weave grammars, gets tightened inside a four-sided gate, then redraws the pressure into a woven crossing that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-weave-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-weave-spa/
```

Primary outputs:

```text
videos/red-dot-weave-spa/red-dot-weave-spa.webm
videos/red-dot-weave-spa/poster-final.png
videos/red-dot-weave-spa/screenshots/01-appearance.png
videos/red-dot-weave-spa/screenshots/02-search.png
videos/red-dot-weave-spa/screenshots/03-tension.png
videos/red-dot-weave-spa/screenshots/04-transformation.png
videos/red-dot-weave-spa/screenshots/05-resolution.png
videos/red-dot-weave-spa/screenshots/mobile-resolution.png
videos/red-dot-weave-spa/review-frames/frame-start.png
videos/red-dot-weave-spa/review-frames/frame-middle.png
videos/red-dot-weave-spa/review-frames/frame-final.png
videos/red-dot-weave-spa/review/contact-sheet.png
videos/red-dot-weave-spa/recording-summary.json
videos/red-dot-weave-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-weave-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps all candidates inside one orthogonal ribbon family, so the point looks like it is refining one structure instead of browsing unrelated symbols.
- The tension beat uses a real four-sided gate with a compressed center rail, so the conflict reads as pressure inside a mechanism rather than a generic pause.
- The transformation beat reveals the woven crossing before the gate fully clears, proving how the resolved emblem is built before the ending simplifies into a calm centered hold.
