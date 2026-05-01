---
title: Mind Map Scale Spine Lines
status: draft
date: 2026-05-01
---

# Purpose

Generate a Manim spike where one source text box emits categories and child elements through growing aloe-like scale spines, forming a generated mind map.

# Hypothesis

If each connection is built from many dense, lance-shaped scale/spine elements that appear in sequence, then the mind-map growth should feel like an aloe-vera crest pushing toward the created node rather than a drawn connector.

# Behavior

The default scene starts with a `Generator` box. Four category boxes grow from the source through very dense red chains of overlapping aloe-like scale/spine polygons. After all category trunks exist, each category emits two child elements through smaller dense scale-spine chains. Settled spines fade back to gray.

| Source | Generated map |
| --- | --- |
| Generator | Input text: prompt, context; Idea groups: themes, clusters; Branch logic: routes, weights; Review loop: frames, audit |

The script is data-driven for quick variants:

```bash
uv run --script spikes/mind-map-scale-spine-lines/main.py --root-text "Roadmap" --branches "Goal:audience,scope;Milestones:now,next;Risks:unknowns,tradeoffs"
```

# Line Algorithm

The spike tests `scale spine line`:

- an invisible Bezier route provides direction,
- each visible unit is a lance-shaped polygonal scale or spine,
- each polygon is oriented by the route tangent,
- dense units overlap and alternate around the route so the chain reads as a growing aloe-like crest,
- active growth is red,
- settled units become low-opacity gray residue,
- the destination node appears after the terminal bud arrives.

# Color System

The video uses the canonical project tokens from `.specs/adr/0002-slide-and-video-color-system.md`:

- `primary-red` for the source box, active spines, buds, and pulse,
- `gray-*` for category boxes, child boxes, settled spine residue, target fields, and staging,
- `white` and `page-background` for local contrast.

# Run

```bash
uv run --script spikes/mind-map-scale-spine-lines/main.py
```

# Output

The render writes:

- `videos/mind-map-scale-spine-lines/mind-map-scale-spine-lines.webm`
- `videos/mind-map-scale-spine-lines/mind-map-scale-spine-lines.png`

The default scene is at least 25 seconds long and includes a final hold for slide integration.
