---
title: Mermaid Requirement Diagram SVG Unfold
status: experimental
---

# Mermaid Requirement Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Requirement Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-requirement-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-requirement-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-requirement-svg-unfold/mermaid-requirement-svg-unfold.webm`
- `videos/mermaid-requirement-svg-unfold/mermaid-requirement-svg-unfold.png`
- `videos/mermaid-requirement-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-requirement-svg-unfold/.generated/fragments/*.svg`
