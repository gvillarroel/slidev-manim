---
title: Red Dot Relay SPA
status: active
date: 2026-05-02
---

# Red Dot Relay SPA

## Purpose

This spike builds a browser-based single-page narrative where one red point carries the story through five visual acts:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters a quiet field, tests three relay grammars, gets compressed inside a narrow handoff pocket, then resolves into a calm centered relay hub where the red core becomes the active connector instead of a traveler looking for a destination.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-relay-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-relay-spa/
```

Primary outputs:

```text
videos/red-dot-relay-spa/red-dot-relay-spa.webm
videos/red-dot-relay-spa/poster-final.png
videos/red-dot-relay-spa/screenshots/01-appearance.png
videos/red-dot-relay-spa/screenshots/02-search.png
videos/red-dot-relay-spa/screenshots/03-tension.png
videos/red-dot-relay-spa/screenshots/04-transformation.png
videos/red-dot-relay-spa/screenshots/05-resolution.png
videos/red-dot-relay-spa/screenshots/mobile-resolution.png
videos/red-dot-relay-spa/review-frames/frame-start.png
videos/red-dot-relay-spa/review-frames/frame-middle.png
videos/red-dot-relay-spa/review-frames/frame-final.png
videos/red-dot-relay-spa/review/contact-sheet.png
videos/red-dot-relay-spa/recording-summary.json
videos/red-dot-relay-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-relay-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically after the final hold.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The search beat keeps the three relay candidates in the middle composition band so the point reads as testing possible handoff grammars rather than wandering between ornaments.
- The tension beat keeps the handoff pocket visibly prepared before the brackets compress inward, so the conflict reads as a constrained transfer instead of a generic squeeze.
- The transformation beat traces a triangular relay circuit before collapsing into a compact hub, then retires the pocket supports so the resolved hold feels connected and calm.
