# Mermaid SVG Component Remap

## Purpose

This spike tests whether Mermaid diagrams can be exported as SVG and then semantically remapped in Manim by moving individual nodes and edges instead of blindly morphing the entire SVG.

The concrete experiment uses:

- a Mermaid `flowchart` as the source diagram,
- a Mermaid `stateDiagram-v2` as the target diagram,
- shared labels (`Collect`, `Review`, `Ship`) as the semantic bridge between both graph types.

The goal is to verify how far Mermaid SVG structure can be reused for component-level animation when the graph type changes.

## Run the render

From the repository root:

```bash
uv run --script spikes/mermaid-svg-component-remap/main.py
```

This writes the rendered assets to:

```text
videos/mermaid-svg-component-remap/
```

## Notes

- The spike exports Mermaid diagrams to `.svg` using `@mermaid-js/mermaid-cli`.
- Mermaid preserves useful semantic groups such as `g.nodes` and `g.edgePaths`.
- Node labels are still emitted as `foreignObject` in this experiment, so the spike overlays text natively in Manim instead of relying on SVG text rendering.
- The remap is semantic for shared nodes and shared edges, and additive for target-only elements such as the state diagram start marker.
