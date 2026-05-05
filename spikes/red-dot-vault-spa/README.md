---
title: Red Dot Vault SPA
status: active
date: 2026-05-05
---

# Red Dot Vault SPA

## Purpose

This spike builds a browser-native single-page narrative where one red point learns how to turn pressure into a chamber.

The five visual acts are:

- appearance
- search for form
- tension
- transformation
- resolution

The point enters from the left, probes three vault-like chamber grammars, gets compressed inside a four-way lock, then opens that same pressure device into a calm centered vault mark.

## Run the Spike

From the repository root:

```bash
uv run --script spikes/red-dot-vault-spa/main.py
```

This starts a local server, records a browser session, captures proof screenshots, extracts review frames, and writes all generated artifacts to:

```text
videos/red-dot-vault-spa/
```

Primary outputs:

```text
videos/red-dot-vault-spa/red-dot-vault-spa.webm
videos/red-dot-vault-spa/poster-final.png
videos/red-dot-vault-spa/screenshots/01-appearance.png
videos/red-dot-vault-spa/screenshots/02-search.png
videos/red-dot-vault-spa/screenshots/03-tension.png
videos/red-dot-vault-spa/screenshots/04-transformation.png
videos/red-dot-vault-spa/screenshots/05-resolution.png
videos/red-dot-vault-spa/screenshots/mobile-resolution.png
videos/red-dot-vault-spa/review-frames/frame-start.png
videos/red-dot-vault-spa/review-frames/frame-middle.png
videos/red-dot-vault-spa/review-frames/frame-final.png
videos/red-dot-vault-spa/review-frames-0.3s/frames/
videos/red-dot-vault-spa/review-frames-0.3s/sheets/contact-sheet-01.png
videos/red-dot-vault-spa/review/contact-sheet.png
videos/red-dot-vault-spa/recording-summary.json
videos/red-dot-vault-spa/browser-validation.json
```

## Run the SPA Without Capturing

From the repository root:

```bash
uv run --script spikes/red-dot-vault-spa/main.py --serve-only
```

Then open the printed local URL in a browser.

## Notes

- The SPA loops automatically in normal browsing.
- Recorded captures use `?capture=1` so the exported WebM holds the final resolution instead of restarting.
- Press `Space` to pause or resume.
- Press `R` to restart the narrative.
- The opening frame already shows the pending vault chamber and calm target skeleton so the first proof frame reads as prepared intent.
- Search keeps all candidate pockets inside the middle composition band so the exploration feels deliberate instead of top-heavy.
- The tension beat keeps the full outer chamber visible while the four shutters squeeze inward, so the conflict reads as a real lock event instead of four unrelated slabs.
- The transformation beat reuses those shutters as the opening force that releases the final chamber grammar.
- Portrait review uses phase-specific crops and scene transforms so the full chamber still reads on mobile without losing the core actor.
