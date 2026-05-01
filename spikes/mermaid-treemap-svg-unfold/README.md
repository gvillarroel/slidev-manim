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
- `videos/mermaid-treemap-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-treemap-svg-unfold/.generated/fragments/*.svg`
