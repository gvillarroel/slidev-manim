---
title: Red Dot Ratchet SPA
status: active
date: 2026-05-04
---

# Red Dot Ratchet SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that motion becomes commitment only after it can lock into direction.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three related ratchet grammars, gets pinned inside a visible tooth-and-pawl throat, then redraws the stage into a calm centered ratchet mark that can hold without explanatory copy.

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
videos/red-dot-ratchet-spa/review-frames-0.3s/sheets/contact-sheet-01.png
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
- The search beat keeps every candidate in the same tooth-and-lock family, so the point reads as refining one mechanical idea instead of browsing unrelated icons.
- The tension beat keeps the pawl, tooth bank, and circular guide visible together, so the conflict reads as one directional lock instead of a generic squeeze.
- The transformation beat traces the wheel first, then settles the teeth and pawl into a centered mark so the final hold feels committed rather than merely decorated.
- The runner also emits 0.3-second continuity review sheets, so the tension-to-transformation cleanup can be checked without rerunning ad hoc extraction commands.
