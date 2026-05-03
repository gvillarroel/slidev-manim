---
title: Red Dot Sling SPA
status: active
date: 2026-05-02
---

# Red Dot Sling SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers that direction becomes clearer when force is visibly stored before release.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three directional grammars, gets pulled backward into a visible sling pocket, then releases into a compact forward emblem that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-sling-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-sling-spa/
```

Primary outputs:

```text
videos/red-dot-sling-spa/red-dot-sling-spa.webm
videos/red-dot-sling-spa/poster-final.png
videos/red-dot-sling-spa/screenshots/01-appearance.png
videos/red-dot-sling-spa/screenshots/02-search.png
videos/red-dot-sling-spa/screenshots/03-tension.png
videos/red-dot-sling-spa/screenshots/04-transformation.png
videos/red-dot-sling-spa/screenshots/05-resolution.png
videos/red-dot-sling-spa/screenshots/mobile-resolution.png
videos/red-dot-sling-spa/review-frames/frame-start.png
videos/red-dot-sling-spa/review-frames/frame-middle.png
videos/red-dot-sling-spa/review-frames/frame-final.png
videos/red-dot-sling-spa/review/contact-sheet.png
videos/red-dot-sling-spa/recording-summary.json
videos/red-dot-sling-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-sling-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps all candidate tests on one directional family so the point feels like it is refining one idea instead of browsing unrelated symbols.
- The tension beat shows the point visibly pulled backward between a rear pocket and a forward slot, so the conflict reads as stored release energy instead of a generic clamp.
- The transformation beat promotes the release lane into the resolved crest before the pocket and slot disappear, proving how the final emblem inherits its direction from the tension device.
