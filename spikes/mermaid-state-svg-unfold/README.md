---
title: Mermaid State Diagram SVG Unfold
status: experimental
---

# Mermaid State Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid State Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and promotes a native Manim state-flow video for the final slide asset. The native path is used because the generic SVG-fragment unfold was slow to render and produced a thin, static strip instead of a readable state mechanism.

## Run

```bash
uv run --script spikes/mermaid-state-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-state-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-state-svg-unfold/mermaid-state-svg-unfold.webm`
- `videos/mermaid-state-svg-unfold/mermaid-state-svg-unfold.png`
- `videos/mermaid-state-svg-unfold/review-frames/`
- `videos/mermaid-state-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-state-svg-unfold/.generated/fragments/*.svg`

## Review Notes

The current render is a 30.960-second transparent WebM at 1600x900. It starts with a visible pending state scaffold, uses one primary-red pulse that stops at receiver entrances, reveals the states into a larger two-row layout, and holds the resolved `Unfolded Video` state with separated corner brackets.

Validation from the latest quality pass:

- 103 white-background review frames extracted every 0.3 seconds.
- Decoded VP9 alpha extrema: `0..255`.
- Frame composition audit: 104 sampled frames, 0 findings, 0 blocking frames.
- Frame crowding audit: 104 sampled frames, 0 blocking frames.
- Resting mobject audit: 7 rest snapshots, 0 blocking snapshots, 1 notice-only final overlap prompt.
