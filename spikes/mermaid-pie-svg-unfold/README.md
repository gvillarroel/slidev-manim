---
title: Mermaid Pie Chart SVG Unfold
status: experimental
---

# Mermaid Pie Chart SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Pie Chart syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-pie-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-pie-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-pie-svg-unfold/mermaid-pie-svg-unfold.webm`
- `videos/mermaid-pie-svg-unfold/mermaid-pie-svg-unfold.png`
- `videos/mermaid-pie-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-pie-svg-unfold/.generated/fragments/*.svg`
