---
title: Mermaid Sequence Diagram SVG Unfold
status: experimental
---

# Mermaid Sequence Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Sequence Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-sequence-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-sequence-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-sequence-svg-unfold/mermaid-sequence-svg-unfold.webm`
- `videos/mermaid-sequence-svg-unfold/mermaid-sequence-svg-unfold.png`
- `videos/mermaid-sequence-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-sequence-svg-unfold/.generated/fragments/*.svg`
