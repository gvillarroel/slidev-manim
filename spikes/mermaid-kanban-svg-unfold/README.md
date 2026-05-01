---
title: Mermaid Kanban SVG Unfold
status: experimental
---

# Mermaid Kanban SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Kanban syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-kanban-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-kanban-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-kanban-svg-unfold/mermaid-kanban-svg-unfold.webm`
- `videos/mermaid-kanban-svg-unfold/mermaid-kanban-svg-unfold.png`
- `videos/mermaid-kanban-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-kanban-svg-unfold/.generated/fragments/*.svg`
