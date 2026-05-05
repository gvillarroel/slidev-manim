# Mermaid Diagram Side By Side

## Purpose

This spike tests a Slidev slide that combines a Mermaid diagram authored in Markdown with a Manim video rendered as a transparent asset.

The goal is to verify that:

- Mermaid can carry the static or structural explanation,
- Manim can reinforce the same idea with motion,
- both can coexist cleanly in one Slidev composition.

## Run the render

From the repository root:

```bash
uv run --script spikes/mermaid-diagram-side-by-side/main.py
```

This writes the rendered assets to:

```text
videos/mermaid-diagram-side-by-side/
```

Expected outputs:

```text
videos/mermaid-diagram-side-by-side/mermaid-diagram-side-by-side.webm
videos/mermaid-diagram-side-by-side/mermaid-diagram-side-by-side.png
videos/mermaid-diagram-side-by-side/review/mermaid-diagram-side-by-side-0.3s/contact-sheet.png
```

## Run the Slidev deck

From the repository root:

```bash
npx @slidev/cli spikes/mermaid-diagram-side-by-side/slides.md
```

To build the deck:

```bash
npx @slidev/cli build spikes/mermaid-diagram-side-by-side/slides.md
```

## Learnings

- Mermaid works well for the explicit flow or structure, while Manim is better for emphasis and motion.
- The combination is easiest to read when the Mermaid diagram stays simple and the video reinforces only one part of the story.
- A transparent WebM plus a white PNG poster remains the most practical delivery pair for Slidev review and playback.
- The Manim companion should not duplicate Mermaid's multicolor diagram style. The refined asset uses neutral cards, short gray route segments, one primary-red pulse, and a terminal output bracket so the motion stays readable beside the static Mermaid flow.
- Keep the pulse outside card borders and keep route gaps around cards. A dot parked on the source or output border reads as a still-frame defect even when the motion is technically correct.
- The current render is a 27.5 second transparent WebM with 92 alpha-on-white review frames at 0.3 second cadence. The latest validation cleared composition, crowding, resting-mobject, duration, and decoded alpha checks.
