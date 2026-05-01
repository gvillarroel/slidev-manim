---
title: Mermaid Radar Chart SVG Unfold
status: experimental
---

# Mermaid Radar Chart SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Radar Chart syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-radar-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-radar-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-radar-svg-unfold/mermaid-radar-svg-unfold.webm`
- `videos/mermaid-radar-svg-unfold/mermaid-radar-svg-unfold.png`
- `videos/mermaid-radar-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-radar-svg-unfold/.generated/fragments/*.svg`
