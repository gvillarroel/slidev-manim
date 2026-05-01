---
title: Red Point Narrative SPA
status: active
date: 2026-04-30
---

# Red Point Narrative SPA

## Purpose

This spike explores a minimal single-page visual narrative where a red point acts as the only strong narrator.

The experience is structured in five acts:

- appearance
- search for form
- tension
- transformation
- resolution

The stage keeps text to a minimum and relies on motion, spacing, and contrast to guide attention.

## Run the SPA Capture

From the repository root:

```bash
uv run --script spikes/red-point-narrative-spa/main.py
```

This validates the JavaScript sources, serves the spike locally, records the SPA to WebM with Playwright, and captures screenshot evidence.

Expected outputs:

```text
videos/red-point-narrative-spa/red-point-narrative-spa.webm
videos/red-point-narrative-spa/screenshots/act-01-appearance.png
videos/red-point-narrative-spa/screenshots/act-02-search.png
videos/red-point-narrative-spa/screenshots/act-03-tension.png
videos/red-point-narrative-spa/screenshots/act-04-transformation.png
videos/red-point-narrative-spa/screenshots/act-05-resolution.png
videos/red-point-narrative-spa/screenshots/poster-final.png
videos/red-point-narrative-spa/review-frames/frame-appearance.png
videos/red-point-narrative-spa/review-frames/frame-search.png
videos/red-point-narrative-spa/review-frames/frame-tension.png
videos/red-point-narrative-spa/review-frames/frame-transformation.png
videos/red-point-narrative-spa/review-frames/frame-resolution.png
videos/red-point-narrative-spa/capture-summary.json
videos/red-point-narrative-spa/recording-summary.json
```

## Run the SPA Locally

From the repository root:

```bash
python -m http.server 4173 --bind 127.0.0.1 --directory spikes/red-point-narrative-spa
```

Then open:

```text
http://127.0.0.1:4173/index.html
```

## Notes

- The visual system follows the repository palette: `primary-red`, grayscale structure, and a light stage.
- The video is authored as a normal slide-ready sequence, so it keeps a slow opening breath and a long resolved hold.
- The capture workflow intentionally separates browser screenshots from the recorded video so still-frame review is deterministic.
