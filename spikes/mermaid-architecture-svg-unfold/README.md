---
title: Mermaid Architecture Diagram SVG Unfold
status: experimental
---

# Mermaid Architecture Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Architecture Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-architecture-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-architecture-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-architecture-svg-unfold/mermaid-architecture-svg-unfold.webm`
- `videos/mermaid-architecture-svg-unfold/mermaid-architecture-svg-unfold.png`
- `videos/mermaid-architecture-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-architecture-svg-unfold/.generated/fragments/*.svg`
