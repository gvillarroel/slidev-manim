---
title: Mermaid Timeline SVG Unfold
status: experimental
---

# Mermaid Timeline SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Timeline syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-timeline-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-timeline-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-timeline-svg-unfold/mermaid-timeline-svg-unfold.webm`
- `videos/mermaid-timeline-svg-unfold/mermaid-timeline-svg-unfold.png`
- `videos/mermaid-timeline-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-timeline-svg-unfold/.generated/fragments/*.svg`
