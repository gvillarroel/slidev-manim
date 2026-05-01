---
title: Mermaid XY Chart SVG Unfold
status: experimental
---

# Mermaid XY Chart SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid XY Chart syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-xy-chart-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-xy-chart-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-xy-chart-svg-unfold/mermaid-xy-chart-svg-unfold.webm`
- `videos/mermaid-xy-chart-svg-unfold/mermaid-xy-chart-svg-unfold.png`
- `videos/mermaid-xy-chart-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-xy-chart-svg-unfold/.generated/fragments/*.svg`
