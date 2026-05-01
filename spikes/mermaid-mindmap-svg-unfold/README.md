---
title: Mermaid Mindmap SVG Unfold
status: experimental
---

# Mermaid Mindmap SVG Unfold

This spike tests a direct `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for a Mermaid `mindmap` diagram.

The experiment keeps the Mermaid source as `diagram.mmd`, renders a complete Mermaid SVG with Mermaid CLI, decomposes the SVG into per-edge and per-node fragment SVG files, and imports those fragments into Manim so the mindmap can unfold progressively from the root to branches and leaves.

Mermaid emits node labels as SVG `foreignObject` HTML. Manim does not import those labels reliably, so the spike preserves the Mermaid-generated node geometry and edge geometry as SVG fragments while rebuilding labels from Mermaid's SVG text metadata as native Manim text.

## Run

```bash
uv run --script spikes/mermaid-mindmap-svg-unfold/main.py
```

The command writes:

- `videos/mermaid-mindmap-svg-unfold/mermaid-mindmap-svg-unfold.webm`
- `videos/mermaid-mindmap-svg-unfold/mermaid-mindmap-svg-unfold.png`
- `videos/mermaid-mindmap-svg-unfold/.generated/mindmap.svg`
- `videos/mermaid-mindmap-svg-unfold/.generated/fragments/**/*.svg`

