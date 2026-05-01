# Manim Graph Flow Lab

This spike tests graph/path/flow narration patterns from ManimCE v0.20.1 for slide-oriented explanation.

The narrative target is a route-choice scene:

- a directed graph starts as a quiet field of possible paths,
- competing paths receive brief gray flow passes without becoming the subject,
- one route is selected in primary red,
- a red pulse travels with a short-lived trace,
- the graph removes unused alternatives and settles into the chosen story.

## Feature Focus

- `DiGraph` with a manual layout for stable route spacing.
- `ShowPassingFlash` for temporary competing-path probes and active route passes.
- `MoveAlongPath` for a single pulse traveling along the selected route.
- `TracedPath` for a short-lived trace that proves the pulse traveled through the route without leaving final-frame residue.
- A pulse halo updater that keeps the guide ring attached to the moving pulse.

`StreamLines` and broad vector fields were reviewed as part of the same feature family, but they are intentionally not part of the final scene because they make route causality feel ambient instead of decision-driven.

## Render

From the repository root:

```powershell
uv run --script spikes/manim-graph-flow-lab/main.py
```

The script writes the promoted render to:

```text
videos/manim-graph-flow-lab/manim-graph-flow-lab.webm
```

It also writes a poster frame to:

```text
videos/manim-graph-flow-lab/manim-graph-flow-lab.png
```

## Review Notes

Render validation should sample the opening graph, competing-path probes, selected route proof, pulse mid-route, cleanup, and final hold. The important acceptance criteria are that the red route is the only active story, the gray alternatives remain subordinate, the pulse visibly causes the selected path, and no guide or trace residue survives into the final simplified graph.

## Latest Validation

The promoted render is:

```text
videos/manim-graph-flow-lab/manim-graph-flow-lab.webm
```

Validation results:

- Duration: 26.900 seconds.
- Frame count: 807 frames at 30 fps.
- Proof contact sheet: `videos/manim-graph-flow-lab/review-frames/contact-sheet.png`.
- Composition audit: 55 sampled frames, 0 findings.
- Resting mobject audit: 5 rest snapshots, 0 blocking findings.

Iteration changes made after proof-frame review:

- Replaced the in-scene title/subtitle with a visual-only graph stage after text spacing and edge-clearance audits showed the text was not helping the route mechanism.
- Replaced the old selected graph with a newly laid out final `DiGraph` during cleanup, because moving the original graph left the final route low and visually stale.
- Tightened cleanup so the old route, candidate paths, pulse, halo, trace, and rings disappear in the same beat as the simplified final route appears.
