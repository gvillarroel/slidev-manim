---
title: Mermaid Entity Relationship Diagram SVG Unfold
status: experimental
---

# Mermaid Entity Relationship Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Entity Relationship Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-entity-relationship-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-entity-relationship-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-entity-relationship-svg-unfold/mermaid-entity-relationship-svg-unfold.webm`
- `videos/mermaid-entity-relationship-svg-unfold/mermaid-entity-relationship-svg-unfold.png`
- `videos/mermaid-entity-relationship-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-entity-relationship-svg-unfold/.generated/fragments/*.svg`
