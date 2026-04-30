---
id: KNOW-0006
title: Generated diagram SVG manipulation in Manim
status: active
date: 2026-04-30
---

# Summary

A Mermaid diagram can be passed through SVG and still remain manipulable in Manim when the generated SVG is normalized into stable semantic group ids for the nodes that need to become video actors.

# Learned Points

1. Keep the Mermaid source (`diagram.mmd`) as the diagram definition, render it with `mmdc -i input.mmd -o output.svg`, then normalize the generated SVG before importing it into Manim.
2. Load Manim actors from per-role fragment SVGs extracted from normalized top-level `<g id="...">` node groups.
3. Keep node labels as native Manim `Text` attached to imported SVG bodies. This avoids the cross-generator fragility of SVG text import while preserving SVG geometry as the actor.
4. Direct transforms are reliable when source and target roles stay semantically and geometrically compatible, such as rounded node bodies.
5. Imported SVG connector strokes can become visually heavy in Manim, especially around arrowheads. For final video quality, native Manim `Arrow` and `CurvedArrow` connectors anchored to SVG role positions can look cleaner while preserving SVG nodes as the manipulated diagram actors.
6. Selection handles or proof dots should sit near node corners, not at node centers, because center dots read as label defects in still frames.
7. Source-layout lanes and destination scaffolds should be cleaned up as the mechanism changes. A lane that remains into the final hold reads as diagram residue rather than structure.
8. `possible_overlap_or_crowding` notices are expected for imported SVG node interiors and route endpoints; full-size frame review plus rest-state audit should decide whether they are real problems.

# Practical Rule

For `Mermaid -> SVG -> Manim`, prefer this pipeline:

- render the `.mmd` file with Mermaid CLI,
- normalize only the SVG groups that need to become video actors into stable role ids,
- extract each role into its own SVG fragment while preserving the Mermaid viewBox,
- import node fragments with `SVGMobject`,
- attach native Manim labels to SVG node bodies,
- draw connector arrows natively from the same role positions when SVG arrowheads look heavy,
- animate roles independently by semantic id,
- remove source scaffolds before the resolved hold,
- validate with proof frames, composition audit, and rest-state audit.
