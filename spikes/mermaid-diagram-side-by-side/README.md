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
