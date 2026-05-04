---
title: Red Dot Radial Focus SPA
status: active
date: 2026-05-01
---

# Red Dot Radial Focus SPA

## Purpose

This spike isolates and deepens the radial fan-out technique where one red center emits several related blocks and then transfers focus between them without losing the hub as the narrative owner.

The sequence uses five visual acts:

- appearance
- fan-out
- focus
- rotation
- resolution

The study expands the earlier three-block burst by adding associated chips, a clear focal handoff, and a deliberate orbital rotation of the whole system.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-radial-focus-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-radial-focus-spa/
```

Primary outputs:

```text
videos/red-dot-radial-focus-spa/red-dot-radial-focus-spa.webm
videos/red-dot-radial-focus-spa/poster-final.png
videos/red-dot-radial-focus-spa/screenshots/01-appearance.png
videos/red-dot-radial-focus-spa/screenshots/02-fanout.png
videos/red-dot-radial-focus-spa/screenshots/03-focus.png
videos/red-dot-radial-focus-spa/screenshots/04-rotation.png
videos/red-dot-radial-focus-spa/screenshots/05-resolution.png
videos/red-dot-radial-focus-spa/screenshots/mobile-resolution.png
videos/red-dot-radial-focus-spa/review-frames/frame-start.png
videos/red-dot-radial-focus-spa/review-frames/frame-middle.png
videos/red-dot-radial-focus-spa/review-frames/frame-final.png
videos/red-dot-radial-focus-spa/review-frames-0.3s/
videos/red-dot-radial-focus-spa/review/contact-sheet.png
videos/red-dot-radial-focus-spa/review/contact-sheet-0.3s.png
videos/red-dot-radial-focus-spa/composition-audit-0.3s/report.md
videos/red-dot-radial-focus-spa/crowding-audit-0.3s/report.md
videos/red-dot-radial-focus-spa/recording-summary.json
videos/red-dot-radial-focus-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-radial-focus-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The fan-out beat keeps the red hub as the owner while the three cards leave on staggered spokes.
- The focus beat reveals associated chips for only one card at a time so the viewer reads one active relation set instead of a simultaneous explosion of detail.
- The rotation beat keeps the whole radial system coherent while the focus handoff moves from one branch to another.
