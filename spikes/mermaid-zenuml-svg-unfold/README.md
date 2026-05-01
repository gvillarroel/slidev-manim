---
title: Mermaid ZenUML SVG Unfold
status: experimental
---

# Mermaid ZenUML SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid ZenUML syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-zenuml-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-zenuml-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-zenuml-svg-unfold/mermaid-zenuml-svg-unfold.webm`
- `videos/mermaid-zenuml-svg-unfold/mermaid-zenuml-svg-unfold.png`
- `videos/mermaid-zenuml-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-zenuml-svg-unfold/.generated/fragments/*.svg`
