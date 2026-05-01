# Mermaid All Diagram Types

## Purpose

This spike renders one small example for every Mermaid diagram type listed in the Mermaid 11.14.0 diagram syntax reference, then presents them as a Manim gallery video.

The experiment verifies that the current Mermaid CLI can generate assets for:

- Flowchart
- Sequence
- Class
- State
- Entity Relationship
- User Journey
- Gantt
- Pie
- Quadrant
- Requirement
- GitGraph
- C4
- Mindmap
- Timeline
- ZenUML
- Sankey
- XY Chart
- Block
- Packet
- Kanban
- Architecture
- Radar
- Treemap
- Venn
- Ishikawa
- TreeView

## Run the render

From the repository root:

```bash
uv run --script spikes/mermaid-all-diagram-types/main.py
```

This writes the rendered assets to:

```text
videos/mermaid-all-diagram-types/
```

The generated Mermaid sources, SVGs, and PNGs are kept under:

```text
videos/mermaid-all-diagram-types/.generated/
```

The primary video is:

```text
videos/mermaid-all-diagram-types/mermaid-all-diagram-types.webm
```

## Notes

- The script pins Mermaid CLI to `@mermaid-js/mermaid-cli@11.14.0` so the set of supported diagram types is stable for this spike.
- Manim displays the Mermaid-rendered PNGs because many Mermaid SVGs contain text, HTML labels, markers, or newer SVG structures that `SVGMobject` does not render faithfully across all diagram types.
- The raw Mermaid SVG for every diagram type is still generated and preserved for inspection.
