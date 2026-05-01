---
title: Mermaid TreeView Diagram SVG Unfold
status: experimental
---

# Mermaid TreeView Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid TreeView Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-treeview-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-treeview-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-treeview-svg-unfold/mermaid-treeview-svg-unfold.webm`
- `videos/mermaid-treeview-svg-unfold/mermaid-treeview-svg-unfold.png`
- `videos/mermaid-treeview-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-treeview-svg-unfold/.generated/fragments/*.svg`
