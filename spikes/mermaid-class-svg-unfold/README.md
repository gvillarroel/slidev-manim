---
title: Mermaid Class Diagram SVG Unfold
status: experimental
---

# Mermaid Class Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Class Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-class-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-class-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-class-svg-unfold/mermaid-class-svg-unfold.webm`
- `videos/mermaid-class-svg-unfold/mermaid-class-svg-unfold.png`
- `videos/mermaid-class-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-class-svg-unfold/.generated/fragments/*.svg`
