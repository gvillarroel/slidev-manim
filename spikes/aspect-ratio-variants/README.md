# Aspect Ratio Variants

## Purpose

This spike tests how Slidev integrates with Manim videos when the same underlying idea is framed in different aspect ratios:

- a wide version for a full-slide composition,
- a tall version for a narrow sidebar or stacked layout,
- a comparison slide that keeps both variants visible at once.

The goal is to verify that the framing, spacing, and readability still hold when the video format changes, instead of forcing one fixed render to fit every slide.

## Run the Manim renders

From the repository root, run:

```bash
uv run --script spikes/aspect-ratio-variants/main.py
```

This renders the spike assets into:

```text
videos/aspect-ratio-variants/
```

Expected outputs:

```text
videos/aspect-ratio-variants/aspect-ratio-variants-wide.webm
videos/aspect-ratio-variants/aspect-ratio-variants-wide.png
videos/aspect-ratio-variants/aspect-ratio-variants-tall.webm
videos/aspect-ratio-variants/aspect-ratio-variants-tall.png
```

## Run the Slidev deck

From the repository root, run:

```bash
npx @slidev/cli spikes/aspect-ratio-variants/slides.md
```

To build the deck instead of serving it interactively:

```bash
npx @slidev/cli build spikes/aspect-ratio-variants/slides.md
```

## Learnings

- Wide and tall variants should be rendered as separate assets when the surrounding slide compositions are materially different.
- A transparent WebM remains the best live delivery format for Slidev, while a white PNG poster is useful for review and screenshot validation.
- Slidev handles the same visual idea well when the slide layout changes, as long as the framing is intentionally adapted to the target space.
- The same Manim concept can support multiple editorial contexts if the spike keeps each variant isolated and clearly documented.
