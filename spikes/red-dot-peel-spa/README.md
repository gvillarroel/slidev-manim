---
title: Red Dot Peel SPA
status: active
date: 2026-05-05
---

# Red Dot Peel SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns that a reveal can feel authored only after a surface visibly peels away.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three folded-surface grammars, compresses beneath a corner flap, then reveals a calm centered panel with a quiet peeled corner instead of an empty stage.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-peel-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-peel-spa/
```

Primary outputs:

```text
videos/red-dot-peel-spa/red-dot-peel-spa.webm
videos/red-dot-peel-spa/poster-final.png
videos/red-dot-peel-spa/screenshots/01-appearance.png
videos/red-dot-peel-spa/screenshots/02-search.png
videos/red-dot-peel-spa/screenshots/03-tension.png
videos/red-dot-peel-spa/screenshots/04-transformation.png
videos/red-dot-peel-spa/screenshots/05-resolution.png
videos/red-dot-peel-spa/screenshots/mobile-resolution.png
videos/red-dot-peel-spa/review-frames/frame-start.png
videos/red-dot-peel-spa/review-frames/frame-middle.png
videos/red-dot-peel-spa/review-frames/frame-final.png
videos/red-dot-peel-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-peel-spa/review/contact-sheet.png
videos/red-dot-peel-spa/recording-summary.json
videos/red-dot-peel-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-peel-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate inside the same folded-surface family, so the point reads as refining one visual grammar instead of browsing unrelated icons.
- The tension beat keeps the panel, the seam, and the flap visible together, so the conflict reads as pressure under a surface instead of a generic squeeze.
- The transformation beat opens the flap outward while the point settles inward, making the reveal read as a causal peel instead of a disconnected morph.
- The runner emits 0.3-second continuity review sheets so the tension-to-transformation cleanup can be checked without ad hoc extraction.
