---
title: Mermaid Sankey Diagram SVG Unfold
status: experimental
---

# Mermaid Sankey Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Sankey Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-sankey-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-sankey-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-sankey-svg-unfold/mermaid-sankey-svg-unfold.webm`
- `videos/mermaid-sankey-svg-unfold/mermaid-sankey-svg-unfold.png`
- `videos/mermaid-sankey-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-sankey-svg-unfold/.generated/fragments/*.svg`
