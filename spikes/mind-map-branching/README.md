---
title: Mind Map Branching
status: draft
date: 2026-04-30
---

# Purpose

Generate a Manim spike where one text box emits categories, and each category grows its own child elements, forming a simple generated mind map.

# Hypothesis

If the scene uses procedural cell growth instead of connector lines, then reveals categories before their child elements, the viewer should read the mind map as a generated structure rather than as a static diagram.

# Behavior

The default scene starts with a `Generator` box. Four category boxes grow from the source through red cell chains, and each category emits two child elements through smaller cell chains. The settled growth residue fades back to gray.

| Source | Generated map |
| --- | --- |
| Generator | Input text: prompt, context; Idea groups: themes, clusters; Branch logic: routes, weights; Review loop: frames, audit |

The script is data-driven for quick variants:

```bash
uv run --script spikes/mind-map-branching/main.py --root-text "Roadmap" --branches "Goal:audience,scope;Milestones:now,next;Risks:unknowns,tradeoffs"
```

# Color System

The video uses the canonical project tokens from `.specs/adr/0002-slide-and-video-color-system.md`:

- `primary-red` for the source box and final hub,
- `primary-red` for active growth cells and pulses,
- `gray-*` for category boxes, child boxes, settled cell residue, target fields, and staging,
- `white` and `page-background` for local contrast.

# Run

```bash
uv run --script spikes/mind-map-branching/main.py
```

# Output

The render writes:

- `videos/mind-map-branching/mind-map-branching.webm`
- `videos/mind-map-branching/mind-map-branching.png`

The default scene is at least 25 seconds long and includes a final hold for slide integration.
