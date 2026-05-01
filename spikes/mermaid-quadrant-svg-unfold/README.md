---
title: Mermaid Quadrant Chart SVG Unfold
status: experimental
---

# Mermaid Quadrant Chart SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Quadrant Chart syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-quadrant-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-quadrant-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-quadrant-svg-unfold/mermaid-quadrant-svg-unfold.webm`
- `videos/mermaid-quadrant-svg-unfold/mermaid-quadrant-svg-unfold.png`
- `videos/mermaid-quadrant-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-quadrant-svg-unfold/.generated/fragments/*.svg`
