---
title: Red Dot Tuning SPA
status: active
date: 2026-05-05
---

# Red Dot Tuning SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn a loose split into a tuned form.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three split-prong candidates, gets compressed inside a narrow throat, then redraws the stage into a calm tuning-fork-like emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-tuning-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts dense review frames, and writes all generated artifacts to:

```text
videos/red-dot-tuning-spa/
```

Primary outputs:

```text
videos/red-dot-tuning-spa/red-dot-tuning-spa.webm
videos/red-dot-tuning-spa/poster-final.png
videos/red-dot-tuning-spa/screenshots/01-appearance.png
videos/red-dot-tuning-spa/screenshots/02-search.png
videos/red-dot-tuning-spa/screenshots/03-tension.png
videos/red-dot-tuning-spa/screenshots/04-transformation.png
videos/red-dot-tuning-spa/screenshots/05-resolution.png
videos/red-dot-tuning-spa/screenshots/mobile-resolution.png
videos/red-dot-tuning-spa/review-frames/frame-start.png
videos/red-dot-tuning-spa/review-frames/frame-middle.png
videos/red-dot-tuning-spa/review-frames/frame-final.png
videos/red-dot-tuning-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-tuning-spa/review/contact-sheet.png
videos/red-dot-tuning-spa/recording-summary.json
videos/red-dot-tuning-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-tuning-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame keeps a faint stem, yoke, and future prongs visible so the entering point is never stranded on an empty lane.
- The search beat stays inside one family of split-prong structures instead of switching between unrelated icons.
- The tension beat pinches the point between two jaws that are visibly narrower than both the candidates and the final resolved hold.
- The transformation beat traces the tuned fork body before it drops into the quiet central stem.
