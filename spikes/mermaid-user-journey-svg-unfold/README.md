---
title: Mermaid User Journey SVG Unfold
status: experimental
---

# Mermaid User Journey SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid User Journey syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-user-journey-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-user-journey-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-user-journey-svg-unfold/mermaid-user-journey-svg-unfold.webm`
- `videos/mermaid-user-journey-svg-unfold/mermaid-user-journey-svg-unfold.png`
- `videos/mermaid-user-journey-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-user-journey-svg-unfold/.generated/fragments/*.svg`
