title: Red Dot Latch SPA
status: active
date: 2026-05-04
---

# Red Dot Latch SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three latch grammars, gets squeezed between a moving arm and a keeper, then turns that pressure into a centered latch-like mark with a calm terminal hold.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-latch-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, generates 0.3-second cadence sheets, and writes all generated artifacts to:

```text
videos/red-dot-latch-spa/
```

Primary outputs:

```text
videos/red-dot-latch-spa/red-dot-latch-spa.webm
videos/red-dot-latch-spa/poster-final.png
videos/red-dot-latch-spa/screenshots/01-appearance.png
videos/red-dot-latch-spa/screenshots/02-search.png
videos/red-dot-latch-spa/screenshots/03-tension.png
videos/red-dot-latch-spa/screenshots/04-transformation.png
videos/red-dot-latch-spa/screenshots/05-resolution.png
videos/red-dot-latch-spa/screenshots/mobile-resolution.png
videos/red-dot-latch-spa/review-frames/frame-start.png
videos/red-dot-latch-spa/review-frames/frame-middle.png
videos/red-dot-latch-spa/review-frames/frame-final.png
videos/red-dot-latch-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-latch-spa/review/contact-sheet.png
videos/red-dot-latch-spa/recording-summary.json
videos/red-dot-latch-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-latch-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps each tested latch candidate visible long enough to read as exploration instead of a random jump.
- The tension beat keeps the moving arm, keeper, and narrowing rails visible around the dot so the conflict reads as a real squeeze.
- The transformation beat traces a continuous latch outline that returns to the center, so the resolved hold feels built from the pressure beat instead of swapped in.
