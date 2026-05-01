---
title: Mermaid Ishikawa Diagram SVG Unfold
status: experimental
---

# Mermaid Ishikawa Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Ishikawa Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-ishikawa-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-ishikawa-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-ishikawa-svg-unfold/mermaid-ishikawa-svg-unfold.webm`
- `videos/mermaid-ishikawa-svg-unfold/mermaid-ishikawa-svg-unfold.png`
- `videos/mermaid-ishikawa-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-ishikawa-svg-unfold/.generated/fragments/*.svg`
