---
title: Mind Map Organic Fractal Lines
status: draft
date: 2026-05-01
---

# Purpose

Generate a Manim spike where one source text box emits categories and child elements through organic fractal line growth, forming a generated mind map.

# Hypothesis

If the scene uses an `organic fractal line` algorithm with a main stem, delayed side tendrils, and fading gray residue, then the same mind-map structure should feel plant-like and generated rather than diagrammatic.

# Behavior

The default scene starts with a `Generator` box. Four category boxes grow from the source through red organic stems with recursive side tendrils. After all category trunks exist, each category emits two child elements through smaller organic branches. Settled stems fade back to gray.

| Source | Generated map |
| --- | --- |
| Generator | Input text: prompt, context; Idea groups: themes, clusters; Branch logic: routes, weights; Review loop: frames, audit |

The script is data-driven for quick variants:

```bash
uv run --script spikes/mind-map-organic-fractal-lines/main.py --root-text "Roadmap" --branches "Goal:audience,scope;Milestones:now,next;Risks:unknowns,tradeoffs"
```

# Line Algorithm

The spike tests `organic fractal line`:

- a smooth main stem grows along an implicit Bezier route,
- side tendrils branch from deterministic positions along the stem,
- second-level twigs appear only on longer category trunks,
- active growth is red,
- settled growth becomes low-opacity gray residue,
- nodes appear after the terminal bud reaches the destination.

# Color System

The video uses the canonical project tokens from `.specs/adr/0002-slide-and-video-color-system.md`:

- `primary-red` for the source box, active stems, buds, and pulse,
- `gray-*` for category boxes, child boxes, settled line residue, target fields, and staging,
- `white` and `page-background` for local contrast.

# Run

```bash
uv run --script spikes/mind-map-organic-fractal-lines/main.py
```

# Output

The render writes:

- `videos/mind-map-organic-fractal-lines/mind-map-organic-fractal-lines.webm`
- `videos/mind-map-organic-fractal-lines/mind-map-organic-fractal-lines.png`

The default scene is at least 25 seconds long and includes a final hold for slide integration.
