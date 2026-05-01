---
title: Mermaid Gantt SVG Unfold
status: experimental
---

# Mermaid Gantt SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Gantt syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-gantt-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-gantt-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-gantt-svg-unfold/mermaid-gantt-svg-unfold.webm`
- `videos/mermaid-gantt-svg-unfold/mermaid-gantt-svg-unfold.png`
- `videos/mermaid-gantt-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-gantt-svg-unfold/.generated/fragments/*.svg`
