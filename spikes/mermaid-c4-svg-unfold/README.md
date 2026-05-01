---
title: Mermaid C4 Diagram SVG Unfold
status: experimental
---

# Mermaid C4 Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid C4 Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-c4-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-c4-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-c4-svg-unfold/mermaid-c4-svg-unfold.webm`
- `videos/mermaid-c4-svg-unfold/mermaid-c4-svg-unfold.png`
- `videos/mermaid-c4-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-c4-svg-unfold/.generated/fragments/*.svg`
