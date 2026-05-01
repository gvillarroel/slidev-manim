---
title: Mermaid Packet Diagram SVG Unfold
status: experimental
---

# Mermaid Packet Diagram SVG Unfold

This spike tests a `Mermaid -> SVG -> fragment SVGs -> Manim` pipeline for the Mermaid Packet Diagram syntax family.

The spike keeps the source diagram in `diagram.mmd`, renders the complete SVG with Mermaid CLI, decomposes the SVG into visible fragment files, and unfolds those fragments progressively in Manim.

## Run

```bash
uv run --script spikes/mermaid-packet-svg-unfold/main.py
```

Useful validation command:

```bash
uv run --script spikes/mermaid-packet-svg-unfold/main.py --assets-only --force-mermaid
```

The render command writes:

- `videos/mermaid-packet-svg-unfold/mermaid-packet-svg-unfold.webm`
- `videos/mermaid-packet-svg-unfold/mermaid-packet-svg-unfold.png`
- `videos/mermaid-packet-svg-unfold/.generated/diagram.svg`
- `videos/mermaid-packet-svg-unfold/.generated/fragments/*.svg`
