---
title: Diagram SVG Video Manipulation
status: draft
date: 2026-04-30
---

# Diagram SVG Video Manipulation

## Purpose

Test whether a generated diagram can become an SVG source and still be manipulated as independent video actors in Manim.

The spike uses this pipeline:

- write a small Mermaid source diagram to `diagram.mmd`,
- render it to SVG with `@mermaid-js/mermaid-cli`,
- normalize Mermaid node groups into stable top-level SVG role ids,
- extract one fragment SVG per node role,
- load node fragments with `SVGMobject`,
- draw connector arrows natively in Manim from the same role positions,
- animate the diagram independently instead of treating it as one flat image.

Labels are rendered as native Manim `Text` objects because SVG text import is less reliable than geometry import across diagram generators.

Connector arrows started as imported SVG fragments, but review showed that Manim's SVG stroke conversion made arrowheads visually heavy. The final spike keeps Mermaid as the source of truth for the inspectable diagram SVG and uses native Manim arrows for the video connectors.

## Hypothesis

If a Mermaid SVG can be normalized into stable node role ids, Manim can animate the diagram as a set of semantic components: selection, separation, layout remapping, route pulsing, and final cleanup. For final video quality, connector arrows may be better as native Manim mobjects anchored to SVG-derived role positions.

## Run

From the repository root:

```bash
uv run --script spikes/diagram-svg-video-manipulation/main.py
```

The script invokes Mermaid CLI through:

```bash
npx -y -p @mermaid-js/mermaid-cli mmdc -i input.mmd -o output.svg -b transparent
```

Node.js/npm must be available on the PATH.

## Output

The render writes:

- `videos/diagram-svg-video-manipulation/diagram-svg-video-manipulation.webm`
- `videos/diagram-svg-video-manipulation/diagram-svg-video-manipulation.png`

Generated source SVGs and role fragments are written under:

- `videos/diagram-svg-video-manipulation/.generated/mermaid/diagram.mmd`
- `videos/diagram-svg-video-manipulation/.generated/mermaid/diagram.svg`
- `videos/diagram-svg-video-manipulation/.generated/mermaid/diagram-normalized.svg`
- `videos/diagram-svg-video-manipulation/.generated/fragments/`

Review frames and audit overlays may be written under:

- `videos/diagram-svg-video-manipulation/review-frames/`
- `videos/diagram-svg-video-manipulation/composition-audit/`
