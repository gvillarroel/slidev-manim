---
title: Mermaid Flowchart SVG Unfold
status: experimental
---

# Mermaid Flowchart SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Flowchart syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-flowchart-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-flowchart-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-flowchart-svg-unfold/mermaid-flowchart-svg-unfold.webm`
- `videos/mermaid-flowchart-svg-unfold/mermaid-flowchart-svg-unfold.png`
- `videos/mermaid-flowchart-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-flowchart-svg-unfold/.generated/fragments/*.svg`
