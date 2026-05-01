---
title: Mermaid Venn Diagram SVG Unfold
status: experimental
---

# Mermaid Venn Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Venn Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-venn-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-venn-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-venn-svg-unfold/mermaid-venn-svg-unfold.webm`
- `videos/mermaid-venn-svg-unfold/mermaid-venn-svg-unfold.png`
- `videos/mermaid-venn-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-venn-svg-unfold/.generated/fragments/*.svg`
