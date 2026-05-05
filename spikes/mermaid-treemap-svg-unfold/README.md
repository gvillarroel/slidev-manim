---
title: Mermaid Treemap SVG Unfold
status: experimental
---

# Mermaid Treemap SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Treemap syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-treemap-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-treemap-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-treemap-svg-unfold/mermaid-treemap-svg-unfold.webm`
- `videos/mermaid-treemap-svg-unfold/mermaid-treemap-svg-unfold.png`
- `videos/mermaid-treemap-svg-unfold/review-frames-0.3s/` with alpha-on-white cadence frames and contact sheets
- `videos/mermaid-treemap-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-treemap-svg-unfold/.generated/fragments/*.svg`

## Latest validation

The polished render is a 25.863 second transparent WebM at 1600x900. The runner clears the spike-local Manim staging directory, forces the transparent Manim render flag, and extracts 86 alpha-on-white review frames at 0.3 second cadence.

- Decoded VP9 alpha range: `0..255`.
- Frame composition audit: 87 sampled frames, 0 blocking frames.
- Frame crowding audit: 87 sampled frames, 0 blocking frames.
- Resting mobject audit: 7 rest snapshots, 0 blocking snapshots, 1 notice-only expected header/scaffold proximity.
