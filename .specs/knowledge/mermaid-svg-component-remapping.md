---
id: KNOW-0003
title: Mermaid SVG component remapping in Manim
status: active
date: 2026-04-15
---

# Summary

Mermaid SVG export is usable as a semantic source for Manim component animation when the goal is to remap related diagram elements between graph types.

# Learned Points

1. Mermaid SVG output keeps useful semantic containers such as `g.nodes`, `g.edgePaths`, and node ids with stable labels.
2. That structure is sufficient to extract individual node and edge fragments as separate SVG files for Manim.
3. Node and edge mapping should be driven by shared semantic labels or explicit metadata, not by raw SVG group ids alone.
4. Mermaid still emits node labels as `foreignObject` in this experiment, so native Manim `Text` overlays are more reliable than depending on SVG text import.
5. Component-level remapping between graph types is practical for shared nodes and shared edges.
6. Target-only elements, such as a state diagram start marker, should be treated as additive elements and faded in separately.

# Practical Rule

- For `Mermaid -> SVG -> Manim`, prefer this pipeline:
  - export Mermaid to SVG,
  - parse semantic groups,
  - rebuild node labels natively in Manim,
  - transform shared components by semantic mapping,
  - fade in or fade out type-specific elements separately.
