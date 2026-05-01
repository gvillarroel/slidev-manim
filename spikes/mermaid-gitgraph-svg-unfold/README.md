---
title: Mermaid GitGraph Diagram SVG Unfold
status: experimental
---

# Mermaid GitGraph Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid GitGraph Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-gitgraph-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-gitgraph-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-gitgraph-svg-unfold/mermaid-gitgraph-svg-unfold.webm`
- `videos/mermaid-gitgraph-svg-unfold/mermaid-gitgraph-svg-unfold.png`
- `videos/mermaid-gitgraph-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-gitgraph-svg-unfold/.generated/fragments/*.svg`
