---
title: Mermaid State Diagram SVG Unfold
status: experimental
---

# Mermaid State Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid State Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-state-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-state-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-state-svg-unfold/mermaid-state-svg-unfold.webm`
- `videos/mermaid-state-svg-unfold/mermaid-state-svg-unfold.png`
- `videos/mermaid-state-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-state-svg-unfold/.generated/fragments/*.svg`
