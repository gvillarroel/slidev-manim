# Mermaid SVG Direct Insert

## Purpose

This spike verifies that a Mermaid-authored diagram can become an SVG through Mermaid CLI and then be inserted into a Manim video as SVG geometry.

The render flow is:

- `spikes/mermaid-svg-direct-insert/diagram.mmd` is the inspectable Mermaid source.
- `mmdc` writes the raw Mermaid output to `videos/mermaid-svg-direct-insert/.generated/diagram.svg`.
- Manim loads the generated visible SVG geometry through `SVGMobject`.
- The node labels are read from the generated Mermaid SVG and added as Manim text because Manim imports the SVG shapes and paths but does not render SVG `<text>` elements.

## Run the render

From the repository root:

```bash
uv run --script spikes/mermaid-svg-direct-insert/main.py
```

This writes the rendered assets to:

```text
videos/mermaid-svg-direct-insert/
```

The primary video is:

```text
videos/mermaid-svg-direct-insert/mermaid-svg-direct-insert.webm
```

## Notes

- The Mermaid CLI package is pinned in the script for reproducible SVG structure.
- The raw Mermaid SVG is kept for inspection before any Manim compatibility handling.
- The Manim-compatible SVG copy only removes invisible/support SVG elements that Manim would otherwise import incorrectly; the visible diagram geometry still comes from Mermaid output.
