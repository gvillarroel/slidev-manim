---
title: Red Dot Fork SPA
status: active
date: 2026-05-03
---

# Red Dot Fork SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point discovers how to resolve a split instead of choosing one branch and abandoning the others.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, tests three branching grammars, gets compressed at a narrow junction, then redraws that conflict into a compact three-tine fork that can hold without explanatory copy.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-fork-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-fork-spa/
```

Primary outputs:

```text
videos/red-dot-fork-spa/red-dot-fork-spa.webm
videos/red-dot-fork-spa/poster-final.png
videos/red-dot-fork-spa/screenshots/01-appearance.png
videos/red-dot-fork-spa/screenshots/02-search.png
videos/red-dot-fork-spa/screenshots/03-tension.png
videos/red-dot-fork-spa/screenshots/04-transformation.png
videos/red-dot-fork-spa/screenshots/05-resolution.png
videos/red-dot-fork-spa/screenshots/mobile-resolution.png
videos/red-dot-fork-spa/review-frames/frame-start.png
videos/red-dot-fork-spa/review-frames/frame-middle.png
videos/red-dot-fork-spa/review-frames/frame-final.png
videos/red-dot-fork-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-fork-spa/review/contact-sheet.png
videos/red-dot-fork-spa/recording-summary.json
videos/red-dot-fork-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-fork-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps every candidate inside one branching family, so the point reads as refining one structural idea instead of browsing unrelated icons.
- The tension beat keeps the branch exits visible while the shoulders and cap close inward, so the conflict reads as unresolved divergence instead of a generic clamp.
- The transformation beat traces the shared stem and all three tines before the final hold quiets into a compact centered fork.
- The runner also emits 0.3-second continuity review sheets, so route-history cleanup between tension and transformation can be checked without rerunning ad hoc extraction commands.
